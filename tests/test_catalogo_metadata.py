"""Regresiones del formato real de tarifas de la API de OpenCode v2."""

import importlib.util
import json
import subprocess
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


class RealCatalogShapeTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / "skills/delegating-to-opencode/scripts/delegate.py"
        spec = importlib.util.spec_from_file_location("metadata_contract", path)
        self.delegate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.delegate)

    def inspect(self, tariffs):
        payload = {
            "location": {"directory": str(ROOT)},
            "data": [{
                "id": "modelo-con-tarifas",
                "modelID": "modelo-con-tarifas",
                "providerID": "cuenta-externa",
                "name": "Modelo de prueba",
                "type": "chat",
                "capabilities": {"tools": True, "input": ["text"], "output": ["text"]},
                "variants": [{"id": "high", "settings": {"reasoningEffort": "high"}}],
                "time": {"released": 0},
                "cost": tariffs,
                "status": "active",
                "enabled": True,
                "limit": {"context": 100000, "output": 8000},
            }],
        }

        def transport(argv, cwd, timeout):
            output = "opencode v2.2.0\n" if "--version" in argv else json.dumps(payload)
            return subprocess.CompletedProcess(argv, 0, stdout=output, stderr="")

        with mock.patch.object(self.delegate, "find_opencode", return_value="opencode.exe"), \
                mock.patch.object(self.delegate, "run_process", side_effect=transport):
            result = self.delegate.doctor(cwd=ROOT)
        self.assertEqual(result["status"], "ok", result)
        return result["catalog"][0]

    def test_zero_tariff_array_from_real_api_is_a_free_candidate(self):
        entry = self.inspect([{"input": 0, "output": 0, "cache": {"read": 0, "write": 0}}])
        self.assertIs(entry["free_candidate"], True)
        self.assertIsNotNone(entry["pricing"])

    def test_positive_tier_or_cache_price_cannot_be_classified_as_free(self):
        for tariffs in (
            [{"input": 0, "output": 0}, {"input": 1, "output": 2}],
            [{"input": 0, "output": 0, "cache": {"read": 0.1, "write": 0}}],
        ):
            with self.subTest(tariffs=tariffs):
                self.assertIs(self.inspect(tariffs)["free_candidate"], False)


if __name__ == "__main__":
    unittest.main()
