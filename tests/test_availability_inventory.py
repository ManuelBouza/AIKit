"""Tests de ciclo de vida del inventario dinámico (Note001)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import availability_refresh as ar
import availability_state as a
import delegate
import pytest
from service_identity import HostContext

from tests.fakes import FakeBinding, api_model


def _ctx(project: Path, state: Path, version: str = "2.2.0") -> HostContext:
    c = HostContext(project / "reg", state, version)
    c.aikit_state.mkdir(parents=True, exist_ok=True)
    return c


def _state_path(ctx: HostContext) -> Path:
    return a.state_path(ctx.aikit_state)


def _binding(ctx: HostContext, catalog: list[dict[str, Any]]) -> FakeBinding:
    return FakeBinding(context=ctx, catalog=catalog)


class TestInventoryLifecycle:
    """Ciclo A+B -> B(changed)+C con deltas reales."""

    def test_added_removed_changed_deltas(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        # Primera refresh: A+B
        b1 = _binding(
            ctx,
            [
                api_model(provider="p", model_id="A"),
                api_model(provider="p", model_id="B"),
            ],
        )
        r1 = ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)
        assert r1.refreshed
        assert sorted(r1.snapshot.models.keys()) == ["p/A", "p/B"]
        assert r1.changes["added"] == ("p/A", "p/B")
        assert r1.changes["removed"] == ()
        assert r1.changes["changed"] == ()
        assert r1.changes["unchanged"] == ()
        assert r1.snapshot.retired_models == {}

        # Segunda refresh: B(changed) + C
        # Cambiar metadatos de B para forzar 'changed'
        changed_b = api_model(
            provider="p", model_id="B", cost=[{"input": 99, "output": 99}]
        )
        b2 = _binding(ctx, [changed_b, api_model(provider="p", model_id="C")])
        r2 = ar.coalesced_refresh(state_path, b2, project, 5.0, force=True)
        assert r2.refreshed
        assert sorted(r2.snapshot.models.keys()) == ["p/B", "p/C"]
        assert r2.changes["added"] == ("p/C",)
        assert r2.changes["removed"] == ("p/A",)
        assert r2.changes["changed"] == ("p/B",)
        assert r2.changes["unchanged"] == ()

        # Retired debe contener A con metadata original
        retired = r2.snapshot.retired_models.get(delegate._project_key(project), {})
        assert "p/A" in retired
        assert retired["p/A"].metadata.model == "p/A"
        # A NO debe estar en models activos
        assert "p/A" not in r2.snapshot.models
        # B debe tener metadata actualizada
        assert r2.snapshot.models["p/B"].metadata.pricing[0].input == 99

    def test_repeated_identical_no_false_changes(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        catalog = [
            api_model(provider="p", model_id="A"),
            api_model(provider="p", model_id="B"),
        ]
        b1 = _binding(ctx, catalog)
        r1 = ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)
        assert r1.refreshed

        b2 = _binding(ctx, catalog)
        r2 = ar.coalesced_refresh(state_path, b2, project, 5.0, force=True)
        assert not r2.refreshed or r2.changes == {
            "added": (),
            "removed": (),
            "changed": (),
            "unchanged": ("p/A", "p/B"),
        }

    def test_model_only_additions_removals(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        b1 = _binding(ctx, [api_model(provider="p", model_id="A")])
        r1 = ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)
        assert r1.changes["added"] == ("p/A",)

        # Solo agregar
        b2 = _binding(
            ctx,
            [
                api_model(provider="p", model_id="A"),
                api_model(provider="p", model_id="B"),
            ],
        )
        r2 = ar.coalesced_refresh(state_path, b2, project, 5.0, force=True)
        assert r2.changes["added"] == ("p/B",)
        assert r2.changes["removed"] == ()

        # Solo quitar
        b3 = _binding(ctx, [api_model(provider="p", model_id="A")])
        r3 = ar.coalesced_refresh(state_path, b3, project, 5.0, force=True)
        assert r3.changes["removed"] == ("p/B",)
        assert r3.changes["added"] == ()


class TestEmptySuccessVsFailed:
    """Snapshot vacío válido vs error preserva inventario previo."""

    def test_valid_empty_catalog_is_real_empty_state(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        # Primero poblar
        b1 = _binding(ctx, [api_model(provider="p", model_id="A")])
        r1 = ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)
        assert "p/A" in r1.snapshot.models

        # Luego catálogo vacío exitoso (no error)
        b2 = _binding(ctx, [])
        r2 = ar.coalesced_refresh(state_path, b2, project, 5.0, force=True)
        assert r2.refreshed
        assert r2.snapshot.models == {}  # Estado vacío real
        assert r2.snapshot.retired_models.get(delegate._project_key(project), {}) == {
            "p/A": r1.snapshot.models["p/A"]
        }

    def test_failed_catalog_preserves_inventory_and_history(
        self, tmp_path: Path
    ) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        b1 = _binding(ctx, [api_model(provider="p", model_id="A")])
        r1 = ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)
        prev_models = dict(r1.snapshot.models)
        prev_retired = {k: dict(v) for k, v in r1.snapshot.retired_models.items()}

        # Error de catálogo
        b2 = _binding(ctx, [api_model(provider="p", model_id="B")])
        b2.catalog_returncode = 1
        r2 = ar.coalesced_refresh(state_path, b2, project, 5.0, force=True)
        assert "catalog_unavailable" in r2.errors
        assert r2.snapshot.models == prev_models
        assert {
            k: dict(v) for k, v in r2.snapshot.retired_models.items()
        } == prev_retired
        # data_sources debe reflejar el error
        assert any(
            s.name == "catalog" and s.status == "error"
            for s in r2.snapshot.data_sources
        )

    def test_malformed_response_preserves_inventory(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        b1 = _binding(ctx, [api_model(provider="p", model_id="A")])
        r1 = ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)

        # Respuesta malformada (no lista)
        class BadBinding(FakeBinding):
            def model_catalog(self, project: Path, *, timeout: float) -> object:
                return "not-a-list"

        b2 = BadBinding(ctx)
        r2 = ar.coalesced_refresh(state_path, b2, project, 5.0, force=True)
        assert r2.snapshot.models == r1.snapshot.models


class TestContextIsolation:
    """Contexto B no revoca A ni admisiones vivas."""

    def test_context_b_removal_does_not_affect_a(self, tmp_path: Path) -> None:
        project_a = tmp_path / "project_a"
        project_a.mkdir()
        project_b = tmp_path / "project_b"
        project_b.mkdir()
        state = tmp_path / "state"
        state.mkdir()

        ctx_a = _ctx(project_a, state)
        ctx_b = _ctx(project_b, state)
        state_path = _state_path(ctx_a)  # mismo archivo estado

        # Poblar A con {A1, A2}
        b_a1 = _binding(
            ctx_a,
            [
                api_model(provider="p", model_id="A1"),
                api_model(provider="p", model_id="A2"),
            ],
        )
        r_a1 = ar.coalesced_refresh(state_path, b_a1, project_a, 5.0, force=True)
        assert sorted(
            r_a1.snapshot.project_models[delegate._project_key(project_a)].keys()
        ) == ["p/A1", "p/A2"]

        # Poblar B con {B1}
        b_b1 = _binding(ctx_b, [api_model(provider="q", model_id="B1")])
        r_b1 = ar.coalesced_refresh(state_path, b_b1, project_b, 5.0, force=True)
        assert "q/B1" in r_b1.snapshot.project_models[delegate._project_key(project_b)]

        # B quita B1
        b_b2 = _binding(ctx_b, [])
        r_b2 = ar.coalesced_refresh(state_path, b_b2, project_b, 5.0, force=True)
        assert r_b2.snapshot.project_models[delegate._project_key(project_b)] == {}
        assert "q/B1" in r_b2.snapshot.retired_models[delegate._project_key(project_b)]

        # A debe seguir intacto
        r_a2 = ar.coalesced_refresh(state_path, b_a1, project_a, 5.0, force=True)
        assert sorted(
            r_a2.snapshot.project_models[delegate._project_key(project_a)].keys()
        ) == ["p/A1", "p/A2"]
        assert (
            r_a2.snapshot.retired_models.get(delegate._project_key(project_a), {}) == {}
        )

    def test_active_counts_exclude_retired(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        b1 = _binding(
            ctx,
            [
                api_model(provider="p", model_id="A"),
                api_model(provider="p", model_id="B"),
            ],
        )
        ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)

        # Quitar B
        b2 = _binding(ctx, [api_model(provider="p", model_id="A")])
        r2 = ar.coalesced_refresh(state_path, b2, project, 5.0, force=True)

        # Activos: solo A
        active = r2.snapshot.project_models[delegate._project_key(project)]
        assert len(active) == 1
        assert "p/A" in active
        assert "p/B" not in active

        # Retired: B
        retired = r2.snapshot.retired_models[delegate._project_key(project)]
        assert len(retired) == 1
        assert "p/B" in retired


class TestReconnection:
    """Reconexión restaura metadata fresca sin promover cuota histórica."""

    def test_reconnection_reads_fresh_metadata(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        # Catálogo inicial con metadata M1
        m1 = api_model(provider="p", model_id="A", cost=[{"input": 1, "output": 1}])
        b1 = _binding(ctx, [m1])
        r1 = ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)
        assert r1.snapshot.models["p/A"].metadata.pricing[0].input == 1

        # Desaparece (va a retired)
        b2 = _binding(ctx, [])
        r2 = ar.coalesced_refresh(state_path, b2, project, 5.0, force=True)
        retired_a = r2.snapshot.retired_models[delegate._project_key(project)]["p/A"]
        assert retired_a.metadata.pricing[0].input == 1

        # Reaparece con metadata M2 distinta
        m2 = api_model(provider="p", model_id="A", cost=[{"input": 99, "output": 99}])
        b3 = _binding(ctx, [m2])
        r3 = ar.coalesced_refresh(state_path, b3, project, 5.0, force=True)

        # Metadata fresca, NO la histórica
        assert r3.snapshot.models["p/A"].metadata.pricing[0].input == 99
        # Quitado de retired
        assert "p/A" not in r3.snapshot.retired_models.get(
            delegate._project_key(project), {}
        )

    def test_no_historical_quota_promotion(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        # Refresh inicial trae modelo SIN quota (refresh no consulta quota por modelo)
        b1 = _binding(ctx, [api_model(provider="p", model_id="A")])
        r1 = ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)
        assert r1.snapshot.models["p/A"].quota is None

        # Desaparece -> va a retired SIN quota
        b2 = _binding(ctx, [])
        r2 = ar.coalesced_refresh(state_path, b2, project, 5.0, force=True)
        retired = r2.snapshot.retired_models[delegate._project_key(project)]["p/A"]
        assert retired.quota is None

        # Reaparece con metadata fresca, quota sigue None (no se promueve historia)
        b3 = _binding(ctx, [api_model(provider="p", model_id="A")])
        r3 = ar.coalesced_refresh(state_path, b3, project, 5.0, force=True)
        assert r3.snapshot.models["p/A"].quota is None


class TestHistoryRetention:
    """Retención acotada, roundtrip snapshot, schema old defaults."""

    def test_snapshot_roundtrip_preserves_retired(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        b1 = _binding(ctx, [api_model(provider="p", model_id="A")])
        ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)

        b2 = _binding(ctx, [])
        ar.coalesced_refresh(state_path, b2, project, 5.0, force=True)

        # Leer snapshot directamente
        loaded = a.read_snapshot(state_path)
        assert loaded is not None
        retired = loaded.retired_models[delegate._project_key(project)]
        assert "p/A" in retired
        assert retired["p/A"].metadata.model == "p/A"

    def test_old_schema_without_retired_loads_defaults(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        state_path = a.state_path(state)

        # Snapshot old schema (sin retired_models)
        old = a.AvailabilitySnapshot(
            schema_version=a.STATE_SCHEMA_VERSION,
            generation=1,
            published_at=datetime.now(timezone.utc),
            catalog_contexts=(),
            models={
                "p/A": a.ModelEntry(
                    metadata=a.ModelMetadata(
                        model="p/A",
                        name="A",
                        pricing=(a.PricingTier(input=0, output=0),),
                        variants=(),
                        tools=True,
                        input_modalities=("text",),
                        output_modalities=("text",),
                        context_limit=None,
                        output_limit=None,
                        free_candidate=True,
                        may_use_openai_quota=False,
                    ),
                    quota=None,
                    context_key="proj",
                )
            },
            data_sources=(),
            project_models={"proj": {}},
        )
        a.write_snapshot(state_path, old)

        loaded = a.read_snapshot(state_path)
        assert loaded is not None
        assert loaded.retired_models == {}

    def test_import_public_terms_preserves_retired(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        b1 = _binding(ctx, [api_model(provider="opencode", model_id="A")])
        ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)

        b2 = _binding(ctx, [])
        r2 = ar.coalesced_refresh(state_path, b2, project, 5.0, force=True)
        pk = delegate._project_key(project)
        assert "opencode/A" in r2.snapshot.retired_models[pk]

        # Importar public terms con provider válido
        from availability_public_terms import PublicTerm, import_public_terms_state

        term = PublicTerm(
            provider="opencode",
            model="A",
            scope="model",
            access_kind="conditional_access",
            conditions={},
            source_url="https://opencode.ai/docs/models/",
            checked_at=datetime.now(timezone.utc),
            source_status="ok",
        )
        snap = import_public_terms_state(state_path, (term,))
        assert "opencode/A" in snap.retired_models[pk]


class TestCLIAndMCP:
    """CLI/MCP expone deltas sin queries extra."""

    def test_cli_refresh_exposes_changes(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)

        from unittest.mock import patch

        import delegate

        # Mock resolve_host_context para usar nuestro ctx
        with patch("delegate.resolve_host_context", return_value=ctx):
            b1 = _binding(ctx, [api_model(provider="p", model_id="A")])
            with patch("delegate.discover_existing", return_value=b1):
                result = delegate.main(
                    ["availability", "refresh", "--cwd", str(project), "--json"]
                )
                assert result == 0

            b2 = _binding(ctx, [api_model(provider="p", model_id="B")])
            with patch("delegate.discover_existing", return_value=b2):
                result = delegate.main(
                    ["availability", "refresh", "--cwd", str(project), "--json"]
                )
                assert result == 0


class TestUnknownProvider:
    """Proveedor desconocido usable localmente con status unverified."""

    def test_unknown_provider_unverified_status(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        # Proveedor no en OFFICIAL_DOMAINS
        catalog = [api_model(provider="future-unknown", model_id="modelX")]
        b = _binding(ctx, catalog)
        r = ar.coalesced_refresh(state_path, b, project, 5.0, force=True)
        assert r.refreshed
        assert "future-unknown/modelX" in r.snapshot.models
        # metadata debe reflejar lo que vino del catálogo
        entry = r.snapshot.models["future-unknown/modelX"]
        assert entry.metadata.model == "future-unknown/modelX"
        # No error de catálogo
        assert "catalog_unavailable" not in r.errors


class TestErrorConditions:
    """Errores preservan inventario y registran intento."""

    def test_wrong_location_preserves_inventory(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        other = tmp_path / "other"
        other.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        b1 = _binding(ctx, [api_model(provider="p", model_id="A")])
        b1.catalog_location = str(other)  # ubicación errónea
        r1 = ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)
        # Debe fallar validación de ubicación y preservar
        assert "catalog_unavailable" in r1.errors or r1.snapshot.models == {}

    def test_timeout_preserves_inventory(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        state = tmp_path / "state"
        state.mkdir()
        ctx = _ctx(project, state)
        state_path = _state_path(ctx)

        b1 = _binding(ctx, [api_model(provider="p", model_id="A")])
        r1 = ar.coalesced_refresh(state_path, b1, project, 5.0, force=True)

        # Timeout muy corto
        b2 = _binding(ctx, [api_model(provider="p", model_id="B")])
        r2 = ar.coalesced_refresh(state_path, b2, project, 0.000001, force=True)
        # Debe fallar por timeout y preservar
        assert (
            "refresh_timeout" in r2.errors or r2.snapshot.models == r1.snapshot.models
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
