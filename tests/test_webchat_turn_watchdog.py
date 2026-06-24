import importlib.util
import json
import sys
import unittest
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "webchat-turn-watchdog.py"


def load_watchdog():
    spec = importlib.util.spec_from_file_location("webchat_turn_watchdog", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class WebchatTurnWatchdogTests(unittest.TestCase):
    def test_parse_ts_ms_treats_z_timestamp_as_utc(self):
        watchdog = load_watchdog()

        parsed = watchdog.parse_ts_ms("2026-06-23T23:17:04.751Z")

        expected = int(datetime(2026, 6, 23, 23, 17, 4, 751000, tzinfo=timezone.utc).timestamp() * 1000)
        self.assertEqual(parsed, expected)

    def test_scan_once_rechecks_overlap_for_unprocessed_lost_turn(self):
        import tempfile

        watchdog = load_watchdog()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sessions_dir = tmp_path / "sessions"
            sessions_dir.mkdir()
            trajectory = sessions_dir / "753762f6-32da-480b-94e5-b72782c033dc.trajectory.jsonl"
            event = {
                "type": "session.ended",
                "ts": "2026-06-23T23:17:04.751Z",
                "sessionKey": "agent:main:dashboard:767ad6c6-754c-4294-8858-964bea759104",
                "sessionId": "753762f6-32da-480b-94e5-b72782c033dc",
                "runId": "5890db17-2401-4d75-935d-e630ee142a61",
                "traceId": "753762f6-32da-480b-94e5-b72782c033dc",
                "seq": 147,
                "data": {"promptError": "codex app-server client closed before turn completed"},
            }
            trajectory.write_text(json.dumps(event) + "\n")
            event_ms = watchdog.parse_ts_ms(event["ts"])
            later_ms = event_ms + 16 * 60 * 60 * 1000
            state_file = tmp_path / "state.json"
            state_file.write_text(json.dumps({"last_scan_ms": later_ms, "processed": []}) + "\n")

            found = watchdog.scan_once(
                Namespace(
                    sessions_dir=sessions_dir,
                    state_file=state_file,
                    log_file=tmp_path / "watchdog.log",
                    initial_lookback_seconds=900,
                    scan_lookback_seconds=24 * 60 * 60,
                    dry_run=True,
                    no_alert=True,
                )
            )

            state = json.loads(state_file.read_text())
            self.assertEqual(found, 1)
            self.assertEqual(
                state["processed"],
                ["753762f6-32da-480b-94e5-b72782c033dc:5890db17-2401-4d75-935d-e630ee142a61:147"],
            )

    def test_scan_once_retries_lost_turn_when_alert_fails(self):
        import tempfile

        watchdog = load_watchdog()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sessions_dir = tmp_path / "sessions"
            sessions_dir.mkdir()
            session_key = "agent:main:dashboard:767ad6c6-754c-4294-8858-964bea759104"
            trajectory = sessions_dir / "753762f6-32da-480b-94e5-b72782c033dc.trajectory.jsonl"
            event = {
                "type": "session.ended",
                "ts": "2026-06-24T14:11:10.000Z",
                "sessionKey": session_key,
                "sessionId": "753762f6-32da-480b-94e5-b72782c033dc",
                "runId": "359b687b-5255-4e89-b4fa-a8216b3f6d50",
                "traceId": "753762f6-32da-480b-94e5-b72782c033dc",
                "seq": 147,
                "data": {"promptError": "codex app-server client closed before turn completed"},
            }
            trajectory.write_text(json.dumps(event) + "\n")
            (sessions_dir / "sessions.json").write_text(
                json.dumps({session_key: {"updatedAt": 1}}) + "\n"
            )
            state_file = tmp_path / "state.json"
            state_file.write_text(json.dumps({"last_scan_ms": watchdog.parse_ts_ms(event["ts"]), "processed": []}) + "\n")

            original_send_telegram = watchdog.send_telegram
            watchdog.send_telegram = lambda message: (False, "gateway unavailable")
            try:
                found = watchdog.scan_once(
                    Namespace(
                        sessions_dir=sessions_dir,
                        state_file=state_file,
                        log_file=tmp_path / "watchdog.log",
                        initial_lookback_seconds=900,
                        scan_lookback_seconds=24 * 60 * 60,
                        dry_run=False,
                        no_alert=False,
                    )
                )
            finally:
                watchdog.send_telegram = original_send_telegram

            state = json.loads(state_file.read_text())
            self.assertEqual(found, 1)
            self.assertEqual(state["processed"], [])
            self.assertIn("lost_turn_retry_pending", (tmp_path / "watchdog.log").read_text())


if __name__ == "__main__":
    unittest.main()
