"""ticket track dispatch-check 命令（0.18.0-W10-017.2）。

取代 PC-050 `cat .claude/dispatch-active.json` 片段，提供 CLI 化的活躍派發判定：
- exit 0: 無活躍派發（檔案不存在 / dispatches=[]，視同已清空）
- exit 1: 有活躍派發（列出每筆 agent_description / ticket_id / dispatched_at）
- exit 2: IO 或 JSON 格式錯誤（stderr + 保守 NO-GO 供 Hook 程式化判定）

語意等價依據：
- PC-050 派發後清點 / 收到完成通知兩處均為讀檔 + 判斷 dispatches 陣列空/非空
- 新 CLI 多加：格式化輸出 + exit code，不改變判定規則
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# dispatch-active.json 屬跨 agent 協調狀態，root 解析改用
# get_ticket_state_root()（非 get_project_root()）——linked worktree 內
# 統一寫入/讀取主倉庫，理由與 get_ticket_state_root docstring 一致。
from ticket_system.lib.paths import get_ticket_state_root

_DISPATCH_ACTIVE_RELPATH = Path(".claude/dispatch-active.json")

# 3-H 個案 1／2：dispatch-check 原判定只收「dispatches 是否為空」，無記錄
# 新鮮度維度，PM 依 WARN 後無可執行下一步（無從分辨活躍派發是剛發出還是
# 已逾時遺留）。沿用 track_dashboard.DEFAULT_STALE_THRESHOLD_MIN（60 分鐘）
# 同一新鮮度慣例，不另立門檻常數。
_STALE_THRESHOLD_MIN = 60


def _format_age(dispatched_at: object, now: datetime) -> str:
    """回傳 dispatched_at 距 now 的新鮮度標註；無法解析（缺失/格式錯誤/
    未來時間）回傳空字串，不猜測。"""
    if not isinstance(dispatched_at, str) or not dispatched_at.strip():
        return ""
    try:
        ts = datetime.fromisoformat(dispatched_at.replace("Z", "+00:00"))
    except ValueError:
        return ""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    age_minutes = (now - ts).total_seconds() / 60
    if age_minutes < 0:
        return ""
    if age_minutes >= _STALE_THRESHOLD_MIN:
        return f" [STALE {age_minutes:.0f}min]"
    return f" ({age_minutes:.0f}min)"


def _format_entry(entry: dict, now: Optional[datetime] = None) -> str:
    desc = entry.get("agent_description", "(unknown)")
    tid = entry.get("ticket_id") or "(no ticket)"
    ts = entry.get("dispatched_at", "(no timestamp)")
    age = _format_age(entry.get("dispatched_at"), now) if now is not None else ""
    return f"  - {desc} | ticket: {tid} | {ts}{age}"


def execute_dispatch_check(args: argparse.Namespace) -> int:
    """執行 dispatch-check 命令。

    Returns:
        0: 無活躍派發；1: 有活躍派發；2: IO/格式錯誤。
    """

    dispatch_file = get_ticket_state_root() / _DISPATCH_ACTIVE_RELPATH

    if not dispatch_file.exists():
        print("[PASS] 無活躍派發，可繼續")
        return 0

    try:
        raw = dispatch_file.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, PermissionError) as e:
        sys.stderr.write(f"[FAIL] dispatch-active.json 讀取失敗: {e}\n")
        return 2
    except json.JSONDecodeError as e:
        sys.stderr.write(f"[FAIL] dispatch-active.json JSON 格式錯誤: {e}\n")
        return 2

    if not isinstance(data, dict):
        sys.stderr.write("[FAIL] dispatch-active.json root 結構不是 dict\n")
        return 2

    dispatches = data.get("dispatches", [])
    if not isinstance(dispatches, list):
        sys.stderr.write("[FAIL] dispatch-active.json dispatches 欄位不是 list\n")
        return 2

    if not dispatches:
        print("[PASS] 無活躍派發，可繼續")
        return 0

    now = datetime.now(timezone.utc)
    stale_count = sum(
        1
        for entry in dispatches
        if isinstance(entry, dict) and "[STALE" in _format_age(entry.get("dispatched_at"), now)
    )
    print(f"[WARN] 有 {len(dispatches)} 個活躍派發：")
    for entry in dispatches:
        if isinstance(entry, dict):
            print(_format_entry(entry, now))
        else:
            print(f"  - (malformed entry: {entry!r})")
    if stale_count:
        print(
            f"[WARN] 其中 {stale_count} 筆逾 {_STALE_THRESHOLD_MIN} 分鐘未見更新"
            "（[STALE] 標記），可能為遺留記錄，建議對照 `track sessions` 或"
            "人工清理"
        )
    return 1


def register_dispatch_check(
    subparsers: argparse._SubParsersAction,
) -> argparse.ArgumentParser:
    """註冊 dispatch-check 子命令。"""
    p = subparsers.add_parser(
        "dispatch-check",
        help="檢查 .claude/dispatch-active.json 活躍派發（0=無/1=有/2=IO錯誤）",
    )
    return p
