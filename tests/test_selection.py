"""Selección explícita de modelo y variante."""

from __future__ import annotations

import pytest

from tests.conftest import Harness
from tests.fakes import DEFAULT_MODEL, FREE_COST, api_model, variant


@pytest.mark.parametrize(
    ("model", "reason", "code"),
    [
        pytest.param(None, "motivo", "model_required", id="modelo-ausente"),
        pytest.param("  ", "motivo", "model_required", id="modelo-vacio"),
        pytest.param(DEFAULT_MODEL, None, "reason_required", id="motivo-ausente"),
        pytest.param(DEFAULT_MODEL, " \t ", "reason_required", id="motivo-vacio"),
    ],
)
def test_required_selection_precedes_process(
    harness: Harness, model: str | None, reason: str | None, code: str
) -> None:
    transport = harness.fake()
    assert harness.run(model=model, reason=reason)["code"] == code
    assert transport.calls == []


@pytest.mark.parametrize(
    ("model", "variant_name"),
    [
        pytest.param("openai/gpt-5.3", None, id="directo"),
        pytest.param("openai/gpt-5.3#high", None, id="incrustada"),
        pytest.param("openai/gpt-5.3", "high", id="flag"),
        pytest.param(" OPENAI /gpt-5.3#HIGH", None, id="mayusculas"),
    ],
)
def test_direct_openai_rejected_before_process(
    harness: Harness, model: str, variant_name: str | None
) -> None:
    transport = harness.fake(
        models=[api_model("gpt-5.3", provider="openai", variants=[variant("high")])]
    )
    result = harness.run(model=model, variant=variant_name)
    assert result["code"] == "provider_not_allowed"
    assert transport.calls == []


@pytest.mark.parametrize(
    "filter_model",
    ["openai/gpt-6.1-sol", "OPENAI/gpt-6.1-sol", " OpenAI /gpt-6.1-sol"],
)
def test_direct_openai_doctor_filter_precedes_process(
    harness: Harness, filter_model: str
) -> None:
    transport = harness.fake()
    assert harness.doctor(model=filter_model)["code"] == "provider_not_allowed"
    assert transport.calls == []


@pytest.mark.parametrize(
    "full_model",
    ["opencode/gpt-6.1-sol#high", "opencode-go/openai/gpt-6.1-sol#high"],
)
def test_third_party_gpt_and_canonical_allowed(
    harness: Harness, full_model: str
) -> None:
    transport = harness.fake(
        models=[
            api_model(
                "gpt-6.1-sol",
                provider="opencode",
                canonical="openai",
                variants=[variant("high", reasoningEffort="high")],
                cost={"input": 3, "output": 15},
            ),
            api_model(
                "openai/gpt-6.1-sol",
                provider="opencode-go",
                canonical="openai",
                variants=[variant("high", reasoningEffort="high")],
                cost={"input": 2, "output": 10},
            ),
        ]
    )
    assert harness.run(model=full_model)["status"] == "ok"
    assert transport.run_calls[0].argv[3] == full_model


@pytest.mark.parametrize("model", ["opencode/apagado", "opencode/ausente"])
def test_disabled_or_absent_model_not_run(harness: Harness, model: str) -> None:
    transport = harness.fake(models=[api_model("apagado", enabled=False)])
    assert harness.run(model=model)["code"] == "model_unavailable"
    assert transport.run_calls == []


@pytest.mark.parametrize(
    ("model", "variant_name"),
    [(DEFAULT_MODEL + "#max", None), (DEFAULT_MODEL, "max")],
    ids=["incrustada", "flag"],
)
def test_unknown_variant_not_run(
    harness: Harness, model: str, variant_name: str | None
) -> None:
    transport = harness.fake(models=[api_model(variants=[variant("high")])])
    assert harness.run(model=model, variant=variant_name)["code"] == "invalid_variant"
    assert transport.run_calls == []


def test_embedded_variant_reports_effort(harness: Harness) -> None:
    transport = harness.fake(
        models=[
            api_model(
                variants=[variant("low"), variant("high", reasoningEffort="high")]
            )
        ]
    )
    result = harness.run(model=DEFAULT_MODEL + "#high")
    assert (result["status"], result["model"], result["variant"], result["effort"]) == (
        "ok",
        DEFAULT_MODEL,
        "high",
        "high",
    )
    assert result["reason"] == "tarea mecánica con herramientas de texto"
    assert transport.run_calls[0].argv[3] == DEFAULT_MODEL + "#high"


def test_model_without_variant_uses_provider_default(harness: Harness) -> None:
    transport = harness.fake(models=[api_model(variants=[])])
    result = harness.run(reason="uso el ajuste predeterminado")
    assert (result["status"], result["variant"], result["effort"], result["model"]) == (
        "ok",
        None,
        "provider_default",
        DEFAULT_MODEL,
    )
    assert transport.run_calls[0].argv[3] == DEFAULT_MODEL


def test_conflicting_variant_precedes_process(harness: Harness) -> None:
    transport = harness.fake()
    assert (
        harness.run(model=DEFAULT_MODEL + "#high", variant="low")["code"]
        == "variant_conflict"
    )
    assert transport.calls == []


def test_variant_flag_is_validated_and_appended(harness: Harness) -> None:
    transport = harness.fake(models=[api_model(variants=[variant("high")])])
    assert harness.run(variant="high")["status"] == "ok"
    assert transport.run_calls[0].argv[3] == DEFAULT_MODEL + "#high"


def test_no_local_config_allows_paid_model(harness: Harness) -> None:
    assert not (harness.project / "opencode.json").exists()
    transport = harness.fake(
        models=[
            api_model(
                "gpt-6.1-sol", provider="opencode-go", cost={"input": 1, "output": 2}
            )
        ]
    )
    result = harness.run(model="opencode-go/gpt-6.1-sol", reason="pago autorizado")
    assert result["status"] == "ok"
    assert len(transport.run_calls) == 1


def test_connected_free_model_needs_no_name_suffix(harness: Harness) -> None:
    transport = harness.fake(
        models=[api_model("modelo-local", provider="proveedor-local", cost=FREE_COST)]
    )
    assert harness.run(model="proveedor-local/modelo-local")["status"] == "ok"
    assert transport.run_calls[0].argv[3] == "proveedor-local/modelo-local"
