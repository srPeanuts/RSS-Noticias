from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from enviar_email import dados_sao_de_hoje, deve_enviar

LISBOA = ZoneInfo("Europe/Lisbon")


def test_schedule_so_as_9h():
    assert deve_enviar(datetime(2026, 1, 15, 9, 30, tzinfo=LISBOA), "schedule") is True
    assert deve_enviar(datetime(2026, 1, 15, 8, 30, tzinfo=LISBOA), "schedule") is False


def test_workflow_run_so_na_primeira_atualizacao():
    assert deve_enviar(datetime(2026, 1, 15, 6, 10, tzinfo=LISBOA), "workflow_run") is True
    assert deve_enviar(datetime(2026, 7, 15, 7, 10, tzinfo=LISBOA), "workflow_run") is True
    assert deve_enviar(datetime(2026, 1, 15, 9, 10, tzinfo=LISBOA), "workflow_run") is False


def test_dispatch_envia_a_qualquer_hora():
    assert deve_enviar(datetime(2026, 1, 15, 15, 0, tzinfo=LISBOA), "workflow_dispatch") is True


@patch("enviar_email.ler", return_value={"hoje": "2026-09-28"})
def test_dados_sao_de_hoje(_ler):
    assert dados_sao_de_hoje(datetime(2026, 9, 28, 10, 0, tzinfo=LISBOA)) is True
    assert dados_sao_de_hoje(datetime(2026, 9, 27, 10, 0, tzinfo=LISBOA)) is False
