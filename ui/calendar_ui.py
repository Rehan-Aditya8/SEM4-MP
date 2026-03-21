import customtkinter as ctk
from database.db import fetch_all
from datetime import datetime
import calendar

class CalendarFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#121212", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(1, weight=1)
        
        self.current_date = datetime.now()
        self.view_month = self.current_date.month
        self.view_year = self.current_date.year

        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.header.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.back_btn = ctk.CTkButton(self.header, text="← Back to Dashboard", width=150, height=35, 
                                      fg_color="#333333", hover_color="#444444", corner_radius=8,
                                      command=lambda: self.master.select_frame_by_name("dashboard"))
        self.back_btn.pack(side="left", padx=15)
        
        self.header_label = ctk.CTkLabel(self.header, text=f"Calendar - {self.current_date.strftime('%B %Y')}", 
                                         font=ctk.CTkFont(size=18, weight="bold"))
        self.header_label.pack(side="left", padx=20)

        # Left Column - Event Details
        self.event_col = ctk.CTkFrame(self, fg_color="transparent")
        self.event_col.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.upcoming_box = ctk.CTkFrame(self.event_col, fg_color="#34495e", corner_radius=10)
        self.upcoming_box.pack(fill="both", expand=True, pady=(0, 10))
        ctk.CTkLabel(self.upcoming_box, text="UPCOMING EVENTS", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.event_scroll = ctk.CTkScrollableFrame(self.upcoming_box, fg_color="transparent")
        self.event_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Middle Column - Main Calendar
        self.cal_main_frame = ctk.CTkFrame(self, fg_color="#34495e", corner_radius=10)
        self.cal_main_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Month Navigation
        self.nav_frame = ctk.CTkFrame(self.cal_main_frame, fg_color="transparent")
        self.nav_frame.pack(fill="x", pady=10)
        
        self.prev_btn = ctk.CTkButton(self.nav_frame, text="<", width=30, command=self.prev_month)
        self.prev_btn.pack(side="left", padx=50)
        
        self.month_year_label = ctk.CTkLabel(self.nav_frame, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.month_year_label.pack(side="left", expand=True)
        
        self.next_btn = ctk.CTkButton(self.nav_frame, text=">", width=30, command=self.next_month)
        self.next_btn.pack(side="right", padx=50)
        
        self.days_grid = ctk.CTkFrame(self.cal_main_frame, fg_color="transparent")
        self.days_grid.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.draw_calendar()
        self.load_upcoming_events()

    def draw_calendar(self):
        # Clear grid
        for widget in self.days_grid.winfo_children():
            widget.destroy()
            
        # Update label
        month_name = calendar.month_name[self.view_month]
        self.month_year_label.configure(text=f"{month_name} {self.view_year}")
        
        # Weekday headers
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, d in enumerate(days):
            ctk.CTkLabel(self.days_grid, text=d, font=ctk.CTkFont(size=12, weight="bold"), text_color="#3498db").grid(row=0, column=i, pady=5)
            
        # Get start day and total days
        # calendar.monthrange returns (weekday of first day, number of days)
        # weekday 0 is Monday, we want 0 as Sunday.
        first_weekday, num_days = calendar.monthrange(self.view_year, self.view_month)
        start_col = (first_weekday + 1) % 7
        
        # Fetch events for the month to highlight
        # Format: YYYY-MM
        month_str = f"{self.view_year}-{self.view_month:02d}"
        events_this_month = fetch_all("SELECT DISTINCT substr(start_time, 1, 10) FROM events WHERE start_time LIKE ?", (f"{month_str}%",))
        event_days = [int(e[0].split('-')[-1]) for e in events_this_month]

        row = 1
        col = start_col
        for day in range(1, num_days + 1):
            is_today = (day == self.current_date.day and 
                        self.view_month == self.current_date.month and 
                        self.view_year == self.current_date.year)
            
            has_event = day in event_days
            
            bg_color = "#3498db" if is_today else "#2c3e50"
            border_color = "#f39c12" if has_event else bg_color
            border_width = 2 if has_event else 0
            
            btn = ctk.CTkButton(self.days_grid, text=str(day), width=50, height=50, 
                                fg_color=bg_color, border_width=border_width, border_color=border_color,
                                font=ctk.CTkFont(size=12, weight="bold" if is_today else "normal"),
                                command=lambda d=day: self.show_day_events(d))
            btn.grid(row=row, column=col, padx=3, pady=3)
            
            col += 1
            if col > 6:
                col = 0
                row += 1

    def load_upcoming_events(self):
        for widget in self.event_scroll.winfo_children():
            widget.destroy()
            
        events = fetch_all("SELECT title, start_time FROM events WHERE start_time >= date('now') ORDER BY start_time LIMIT 10")
        if not events:
            ctk.CTkLabel(self.event_scroll, text="No upcoming events", font=ctk.CTkFont(size=11, slant="italic")).pack(pady=10)
            return

        for title, start_time in events:
            e_frame = ctk.CTkFrame(self.event_scroll, fg_color="#2c3e50", corner_radius=5)
            e_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(e_frame, text=title, font=ctk.CTkFont(size=11, weight="bold"), anchor="w").pack(fill="x", padx=10, pady=(5, 0))
            ctk.CTkLabel(e_frame, text=start_time, font=ctk.CTkFont(size=9), text_color="gray", anchor="w").pack(fill="x", padx=10, pady=(0, 5))

    def prev_month(self):
        self.view_month -= 1
        if self.view_month < 1:
            self.view_month = 12
            self.view_year -= 1
        self.draw_calendar()

    def next_month(self):
        self.view_month += 1
        if self.view_month > 12:
            self.view_month = 1
            self.view_year += 1
        self.draw_calendar()

    def show_day_events(self, day):
        # Placeholder for showing specific day events in the sidebar
        pass

    def refresh(self):
        self.draw_calendar()
        self.load_upcoming_events()
