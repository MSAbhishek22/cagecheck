"""CageCheck runtime cage — fresh code, written 3 Nov 2026 in the Vultr event window.

Local layer (this sandbox): a child Python process with a restricted
import hook, a cage-only open(), a blocked socket/subprocess, secret-scrubbed
env, and resource limits. This is process + patch isolation, NOT a
kernel/container boundary. The real boundary on Vultr is a throwaway Docker
container per check (see Dockerfile + VULTR_DEPLOY.md), destroyed after
each check. Never present this local layer as container isolation.
"""
import json
import os
import resource
import subprocess
import sys
import tempfile
import textwrap

RUNNER = textwrap.dedent('''
    import builtins, io, json, os, sys

    CAGE = os.environ["CAGE_DIR"]

    class BlockedError(Exception):
        pass

    def _inside(path):
        try:
            real = os.path.realpath(path)
            return os.path.commonpath([real, CAGE]) == CAGE
        except Exception:
            return False

    def cage_open(path, *args, **kwargs):
        p = os.fspath(path)
        if not _inside(p):
            raise BlockedError(f"open blocked outside cage: {p}")
        if any(f in p for f in (".ssh", ".aws", ".gnupg", ".kube", ".netrc", ".env", "id_ed25519", "id_rsa")):
            raise BlockedError(f"secret path blocked: {p}")
        return builtins_open(p, *args, **kwargs)

    builtins_open = builtins.open
    builtins.open = cage_open
    io.open = cage_open

    _real_import = builtins.__import__
    BLOCKED_MODS = {"subprocess", "socket", "urllib", "urllib.request", "requests", "http.client"}
    def cage_import(name, *args, **kwargs):
        top = name.split(".")[0]
        if name in BLOCKED_MODS or top in BLOCKED_MODS:
            raise BlockedError(f"import blocked: {name}")
        return _real_import(name, *args, **kwargs)
    builtins.__import__ = cage_import

    # Env scrubbing is done by the parent (cage.py); the runner also
    # refuses to print secret-like env values.
    snippet_path = sys.argv[1]
    with builtins_open(snippet_path, "r") as f:
        code = f.read()
    try:
        exec(compile(code, "<snippet>", "exec"), {"__name__": "__main__"})
        print(json.dumps({"ok": True, "blocked": None}))
    except BlockedError as exc:
        print(json.dumps({"ok": False, "blocked": str(exc)}))
    except Exception as exc:
        print(json.dumps({"ok": False, "blocked": None, "error": f"{type(exc).__name__}: {exc}"}))
''')


def _scrubbed_env(cage_dir):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "CAGE_DIR": cage_dir, "PYTHONPATH": ""}
    return env


def _limits():
    def preexec():
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
            resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
            resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
        except Exception:
            pass
    return preexec


def run_in_cage(snippet, timeout=5):
    """Run snippet in the local cage. Returns dict(ok, blocked, error, output)."""
    with tempfile.TemporaryDirectory(prefix="cagecheck-") as cage_dir:
        snippet_path = os.path.join(cage_dir, "snippet.py")
        runner_path = os.path.join(cage_dir, "runner.py")
        with open(snippet_path, "w") as f:
            f.write(snippet)
        with open(runner_path, "w") as f:
            f.write(RUNNER)
        try:
            proc = subprocess.run(
                [sys.executable, runner_path, snippet_path],
                capture_output=True, text=True, timeout=timeout,
                env=_scrubbed_env(cage_dir), preexec_fn=_limits(),
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "blocked": "resource limit: 5s timeout exceeded", "error": None, "output": ""}
        out = proc.stdout.strip().splitlines()
        # Last line is the runner's JSON report; earlier lines are snippet output.
        report = {"ok": True, "blocked": None, "error": None}
        printed = []
        for line in out:
            try:
                parsed = json.loads(line)
                if isinstance(parsed, dict) and ("ok" in parsed or "blocked" in parsed):
                    report = parsed
                    continue
            except Exception:
                pass
            printed.append(line)
        output = "\n".join(printed)[:64 * 1024]
        return {"ok": bool(report.get("ok")), "blocked": report.get("blocked"),
                "error": report.get("error"), "output": output}
