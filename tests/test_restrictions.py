"""Certificado conservador de restricciones de OpenCode y su uso en `run`."""

from __future__ import annotations

from typing import Any

import pytest
import restrictions

from tests.conftest import Harness
from tests.fakes import DEFAULT_MODEL, api_model, variant

PROVIDER_DENY: dict[str, Any] = {
    "action": "provider.use",
    "resource": "openai",
    "effect": "deny",
}
TOOL_DENY: dict[str, Any] = {
    "action": "tool.use",
    "resource": "subagent:*",
    "effect": "deny",
}


def rule(action: str, resource: str, effect: str) -> dict[str, Any]:
    return {"action": action, "resource": resource, "effect": effect}


def document(info: dict[str, Any]) -> dict[str, Any]:
    return {"type": "document", "path": "C:/cfg/opencode.json", "info": info}


def directory() -> dict[str, Any]:
    return {"type": "directory", "path": "C:/cfg/opencode"}


def test_certifica_los_dos_bloqueos_en_un_documento() -> None:
    payload = [document({"policies": [PROVIDER_DENY, TOOL_DENY]})]
    assert restrictions.configuration_is_restricted(payload) is True


def test_certifica_bloqueos_repartidos_entre_documentos() -> None:
    payload = [
        document({"policies": [PROVIDER_DENY]}),
        directory(),
        document({"policies": [TOOL_DENY]}),
    ]
    assert restrictions.configuration_is_restricted(payload) is True


def test_certifica_solo_configuracion_global_sin_archivo_local() -> None:
    payload = [document({"policies": [PROVIDER_DENY, TOOL_DENY]})]
    assert restrictions.configuration_is_restricted(payload) is True


def test_certifica_policies_experimentales() -> None:
    payload = [document({"experimental": {"policies": [PROVIDER_DENY, TOOL_DENY]}})]
    assert restrictions.configuration_is_restricted(payload) is True


def test_certifica_policies_heredadas_junto_a_las_heredadas_por_defecto() -> None:
    payload = [
        document(
            {
                "policies": [PROVIDER_DENY],
                "experimental": {"policies": [TOOL_DENY]},
            }
        )
    ]
    assert restrictions.configuration_is_restricted(payload) is True


def test_una_fuente_sin_politicas_no_invalida_el_certificado() -> None:
    payload = [
        document({"plugins": ["superpowers"]}),
        directory(),
        document({"policies": [PROVIDER_DENY, TOOL_DENY]}),
    ]
    assert restrictions.configuration_is_restricted(payload) is True


@pytest.mark.parametrize(
    "rules",
    [
        pytest.param([], id="sin-politicas"),
        pytest.param([PROVIDER_DENY], id="sin-bloqueo-de-herramienta"),
        pytest.param([TOOL_DENY], id="sin-bloqueo-de-proveedor"),
    ],
)
def test_sin_los_dos_bloqueos_no_hay_certificado(rules: list[dict[str, Any]]) -> None:
    assert (
        restrictions.configuration_is_restricted([document({"policies": rules})])
        is False
    )


@pytest.mark.parametrize(
    "resource",
    [
        pytest.param("openai", id="exacto"),
        pytest.param("open*", id="asterisco-final"),
        pytest.param("*", id="todo"),
        pytest.param("*openai*", id="contiene"),
        pytest.param("?penai", id="interrogacion-inicial"),
        pytest.param("open?i", id="interrogacion-media"),
    ],
)
def test_allow_de_proveedor_que_casa_openai_invalida(resource: str) -> None:
    payload = [
        document(
            {
                "policies": [
                    PROVIDER_DENY,
                    TOOL_DENY,
                    rule("provider.use", resource, "allow"),
                ]
            }
        )
    ]
    assert restrictions.configuration_is_restricted(payload) is False


def test_allow_de_proveedor_anterior_al_deny_invalida() -> None:
    payload = [
        document(
            {
                "policies": [
                    rule("provider.use", "openai", "allow"),
                    PROVIDER_DENY,
                    TOOL_DENY,
                ]
            }
        )
    ]
    assert restrictions.configuration_is_restricted(payload) is False


def test_allow_de_proveedor_en_otra_fuente_invalida() -> None:
    payload = [
        document({"policies": [rule("provider.use", "openai", "allow")]}),
        document({"policies": [PROVIDER_DENY, TOOL_DENY]}),
    ]
    assert restrictions.configuration_is_restricted(payload) is False


def test_allow_de_proveedor_ajeno_no_invalida() -> None:
    payload = [
        document(
            {
                "policies": [
                    PROVIDER_DENY,
                    TOOL_DENY,
                    rule("provider.use", "anthropic", "allow"),
                ]
            }
        )
    ]
    assert restrictions.configuration_is_restricted(payload) is True


@pytest.mark.parametrize(
    "resource",
    [
        pytest.param("subagent:general", id="general"),
        pytest.param("subagent:*", id="asterisco"),
        pytest.param("subagent", id="sin-dos-puntos"),
        pytest.param("sub*", id="prefijo-ambiguo"),
        pytest.param("?ubagent:*", id="interrogacion"),
    ],
)
def test_allow_de_herramienta_ambigua_invalida(resource: str) -> None:
    payload = [
        document(
            {
                "policies": [
                    PROVIDER_DENY,
                    TOOL_DENY,
                    rule("tool.use", resource, "allow"),
                ]
            }
        )
    ]
    assert restrictions.configuration_is_restricted(payload) is False


def test_allow_de_herramienta_no_relacionada_permite_ejecutar() -> None:
    payload = [
        document(
            {
                "policies": [
                    PROVIDER_DENY,
                    TOOL_DENY,
                    rule("tool.use", "shell:*", "allow"),
                ]
            }
        )
    ]
    assert restrictions.configuration_is_restricted(payload) is True


def test_allow_de_integracion_no_afecta_el_certificado() -> None:
    payload = [
        document(
            {
                "policies": [
                    PROVIDER_DENY,
                    TOOL_DENY,
                    rule("integration.use", "mcp:*", "allow"),
                ]
            }
        )
    ]
    assert restrictions.configuration_is_restricted(payload) is True


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="no-lista"),
        pytest.param([], id="lista-vacia"),
        pytest.param("texto", id="cadena"),
        pytest.param([{"path": "C:/cfg"}], id="sin-tipo"),
        pytest.param([{"type": "managed", "info": {}}], id="tipo-desconocido"),
        pytest.param([{"type": "document", "path": "C:/cfg"}], id="documento-sin-info"),
        pytest.param([{"type": "document", "info": []}], id="info-no-objeto"),
        pytest.param([{"type": "directory", "info": {}}], id="directorio-con-info"),
        pytest.param(
            [{"type": "document", "info": {"policies": {}}}], id="policies-no-lista"
        ),
        pytest.param(
            [{"type": "document", "info": {"experimental": []}}],
            id="experimental-no-objeto",
        ),
    ],
)
def test_formatos_desconocidos_o_malformados_no_certifican(payload: object) -> None:
    assert restrictions.configuration_is_restricted(payload) is False


@pytest.mark.parametrize(
    "malformed",
    [
        pytest.param(
            {"action": "provider.use", "resource": "openai"}, id="sin-clave-efecto"
        ),
        pytest.param(
            {
                "action": "provider.use",
                "resource": "openai",
                "effect": "deny",
                "motivo": "extra",
            },
            id="clave-extra",
        ),
        pytest.param(
            {"action": "provider.use", "resource": 7, "effect": "deny"},
            id="recurso-no-texto",
        ),
        pytest.param(
            {"action": "provider.use", "resource": "openai", "effect": "quizá"},
            id="efecto-desconocido",
        ),
        pytest.param(
            {"action": "otro.use", "resource": "openai", "effect": "deny"},
            id="accion-desconocida",
        ),
    ],
)
def test_una_regla_malformada_no_certifica(malformed: dict[str, Any]) -> None:
    payload = [document({"policies": [malformed, TOOL_DENY]})]
    assert restrictions.configuration_is_restricted(payload) is False


def test_run_rechaza_un_destino_sin_bloqueos_acreditados(harness: Harness) -> None:
    transport = harness.fake(config_sources=[document({"policies": [PROVIDER_DENY]})])
    result = harness.run()
    assert result["code"] == "unsafe_configuration"
    assert transport.run_calls == []


def test_run_rechaza_un_allow_sobrepuesto(harness: Harness) -> None:
    transport = harness.fake(
        config_sources=[
            document(
                {
                    "policies": [
                        rule("provider.use", "openai", "allow"),
                        PROVIDER_DENY,
                        TOOL_DENY,
                    ]
                }
            )
        ]
    )
    result = harness.run()
    assert result["code"] == "unsafe_configuration"
    assert transport.run_calls == []


def test_run_falla_si_la_comprobacion_de_configuracion_falla(harness: Harness) -> None:
    transport = harness.fake(
        config_returncode=4,
        config_stdout="TOKEN=secreto-config",
        config_stderr="fallo TOKEN=secreto-config-stderr",
    )
    result = harness.run()
    assert result["code"] == "config_check_failed"
    assert transport.run_calls == []
    assert "secreto-config" not in result["message"]
    assert "secreto-config-stderr" not in result["message"]


def test_run_falla_con_json_de_configuracion_invalido(harness: Harness) -> None:
    transport = harness.fake(config_stdout="{no es json TOKEN=secreto-config")
    result = harness.run()
    assert result["code"] == "config_check_failed"
    assert transport.run_calls == []
    assert "secreto-config" not in result["message"]


def test_run_admite_un_destino_configurado_correctamente(harness: Harness) -> None:
    transport = harness.fake()
    result = harness.run()
    assert result["status"] == "ok"
    assert len(transport.run_calls) == 1


def test_la_comprobacion_ocurre_antes_del_catalogo_y_de_la_ejecucion(
    harness: Harness,
) -> None:
    transport = harness.fake()
    assert harness.run()["status"] == "ok"
    assert harness.binding is not None
    assert [kind for kind, _path in harness.binding.calls] == [
        "config",
        "openapi",
        "integrations",
        "catalog",
        "usage",
    ]
    assert {path for _kind, path in harness.binding.calls if path is not None} == {
        harness.project.resolve()
    }
    assert len(transport.run_calls) == 1


def test_la_comprobacion_conserva_los_errores_explicitos_de_seleccion(
    harness: Harness,
) -> None:
    harness.fake(models=[api_model(variants=[variant("high")])])
    result = harness.run(model=DEFAULT_MODEL + "#inexistente")
    assert result["code"] == "invalid_variant"


def test_la_comprobacion_no_omite_la_seleccion_de_variante(harness: Harness) -> None:
    harness.fake(models=[api_model(variants=[variant("high")])])
    result = harness.run(model=DEFAULT_MODEL + "#high")
    assert result["status"] == "ok"
    assert result["variant"] == "high"
    assert result["effort"] == "high"


def test_el_gpt_de_opencode_go_sigue_disponible(harness: Harness) -> None:
    harness.fake(models=[api_model("gpt-5-codex", provider="opencode-go")])
    result = harness.run(model="opencode-go/gpt-5-codex")
    assert result["status"] == "ok"


def test_doctor_no_exige_certificado_de_restricciones(harness: Harness) -> None:
    harness.fake(config_sources=[document({"policies": []})])
    result = harness.doctor()
    assert result["status"] == "ok"
    assert harness.binding is not None
    assert harness.binding.config_calls == [harness.project.resolve()]
