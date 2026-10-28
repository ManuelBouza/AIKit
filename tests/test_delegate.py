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
VALID_POLICY = {
    "policies": [
        {"action": "provider.use", "resource": "*", "effect": "deny"},
        {"action": "provider.use", "resource": "opencode", "effect": "allow"},
        {"action": "tool.use", "resource": "subagent:*", "effect": "deny"},
    ]
}


def load_delegate():
    spec = importlib.util.spec_from_file_location("delegate_under_test", DELEGATE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_project(directory, policy=VALID_POLICY):
    root = Path(directory)
    (root / "opencode.json").write_text(
        json.dumps(policy, ensure_ascii=False), encoding="utf-8"
    )
    return root


def write_task(directory, text="Tarea de prueba"):
    path = Path(directory) / "tarea.txt"
    path.write_text(text, encoding="utf-8")
    return path


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
        catalog=None,
        run_stdout="",
        run_returncode=0,
        run_stderr="",
        fail_run=False,
        timeout_error=False,
        version_returncode=0,
        version_stderr="",
        models_returncode=0,
        models_stderr="",
    ):
        self.version = version
        self.catalog = catalog or []
        self.run_stdout = run_stdout
        self.run_returncode = run_returncode
        self.run_stderr = run_stderr
        self.fail_run = fail_run
        self.timeout_error = timeout_error
        self.version_returncode = version_returncode
        self.version_stderr = version_stderr
        self.models_returncode = models_returncode
        self.models_stderr = models_stderr
        self.calls = []

    def __call__(self, argv, cwd, timeout):
        argv = list(argv)
        self.calls.append((argv, str(cwd), timeout))
        if self.timeout_error and "run" in argv:
            raise self.module.DelegateError("timeout", "OpenCode excedió el tiempo")
        if "--version" in argv:
            return subprocess.CompletedProcess(
                argv,
                self.version_returncode,
                stdout=self.version + "\n",
                stderr=self.version_stderr,
            )
        if "models" in argv:
            return subprocess.CompletedProcess(
                argv,
                self.models_returncode,
                stdout="\n".join(self.catalog) + "\n",
                stderr=self.models_stderr,
            )
        if "run" in argv:
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
        return [call for call in self.calls if "run" in call[0]]


class DelegateTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delegate = load_delegate()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.project = write_project(self._tmp.name)
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
            "model": None,
            "variant": None,
            "agent": "build",
            "timeout": 30,
        }
        values.update(overrides)
        return self.delegate.run_task(**values)

    def doctor(self, **overrides):
        values = {"cwd": self.project, "timeout": 30}
        values.update(overrides)
        return self.delegate.doctor(**values)

    # --- Rechazos que no deben invocar un modelo -------------------------

    def test_rejects_openai_model_without_invoking_opencode(self):
        transport = self.fake()
        result = self.run_task(model="openai/gpt-5")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "provider_not_allowed")
        self.assertEqual(transport.calls, [])

    def test_rejects_openai_even_without_project_policy(self):
        transport = self.fake()
        (self.project / "opencode.json").unlink()
        result = self.run_task(model="openai/gpt-5")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "provider_not_allowed")
        self.assertEqual(transport.calls, [])

    def test_rejects_model_outside_exact_allowlist_without_calls(self):
        transport = self.fake()
        result = self.run_task(model="opencode/otro-modelo-free")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "model_not_allowed")
        self.assertEqual(transport.calls, [])

    def test_rejects_missing_project_policy_before_running(self):
        transport = self.fake()
        (self.project / "opencode.json").unlink()
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "policy_missing")
        self.assertIn("opencode.json", result["message"])
        self.assertEqual(transport.calls, [])

    def test_rejects_policy_that_allows_openai(self):
        transport = self.fake()
        write_project(
            self.project,
            {
                "policies": [
                    {"action": "provider.use", "resource": "*", "effect": "allow"},
                    {"action": "provider.use", "resource": "opencode", "effect": "allow"},
                    {"action": "tool.use", "resource": "subagent:*", "effect": "deny"},
                ]
            },
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "policy_invalid")
        self.assertEqual(transport.calls, [])

    def test_rejects_policy_without_subagent_denial(self):
        transport = self.fake()
        write_project(
            self.project,
            {
                "policies": [
                    {"action": "provider.use", "resource": "*", "effect": "deny"},
                    {"action": "provider.use", "resource": "opencode", "effect": "allow"},
                ]
            },
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "policy_invalid")
        self.assertEqual(transport.calls, [])

    def test_rejects_policy_allowing_openai_after_valid_entries(self):
        transport = self.fake()
        write_project(
            self.project,
            {
                "policies": [
                    {"action": "provider.use", "resource": "*", "effect": "deny"},
                    {"action": "provider.use", "resource": "opencode", "effect": "allow"},
                    {"action": "provider.use", "resource": "openai", "effect": "allow"},
                    {"action": "tool.use", "resource": "subagent:*", "effect": "deny"},
                ]
            },
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "policy_invalid")
        self.assertEqual(transport.calls, [])

    def test_rejects_policy_allowing_wildcard_after_valid_entries(self):
        transport = self.fake()
        write_project(
            self.project,
            {
                "policies": [
                    {"action": "provider.use", "resource": "*", "effect": "deny"},
                    {"action": "provider.use", "resource": "opencode", "effect": "allow"},
                    {"action": "provider.use", "resource": "*", "effect": "allow"},
                    {"action": "tool.use", "resource": "subagent:*", "effect": "deny"},
                ]
            },
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "policy_invalid")
        self.assertEqual(transport.calls, [])

    def test_rejects_tool_denial_without_star_suffix(self):
        transport = self.fake()
        write_project(
            self.project,
            {
                "policies": [
                    {"action": "provider.use", "resource": "*", "effect": "deny"},
                    {"action": "provider.use", "resource": "opencode", "effect": "allow"},
                    {"action": "tool.use", "resource": "subagent", "effect": "deny"},
                ]
            },
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "policy_invalid")
        self.assertEqual(transport.calls, [])

    def test_rejects_policy_allowing_any_tool_use(self):
        transport = self.fake()
        write_project(
            self.project,
            {
                "policies": [
                    {"action": "provider.use", "resource": "*", "effect": "deny"},
                    {"action": "provider.use", "resource": "opencode", "effect": "allow"},
                    {"action": "tool.use", "resource": "subagent:*", "effect": "deny"},
                    {"action": "tool.use", "resource": "read", "effect": "allow"},
                ]
            },
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "policy_invalid")
        self.assertEqual(transport.calls, [])

    def test_rejects_deny_star_placed_after_allow_opencode(self):
        transport = self.fake()
        write_project(
            self.project,
            {
                "policies": [
                    {"action": "provider.use", "resource": "opencode", "effect": "allow"},
                    {"action": "provider.use", "resource": "*", "effect": "deny"},
                    {"action": "tool.use", "resource": "subagent:*", "effect": "deny"},
                ]
            },
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "policy_invalid")
        self.assertEqual(transport.calls, [])

    def test_rejects_openai_star_as_substitute_for_deny_all(self):
        transport = self.fake()
        write_project(
            self.project,
            {
                "policies": [
                    {"action": "provider.use", "resource": "openai/*", "effect": "deny"},
                    {"action": "provider.use", "resource": "opencode", "effect": "allow"},
                    {"action": "tool.use", "resource": "subagent:*", "effect": "deny"},
                ]
            },
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "policy_invalid")
        self.assertEqual(transport.calls, [])

    def test_rejects_old_openai_denial_before_allow(self):
        transport = self.fake()
        write_project(
            self.project,
            {
                "policies": [
                    {"action": "provider.use", "resource": "openai", "effect": "deny"},
                    {"action": "provider.use", "resource": "opencode", "effect": "allow"},
                    {"action": "tool.use", "resource": "subagent:*", "effect": "deny"},
                ]
            },
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "policy_invalid")
        self.assertEqual(transport.calls, [])

    def test_rejects_missing_directory(self):
        transport = self.fake()
        result = self.run_task(cwd=self.project / "no-existe")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "invalid_cwd")
        self.assertEqual(transport.calls, [])

    def test_rejects_empty_task(self):
        transport = self.fake()
        empty = write_task(self._tmp.name, "  \n\t ")
        result = self.run_task(task_file=empty)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "empty_task")
        self.assertEqual(transport.calls, [])

    def test_rejects_variant_flag_conflict(self):
        transport = self.fake()
        result = self.run_task(
            model="opencode/deepseek-v4.1-flash-free#high", variant="low"
        )
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "variant_conflict")
        self.assertEqual(transport.calls, [])

    def test_rejects_model_absent_from_catalog(self):
        transport = self.fake(
            catalog=["opencode/glm-5.3-flash-free"],
            run_stdout=text_event("ok") + "\n" + finish_event(cost=0),
        )
        result = self.run_task(model="opencode/deepseek-v4.1-flash-free")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "model_unavailable")
        self.assertEqual(transport.run_calls(), [])

    def test_rejects_opencode_v1(self):
        transport = self.fake(version="1.9.0")
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "unsupported_version")
        self.assertEqual(transport.run_calls(), [])

    def test_rejects_invalid_timeouts_before_any_call(self):
        transport = self.fake()
        for value in (float("nan"), float("inf"), float("-inf"), 3601):
            with self.subTest(value=value):
                result = self.run_task(timeout=value)
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["code"], "invalid_timeout")
        self.assertEqual(transport.calls, [])

    def test_accepts_timeout_at_documented_limit(self):
        transport = self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            run_stdout=text_event("ok") + "\n" + finish_event(cost=0),
        )
        result = self.run_task(timeout=3600)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(transport.run_calls()[0][2], 3600)

    def test_rejects_catalog_with_foreign_provider_before_run(self):
        transport = self.fake(
            catalog=["opencode/mimo-v2.6-flash-free", "openai/gpt-5"],
            run_stdout=text_event("ok") + "\n" + finish_event(cost=0),
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "unsafe_catalog")
        self.assertEqual(transport.run_calls(), [])

    # --- Construcción de argumentos --------------------------------------

    def test_builds_arguments_in_order_with_spaces_and_variant(self):
        task_text = 'Arregla "esto" & aquello\ncon espacios'
        task = write_task(self._tmp.name, task_text)
        transport = self.fake(
            catalog=[
                "opencode/mimo-v2.6-flash-free",
                "opencode/deepseek-v4.1-flash-free",
                "opencode/glm-5.3-flash-free",
            ],
            run_stdout=text_event("hecho") + "\n" + finish_event(cost=0),
        )
        result = self.run_task(
            task_file=task,
            model="opencode/deepseek-v4.1-flash-free#high",
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
                "opencode/deepseek-v4.1-flash-free#high",
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

    def test_task_starting_with_option_and_metacharacters_is_prefixed(self):
        original = '--auto & "comillas" | > $HOME ; ñ'
        task = write_task(self._tmp.name, original)
        transport = self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            run_stdout=text_event("ok") + "\n" + finish_event(cost=0),
        )
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

    def test_variant_flag_is_folded_into_model(self):
        transport = self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            run_stdout=text_event("ok") + "\n" + finish_event(cost=0),
        )
        result = self.run_task(variant="presupuesto")
        self.assertEqual(result["status"], "ok")
        argv = transport.run_calls()[0][0]
        self.assertEqual(
            argv[argv.index("--model") + 1],
            "opencode/mimo-v2.6-flash-free#presupuesto",
        )

    def test_plan_agent_and_default_model(self):
        transport = self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            run_stdout=text_event("ok") + "\n" + finish_event(cost=0),
        )
        result = self.run_task(agent="plan")
        self.assertEqual(result["status"], "ok")
        argv = transport.run_calls()[0][0]
        self.assertEqual(argv[argv.index("--agent") + 1], "plan")
        self.assertEqual(
            argv[argv.index("--model") + 1], "opencode/mimo-v2.6-flash-free"
        )

    # --- Análisis de eventos y salida ------------------------------------

    def test_error_event_with_exit_zero_is_error(self):
        self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            run_stdout=text_event("parcial") + "\n" + error_event("sin cuota"),
            run_returncode=0,
        )
        with redirect_stdout(io.StringIO()):
            code = self.delegate.main(
                [
                    "run",
                    "--cwd",
                    str(self.project),
                    "--task-file",
                    str(self.task),
                ]
            )
        self.assertEqual(code, 1)

    def test_error_event_message_is_returned(self):
        self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            run_stdout=error_event("sin cuota"),
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "opencode_event_error")
        self.assertIn("sin cuota", result["message"])

    def test_empty_output_is_error(self):
        self.fake(catalog=["opencode/mimo-v2.6-flash-free"], run_stdout="")
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "empty_output")

    def test_timeout_is_error(self):
        self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            timeout_error=True,
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "timeout")

    def test_nonzero_exit_is_error_without_leaking_output(self):
        self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
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
        self.fake(
            version_returncode=3,
            version_stderr="TOKEN=secreto-version",
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "version_check_failed")
        self.assertIn("3", result["message"])
        self.assertNotIn("secreto-version", result["message"])

    def test_catalog_failure_does_not_leak_output(self):
        self.fake(
            models_returncode=5,
            models_stderr="TOKEN=secreto-catalogo",
        )
        result = self.run_task()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "catalog_unavailable")
        self.assertIn("5", result["message"])
        self.assertNotIn("secreto-catalogo", result["message"])

    def test_missing_cost_is_null_not_zero(self):
        self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            run_stdout=text_event("ok") + "\n" + finish_event(),
        )
        result = self.run_task()
        self.assertEqual(result["status"], "ok")
        self.assertIsNone(result["cost"])

    def test_reported_cost_is_preserved(self):
        self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            run_stdout=text_event("ok") + "\n" + finish_event(cost=0),
        )
        result = self.run_task()
        self.assertEqual(result["cost"], 0)

    def test_summary_is_truncated_to_4000_characters(self):
        self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            run_stdout=text_event("x" * 5000) + "\n" + finish_event(cost=0),
        )
        result = self.run_task()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["summary"]), 4000)

    def test_success_returns_session_and_summary(self):
        self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            run_stdout=text_event("informe final", session="ses_abc")
            + "\n"
            + finish_event(cost=0, session="ses_abc"),
        )
        result = self.run_task()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["session"], "ses_abc")
        self.assertEqual(result["summary"], "informe final")
        self.assertEqual(result["model"], "opencode/mimo-v2.6-flash-free")

    def test_main_prints_one_compact_json_line(self):
        self.fake(
            catalog=["opencode/mimo-v2.6-flash-free"],
            run_stdout=text_event("ok") + "\n" + finish_event(cost=0),
        )
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = self.delegate.main(
                [
                    "run",
                    "--cwd",
                    str(self.project),
                    "--task-file",
                    str(self.task),
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
        bad_cwd = Path(self._tmp.name) / "carpeta-inexistente-ñandú"
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

    # --- doctor -----------------------------------------------------------

    def test_doctor_reports_version_catalog_and_allowed_availability(self):
        transport = self.fake(
            version="2.2.0",
            catalog=[
                "opencode/mimo-v2.6-flash-free",
                "opencode/glm-5.3-flash-free",
            ],
        )
        result = self.doctor()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["version"], "2.2.0")
        self.assertEqual(result["catalog_count"], 2)
        availability = {entry["model"]: entry["available"] for entry in result["allowed_models"]}
        self.assertTrue(availability["opencode/mimo-v2.6-flash-free"])
        self.assertTrue(availability["opencode/glm-5.3-flash-free"])
        self.assertFalse(availability["opencode/deepseek-v4.1-flash-free"])
        self.assertEqual(len(transport.calls), 2)

    def test_doctor_rejects_v1(self):
        self.fake(version="1.0.0")
        result = self.doctor()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "unsupported_version")

    def test_doctor_reports_unsafe_catalog_as_error(self):
        self.fake(
            catalog=["opencode/mimo-v2.6-flash-free", "openai/gpt-5"],
        )
        result = self.doctor()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "unsafe_catalog")

    # --- Descubrimiento del binario --------------------------------------

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

    def test_repo_policy_is_valid(self):
        self.delegate.validate_project_policy(ROOT)

    def test_policy_rejects_paid_model_entries(self):
        policy = {
            "default_model": "opencode/mimo-v2.6-flash-free",
            "allowed_models": ["opencode/mimo-v2.6-flash-free", "openai/gpt-5"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            path.write_text(json.dumps(policy), encoding="utf-8")
            with self.assertRaises(self.delegate.DelegateError) as ctx:
                self.delegate.load_policy(path)
        self.assertEqual(ctx.exception.code, "policy_invalid")


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
