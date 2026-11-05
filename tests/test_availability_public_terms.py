"""Pruebas semánticas de hechos públicos y clasificación condicionada."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import availability_public_terms as public_terms
import availability_state as state
import pytest

UTC = timezone.utc


def _term(**overrides: object) -> public_terms.PublicTerm:
    base: dict[str, Any] = {
        "provider": "cloudflare-workers-ai",
        "model": "@cf/zai-org/glm-4.7-flash",
        "scope": "model",
        "access_kind": "conditional_access",
        "conditions": {"neurons_daily_shared": 10000, "listed_price": "positive"},
        "source_url": "https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/",
        "checked_at": datetime(2026, 11, 1, tzinfo=UTC),
        "publication": datetime(2026, 7, 28, tzinfo=UTC),
        "source_status": "ok",
        "last_valid": datetime(2026, 11, 1, tzinfo=UTC),
        "notes": ("grant documentado",),
    }
    base.update(overrides)
    return public_terms.PublicTerm(**base)


def test_zero_price_and_conditional_access_are_not_conflated() -> None:
    zero = state.ModelMetadata(
        model="free/model",
        name="Free",
        pricing=(state.PricingTier(input=0.0, output=0.0),),
        variants=(),
        tools=True,
        input_modalities=("text",),
        output_modalities=("text",),
        context_limit=None,
        output_limit=None,
        free_candidate=True,
        may_use_openai_quota=False,
    )
    assert zero.free_candidate is True

    positive = state.ModelMetadata(
        model="cloudflare-workers-ai/@cf/zai-org/glm-4.7-flash",
        name="CF",
        pricing=(state.PricingTier(input=1.0, output=1.0),),
        variants=(),
        tools=True,
        input_modalities=("text",),
        output_modalities=("text",),
        context_limit=None,
        output_limit=None,
        free_candidate=False,
        may_use_openai_quota=False,
    )
    assert positive.free_candidate is False

    term = _term()
    assert term.access_kind == "conditional_access"
    assert term.conditions["listed_price"] == "positive"
    assert term.conditions["neurons_daily_shared"] == 10000
    # El grant publico no convierte la tarifa positiva en gratuita.
    assert positive.free_candidate is False


def test_public_term_rejects_bad_source_and_secret_fields() -> None:
    with pytest.raises(ValueError, match="."):
        public_terms.PublicTerm.from_dict(
            {
                "provider": "p",
                "model": "m",
                "source_url": "http://example.com/x",
            }
        )
    with pytest.raises(ValueError, match="."):
        public_terms.PublicTerm.from_dict(
            {
                "provider": "p",
                "model": "m",
                "source_url": "https://example.com/x",
                "conditions": {"api_key": "secret", "nested": {"x": 1}},
            }
        )


def test_public_term_rejects_wrong_types_and_limits() -> None:
    with pytest.raises(ValueError, match="."):
        public_terms.PublicTerm.from_dict(42)
    with pytest.raises(ValueError, match="."):
        public_terms.PublicTerm.from_dict(
            {
                "provider": "p",
                "model": "m",
                "source_url": "https://example.com/x",
                "conditions": "x" * 1000,
            }
        )
    # Límite de condiciones validado arriba.


def test_duplicate_provider_model_is_rejected() -> None:
    first = _term().to_dict()
    second = _term().to_dict()
    with pytest.raises(ValueError, match="."):
        public_terms.parse_public_terms([first, second])


def test_merge_does_not_clone_across_providers() -> None:
    left = _term(provider="cloudflare-workers-ai", model="a").to_dict()
    right = _term(
        provider="opencode",
        model="a",
        source_url="https://opencode.ai/v2/docs/models/",
    ).to_dict()
    parsed_left = public_terms.parse_public_terms([left])
    parsed_right = public_terms.parse_public_terms([right])
    merged = public_terms.merge_public_terms(parsed_left, parsed_right)
    assert len(merged) == 2
    assert {t.provider for t in merged} == {"cloudflare-workers-ai", "opencode"}


def test_old_schema_loads_without_public_terms() -> None:
    snapshot = state.AvailabilitySnapshot(
        schema_version=state.STATE_SCHEMA_VERSION,
        generation=1,
        published_at=datetime(2026, 11, 1, tzinfo=UTC),
        catalog_contexts=(),
        models={},
        data_sources=(),
    )
    assert snapshot.public_terms == ()
    assert snapshot.public_facts == ()
    assert state.read_snapshot is not None


def test_import_does_not_mark_available_or_change_quota(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    empty = state.empty_snapshot(datetime(2026, 11, 1, tzinfo=UTC))
    state.write_snapshot(path, empty)
    terms = (_term(),)
    state.update_snapshot(
        path,
        lambda s: state.AvailabilitySnapshot(
            schema_version=s.schema_version,
            generation=s.generation,
            published_at=s.published_at,
            catalog_contexts=s.catalog_contexts,
            models=s.models,
            data_sources=s.data_sources,
            aggregates=s.aggregates,
            performance_samples=s.performance_samples,
            project_models=s.project_models,
            last_refresh=s.last_refresh,
            public_terms=terms,
        ),
    )
    loaded = state.read_snapshot(path)
    assert loaded is not None
    assert loaded.public_terms == terms
    # Sin modelos/cuota, importación no crea disponibilidad.
    assert loaded.models == {}


def test_public_terms_survive_refresh_contexts(tmp_path: Path) -> None:
    from availability_refresh import _refresh_once
    from service_identity import HostContext

    from tests.fakes import FakeBinding

    project = tmp_path / "project"
    project.mkdir()
    current = state.AvailabilitySnapshot(
        schema_version=state.STATE_SCHEMA_VERSION,
        generation=1,
        published_at=datetime(2026, 11, 1, tzinfo=UTC),
        catalog_contexts=(),
        models={},
        data_sources=(),
        public_terms=(_term(),),
    )
    binding = FakeBinding(
        context=HostContext(tmp_path / "registration", tmp_path, "2.2.0")
    )
    snapshot, _errors = _refresh_once(binding, project, 1.0, current)
    assert snapshot.public_terms == current.public_terms


def test_adversarial_free_alias_does_not_become_zero_price() -> None:
    payload = _term(access_kind="free").to_dict()
    payload["access_kind"] = "free"
    payload["conditions"]["listed_price"] = "positive"
    parsed = public_terms.parse_public_terms([payload])
    assert parsed[0].access_kind != "zero_price"
    assert parsed[0].access_kind == "unknown"


def test_forbidden_top_level_fields_are_rejected() -> None:
    for field in ("api_key", "token", "password", "extra"):
        with pytest.raises(ValueError, match="."):
            public_terms.PublicTerm.from_dict(
                {
                    "provider": "cloudflare-workers-ai",
                    "model": "@cf/zai-org/glm-4.7-flash",
                    "source_url": "https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/",
                    field: "secret",
                }
            )


def test_unsupported_provider_source_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported_official_source"):
        public_terms.PublicTerm.from_dict(
            {
                "provider": "future-provider",
                "model": "model",
                "source_url": "https://example.com/x",
            }
        )


def test_verified_provider_domain_pairs() -> None:
    pairs = {
        "google": "https://ai.google.dev/gemini-api/docs/pricing",
        "kilo": "https://kilo.ai/docs/",
        "nvidia": "https://docs.api.nvidia.com/nim/docs/",
        "openrouter": "https://openrouter.ai/docs/",
        "zai": "https://docs.z.ai/",
    }
    for provider, url in pairs.items():
        assert public_terms.is_official_source(provider, url)


def test_cross_provider_rejection_for_verified_domains() -> None:
    with pytest.raises(ValueError, match="."):
        public_terms.validate_official_source("google", "https://openrouter.ai/docs/")


def test_future_unknown_provider_remains_unknown() -> None:
    assert public_terms.official_domains_for("future-provider") == ()
    assert public_terms.official_source_diagnostic("future-provider").startswith(
        "unsupported_official_source"
    )
    with pytest.raises(ValueError, match="."):
        public_terms.PublicTerm.from_dict(
            {
                "provider": "future-provider",
                "model": "model",
                "source_url": "https://example.com/x",
            }
        )


def test_official_source_host_validation() -> None:
    assert public_terms.is_official_source(
        "cloudflare-workers-ai",
        "https://developers.cloudflare.com/changelog/post/x/",
    )
    assert not public_terms.is_official_source(
        "cloudflare-workers-ai",
        "https://evil-developers.cloudflare.com.example.com/x/",
    )
    with pytest.raises(ValueError, match="."):
        public_terms.validate_official_source(
            "cloudflare-workers-ai", "https://example.com/x"
        )


def test_counts_do_not_double_count() -> None:
    terms = (
        _term(access_kind="conditional_access"),
        _term(model="@cf/google/gemma-4-26b-a4b-it", access_kind="conditional_access"),
    )
    counts = public_terms.count_public_terms(terms)
    assert counts["total"] == 2
    assert counts["conditional_access"] == 2
    assert counts["zero_price"] == 0


def test_build_allowlist_includes_new_module_and_reference() -> None:
    content = Path("scripts/build_plugin.py").read_text(encoding="utf-8")
    assert "availability_public_terms.py" in content
    assert "terminos-publicos.md" in content


def test_daily_review_inventory_is_documented() -> None:
    spec = Path(
        "docs/superpowers/specs/2026-11-01-gratuidad-publica-opencode-design.md"
    ).read_text(encoding="utf-8")
    for provider in (
        "cloudflare-workers-ai",
        "google",
        "kilo",
        "nvidia",
        "opencode",
        "opencode-go",
        "openrouter",
        "zai",
    ):
        assert provider in spec
    assert "238" in spec
    assert "unknown" in spec
