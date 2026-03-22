import customtkinter as ctk
import os
from PIL import Image
from services.outlook_service import OutlookService
from services.parser import EmailParser
from database.db import execute_query, fetch_all
from ui.analytics_ui import AnalyticsFrame
from services.blocker_service import toggle_block, is_block_active, block_websites, unblock_websites, is_admin

class Toast(ctk.CTkFrame):
    def __init__(self, master, message, color="#2ecc71", **kwargs):
        super().__init__(master, fg_color=color, corner_radius=10, **kwargs)
        self.label = ctk.CTkLabel(self, text=message, text_color="white", font=ctk.CTkFont(size=13, weight="bold"))
        self.label.pack(padx=20, pady=10)
        
        # Position at the top center of the master
        self.place(relx=0.5, rely=0.1, anchor="n")
        
        # Auto-dismiss after 2s
        self.after(2000, self.destroy_toast)
        
    def destroy_toast(self):
        self.destroy()

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#121212", **kwargs)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left Side - Focus & Outlook
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.left_container, text="ZENITHFOCUS", font=ctk.CTkFont(size=32, weight="bold"), text_color="white")
        self.logo_label.pack(anchor="w", padx=10, pady=(10, 30))
        
        self.mode_btn_frame = ctk.CTkFrame(self.left_container, fg_color="transparent")
        self.mode_btn_frame.pack(fill="x", pady=10)
        
        self.focus_mode_btn = ctk.CTkButton(self.mode_btn_frame, text="Focus Mode", fg_color="#d35400", hover_color="#e67e22", text_color="white", font=ctk.CTkFont(size=14, weight="bold"), height=35, corner_radius=8, command=self.toggle_focus)
        self.focus_mode_btn.pack(side="left", padx=10)
        
        self.coding_mode_btn = ctk.CTkButton(self.mode_btn_frame, text="Coding Mode", fg_color="#2980b9", hover_color="#3498db", 
                                            text_color="white", font=ctk.CTkFont(size=14, weight="bold"), height=35, corner_radius=8,
                                            command=self.show_coding_stats)
        self.coding_mode_btn.pack(side="left", padx=10)

        # Removed Quick Block switch
        self.update_focus_button_state()
        
        # Outlook Summary Box
        self.outlook_box = ctk.CTkFrame(self.left_container, fg_color="#1e1e1e", corner_radius=15)
        self.outlook_box.pack(fill="both", expand=True, pady=20)
        
        self.header_bar = ctk.CTkFrame(self.outlook_box, fg_color="#252525", height=40, corner_radius=10)
        self.header_bar.pack(fill="x", padx=10, pady=10)
        self.header_bar.pack_propagate(False)
        
        self.outlook_title = ctk.CTkLabel(self.header_bar, text="Outlook Summary", text_color="white", font=ctk.CTkFont(size=16, weight="bold"))
        self.outlook_title.pack(side="left", padx=20)
        
        # Outlook filter dropdown
        self.outlook_filter_var = ctk.StringVar(value="All")
        self.outlook_filter = ctk.CTkComboBox(self.header_bar, values=["All", "Urgent", "Upcoming", "Later"], 
                                             variable=self.outlook_filter_var, command=lambda _: self.load_data(),
                                             width=120, height=28, corner_radius=8, fg_color="#333333", border_color="#444444")
        self.outlook_filter.pack(side="right", padx=10)
        
        self.scroll_emails = ctk.CTkScrollableFrame(self.outlook_box, fg_color="transparent", height=400)
        self.scroll_emails.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Right Side - Widgets
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_rowconfigure(0, weight=1)
        self.right_container.grid_rowconfigure(1, weight=1)
        self.right_container.grid_rowconfigure(2, weight=2) # To-Do gets more space
        
        # Mini Analytics
        self.ana_widget = ctk.CTkFrame(self.right_container, fg_color="#1e1e1e", corner_radius=15)
        self.ana_widget.grid(row=0, column=0, pady=(0, 10), sticky="nsew")
        # Removed pack_propagate(False) to allow auto-sizing or set min height
        self.ana_widget.grid_rowconfigure(0, weight=1)
        
        ctk.CTkLabel(self.ana_widget, text="Daily Productivity", font=ctk.CTkFont(size=12, weight="bold"), text_color="white").pack(pady=5)
        
        # Placeholder for Pie Chart (similar to reference)
        self.canvas_ana = ctk.CTkCanvas(self.ana_widget, width=120, height=120, bg="#1e1e1e", highlightthickness=0)
        self.canvas_ana.pack(pady=5)
        self.canvas_ana.create_oval(10, 10, 110, 110, fill="#2980b9", outline="")
        self.canvas_ana.create_arc(10, 10, 110, 110, start=0, extent=120, fill="#e74c3c", outline="")
        self.canvas_ana.create_arc(10, 10, 110, 110, start=120, extent=60, fill="#f1c40f", outline="")

        ctk.CTkButton(self.ana_widget, text="EXPAND", text_color="white", fg_color="#2980b9", hover_color="#3498db", font=ctk.CTkFont(size=10, weight="bold"), height=25, corner_radius=8, command=lambda: master.select_frame_by_name("analytics")).pack(pady=5)
        
        # Mini Calendar
        self.cal_widget = ctk.CTkFrame(self.right_container, fg_color="#1e1e1e", corner_radius=15)
        self.cal_widget.grid(row=1, column=0, pady=10, sticky="nsew")
        self.cal_widget.grid_rowconfigure(0, weight=1)
        
        ctk.CTkLabel(self.cal_widget, text="March 2026", text_color="white", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "calendar_icon.png")
            pil_img = Image.open(icon_path)
            # Scaled up significantly to fill space
            self.cal_icon = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(100, 100))
            self.cal_icon_label = ctk.CTkLabel(self.cal_widget, image=self.cal_icon, text="")
            self.cal_icon_label.pack(pady=10, fill="both", expand=True)
        except Exception as e:
            print("Error loading calendar icon:", e)
            
        # Removed placeholder "Calendar Grid Here" label
        
        ctk.CTkButton(self.cal_widget, text="EXPAND", text_color="white", fg_color="#2980b9", hover_color="#3498db", font=ctk.CTkFont(size=10, weight="bold"), height=25, corner_radius=8, command=lambda: master.select_frame_by_name("calendar")).pack(pady=10)
        
        # Mini Todo
        self.todo_widget = ctk.CTkFrame(self.right_container, fg_color="#1e1e1e", corner_radius=15)
        self.todo_widget.grid(row=2, column=0, pady=10, sticky="nsew")
        ctk.CTkLabel(self.todo_widget, text="To-Do List", text_color="white", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        # To-Do Input Area
        self.todo_input_frame = ctk.CTkFrame(self.todo_widget, fg_color="transparent")
        self.todo_input_frame.pack(fill="x", padx=10, pady=5)
        
        self.todo_entry = ctk.CTkEntry(self.todo_input_frame, placeholder_text="New task...", height=32, corner_radius=8)
        self.todo_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.todo_add_btn = ctk.CTkButton(self.todo_input_frame, text="+", width=32, height=32, corner_radius=8, fg_color="#27ae60", hover_color="#2ecc71", command=self.add_task)
        self.todo_add_btn.pack(side="right")
        
        # To-Do Scrollable List
        self.todo_list_frame = ctk.CTkScrollableFrame(self.todo_widget, fg_color="transparent", height=250)
        self.todo_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.load_data()

    def load_data(self):
        if not self.winfo_exists(): return # Prevent crash if widget is gone
        
        # Clear existing
        for widget in self.scroll_emails.winfo_children():
            widget.destroy()
        
        self.refresh_todo()

        # Load Emails
        service = OutlookService()
        emails = service.fetch_emails()
        filter_val = self.outlook_filter_var.get()
        
        # Get completed titles
        completed = fetch_all("SELECT title FROM completed_entities")
        completed_titles = [c[0] for c in completed]
        
        for email in emails:
            if email['subject'] in completed_titles:
                continue
                
            urgency = EmailParser.get_urgency(email)
            if filter_val != "All" and urgency != filter_val:
                continue
                
            info = EmailParser.extract_info(email)
            
            e_frame = ctk.CTkFrame(self.scroll_emails, fg_color="transparent")
            e_frame.pack(fill="x", pady=5, padx=5)
            
            # Horizontal layout for title and buttons
            inner_row = ctk.CTkFrame(e_frame, fg_color="transparent")
            inner_row.pack(fill="x", expand=True)
            
            # Categorize the email for display
            display_category = EmailParser.categorize(email)
            title_text = f"{display_category.upper()}: {info['title']}"
            
            # Urgency chip
            urgency_colors = {"Urgent": "#e74c3c", "Upcoming": "#f39c12", "Later": "#7f8c8d"}
            chip_color = urgency_colors.get(urgency, "#7f8c8d")
            
            # Container for subject and chip
            info_container = ctk.CTkFrame(inner_row, fg_color="transparent")
            info_container.pack(side="left", fill="x", expand=True)
            
            # SUBJECT FIRST
            title_label = ctk.CTkLabel(info_container, text=info['title'], text_color="white", font=ctk.CTkFont(size=13, weight="bold"), 
                                      anchor="w", wraplength=250)
            title_label.pack(side="left", padx=(0, 10))
            
            # TAG SECOND
            urgency_chip = ctk.CTkLabel(info_container, text=urgency.upper(), font=ctk.CTkFont(size=9, weight="bold"), 
                                       fg_color=chip_color, text_color="white", corner_radius=10, width=60, height=20)
            urgency_chip.pack(side="left")
            
            # Buttons and horizontal alignment
            btn_row = ctk.CTkFrame(inner_row, fg_color="transparent")
            btn_row.pack(side="right")
            
            add_cal_btn = ctk.CTkButton(btn_row, text="Add to Cal", width=80, height=28, fg_color="#2980b9", hover_color="#3498db", corner_radius=6, font=ctk.CTkFont(size=11), command=lambda e=email: self.add_to_calendar(e))
            add_cal_btn.pack(side="left", padx=2)
            
            add_todo_btn = ctk.CTkButton(btn_row, text="Add to ToDo", width=90, height=28, fg_color="#27ae60", hover_color="#2ecc71", corner_radius=6, font=ctk.CTkFont(size=11), command=lambda e=email: self.add_to_todo(e))
            add_todo_btn.pack(side="left", padx=2)
            
            # Divider
            ctk.CTkFrame(e_frame, fg_color="#333333", height=1).pack(fill="x", pady=(8, 0))

        # Tasks are already loaded in self.refresh_todo()

    def add_to_todo(self, email):
        info = EmailParser.extract_info(email)
        # Prevent duplicates
        existing = fetch_all("SELECT id FROM tasks WHERE title = ?", (info['title'],))
        if existing:
            Toast(self, "Already in ToDo!", color="#e67e22")
            return
            
        execute_query("INSERT INTO tasks (title, description, deadline, category) VALUES (?, ?, ?, ?)",
                      (info['title'], email['body'], info['deadline'], 'ToDo'))
        Toast(self, "Added to ToDo!")
        self.load_data() # Refresh

    def add_to_calendar(self, email):
        info = EmailParser.extract_info(email)
        # Prevent duplicates
        existing = fetch_all("SELECT id FROM events WHERE title = ?", (info['title'],))
        if existing:
            Toast(self, "Already in Calendar!", color="#e67e22")
            return
            
        execute_query("INSERT INTO events (title, start_time) VALUES (?, ?)",
                      (info['title'], info['deadline']))
        #print(f"Added event: {info['title']}")
        Toast(self, "Added to Calendar!", color="#2980b9")

    def toggle_focus(self):
        if not is_admin():
            Toast(self, "Administrator permission required to enable Focus Mode", color="#e74c3c")
            return

        active = is_block_active()
        if active:
            if unblock_websites():
                Toast(self, "Focus Mode Disabled", color="#d35400")
            else:
                Toast(self, "Error: Could not disable Focus Mode", color="#e74c3c")
        else:
            if block_websites():
                Toast(self, "Focus Mode Enabled – Distractions Blocked", color="#27ae60")
            else:
                Toast(self, "Error: Could not enable Focus Mode", color="#e74c3c")
        
        self.update_focus_button_state()
        
        # Sync with settings frame if it's already created
        if hasattr(self.master, 'settings_frame'):
            self.master.settings_frame.refresh_status()

    def update_focus_button_state(self):
        active = is_block_active()
        if active:
            self.focus_mode_btn.configure(text="Focus ON", fg_color="#27ae60", hover_color="#2ecc71")
        else:
            self.focus_mode_btn.configure(text="Focus Mode", fg_color="#d35400", hover_color="#e67e22")

    # ===== TODO CRUD =====
    def refresh_todo(self):
        if not self.winfo_exists() or not self.todo_list_frame.winfo_exists(): return
        
        for widget in self.todo_list_frame.winfo_children():
            widget.destroy()
            
        # Load Tasks
        tasks = fetch_all("SELECT id, title, status FROM tasks WHERE status != 'completed' ORDER BY created_at DESC LIMIT 5")
        for task_id, title, status in tasks:
            item_frame = ctk.CTkFrame(self.todo_list_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=2)
            
            var = ctk.BooleanVar(value=(status == 'completed'))
            cb = ctk.CTkCheckBox(item_frame, text=title, variable=var, text_color="white", font=ctk.CTkFont(size=12), border_width=2, corner_radius=5,
                                 command=lambda i=task_id, v=var, t=title: self.toggle_todo(i, v, t))
            cb.pack(side="left", padx=5)
            
            btn_del = ctk.CTkButton(item_frame, text="🗑", width=20, height=20, fg_color="transparent", text_color="#e74c3c", hover_color="#333333",
                                    command=lambda i=task_id: self.delete_task(i))
            btn_del.pack(side="right", padx=5)

    def add_task(self):
        title = self.todo_entry.get()
        if title.strip():
            execute_query("INSERT INTO tasks (title, status) VALUES (?, ?)", (title, 'pending'))
            self.todo_entry.delete(0, 'end')
            self.refresh_todo()

    def delete_task(self, task_id):
        execute_query("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.refresh_todo()

    def sync_completion(self, title, is_completed):
        status = 'completed' if is_completed else 'pending'
        execute_query("UPDATE tasks SET status = ? WHERE title = ?", (status, title))
        execute_query("UPDATE events SET status = ? WHERE title = ?", (status, title))
        
        if is_completed:
            execute_query("INSERT OR IGNORE INTO completed_entities (title) VALUES (?)", (title,))
        else:
            execute_query("DELETE FROM completed_entities WHERE title = ?", (title,))
        
        self.load_data()
        self.refresh_todo()

    def toggle_todo(self, task_id, var, title):
        self.sync_completion(title, var.get())

    def show_coding_stats(self):
        # Fetch today's stats
        from database.db import fetch_all
        import pandas as pd
        
        # Today's logs
        query = "SELECT timestamp, is_productive, app_name FROM logs WHERE date(timestamp, 'localtime') = date('now', 'localtime')"
        logs = fetch_all(query)
        
        if not logs:
            total_time = "0m"
            most_used = "N/A"
            dist_time = "0m"
        else:
            df = pd.DataFrame(logs, columns=['ts', 'prod', 'app'])
            df['ts'] = pd.to_datetime(df['ts'])
            df['dur'] = df['ts'].diff().shift(-1).dt.total_seconds().clip(upper=900).fillna(10)
            
            total_s = df['dur'].sum()
            total_time = f"{int(total_s//3600)}h {int((total_s%3600)//60)}m" if total_s >= 3600 else f"{int(total_s//60)}m"
            
            most_used = df.groupby('app')['dur'].sum().idxmax().replace(".exe", "").capitalize()
            if len(most_used) > 15: most_used = most_used[:12] + "..."
            
            dist_s = df[df['prod'] == 0]['dur'].sum()
            dist_time = f"{int(dist_s//60)}m"

        # Show Popup
        popup = StatsPopup(self, total_time, most_used, dist_time)
        popup.place(relx=0.5, rely=0.5, anchor="center")

class StatsPopup(ctk.CTkFrame):
    def __init__(self, master, total_time, most_used, dist_time, **kwargs):
        super().__init__(master, fg_color="#1e1e1e", corner_radius=15, border_width=2, border_color="#3498db", **kwargs)
        
        ctk.CTkLabel(self, text="TODAY'S STATS", font=ctk.CTkFont(size=14, weight="bold"), text_color="#3498db").pack(pady=(15, 10), padx=30)
        
        self.add_stat("Total Tracked:", total_time, "#ffffff")
        self.add_stat("Most Used App:", most_used, "#9b59b6")
        self.add_stat("Distraction Time:", dist_time, "#e74c3c")
        
        ctk.CTkButton(self, text="CLOSE", fg_color="#333333", hover_color="#444444", width=100, height=30, corner_radius=8, 
                      command=self.destroy).pack(pady=15)

    def add_stat(self, label, value, color):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=11), text_color="#aaaaaa").pack(side="left")
        ctk.CTkLabel(f, text=value, font=ctk.CTkFont(size=12, weight="bold"), text_color=color).pack(side="right")

