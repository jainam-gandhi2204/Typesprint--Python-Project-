"""
History Manager for Typing Speed Tracker.
Handles storing test records in JSON format and computing statistical summaries.
"""

import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "typing_history.json")


class HistoryManager:
    def __init__(self, filepath=HISTORY_FILE):
        self.filepath = filepath
        self.records = self._load()

    def _load(self):
        """Load records from JSON file. Returns empty list if file doesn't exist."""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            return []

    def save_record(self, wpm: int, accuracy: float, difficulty: str, duration_sec: int, errors: int):
        """Append a new test record and save to file."""
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "wpm": int(wpm),
            "accuracy": round(accuracy, 1),
            "difficulty": difficulty,
            "duration": duration_sec,
            "errors": errors
        }
        self.records.insert(0, record)  # Most recent first
        # Limit to last 50 records
        self.records = self.records[:50]
        self._write()
        return record

    def _write(self):
        """Write records to JSON file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=2)
        except IOError as e:
            print(f"Error saving history: {e}")

    def get_summary(self):
        """Calculate aggregate statistics."""
        if not self.records:
            return {
                "total_tests": 0,
                "best_wpm": 0,
                "avg_wpm": 0,
                "avg_accuracy": 0.0
            }

        total_tests = len(self.records)
        best_wpm = max(r["wpm"] for r in self.records)
        avg_wpm = round(sum(r["wpm"] for r in self.records) / total_tests)
        avg_accuracy = round(sum(r["accuracy"] for r in self.records) / total_tests, 1)

        return {
            "total_tests": total_tests,
            "best_wpm": best_wpm,
            "avg_wpm": avg_wpm,
            "avg_accuracy": avg_accuracy
        }

    def clear(self):
        """Clear all saved history."""
        self.records = []
        self._write()
