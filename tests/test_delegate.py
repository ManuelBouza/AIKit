import copy
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
DELEGATE_PATH = ROOT / "skills" / "delegating-to-opencode" / "scripts" / "delegate.py"
FREE_COST = {"input": 0, "output": 0, "cache": {"read": 0, "write": 0}}
DEFAULT_MODEL = "opencode/mimo-v2.6-flash-free"


def load_delegate():
    spec = importlib.util.spec_from_file_location("delegate_under_test", DELEGATE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_task(directory, text="Tarea de prueba"):
    path = Path(directory) / "tarea.txt"
    path.write_text(text, encoding="utf-8")
    return path


def api_model(
    model_id="mimo-v2.6-flash-free",
    provider="opencode",
    name=None,
    enabled=True,
    variants=None,
    cost=FREE_COST,
    capabilities=None,
    limit=None,
    **extra,
):
    model = {
        "id": model_id,
        "providerID": provider,
        "name": name or model_id,
        "enabled": enabled,
        "type": "chat",
        "capabilities": capabilities
        if capabilities is not None
        else {"tools": True, "input": ["text"], "output": ["text"]},
        "variants": variants or [],
        "limit": limit if limit is not None else {"context": 100000, "output": 8000},
    }
    if cost is not None:
        model["cost"] = copy.deepcopy(cost)
    model.update(extra)
    return model


def variant(variant_id, **settings):
    return {"id": variant_id, "settings": settings}


def text_event(text, session="ses_prueba"):
    return json.dumps(
        {
            "type": "text",
            "sessionID": session,
            "part": {"type": "text", "text": text},
        },
        ensure_ascii=False,
    )


def finish_event(cost=None, session="ses_prueba"):
    part = {"type": "step-finish", "reason": "stop"}
    if cost is not None:
        part["cost"] = cost
    return json.dumps(
        {"type": "step_finish", "sessionID": session, "part": part},
        ensure_ascii=False,
    )


def error_event(message="fallo del proveedor", session="ses_prueba"):
    return json.dumps(
        {
            "type": "error",
            "sessionID": session,
            "error": {"name": "ProviderError", "data": {"message": message}},
        },
        ensure_ascii=False,
    )


class FakeTransport:
    def __init__(
        self,
        version="2.2.0",
        models=None,
        run_stdout=None,
        run_returncode=0,
        run_stderr="",
        fail_run=False,
        timeout_error=False,
        version_returncode=0,
        version_stderr="",
        catalog_returncode=0,
        catalog_stderr="",
    ):
        self.version = version
        self.models = [api_model()] if models is None else models
        self.run_stdout = (
            text_event("ok") + "\n" + finish_event(cost=0)
            if run_stdout is None
            else run_stdout
        )
        self.run_returncode = run_returncode
        self.run_stderr = run_stderr
        self.fail_run = fail_run
        self.timeout_error = timeout_error
        self.version_returncode = version_returncode
        self.version_stderr = version_stderr
        self.catalog_returncode = catalog_returncode
        self.catalog_stderr = catalog_stderr
        self.calls = []

    def __call__(self, argv, cwd, timeout):
        argv = list(argv)
        self.calls.append((argv, str(cwd), timeout))
        if argv[1:2] == ["--version"]:
            return subprocess.CompletedProcess(
                argv,
                self.version_returncode,
                stdout=self.version + "\n",
                stderr=self.version_stderr,
            )
        if argv[1:3] == ["api", "--standalone"]:
            payload = {
                "location": {"directory": str(cwd)},
                "data": self.models,
            }
            return subprocess.CompletedProcess(
                argv,
                self.catalog_returncode,
                stdout=json.dumps(payload, ensure_ascii=False),
                stderr=self.catalog_stderr,
            )
        if argv[1:2] == ["run"]:
            if self.timeout_error:
                raise self.module.DelegateError("timeout", "OpenCode excedió el tiempo")
            if self.fail_run:
                raise self.module.DelegateError(
                    "opencode_failed", "no se pudo iniciar OpenCode"
                )
            return subprocess.CompletedProcess(
                argv,
                self.run_returncode,
                stdout=self.run_stdout,
                stderr=self.run_stderr,
            )
        raise AssertionError("Llamada inesperada: %r" % (argv,))

    def run_calls(self):
        return [call for call in self.calls if call[0][1:2] == ["run"]]


class DelegateTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delegate = load_delegate()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.project = Path(self._tmp.name)
        self.task = write_task(self._tmp.name)

    def fake(self, **kwargs):
        transport = FakeTransport(**kwargs)
        transport.module = self.delegate
        patcher = mock.patch.object(self.delegate, "run_process", transport)
        patcher.start()
        self.addCleanup(patcher.stop)
        finder = mock.patch.object(
            self.delegate, "find_opencode", return_value="C:/fake/opencode.exe"
        )
        finder.start()
        self.addCleanup(finder.stop)
        return transport

    def run_task(self, **overrides):
        values = {
            "cwd": self.project,
            "task_file": self.task,
            "model": DEFAULT_MODEL,
            "variant": None,
            "reason": "tarea mecánica con herramientas de texto",
            "agent": "build",
            "timeout": 30,
        }
        values.update(overrides)
        return self.delegate.run_task(**values)

    def doctor(self, **overrides):
        values = {"cwd": self.project, "timeout": 30}
        values.update(overrides)
        return self.delegate.doctor(**values)

    # --- Selección explícita y catálogo conectado ------------------------

    def test_missing_model_and_reason_fail_before_any_subprocess(self):
        transport = self.fake()
        for overrides, code in (
            ({"model": None}, "model_required"),
            ({"model": "  "}, "model_required"),
            ({"reason": None}, "reason_required"),
            ({"reason": " \t "}, "reason_required"),
        ):
            with self.subTest(overrides=overrides):
                result = self.run_task(**overrides)
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["code"], code)
        self.assertEqual(transport.calls, [])

    def test_main_reports_missing_model_and_reason_as_json(self):
        transport = self.fake()
        for args, code in (
            (["run", "--cwd", str(self.project), "--task-file", str(self.task)], "model_required"),
            (
                [
                    "run",
                    "--cwd",
                    str(self.project),
                    "--task-file",
                    str(self.task),
                    "--model",
                    DEFAULT_MODEL,
                ],
                "reason_required",
            ),
        ):
            with self.subTest(code=code):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    exit_code = self.delegate.main(args)
                payload = json.loads(buffer.getvalue())
                self.assertEqual(exit_code, 1)
                self.assertEqual(payload["code"], code)
        self.assertEqual(transport.calls, [])

    def test_paid_openai_and_multiprovider_models_are_allowed(self):
        paid_openai = api_model(
            "gpt-5.3",
            provider="openai",
            name="GPT de pago",
            variants=[variant("high", reasoningEffort="high")],
            cost={"input": 3, "output": 15, "cache": {"read": 0.3, "write": 3}},
        )
        paid_anthropic = api_model(
            "claude-ficticio",
            provider="anthropic",
            name="Claude ficticio",
            cost={"input": 2, "output": 10},
        )
        transport = self.fake(models=[paid_openai, paid_anthropic])
        for full_model in ("openai/gpt-5.3#high", "anthropic/claude-ficticio"):
            with self.subTest(model=full_model):
                result = self.run_task(
                    model=full_model,
                    reason="capacidad necesaria para una revisión compleja",
                )
                self.assertEqual(result["status"], "ok")
                self.assertEqual(
                    transport.run_calls()[-1][0][
                        transport.run_calls()[-1][0].index("--model") + 1
                    ],
                    full_model,
                )

    def test_disabled_or_absent_models_are_not_executed(self):
        disabled = api_model("apagado", enabled=False)
        transport = self.fake(models=[disabled])
        for model in ("opencode/apagado", "opencode/ausente"):
            with self.subTest(model=model):
                result = self.run_task(model=model)
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["code"], "model_unavailable")
        self.assertEqual(transport.run_calls(), [])

    def test_unknown_variants_are_rejected_before_run(self):
        model = api_model(variants=[variant("high", reasoningEffort="high")])
        transport = self.fake(models=[model])
        for overrides in (
            {"model": "opencode/mimo-v2.6-flash-free#max"},
            {"variant": "max"},
        ):
            with self.subTest(overrides=overrides):
                result = self.run_task(**overrides)
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["code"], "invalid_variant")
        self.assertEqual(transport.run_calls(), [])

    def test_real_variant_is_passed_and_reported(self):
        model = api_model(
            variants=[
                variant("low", reasoningEffort="low"),
                variant("high", reasoningEffort="high"),
            ]
        )
        transport = self.fake(models=[model])
        result = self.run_task(model=DEFAULT_MODEL + "#high")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["model"], DEFAULT_MODEL)
        self.assertEqual(result["variant"], "high")
        self.assertEqual(result["effort"], "high")
        self.assertEqual(result["reason"], "tarea mecánica con herramientas de texto")
        argv = transport.run_calls()[0][0]
        self.assertEqual(argv[argv.index("--model") + 1], DEFAULT_MODEL + "#high")

    def test_no_variant_reports_provider_default_and_models_without_variants_work(self):
        model = api_model(variants=[])
        transport = self.fake(models=[model])
        result = self.run_task(
            reason="tarea simple; el modelo no ofrece variantes y uso el ajuste predeterminado"
        )
        self.assertEqual(result["status"], "ok")
        self.assertIsNone(result["variant"])
        self.assertEqual(result["effort"], "provider_default")
        self.assertEqual(result["model"], DEFAULT_MODEL)
        argv = transport.run_calls()[0][0]
        self.assertEqual(argv[argv.index("--model") + 1], DEFAULT_MODEL)

    def test_variant_flag_and_embedded_variant_conflict_without_subprocess(self):
        transport = self.fake()
        result = self.run_task(model=DEFAULT_MODEL + "#high", variant="low")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "variant_conflict")
        self.assertEqual(transport.calls, [])

    def test_variant_flag_is_validated_and_folded_into_model(self):
        model = api_model(variants=[variant("high", reasoningEffort="high")])
        transport = self.fake(models=[model])
        result = self.run_task(variant="high")
        self.assertEqual(result["status"], "ok")
        argv = transport.run_calls()[0][0]
        self.assertEqual(argv[argv.index("--model") + 1], DEFAULT_MODEL + "#high")

    def test_absent_local_config_does_not_block_paid_execution(self):
        self.assertFalse((self.project / "opencode.json").exists())
        model = api_model("gpt-5.3", provider="openai", cost={"input": 1, "output": 2})
        transport = self.fake(models=[model])
        result = self.run_task(model="openai/gpt-5.3", reason="pago autorizado por el usuario")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(transport.run_calls()), 1)

    def test_any_connected_free_model_without_suffix_can_execute(self):
        model = api_model("modelo-local", provider="proveedor-local", cost=FREE_COST)
        transport = self.fake(models=[model])
        result = self.run_task(model="proveedor-local/modelo-local")
        self.assertEqual(result["status"], "ok")
        argv = transport.run_calls()[0][0]
        self.assertEqual(
            argv[argv.index("--model") + 1], "proveedor-local/modelo-local"
        )

    # --- Catálogo y doctor ------------------------------------------------

    def test_doctor_reports_compact_catalog_without_provider_secrets(self):
        model = api_model(
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
            capabilities={"tools": True, "input": ["text", "image"], "output": ["text"]},
            limit={"context": 200000, "input": 150000, "output": 20000},
            cost={"input": 1.25, "output": 5.5, "cache": {"read": 0.1, "write": 1.5}},
        )
        self.fake(models=[model])
        result = self.doctor()
        self.assertEqual(result["status"], "ok")
        encoded = json.dumps(result, ensure_ascii=False)
        for secret in ("secreto-variante", "secreto-body", "secreto-modelo", "secreto-api"):
            self.assertNotIn(secret, encoded)
        entry = result["catalog"][0]
        self.assertEqual(entry["model"], DEFAULT_MODEL)
        self.assertEqual(entry["name"], "Modelo visible")
        self.assertEqual(entry["pricing"], {"input": 1.25, "output": 5.5, "cache": {"read": 0.1, "write": 1.5}})
        self.assertEqual(entry["variants"], [{"id": "high", "reasoningEffort": "high", "thinkingBudget": 4096}])
        self.assertTrue(entry["tools"])
        self.assertEqual(entry["input"], ["text", "image"])
        self.assertEqual(entry["output"], ["text"])
        self.assertEqual(entry["limits"], {"context": 200000, "input": 150000, "output": 20000})

    def test_doctor_reports_all_pricing_tiers_without_level_secrets(self):
        model = api_model(
            cost=[
                {
                    "input": 0,
                    "output": 0,
                    "cache": {"read": 0, "write": 0},
                    "headers": {"Authorization": "Bearer secreto-nivel-base"},
                    "body": {"token": "secreto-body-base"},
                },
                {
                    "tier": {
                        "type": "context",
                        "size": 32768,
                        "headers": {"Authorization": "Bearer secreto-nivel-alto"},
                    },
                    "input": 10,
                    "output": 50,
                    "cache": {"read": 1, "write": 2},
                    "settings": {"apiKey": "secreto-settings-alto"},
                },
            ]
        )
        self.fake(models=[model])
        result = self.doctor()
        self.assertEqual(result["status"], "ok")
        encoded = json.dumps(result, ensure_ascii=False)
        for secret in (
            "secreto-nivel-base",
            "secreto-body-base",
            "secreto-nivel-alto",
            "secreto-settings-alto",
        ):
            self.assertNotIn(secret, encoded)
        entry = result["catalog"][0]
        self.assertEqual(
            entry["pricing"],
            {"input": 0, "output": 0, "cache": {"read": 0, "write": 0}},
        )
        self.assertEqual(
            entry["pricing_tiers"],
            [
                {"input": 0, "output": 0, "cache": {"read": 0, "write": 0}},
                {
                    "tier": {"type": "context", "size": 32768},
                    "input": 10,
                    "output": 50,
                    "cache": {"read": 1, "write": 2},
                },
            ],
        )
        self.assertFalse(entry["free_candidate"])

    def test_unknown_prices_are_null_and_zero_openai_is_not_free(self):
        unknown = api_model("sin-precio", cost=None)
        openai_zero = api_model("gpt-5.3", provider="openai", cost=FREE_COST)
        free = api_model("modelo-gratuito", cost=FREE_COST)
        self.fake(models=[unknown, openai_zero, free])
        result = self.doctor()
        entries = {entry["model"]: entry for entry in result["catalog"]}
        self.assertIsNone(entries["opencode/sin-precio"]["pricing"])
        self.assertIsNone(entries["opencode/sin-precio"]["pricing_tiers"])
        self.assertIsNone(entries["opencode/sin-precio"]["free_candidate"])
        self.assertEqual(entries["openai/gpt-5.3"]["pricing"]["input"], 0)
        self.assertFalse(entries["openai/gpt-5.3"]["free_candidate"])
        self.assertTrue(entries["openai/gpt-5.3"]["may_use_openai_quota"])
        self.assertTrue(entries["opencode/modelo-gratuito"]["free_candidate"])
        self.assertFalse(entries["opencode/modelo-gratuito"]["may_use_openai_quota"])

    def test_free_candidate_uses_metadata_not_name_suffix(self):
        paid_with_free_name = api_model(
            "parece-free",
            cost={"input": 1, "output": 2},
        )
        free_without_suffix = api_model(
            "modelo-local",
            provider="proveedor-local",
            cost=FREE_COST,
        )
        self.fake(models=[paid_with_free_name, free_without_suffix])
        result = self.doctor()
        entries = {entry["model"]: entry for entry in result["catalog"]}
        self.assertFalse(entries["opencode/parece-free"]["free_candidate"])
        self.assertTrue(entries["proveedor-local/modelo-local"]["free_candidate"])

    def test_doctor_orders_free_candidates_first_and_filters_by_model(self):
        expensive = api_model("caro", cost={"input": 9, "output": 18})
        openai_zero = api_model("gpt-5.3", provider="openai", cost=FREE_COST)
        free_b = api_model("zeta-free", cost=FREE_COST)
        free_a = api_model("alfa-free", cost=FREE_COST)
        self.fake(models=[expensive, openai_zero, free_b, free_a])
        result = self.doctor()
        self.assertEqual(result["catalog_count"], 4)
        free_flags = [entry["free_candidate"] for entry in result["catalog"]]
        self.assertEqual(free_flags[:2], [True, True])
        self.assertEqual(
            {entry["model"] for entry in result["catalog"][:2]},
            {"opencode/alfa-free", "opencode/zeta-free"},
        )
        filtered = self.doctor(model="opencode/alfa-free")
        self.assertEqual(filtered["catalog_count"], 4)
        self.assertEqual(len(filtered["catalog"]), 1)
        self.assertEqual(filtered["catalog"][0]["model"], "opencode/alfa-free")

    def test_doctor_reports_version_and_count(self):
        transport = self.fake(
            version="2.2.0",
            models=[api_model("uno"), api_model("dos")],
        )
        result = self.doctor()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["version"], "2.2.0")
        self.assertEqual(result["catalog_count"], 2)
        self.assertEqual(len(result["catalog"]), 2)
        self.assertEqual(len(transport.calls), 2)

    def test_doctor_rejects_v1(self):
        self.fake(version="1.0.0")
        result = self.doctor()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "unsupported_version")

    def test_catalog_failure_does_not_leak_output(self):
        self.fake(
            catalog_returncode=5,
            catalog_stderr="TOKEN=secreto-catalogo",
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "catalog_unavailable")
        self.assertIn("5", result["message"])
        self.assertNotIn("secreto-catalogo", result["message"])

    # --- Construcción de argumentos y transporte -------------------------

    def test_builds_arguments_in_order_with_spaces_and_variant(self):
        task_text = 'Arregla "esto" & aquello\ncon espacios'
        task = write_task(self._tmp.name, task_text)
        model = api_model(variants=[variant("high", reasoningEffort="high")])
        transport = self.fake(models=[model])
        result = self.run_task(
            task_file=task,
            model=DEFAULT_MODEL + "#high",
            reason="integración acotada; variante alta disponible",
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(transport.run_calls()), 1)
        argv, cwd, timeout = transport.run_calls()[0]
        self.assertEqual(
            argv,
            [
                "C:/fake/opencode.exe",
                "run",
                "--model",
                DEFAULT_MODEL + "#high",
                "--agent",
                "build",
                "--standalone",
                "--format",
                "json",
                "--",
                "Tarea delegada (contenido literal):\n\n" + task_text.strip(),
            ],
        )
        self.assertEqual(cwd, str(self.project.resolve()))
        self.assertEqual(timeout, 30)
        self.assertNotIn("--variant", argv)
        self.assertNotIn("--effort", argv)
        self.assertNotIn("--auto", argv)
        self.assertNotIn("--allow-paid", argv)

    def test_task_starting_with_option_and_metacharacters_is_prefixed(self):
        original = '--auto & "comillas" | > $HOME ; ñ'
        task = write_task(self._tmp.name, original)
        transport = self.fake()
        result = self.run_task(task_file=task)
        self.assertEqual(result["status"], "ok")
        argv = transport.run_calls()[0][0]
        prefix = "Tarea delegada (contenido literal):\n\n"
        self.assertEqual(argv[-2], "--")
        self.assertEqual(argv[-1], prefix + original)
        self.assertTrue(argv[-1].startswith(prefix))
        self.assertFalse(argv[-1].startswith("-"))
        self.assertEqual(argv[-1][len(prefix):], original)
        self.assertEqual(argv.count("--auto"), 0)

    def test_plan_agent_is_forwarded(self):
        transport = self.fake()
        result = self.run_task(agent="plan")
        self.assertEqual(result["status"], "ok")
        argv = transport.run_calls()[0][0]
        self.assertEqual(argv[argv.index("--agent") + 1], "plan")

    def test_rejects_invalid_timeouts_before_any_call(self):
        transport = self.fake()
        for value in (float("nan"), float("inf"), float("-inf"), 3601):
            with self.subTest(value=value):
                result = self.run_task(timeout=value)
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["code"], "invalid_timeout")
        self.assertEqual(transport.calls, [])

    def test_accepts_timeout_at_documented_limit(self):
        transport = self.fake()
        result = self.run_task(timeout=3600)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(transport.run_calls()[0][2], 3600)

    # --- Análisis de eventos y salida ------------------------------------

    def test_error_event_with_exit_zero_is_error(self):
        self.fake(run_stdout=text_event("parcial") + "\n" + error_event("sin cuota"))
        with redirect_stdout(io.StringIO()):
            code = self.delegate.main(
                [
                    "run",
                    "--cwd",
                    str(self.project),
                    "--task-file",
                    str(self.task),
                    "--model",
                    DEFAULT_MODEL,
                    "--reason",
                    "tarea mecánica",
                ]
            )
        self.assertEqual(code, 1)

    def test_error_event_message_is_returned(self):
        self.fake(run_stdout=error_event("sin cuota"))
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "opencode_event_error")
        self.assertIn("sin cuota", result["message"])

    def test_empty_output_is_error(self):
        self.fake(run_stdout="")
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "empty_output")

    def test_timeout_is_error(self):
        self.fake(timeout_error=True)
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "timeout")

    def test_nonzero_exit_is_error_without_leaking_output(self):
        self.fake(
            run_stdout="TOKEN=secreto-en-stdout",
            run_stderr="fallo de transporte TOKEN=secreto-en-stderr",
            run_returncode=7,
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "opencode_failed")
        self.assertIn("7", result["message"])
        self.assertNotIn("secreto-en-stdout", result["message"])
        self.assertNotIn("secreto-en-stderr", result["message"])
        self.assertNotIn("fallo de transporte", result["message"])

    def test_version_failure_does_not_leak_output(self):
        self.fake(version_returncode=3, version_stderr="TOKEN=secreto-version")
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "version_check_failed")
        self.assertIn("3", result["message"])
        self.assertNotIn("secreto-version", result["message"])

    def test_missing_cost_is_null_not_zero(self):
        self.fake(run_stdout=text_event("ok") + "\n" + finish_event())
        result = self.run_task()
        self.assertEqual(result["status"], "ok")
        self.assertIsNone(result["cost"])

    def test_reported_cost_is_preserved(self):
        self.fake(run_stdout=text_event("ok") + "\n" + finish_event(cost=0))
        result = self.run_task()
        self.assertEqual(result["cost"], 0)

    def test_summary_is_truncated_to_4000_characters(self):
        self.fake(run_stdout=text_event("x" * 5000) + "\n" + finish_event(cost=0))
        result = self.run_task()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["summary"]), 4000)

    def test_success_returns_session_selection_reason_and_summary(self):
        self.fake(
            run_stdout=text_event("informe final", session="ses_abc")
            + "\n"
            + finish_event(cost=0, session="ses_abc"),
        )
        result = self.run_task(reason="delegación gratuita suficiente")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["session"], "ses_abc")
        self.assertEqual(result["summary"], "informe final")
        self.assertEqual(result["model"], DEFAULT_MODEL)
        self.assertIsNone(result["variant"])
        self.assertEqual(result["effort"], "provider_default")
        self.assertEqual(result["reason"], "delegación gratuita suficiente")
        self.assertEqual(result["agent"], "build")
        self.assertEqual(result["cost"], 0)

    def test_main_prints_one_compact_json_line(self):
        self.fake()
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = self.delegate.main(
                [
                    "run",
                    "--cwd",
                    str(self.project),
                    "--task-file",
                    str(self.task),
                    "--model",
                    DEFAULT_MODEL,
                    "--reason",
                    "tarea mecánica",
                ]
            )
        output = buffer.getvalue()
        self.assertEqual(code, 0)
        self.assertEqual(len(output.strip().splitlines()), 1)
        parsed = json.loads(output)
        self.assertEqual(
            output.strip(),
            json.dumps(parsed, ensure_ascii=True, separators=(",", ":")),
        )

    def test_main_emits_ascii_json_even_with_cp1252_stdout(self):
        bad_cwd = self.project / "carpeta-inexistente-ñandú"
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp1252"
        completed = subprocess.run(
            [
                sys.executable,
                str(DELEGATE_PATH),
                "doctor",
                "--cwd",
                str(bad_cwd),
                "--timeout",
                "30",
            ],
            capture_output=True,
            env=env,
            timeout=30,
            check=False,
        )
        decoded = completed.stdout.decode("ascii")
        payload = json.loads(decoded)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["code"], "invalid_cwd")
        self.assertIn("ñandú", payload["message"])

    # --- Política de preferencias y binario ------------------------------

    def test_policy_contains_only_preferences_without_closed_list(self):
        policy = self.delegate.load_policy()
        self.assertEqual(
            policy,
            {"prefer_free": True, "require_selection_reason": True},
        )

    def test_policy_rejects_invalid_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            path.write_text(json.dumps({"default_model": "x"}), encoding="utf-8")
            with self.assertRaises(self.delegate.DelegateError) as ctx:
                self.delegate.load_policy(path)
        self.assertEqual(ctx.exception.code, "policy_invalid")

    def test_resolves_windows_npm_shim_to_sibling_exe(self):
        with tempfile.TemporaryDirectory() as directory:
            shim = Path(directory) / "opencode.ps1"
            shim.write_text("shim", encoding="utf-8")
            exe = (
                Path(directory)
                / "node_modules"
                / "@opencode"
                / "cli"
                / "bin"
                / "opencode.exe"
            )
            exe.parent.mkdir(parents=True)
            exe.write_text("exe", encoding="utf-8")
            found = self.delegate.resolve_opencode(
                which_result=str(shim), is_windows=True
            )
            self.assertEqual(Path(found), exe)

    def test_rejects_windows_shim_without_native_exe(self):
        for suffix in (".cmd", ".bat", ".ps1"):
            with self.subTest(suffix=suffix):
                with tempfile.TemporaryDirectory() as directory:
                    shim = Path(directory) / ("opencode" + suffix)
                    shim.write_text("shim", encoding="utf-8")
                    with self.assertRaises(self.delegate.DelegateError) as ctx:
                        self.delegate.resolve_opencode(
                            which_result=str(shim), is_windows=True
                        )
                    self.assertEqual(ctx.exception.code, "opencode_missing")

    def test_rejects_unknown_windows_extension(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "opencode.py"
            script.write_text("script", encoding="utf-8")
            with self.assertRaises(self.delegate.DelegateError) as ctx:
                self.delegate.resolve_opencode(
                    which_result=str(script), is_windows=True
                )
        self.assertEqual(ctx.exception.code, "opencode_missing")

    def test_accepts_direct_windows_exe(self):
        with tempfile.TemporaryDirectory() as directory:
            exe = Path(directory) / "opencode.exe"
            exe.write_text("exe", encoding="utf-8")
            found = self.delegate.resolve_opencode(
                which_result=str(exe), is_windows=True
            )
        self.assertEqual(Path(found), exe)

    def test_uses_unix_binary_as_found(self):
        found = self.delegate.resolve_opencode(
            which_result="/usr/local/bin/opencode", is_windows=False
        )
        self.assertEqual(found, "/usr/local/bin/opencode")


class TimeoutValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delegate = load_delegate()

    def test_api_rejects_nonfinite_and_out_of_range_timeouts(self):
        for value in (float("nan"), float("inf"), float("-inf"), 3601):
            with self.subTest(value=value):
                with self.assertRaises(self.delegate.DelegateError) as ctx:
                    self.delegate._validate_timeout(value)
                self.assertEqual(ctx.exception.code, "invalid_timeout")

    def test_api_accepts_limit(self):
        self.assertEqual(self.delegate._validate_timeout(3600), 3600)

    def test_cli_rejects_nonfinite_and_out_of_range_timeouts(self):
        parser = self.delegate._parser()
        for value in ("nan", "inf", "-inf", "3601"):
            with self.subTest(value=value):
                with self.assertRaises(SystemExit):
                    with redirect_stderr(io.StringIO()):
                        parser.parse_args(
                            ["doctor", "--cwd", ".", "--timeout", value]
                        )

    def test_cli_accepts_limit(self):
        args = self.delegate._parser().parse_args(
            ["doctor", "--cwd", ".", "--timeout", "3600"]
        )
        self.assertEqual(args.timeout, 3600)


class RunProcessTimeoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delegate = load_delegate()

    def test_timeout_kills_only_its_process_tree(self):
        class FakeProcess:
            pid = 4321

            def __init__(self):
                self.calls = 0

            def communicate(self, timeout=None):
                self.calls += 1
                if self.calls == 1:
                    raise subprocess.TimeoutExpired(["opencode"], timeout)
                return "", ""

        process = FakeProcess()
        with mock.patch.object(
            self.delegate.subprocess, "Popen", return_value=process
        ) as popen, mock.patch.object(self.delegate, "_kill_tree") as kill:
            with self.assertRaises(self.delegate.DelegateError) as ctx:
                self.delegate.run_process(["opencode"], cwd=ROOT, timeout=1)
        self.assertEqual(ctx.exception.code, "timeout")
        kill.assert_called_once_with(process)
        kwargs = popen.call_args.kwargs
        self.assertIs(kwargs.get("shell"), False)
        self.assertEqual(kwargs.get("cwd"), str(ROOT))


if __name__ == "__main__":
    unittest.main()
