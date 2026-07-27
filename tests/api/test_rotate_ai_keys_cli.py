import os
import subprocess


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "python", "-m", "packages.backend.bootstrap", *arguments],
        text=True,
        capture_output=True,
        env=os.environ.copy(),
        check=False,
        start_new_session=True,
    )


def test_bootstrap_cli_exposes_rotation_without_master_key_arguments() -> None:
    root = _run("--help")
    rotation = _run("rotate-ai-keys", "--help")

    assert root.returncode == 0
    assert "rotate-ai-keys" in root.stdout
    assert rotation.returncode == 0
    assert "--target-key-id" in rotation.stdout
    assert "--batch-size" in rotation.stdout
    assert "--after-profile-id" in rotation.stdout
    assert "--dry-run" in rotation.stdout
    assert "--master-key" not in rotation.stdout + rotation.stderr
    assert "--key-file" not in rotation.stdout + rotation.stderr


def test_rotation_cli_reports_missing_external_configuration_without_leaking_secrets() -> None:
    result = _run("rotate-ai-keys", "--target-key-id", "new-key", "--dry-run")
    combined = result.stdout + result.stderr

    assert result.returncode == 2
    assert "外部 AI 主密钥" in combined
    assert "扫描" not in combined
    assert "api_key" not in combined.lower()
