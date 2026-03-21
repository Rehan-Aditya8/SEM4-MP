import customtkinter as ctk
from database.db import init_db
from services.tracker import ActivityTracker
from ui.dashboard import DashboardFrame
from ui.calendar_ui import CalendarFrame
from ui.analytics_ui import AnalyticsFrame
from ui.settings_ui import SettingsUI

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FocusDeskApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FocusDesk - Productivity App")
        self.geometry("1100x700")

        # Initialize Database
        init_db()

        # Initialize Activity Tracker
        self.tracker = ActivityTracker(interval=15)
        self.tracker.start()

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Content Frames
        self.dashboard_frame = DashboardFrame(self, corner_radius=0)
        self.calendar_frame = CalendarFrame(self, corner_radius=0)
        self.analytics_frame = AnalyticsFrame(self, corner_radius=0)
        self.settings_frame = SettingsUI(self, corner_radius=0)

        # Select default frame
        self.select_frame_by_name("dashboard")

    def select_frame_by_name(self, name):
        # Show selected frame
        if name == "dashboard":
            self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
            self.dashboard_frame.update_switch_state()
        else:
            self.dashboard_frame.grid_forget()
            
        if name == "calendar":
            self.calendar_frame.grid(row=0, column=0, sticky="nsew")
            self.calendar_frame.refresh()
        else:
            self.calendar_frame.grid_forget()

        if name == "analytics":
            self.analytics_frame.grid(row=0, column=0, sticky="nsew")
            self.analytics_frame.show_charts()
        else:
            self.analytics_frame.grid_forget()

        if name == "settings":
            self.settings_frame.grid(row=0, column=0, sticky="nsew")
            self.settings_frame.refresh_status()
        else:
            self.settings_frame.grid_forget()

    def on_closing(self):
        self.tracker.stop()
        self.destroy()

if __name__ == "__main__":
    app = FocusDeskApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
