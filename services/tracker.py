import time
import threading
import win32gui
import win32process
import psutil
import json
import os

from database.db import execute_query


class ActivityTracker:
    def __init__(self, interval=10):
        self.interval = interval
        self.running = False
        self.thread = None

        # Load categories from JSON
        self.categories = self.load_categories()
        
        # Track last state to avoid redundant logging
        self.last_app = None
        self.last_title = None

    # ===== LOAD CATEGORY CONFIG =====
    def load_categories(self):
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "data", "app_categories.json")
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print("Error loading categories:", e)
            return {
                "productive_apps": [],
                "productive_keywords": [],
                "distraction_keywords": []
            }

    # ===== GET ACTIVE WINDOW INFO =====
    def get_active_window_info(self):
        try:
            window = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(window)

            pid = win32process.GetWindowThreadProcessId(window)[1]
            process = psutil.Process(pid)
            app_name = process.name().lower()

            is_productive = self.classify_activity(app_name, title)

            return title, app_name, is_productive

        except Exception as e:
            print("Error getting active window:", e)
            return "Idle", "N/A", 1

    # ===== CLASSIFICATION LOGIC =====
    def classify_activity(self, app_name, title):
        title = title.lower()

        # Special handling for browsers
        if "chrome" in app_name or "brave" in app_name or "edge" in app_name:
            for kw in self.categories.get("distraction_keywords", []):
                if kw in title:
                    return 0

            for kw in self.categories.get("productive_keywords", []):
                if kw in title:
                    return 1

        # Existing logic for other apps
        for kw in self.categories.get("distraction_keywords", []):
            if kw in title:
                return 0

        if app_name in self.categories.get("productive_apps", []):
            return 1

        # Default: assume productive (safer)
        return 1

    # ===== LOG ACTIVITY =====
    def log_activity(self):
        while self.running:
            title, app, productive = self.get_active_window_info()

            if app != self.last_app or title != self.last_title:
                try:
                    execute_query(
                        """
                        INSERT INTO logs (window_title, app_name, is_productive, timestamp)
                        VALUES (?, ?, ?, datetime('now'))
                        """,
                        (title, app, productive)
                    )
                    self.last_app = app
                    self.last_title = title
                except Exception as e:
                    print("DB insert error:", e)

            time.sleep(self.interval)

    # ===== START TRACKER =====
    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self.log_activity, daemon=True)
        self.thread.start()

        print("Activity Tracker Started")

    # ===== STOP TRACKER =====
    def stop(self):
        self.running = False
        print("Activity Tracker Stopped")