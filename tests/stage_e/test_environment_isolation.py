from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from stage_e_harness.canonical import Refusal
from stage_e_harness.environment import EXPECTED_ENVIRONMENT, validate_framework_origin
from scripts.validate_stage_e_harness import _isolated_python_path


class StageEEnvironmentIsolationTests(unittest.TestCase):
    def test_reference_environment_is_exact_and_closed(self) -> None:
        self.assertEqual(EXPECTED_ENVIRONMENT["architecture"], "linux/amd64")
        self.assertEqual(EXPECTED_ENVIRONMENT["python_version"], "3.14.4-final")
        self.assertEqual(EXPECTED_ENVIRONMENT["sqlite_version_info"], [3, 46, 1])
        self.assertEqual(EXPECTED_ENVIRONMENT["network"], "OFFLINE")

    def test_source_checkout_origin_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            site = root / "site-packages"; site.mkdir()
            source = root / "source"; source.mkdir()
            origin = source / "ebu_framework" / "__init__.py"; origin.parent.mkdir(); origin.touch()
            with self.assertRaises(Refusal):
                validate_framework_origin(str(origin), str(site), str(source))

            base_python = root / "base-python"
            base_python.touch()
            environment = root / "isolated"
            (environment / "bin").mkdir(parents=True)
            (environment / "pyvenv.cfg").touch()
            venv_python = environment / "bin" / "python"
            venv_python.symlink_to(base_python)
            self.assertEqual(_isolated_python_path(venv_python), venv_python.absolute())
            self.assertNotEqual(_isolated_python_path(venv_python), venv_python.resolve())

            (environment / "pyvenv.cfg").unlink()
            with self.assertRaises(Refusal):
                _isolated_python_path(venv_python)


if __name__ == "__main__":
    unittest.main()
