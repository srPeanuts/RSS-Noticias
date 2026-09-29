from unittest.mock import MagicMock, patch

import pytest
import requests

from rede import obter


def _resposta(codigo=200):
    r = MagicMock()
    r.status_code = codigo
    if codigo >= 400:
        r.raise_for_status.side_effect = requests.HTTPError(response=r)
    else:
        r.raise_for_status.return_value = None
    return r


@patch("rede.sleep")
@patch("rede.requests.get")
def test_retry_em_timeout(mock_get, _sleep):
    mock_get.side_effect = [requests.Timeout(), _resposta(200)]
    obter("https://exemplo.pt/rss")
    assert mock_get.call_count == 2


@patch("rede.sleep")
@patch("rede.requests.get")
def test_retry_em_503(mock_get, _sleep):
    mock_get.side_effect = [_resposta(503), _resposta(200)]
    obter("https://exemplo.pt/rss")
    assert mock_get.call_count == 2


@patch("rede.requests.get")
def test_nao_retry_em_404(mock_get):
    mock_get.return_value = _resposta(404)
    with pytest.raises(requests.HTTPError):
        obter("https://exemplo.pt/rss")
    assert mock_get.call_count == 1
