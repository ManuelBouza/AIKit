"""Catálogo conectado, precios y salida saneada de doctor."""

from __future__ import annotations

import json
from typing import Any

import pytest

from tests.conftest import Harness
from tests.fakes import DEFAULT_MODEL, FREE_COST, api_model, variant


def catalog_entries(harness: Harness) -> dict[str, dict[str, Any]]:
    result = harness.doctor()
    assert result["status"] == "ok"
    return {entry["model"]: entry for entry in result["catalog"]}


def test_compact_catalog_hides_model_and_variant_secrets(harness: Harness) -> None:
    harness.fake(
        models=[
            api_model(
                variants=[
                    {
                        "id": "high",
                        "settings": {
                            "reasoningEffort": "high",
                            "thinkingBudget": 4096,
                            "headers": {"Authorization": "Bearer secreto-variante"},
                            "body": {"token": "secreto-body"},
                        },
                    }
                ],
                headers={"Authorization": "Bearer secreto-modelo"},
                body={"apiKey": "secreto-api"},
                name="Modelo visible",
                capabilities={
                    "tools": True,
                    "input": ["text", "image"],
                    "output": ["text"],
                },
                limit={"context": 200000, "input": 150000, "output": 20000},
                cost={
                    "input": 1.25,
                    "output": 5.5,
                    "cache": {"read": 0.1, "write": 1.5},
                },
            )
        ]
    )
    result = harness.doctor()
    encoded = json.dumps(result, ensure_ascii=False)
    for secret in ("secreto-variante", "secreto-body", "secreto-modelo", "secreto-api"):
        assert secret not in encoded
    entry = result["catalog"][0]
    assert entry["model"] == DEFAULT_MODEL
    assert entry["name"] == "Modelo visible"
    assert entry["pricing"] == {
        "input": 1.25,
        "output": 5.5,
        "cache": {"read": 0.1, "write": 1.5},
    }
    assert entry["variants"] == [
        {"id": "high", "reasoningEffort": "high", "thinkingBudget": 4096}
    ]
    assert (entry["tools"], entry["input"], entry["output"]) == (
        True,
        ["text", "image"],
        ["text"],
    )
    assert entry["limits"] == {"context": 200000, "input": 150000, "output": 20000}


def test_direct_openai_hidden_but_third_party_gpt_retained(harness: Harness) -> None:
    harness.fake(
        models=[
            api_model("gpt-6.1-sol", provider="openai", canonical="openai"),
            api_model("gpt-6.1-sol", provider="opencode", canonical="openai"),
            api_model("openai/gpt-6.1-sol", provider="opencode-go", canonical="openai"),
            api_model("openai/gpt-6.1-sol", provider="openrouter", canonical="openai"),
        ]
    )
    entries = catalog_entries(harness)
    assert set(entries) == {
        "opencode/gpt-6.1-sol",
        "opencode-go/openai/gpt-6.1-sol",
        "openrouter/openai/gpt-6.1-sol",
    }


def test_pricing_tiers_are_complete_and_sanitized(harness: Harness) -> None:
    harness.fake(
        models=[
            api_model(
                cost=[
                    {
                        "input": 0,
                        "output": 0,
                        "cache": {"read": 0, "write": 0},
                        "headers": {"Authorization": "secreto-base"},
                        "body": {"token": "secreto-body"},
                    },
                    {
                        "tier": {
                            "type": "context",
                            "size": 32768,
                            "headers": {"Authorization": "secreto-alto"},
                        },
                        "input": 10,
                        "output": 50,
                        "cache": {"read": 1, "write": 2},
                        "settings": {"apiKey": "secreto-settings"},
                    },
                ]
            )
        ]
    )
    result = harness.doctor()
    encoded = json.dumps(result, ensure_ascii=False)
    for secret in ("secreto-base", "secreto-body", "secreto-alto", "secreto-settings"):
        assert secret not in encoded
    entry = result["catalog"][0]
    assert entry["pricing"] == {
        "input": 0,
        "output": 0,
        "cache": {"read": 0, "write": 0},
    }
    assert entry["pricing_tiers"] == [
        {"input": 0, "output": 0, "cache": {"read": 0, "write": 0}},
        {
            "tier": {"type": "context", "size": 32768},
            "input": 10,
            "output": 50,
            "cache": {"read": 1, "write": 2},
        },
    ]
    assert entry["free_candidate"] is False


def test_unknown_prices_and_quota_metadata(harness: Harness) -> None:
    harness.fake(
        models=[
            api_model("sin-precio", cost=None),
            api_model("gpt-5.3", provider="openai", cost=FREE_COST),
            api_model(
                "gpt-6.1-sol",
                provider="opencode-go",
                canonical="openai",
                cost=FREE_COST,
            ),
            api_model("modelo-gratuito", cost=FREE_COST),
        ]
    )
    entries = catalog_entries(harness)
    assert "openai/gpt-5.3" not in entries
    assert entries["opencode/sin-precio"]["pricing"] is None
    assert entries["opencode/sin-precio"]["pricing_tiers"] is None
    assert entries["opencode/sin-precio"]["free_candidate"] is None
    for model in ("opencode-go/gpt-6.1-sol", "opencode/modelo-gratuito"):
        assert entries[model]["free_candidate"] is True
        assert entries[model]["may_use_openai_quota"] is False


@pytest.mark.parametrize(
    ("model_id", "provider", "rates", "free"),
    [
        pytest.param(
            "modelo-con-tarifas", "cuenta-externa", [FREE_COST], True, id="array-cero"
        ),
        pytest.param(
            "modelo-con-tarifas",
            "cuenta-externa",
            [{"input": 0, "output": 0}, {"input": 1, "output": 2}],
            False,
            id="tier-pago",
        ),
        pytest.param(
            "modelo-con-tarifas",
            "cuenta-externa",
            [{"input": 0, "output": 0, "cache": {"read": 0.1, "write": 0}}],
            False,
            id="cache-pago",
        ),
        pytest.param(
            "parece-free",
            "opencode",
            [{"input": 1, "output": 2}],
            False,
            id="nombre-free-pago",
        ),
        pytest.param(
            "modelo-local", "proveedor-local", [FREE_COST], True, id="sin-sufijo-gratis"
        ),
    ],
)
def test_free_candidate_uses_api_rates_not_name(
    harness: Harness,
    model_id: str,
    provider: str,
    rates: list[dict[str, Any]],
    free: bool,
) -> None:
    harness.fake(
        models=[
            api_model(
                model_id,
                provider=provider,
                name="Modelo de prueba",
                variants=[variant("high", reasoningEffort="high")],
                cost=rates,
                modelID=model_id,
                time={"released": 0},
                status="active",
            )
        ]
    )
    entry = catalog_entries(harness)[f"{provider}/{model_id}"]
    assert entry["free_candidate"] is free
    assert entry["pricing"] is not None


def test_doctor_sort_count_and_filter(harness: Harness) -> None:
    harness.fake(
        models=[
            api_model("caro", cost={"input": 9, "output": 18}),
            api_model("gpt-5.3", provider="openai", cost=FREE_COST),
            api_model("zeta-free"),
            api_model("alfa-free"),
        ]
    )
    result = harness.doctor()
    assert result["catalog_count"] == 3
    assert [entry["model"] for entry in result["catalog"]] == [
        "opencode/alfa-free",
        "opencode/zeta-free",
        "opencode/caro",
    ]
    filtered = harness.doctor(model="opencode/alfa-free")
    assert filtered["catalog_count"] == 3
    assert [entry["model"] for entry in filtered["catalog"]] == ["opencode/alfa-free"]


def test_catalog_prefers_free_then_go_without_hiding_other_providers(
    harness: Harness,
) -> None:
    harness.fake(
        models=[
            api_model("paid", provider="opencode", cost={"input": 1, "output": 2}),
            api_model("unknown", provider="other", cost=None),
            api_model("paid", provider="opencode-go", cost={"input": 1, "output": 2}),
            api_model("free", provider="opencode-go", cost=FREE_COST),
            api_model("free", provider="opencode", cost=FREE_COST),
        ]
    )
    assert [item["model"] for item in harness.doctor()["catalog"]] == [
        "opencode-go/free",
        "opencode/free",
        "opencode-go/paid",
        "other/unknown",
        "opencode/paid",
    ]
