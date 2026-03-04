"""告警去重状态持久化。"""

from __future__ import annotations

import json
import time
from pathlib import Path


class AlertStateStore:
    """维护并持久化告警去重状态。"""

    def __init__(self, state_file: Path | None = None):
        default_state = Path.home() / ".stock_monitor" / "alert_state.json"
        self.state_file = Path(state_file or default_state)
        self.alert_log: list[dict] = []
        self._load()

    def _load(self) -> None:
        if not self.state_file.exists():
            self.alert_log = []
            return
        try:
            with self.state_file.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if isinstance(payload, list):
                self.alert_log = payload
            else:
                self.alert_log = []
        except Exception:  # noqa: BLE001
            self.alert_log = []

    def _save(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with self.state_file.open("w", encoding="utf-8") as handle:
            json.dump(self.alert_log, handle, ensure_ascii=False, indent=2)

    def cleanup(self, window_seconds: int = 1800) -> None:
        now = time.time()
        self.alert_log = [
            item
            for item in self.alert_log
            if now - float(item.get("t", 0)) < window_seconds
        ]

    def alerted_recently(
        self,
        code: str,
        alert_type: str,
        window_seconds: int = 1800,
    ) -> bool:
        self.cleanup(window_seconds)
        for item in self.alert_log:
            if item.get("c") == code and item.get("a") == alert_type:
                return True
        return False

    def record_alert(self, code: str, alert_type: str) -> None:
        self.alert_log.append({"c": code, "a": alert_type, "t": time.time()})
        self.cleanup()
        self._save()
