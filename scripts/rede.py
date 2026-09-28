"""Pedidos HTTP com retries para falhas temporárias (timeout, 429, 5xx)."""

from time import sleep

import requests

CABECALHOS = {"User-Agent": "Mozilla/5.0 (compatible; NoticiasPT/1.0; uso pessoal)"}
CODIGOS_RETRY = {408, 425, 429, 500, 502, 503, 504}


def obter(url: str, *, params=None, timeout=25, tentativas=3) -> requests.Response:
    """GET com 2–3 tentativas e espera crescente. Não insiste em 403/404."""
    ultimo = None
    for i in range(tentativas):
        try:
            r = requests.get(url, headers=CABECALHOS, params=params, timeout=timeout)
            r.raise_for_status()
            return r
        except requests.HTTPError as e:
            ultimo = e
            codigo = getattr(e.response, "status_code", 0) or 0
            if codigo not in CODIGOS_RETRY or i == tentativas - 1:
                raise
        except requests.RequestException as e:
            ultimo = e
            if i == tentativas - 1:
                raise
        sleep(1.5 * (i + 1))
    raise ultimo
