"""Unit tests for skill_sync.cli exclude-file logic and content-hash sync comparison."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill_sync.cli import (  # noqa: E402
    _classify_sync_status,
    _extract_local_manifest,
    _has_local_override,
    _should_exclude_file,
    build_parser,
    compute_content_hash,
    compute_diff,
    EXCLUDE_DIRS,
    print_diff_preview,
    prune_dst_only,
    SKILL_SYNC_OVERRIDE_MARKER,
    update_sync_manifest,
)


def test_hook_logs_top_level_jsonl_excluded():
    assert _should_exclude_file(".claude/hook-logs/cli-force-usage.jsonl") is True


def test_hook_logs_nested_subdir_excluded():
    assert _should_exclude_file(".claude/hook-logs/identity-guard/usage.log") is True


def test_hook_logs_dir_registered_in_exclude_dirs():
    assert "hook-logs" in EXCLUDE_DIRS


def test_regular_skill_file_not_excluded():
    assert _should_exclude_file("SKILL.md") is False
    assert _should_exclude_file("scripts/run.py") is False


def test_existing_exclude_dirs_still_work():
    assert _should_exclude_file(".venv/lib/site-packages/foo.py") is True
    assert _should_exclude_file("__pycache__/cli.cpython-314.pyc") is True
    assert _should_exclude_file(".pytest_cache/v/cache/nodeids") is True


def test_compute_diff_excludes_hook_logs_from_added(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    (src / "SKILL.md").write_text("hello")
    hook_logs_dir = src / ".claude" / "hook-logs" / "identity-guard"
    hook_logs_dir.mkdir(parents=True)
    (hook_logs_dir / "usage.log").write_text("runtime state")
    (src / ".claude" / "hook-logs" / "cli-force-usage.jsonl").write_text("{}")

    diff = compute_diff(src, dst)

    assert "SKILL.md" in diff["added"]
    assert not any("hook-logs" in f for f in diff["added"])
    assert not any("hook-logs" in f for f in diff["modified"])
    assert not any("hook-logs" in f for f in diff["dst_only"])


def _write_skill(base: Path, name: str, version: str, body: str) -> Path:
    """建立測試用 skill 目錄，SKILL.md 含指定版本字串與內文，回傳該目錄路徑。"""
    skill_dir = base / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"# {name}\n\n**Version**: {version}\n\n{body}\n"
    )
    return skill_dir


class _FakeCompletedProcess:
    """替代 subprocess.CompletedProcess，讓 update_sync_manifest 的測試不觸發真實 git/網路操作。"""

    def __init__(self, returncode: int = 0) -> None:
        self.returncode = returncode
        self.stdout = ""
        self.stderr = ""


# --- compute_content_hash ---------------------------------------------------


def test_content_hash_identical_content_produces_identical_hash(tmp_path):
    a = _write_skill(tmp_path / "a", "wrap-decision", "2.5.0", "same body")
    b = _write_skill(tmp_path / "b", "wrap-decision", "2.5.0", "same body")

    assert compute_content_hash(a) == compute_content_hash(b)


def test_content_hash_different_content_produces_different_hash(tmp_path):
    a = _write_skill(tmp_path / "a", "wrap-decision", "2.5.0", "content A")
    b = _write_skill(tmp_path / "b", "wrap-decision", "2.5.0", "content B")

    assert compute_content_hash(a) != compute_content_hash(b)


def test_content_hash_ignores_mtime(tmp_path):
    skill_dir = _write_skill(tmp_path, "wrap-decision", "2.5.0", "body")
    first = compute_content_hash(skill_dir)

    (skill_dir / "SKILL.md").touch()  # 更新 mtime，不改內容

    assert compute_content_hash(skill_dir) == first


def test_content_hash_excludes_override_marker_file(tmp_path):
    skill_dir = _write_skill(tmp_path, "wrap-decision", "2.5.0", "body")
    without_marker = compute_content_hash(skill_dir)

    (skill_dir / SKILL_SYNC_OVERRIDE_MARKER).write_text("local customization notice")

    assert compute_content_hash(skill_dir) == without_marker


def test_content_hash_excludes_hook_logs_dir(tmp_path):
    skill_dir = _write_skill(tmp_path, "wrap-decision", "2.5.0", "body")
    without_logs = compute_content_hash(skill_dir)

    hook_logs = skill_dir / "hook-logs"
    hook_logs.mkdir()
    (hook_logs / "usage.log").write_text("runtime state")

    assert compute_content_hash(skill_dir) == without_logs


def test_content_hash_returns_none_for_missing_dir(tmp_path):
    assert compute_content_hash(tmp_path / "does-not-exist") is None


# --- regression: 同號不同內容不再被判為 up_to_date（0.2.1-W3-124 §11.2） ------


def test_blog_and_canonical_2_5_0_same_version_different_content_are_diverged(tmp_path):
    """blog 的 2.5.0（基礎設施累積型絆腳索）與 canonical 的 2.5.0（行前預想配早期警訊）
    版本字串相同、內容不同；修改前的字串比對會誤判為 up_to_date，本測試證明
    改用內容雜湊後兩者被正確識別為分歧。"""
    local_dir = _write_skill(
        tmp_path / "local", "wrap-decision", "2.5.0",
        "基礎設施累積型絆腳索：blog 專案本地演化內容",
    )
    remote_dir = _write_skill(
        tmp_path / "remote", "wrap-decision", "2.5.0",
        "行前預想配早期警訊：canonical 演化內容",
    )

    local_manifest = {
        "wrap-decision": {
            "version": "2.5.0",
            "hash": compute_content_hash(local_dir),
        }
    }
    remote_manifest = {
        "wrap-decision": {
            "version": "2.5.0",
            "hash": compute_content_hash(remote_dir),
        }
    }

    up_to_date, diverged, overridden, skipped = _classify_sync_status(
        local_manifest, remote_manifest, tmp_path / "local"
    )

    assert up_to_date == []
    assert overridden == []
    assert skipped == []
    assert len(diverged) == 1
    name, local_display, remote_display = diverged[0]
    assert name == "wrap-decision"
    assert local_display == "2.5.0"
    assert remote_display == "2.5.0"


# --- _classify_sync_status ---------------------------------------------------


def test_classify_sync_status_up_to_date_when_hash_matches(tmp_path):
    local_manifest = {"foo": {"version": "1.0.0", "hash": "same-hash"}}
    remote_manifest = {"foo": {"version": "1.0.0", "hash": "same-hash"}}

    up_to_date, diverged, overridden, skipped = _classify_sync_status(
        local_manifest, remote_manifest, tmp_path
    )

    assert up_to_date == ["foo"]
    assert diverged == []
    assert overridden == []
    assert skipped == []


def test_classify_sync_status_skips_remote_without_hash_field(tmp_path):
    """remote 尚為舊格式（純版本字串）時不誤判為分歧或同步，改列為待更新的 skipped。"""
    local_manifest = {"foo": {"version": "1.0.0", "hash": "abc"}}
    remote_manifest = {"foo": "1.0.0"}  # 舊格式：純字串，無 hash 欄位

    up_to_date, diverged, overridden, skipped = _classify_sync_status(
        local_manifest, remote_manifest, tmp_path
    )

    assert skipped == ["foo"]
    assert up_to_date == []
    assert diverged == []


def test_classify_sync_status_respects_local_override_marker(tmp_path):
    skill_dir = tmp_path / "foo"
    skill_dir.mkdir()
    (skill_dir / SKILL_SYNC_OVERRIDE_MARKER).write_text("intentional customization")

    local_manifest = {"foo": {"version": "1.0.0", "hash": "local-hash"}}
    remote_manifest = {"foo": {"version": "2.0.0", "hash": "remote-hash"}}

    up_to_date, diverged, overridden, skipped = _classify_sync_status(
        local_manifest, remote_manifest, tmp_path
    )

    assert overridden == ["foo"]
    assert up_to_date == []
    assert diverged == []
    assert skipped == []


def test_has_local_override_false_when_marker_absent(tmp_path):
    (tmp_path / "foo").mkdir()
    assert _has_local_override(tmp_path / "foo") is False


# --- _extract_local_manifest -------------------------------------------------


def test_extract_local_manifest_builds_hash_and_version(tmp_path):
    skills_dir = tmp_path / "skills"
    skill_dir = _write_skill(skills_dir, "wrap-decision", "2.7.0", "body")

    manifest = _extract_local_manifest(skills_dir)

    assert manifest["wrap-decision"]["version"] == "2.7.0"
    assert manifest["wrap-decision"]["hash"] == compute_content_hash(skill_dir)


def test_extract_local_manifest_empty_dir_returns_empty(tmp_path):
    assert _extract_local_manifest(tmp_path / "no-such-dir") == {}


# --- prune_dst_only（--prune 刪除傳播，0.2.1-W3-350） ------------------------
#
# push 對 remote-only 檔案的預設是保留（避免誤刪上游內容），代價是本地的刪除與
# 更名永遠傳不到遠端，殘留檔會被其他 consumer 專案 pull 下去。--prune 是顯式
# opt-in 的刪除路徑，預設行為不變。


def test_prune_deletes_dst_only_files(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "SKILL.md").write_text("kept")
    (dst / "SKILL.md").write_text("kept")
    (dst / "obsolete-hook.py").write_text("removed locally")

    diff = compute_diff(src, dst)
    removed = prune_dst_only(dst, diff)

    assert removed == 1
    assert not (dst / "obsolete-hook.py").exists()
    assert (dst / "SKILL.md").exists()


def test_prune_removes_directories_left_empty(tmp_path):
    """刪光某目錄下所有檔案後該目錄應一併消失，否則遠端留下空殼目錄。"""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    (src / "SKILL.md").write_text("kept")
    hooks = dst / "hooks"
    hooks.mkdir(parents=True)
    (dst / "SKILL.md").write_text("kept")
    (hooks / "old-a.py").write_text("gone")
    (hooks / "old-b.py").write_text("gone")

    diff = compute_diff(src, dst)
    prune_dst_only(dst, diff)

    assert not hooks.exists()


def test_prune_leaves_excluded_dirs_untouched(tmp_path):
    """project-integration 等排除目錄不進 dst_only，故 prune 不得波及。"""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "SKILL.md").write_text("kept")
    (dst / "SKILL.md").write_text("kept")
    (dst / "obsolete-hook.py").write_text("removed locally")
    integration = dst / "project-integration"
    integration.mkdir(parents=True)
    (integration / "triggers.md").write_text("consumer-specific")

    diff = compute_diff(src, dst)
    removed = prune_dst_only(dst, diff)

    # removed > 0 使空目錄清理實際執行，確認該掃描不會波及排除目錄
    assert removed == 1
    assert (integration / "triggers.md").exists()


def test_prune_returns_zero_when_no_dst_only(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "SKILL.md").write_text("same")
    (dst / "SKILL.md").write_text("same")

    diff = compute_diff(src, dst)

    assert prune_dst_only(dst, diff) == 0


def test_push_parser_accepts_prune_flag():
    """--prune 必須是 push 的合法旗標，且預設關閉（安全預設不因新增旗標改變）。"""
    parser = build_parser()

    with_prune = parser.parse_args(["push", "demo-skill", "--prune"])
    without_prune = parser.parse_args(["push", "demo-skill"])

    assert with_prune.prune is True
    assert without_prune.prune is False


def test_pull_parser_has_no_prune_flag():
    """prune 僅適用 push 方向；pull 誤帶會刪本地檔案，故不提供此旗標。"""
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["pull", "demo-skill", "--prune"])


def test_preview_labels_dst_only_as_prune_when_enabled(capsys):
    """預覽標籤必須隨 --prune 改變，否則使用者看到 preserved 卻發生刪除。"""
    diff = {"added": [], "modified": [], "unchanged": [], "dst_only": ["hooks/old.py"]}

    print_diff_preview(diff, direction="push", prune=True)
    pruning_output = capsys.readouterr().out

    print_diff_preview(diff, direction="push", prune=False)
    preserving_output = capsys.readouterr().out

    assert "prune" in pruning_output.lower()
    assert "preserved" in preserving_output.lower()
    assert "preserved" not in pruning_output.lower()


# --- update_sync_manifest（不觸發真實 git/網路操作） -------------------------


def test_update_sync_manifest_writes_hash_matching_extract_local_manifest(tmp_path, monkeypatch):
    skill_dir = _write_skill(tmp_path, "wrap-decision", "2.5.0", "canonical content")

    monkeypatch.setattr(
        "skill_sync.cli.subprocess.run",
        lambda *a, **k: _FakeCompletedProcess(returncode=0),
    )

    update_sync_manifest(tmp_path)

    written = json.loads((tmp_path / "versions.json").read_text())
    assert written["wrap-decision"]["version"] == "2.5.0"
    assert written["wrap-decision"]["hash"] == compute_content_hash(skill_dir)
