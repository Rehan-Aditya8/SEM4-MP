import customtkinter as ctk
from database.db import fetch_all, execute_query
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
        self.selected_date = self.current_date.day # Default to today

        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.header.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.back_btn = ctk.CTkButton(self.header, text="← Back to Dashboard", width=150, height=35, 
                                      fg_color="#333333", hover_color="#444444", corner_radius=8,
                                      command=lambda: self.master.select_frame_by_name("dashboard"))
        self.back_btn.pack(side="left", padx=15)
        
        self.header_label = ctk.CTkLabel(self.header, text=f"Calendar - {self.current_date.strftime('%B %Y')}", 
                                         font=ctk.CTkFont(size=22, weight="bold"), text_color="white")
        self.header_label.pack(side="left", padx=20)

        # Left Column - Event Details
        self.event_col = ctk.CTkFrame(self, fg_color="transparent")
        self.event_col.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.upcoming_box = ctk.CTkFrame(self.event_col, fg_color="#1e1e1e", corner_radius=15, border_width=1, border_color="#333333")
        self.upcoming_box.pack(fill="both", expand=True, pady=(0, 10))
        ctk.CTkLabel(self.upcoming_box, text="UPCOMING EVENTS", font=ctk.CTkFont(size=14, weight="bold"), text_color="#3498db").pack(pady=15)
        
        self.event_scroll = ctk.CTkScrollableFrame(self.upcoming_box, fg_color="transparent")
        self.event_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Middle Column - Main Calendar
        self.cal_main_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=15, border_width=1, border_color="#333333")
        self.cal_main_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Month Navigation
        self.nav_frame = ctk.CTkFrame(self.cal_main_frame, fg_color="transparent")
        self.nav_frame.pack(fill="x", pady=10)
        
        self.prev_btn = ctk.CTkButton(self.nav_frame, text="<", width=40, height=40, fg_color="#333333", hover_color="#444444", corner_radius=20, command=self.prev_month)
        self.prev_btn.pack(side="left", padx=50)
        
        self.month_year_label = ctk.CTkLabel(self.nav_frame, text="", font=ctk.CTkFont(size=22, weight="bold"), text_color="white")
        self.month_year_label.pack(side="left", expand=True)
        
        self.next_btn = ctk.CTkButton(self.nav_frame, text=">", width=40, height=40, fg_color="#333333", hover_color="#444444", corner_radius=20, command=self.next_month)
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
            
            is_selected = (day == self.selected_date)
            has_event = day in event_days
            
            # Base colors
            if is_today:
                fg_color = "#3498db" 
                hover_color = "#2980b9"
                text_color = "white"
            elif is_selected:
                fg_color = "#2c3e50"
                hover_color = "#34495e"
                text_color = "#3498db"
            else:
                fg_color = "transparent"
                hover_color = "#2c3e50"
                text_color = "white"

            # Create day button container for the dot
            day_btn = ctk.CTkButton(self.days_grid, text=str(day), width=60, height=60, 
                                fg_color=fg_color, hover_color=hover_color,
                                text_color=text_color,
                                border_width=2 if is_selected else 0,
                                border_color="#3498db" if is_selected else "#2c3e50",
                                font=ctk.CTkFont(size=14, weight="bold" if (is_today or is_selected) else "normal"),
                                command=lambda d=day: self.select_day(d))
            day_btn.grid(row=row, column=col, padx=5, pady=5)
            
            # Add event indicator dot if needed
            if has_event:
                dot = ctk.CTkLabel(day_btn, text="•", font=ctk.CTkFont(size=20), text_color="#f39c12", fg_color="transparent")
                dot.place(relx=0.5, rely=0.8, anchor="center")
            
            col += 1
            if col > 6:
                col = 0
                row += 1

    def select_day(self, day):
        self.selected_date = day
        self.draw_calendar()
        self.show_day_events(day)

    def load_upcoming_events(self):
        self.render_events("SELECT title, start_time FROM events WHERE status != 'completed' AND start_time >= date('now') ORDER BY start_time LIMIT 10")

    def render_events(self, query, params=()):
        for widget in self.event_scroll.winfo_children():
            widget.destroy()
            
        events = fetch_all(query, params)
        if not events:
            ctk.CTkLabel(self.event_scroll, text="No upcoming events", font=ctk.CTkFont(size=11, slant="italic")).pack(pady=10)
            return

        for title, start_time in events:
            e_frame = ctk.CTkFrame(self.event_scroll, fg_color="#1a1a1a", corner_radius=8, border_width=1, border_color="#333333")
            e_frame.pack(fill="x", pady=4, padx=5)
            
            info_frame = ctk.CTkFrame(e_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=12, pady=8)
            
            ctk.CTkLabel(info_frame, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="white", anchor="w").pack(fill="x")
            ctk.CTkLabel(info_frame, text=start_time, font=ctk.CTkFont(size=10), text_color="#aaaaaa", anchor="w").pack(fill="x")
            
            btn_done = ctk.CTkButton(e_frame, text="✓", width=30, height=30, fg_color="transparent", 
                                     hover_color="#27ae60", text_color="#2ecc71", 
                                     command=lambda t=title: self.complete_event(t))
            btn_done.pack(side="right", padx=5)

    def complete_event(self, title):
        execute_query("UPDATE events SET status = 'completed' WHERE title = ?", (title,))
        execute_query("INSERT OR IGNORE INTO completed_entities (title) VALUES (?)", (title,))
        execute_query("UPDATE tasks SET status = 'completed' WHERE title = ?", (title,))
        self.refresh()

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
        # Format: YYYY-MM-DD
        date_str = f"{self.view_year}-{self.view_month:02d}-{day:02d}"
        self.render_events("SELECT title, start_time FROM events WHERE start_time LIKE ? ORDER BY start_time", (f"{date_str}%",))
        
        # Override header text for clarity
        ctk.CTkLabel(self.upcoming_box, text=f"EVENTS FOR {day} {calendar.month_name[self.view_month]}", 
                    font=ctk.CTkFont(size=12)).pack(pady=5, before=self.event_scroll)

    def refresh(self):
        self.draw_calendar()
        self.load_upcoming_events()
