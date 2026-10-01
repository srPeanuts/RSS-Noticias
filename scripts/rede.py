"""Pedidos HTTP com retries para falhas temporárias (timeout, 429, 5xx).

- Cada thread reutiliza a mesma ligação (requests.Session, "keep-alive"), o que poupa tempo
  quando se pedem várias páginas ao mesmo site (as 14 capas do VerCapas, os 4 feeds da RTP...).
- No máximo POR_SITE pedidos em simultâneo ao mesmo site, para não sobrecarregar ninguém.
- Timeouts curtos: um site em baixo deixa de prender a recolha durante muito tempo.
"""

import threading
from collections import defaultdict
from time import sleep
from urllib.parse import urlsplit

import requests

CABECALHOS = {"User-Agent": "Mozilla/5.0 (compatible; NoticiasPT/1.0; uso pessoal)"}
CODIGOS_RETRY = {408, 425, 429, 500, 502, 503, 504}
TIMEOUT = (5, 15)        # (segundos para ligar, segundos à espera de resposta)
TENTATIVAS = 2
POR_SITE = 4

_local = threading.local()
_trinco = threading.Lock()
_limites = defaultdict(lambda: threading.BoundedSemaphore(POR_SITE))


def _sessao() -> requests.Session:
    """Uma Session por thread (a Session não é garantidamente segura entre threads)."""
    s = getattr(_local, "sessao", None)
    if s is None:
        s = requests.Session()
        s.headers.update(CABECALHOS)
        _local.sessao = s
    return s


def _limite(url: str) -> threading.BoundedSemaphore:
    with _trinco:
        return _limites[urlsplit(url).hostname or ""]


def obter(url: str, *, params=None, timeout=TIMEOUT, tentativas=TENTATIVAS) -> requests.Response:
    """GET com tentativas e espera crescente. Não insiste em 403/404."""
    ultimo = None
    for i in range(tentativas):
        try:
            with _limite(url):
                r = _sessao().get(url, params=params, timeout=timeout)
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
