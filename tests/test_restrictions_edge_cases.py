"""Regresiones de los hallazgos de revisión sobre el certificado.

Cubre la semántica de comodines documentada por OpenCode, los tipos de fuente
no textuales y la diferencia entre ausencia y valor `null` en las políticas.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
import restrictions

from tests.conftest import Harness
from tests.fakes import deny_provider, deny_subagent, policy_rule


def document(info: dict[str, Any]) -> dict[str, Any]:
    return {"type": "document", "path": "C:/cfg/opencode.json", "info": info}


def bloqueos() -> dict[str, Any]:
    return {"policies": [deny_provider(), deny_subagent()]}


@pytest.mark.parametrize(
    ("pattern", "value", "expected"),
    [
        pytest.param(
            "openai *",
            "openai",
            True,
            id="sufijo-con-espacio-cubre-sin-argumentos",
        ),
        pytest.param(
            "openai *",
            "openai gpt-5",
            True,
            id="sufijo-con-espacio-cubre-con-argumentos",
        ),
        pytest.param(
            "openai *",
            "openaiX",
            False,
            id="sufijo-con-espacio-no-une-sin-espacio",
        ),
        pytest.param(
            "open?i *",
            "openai",
            True,
            id="interrogacion-con-sufijo",
        ),
        pytest.param(
            "* *",
            "openai",
            True,
            id="comodines-con-sufijo",
        ),
        pytest.param(
            "openai",
            "openai",
            True,
            id="literal",
        ),
        pytest.param(
            "open[a]i",
            "openai",
            False,
            id="corchetes-no-son-comodines",
        ),
        pytest.param(
            "open[a]i",
            "open[a]i",
            True,
            id="corchetes-literales-iguales",
        ),
    ],
)
def test_el_comodinal_final_cubre_el_valor_sin_argumentos(
    pattern: str, value: str, expected: bool
) -> None:
    assert restrictions._pattern_matches(pattern, value) is expected


def test_un_allow_de_proveedor_con_sufijo_invalida_el_certificado() -> None:
    payload = [
        document(
            {
                "policies": [
                    deny_provider(),
                    deny_subagent(),
                    policy_rule("provider.use", "openai *", "allow"),
                ]
            }
        )
    ]
    assert restrictions.configuration_is_restricted(payload) is False


@pytest.mark.parametrize(
    "source_type",
    [
        pytest.param([], id="lista"),
        pytest.param({}, id="mapa"),
    ],
)
def test_un_tipo_de_fuente_no_textual_no_certifica(source_type: object) -> None:
    assert restrictions.configuration_is_restricted([{"type": source_type}]) is False


def test_run_rechaza_un_tipo_de_fuente_no_textual(harness: Harness) -> None:
    stdout = json.dumps([{"type": [], "path": "TOKEN=secreto-config"}])
    transport = harness.fake(config_stdout=stdout)
    result = harness.run()
    assert result["code"] == "unsafe_configuration"
    assert transport.run_calls == []
    assert list(result) == ["status", "code", "message"]
    assert "secreto-config" not in result["message"]
    assert json.dumps(result, sort_keys=True) == json.dumps(
        harness.run(), sort_keys=True
    )


@pytest.mark.parametrize(
    "info",
    [
        pytest.param({"policies": None}, id="policies-nulas"),
        pytest.param({"experimental": None}, id="experimental-nulo"),
        pytest.param(
            {"experimental": {"policies": None}}, id="policies-experimentales-nulas"
        ),
    ],
)
def test_un_valor_nulo_invalida_el_certificado(info: dict[str, Any]) -> None:
    payload = [document(info), document(bloqueos())]
    assert restrictions.configuration_is_restricted(payload) is False


def test_la_ausencia_de_policies_no_invalida_el_certificado() -> None:
    payload = [document({"plugins": ["superpowers"]}), document(bloqueos())]
    assert restrictions.configuration_is_restricted(payload) is True


def test_run_rechaza_un_valor_nulo_en_las_politicas(harness: Harness) -> None:
    transport = harness.fake(
        config_sources=[document({"policies": None}), document(bloqueos())]
    )
    result = harness.run()
    assert result["code"] == "unsafe_configuration"
    assert transport.run_calls == []
    assert "secreto" not in result["message"]
