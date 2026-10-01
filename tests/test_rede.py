from unittest.mock import MagicMock, patch

import pytest
import requests

import rede
from rede import obter


def _resposta(codigo=200):
    r = MagicMock()
    r.status_code = codigo
    if codigo >= 400:
        r.raise_for_status.side_effect = requests.HTTPError(response=r)
    else:
        r.raise_for_status.return_value = None
    return r


def _sessao_falsa(*respostas):
    s = MagicMock()
    s.get.side_effect = list(respostas)
    return s


@patch("rede.sleep")
def test_retry_em_timeout(_sleep):
    s = _sessao_falsa(requests.Timeout(), _resposta(200))
    with patch("rede._sessao", return_value=s):
        obter("https://exemplo.pt/rss")
    assert s.get.call_count == 2


@patch("rede.sleep")
def test_retry_em_503(_sleep):
    s = _sessao_falsa(_resposta(503), _resposta(200))
    with patch("rede._sessao", return_value=s):
        obter("https://exemplo.pt/rss")
    assert s.get.call_count == 2


def test_nao_retry_em_404():
    s = _sessao_falsa(_resposta(404))
    with patch("rede._sessao", return_value=s):
        with pytest.raises(requests.HTTPError):
            obter("https://exemplo.pt/rss")
    assert s.get.call_count == 1


@patch("rede.sleep")
def test_desiste_ao_fim_das_tentativas(_sleep):
    s = _sessao_falsa(*[requests.ConnectionError()] * rede.TENTATIVAS)
    with patch("rede._sessao", return_value=s):
        with pytest.raises(requests.ConnectionError):
            obter("https://exemplo.pt/rss")
    assert s.get.call_count == rede.TENTATIVAS


def test_mesma_sessao_na_mesma_thread():
    assert rede._sessao() is rede._sessao()


def test_limite_por_site():
    assert rede._limite("https://www.vercapas.com/a") is rede._limite("https://www.vercapas.com/b")
    assert rede._limite("https://www.vercapas.com/a") is not rede._limite("https://www.rtp.pt/rss")
