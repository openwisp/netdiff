"""Check test-entry-point restrictions without running application tests."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class CiStandardizationTests(unittest.TestCase):
    def test_rejects_unsafe_labels_and_flags(self):
        for argument in (
            "--plugin=other",
            "--config=other",
            "os.system",
            "tests.test_x.Helper.test_run",
            "tests.test_olsr:TestOlsrParser",
        ):
            with self.subTest(argument=argument):
                result = subprocess.run(
                    [str(ROOT / "runtests"), argument],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("unsupported", result.stderr.lower())

    def test_selected_testcase_and_non_test_class(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy2(ROOT / "runtests", root / "runtests")
            (root / "tests").mkdir()
            (root / "tests" / "__init__.py").touch()
            (root / "tests" / "test_probe.py").write_text(
                "import unittest\n"
                "class TestProbe(unittest.TestCase):\n    def test_ok(self): pass\n"
                "class Helper:\n    def test_bad(self): pass\n"
            )
            (root / "nose2.py").write_text(
                'import sys\ndef discover(): print("|".join(sys.argv[1:]))\n'
            )
            env = {**os.environ, "PYTHONPATH": str(root)}
            valid = subprocess.run(
                [str(root / "runtests"), "tests.test_probe.TestProbe.test_ok", "-v"],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
            )
            invalid = subprocess.run(
                [str(root / "runtests"), "tests.test_probe.Helper.test_bad"],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
            )
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertEqual(valid.stdout.strip(), "tests.test_probe.TestProbe.test_ok|-v")
        self.assertEqual(invalid.returncode, 2)
        self.assertNotIn("test_bad", invalid.stdout)
