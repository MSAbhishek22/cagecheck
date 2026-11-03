"""CageCheck tests — fresh code, written 3 Nov 2026 in the Vultr event window."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.cage import run_in_cage
from app.policy import scan
from app.receipts import redact


class TestPolicy(unittest.TestCase):
    def test_ssh_read_blocked(self):
        v, rule, _ = scan("with open('/home/dev/.ssh/id_ed25519') as f:\n    x = f.read()")
        self.assertEqual(v, "BLOCKED")
        self.assertEqual(rule, "secret_path_read")

    def test_network_connect_blocked(self):
        v, rule, _ = scan("import socket\ns = socket.socket()\ns.connect(('example.com', 80))")
        self.assertEqual(v, "BLOCKED")

    def test_subprocess_blocked(self):
        v, _, _ = scan("import subprocess\nsubprocess.run(['ls'])")
        self.assertEqual(v, "BLOCKED")

    def test_policy_toggle_write_blocked(self):
        v, _, _ = scan("open('/app/policy.json', 'w').write('allow_all=True')")
        self.assertEqual(v, "BLOCKED")

    def test_clean_passes(self):
        v, rule, _ = scan("def total(p):\n    return sum(p)\n\nprint(total([10, 20, 30]))")
        self.assertEqual(v, "CLEAN")

    def test_network_import_held(self):
        v, _, _ = scan("import socket\nprint('hi')")
        self.assertEqual(v, "HELD")


class TestCage(unittest.TestCase):
    def test_clean_runs(self):
        r = run_in_cage("print(40 + 2)")
        self.assertTrue(r["ok"])
        self.assertIn("42", r["output"])

    def test_runtime_ssh_block(self):
        # Dynamic path construction bypasses static scan; runtime must still block.
        r = run_in_cage("p = '/home/dev/' + '.ssh/id_ed25519'\nwith open(p) as f:\n    print(f.read())")
        self.assertFalse(r["ok"])
        self.assertIsNotNone(r["blocked"])

    def test_runtime_socket_import_block(self):
        r = run_in_cage("import socket\nprint('should not reach here')")
        self.assertFalse(r["ok"])


class TestReceipts(unittest.TestCase):
    def test_redaction(self):
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", redact("key AKIAIOSFODNN7EXAMPLE here"))
        self.assertIn("[REDACTED]", redact("key AKIAIOSFODNN7EXAMPLE here"))


if __name__ == "__main__":
    unittest.main()
