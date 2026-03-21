import customtkinter as ctk
from services.outlook_service import OutlookService
from services.parser import EmailParser
from database.db import execute_query, fetch_all
from ui.analytics_ui import AnalyticsFrame
from services.blocker_service import toggle_block, is_block_active

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
        
        self.focus_mode_btn = ctk.CTkButton(self.mode_btn_frame, text="Focus Mode", fg_color="#d35400", hover_color="#e67e22", text_color="white", font=ctk.CTkFont(size=14, weight="bold"), height=35, corner_radius=8)
        self.focus_mode_btn.pack(side="left", padx=10)
        
        self.coding_mode_btn = ctk.CTkButton(self.mode_btn_frame, text="Coding Mode", fg_color="#2980b9", hover_color="#3498db", text_color="white", font=ctk.CTkFont(size=14, weight="bold"), height=35, corner_radius=8)
        self.coding_mode_btn.pack(side="left", padx=10)

        self.blocker_switch = ctk.CTkSwitch(
            self.mode_btn_frame, 
            text="Quick Block", 
            text_color="white", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            command=self.quick_toggle,
            width=150,
            height=40,
            switch_width=60,
            switch_height=30
        )
        self.blocker_switch.pack(side="left", padx=20)
        self.update_switch_state()
        
        # Outlook Summary Box
        self.outlook_box = ctk.CTkFrame(self.left_container, fg_color="#1e1e1e", corner_radius=15)
        self.outlook_box.pack(fill="both", expand=True, pady=20)
        
        self.header_bar = ctk.CTkFrame(self.outlook_box, fg_color="#252525", height=40, corner_radius=10)
        self.header_bar.pack(fill="x", padx=10, pady=10)
        self.header_bar.pack_propagate(False)
        
        self.outlook_title = ctk.CTkLabel(self.header_bar, text="Outlook Summary", text_color="white", font=ctk.CTkFont(size=16, weight="bold"))
        self.outlook_title.pack(expand=True)
        
        self.scroll_emails = ctk.CTkScrollableFrame(self.outlook_box, fg_color="transparent", height=400)
        self.scroll_emails.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Right Side - Widgets
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Mini Analytics
        self.ana_widget = ctk.CTkFrame(self.right_container, fg_color="#1e1e1e", corner_radius=15, height=200)
        self.ana_widget.pack(fill="x", pady=(0, 10))
        self.ana_widget.pack_propagate(False)
        
        ctk.CTkLabel(self.ana_widget, text="Daily Productivity", font=ctk.CTkFont(size=12, weight="bold"), text_color="white").pack(pady=5)
        
        # Placeholder for Pie Chart (similar to reference)
        self.canvas_ana = ctk.CTkCanvas(self.ana_widget, width=120, height=120, bg="#1e1e1e", highlightthickness=0)
        self.canvas_ana.pack(pady=5)
        self.canvas_ana.create_oval(10, 10, 110, 110, fill="#2980b9", outline="")
        self.canvas_ana.create_arc(10, 10, 110, 110, start=0, extent=120, fill="#e74c3c", outline="")
        self.canvas_ana.create_arc(10, 10, 110, 110, start=120, extent=60, fill="#f1c40f", outline="")

        ctk.CTkButton(self.ana_widget, text="EXPAND", text_color="white", fg_color="#2980b9", hover_color="#3498db", font=ctk.CTkFont(size=10, weight="bold"), height=25, corner_radius=8, command=lambda: master.select_frame_by_name("analytics")).pack(pady=5)
        
        # Mini Calendar
        self.cal_widget = ctk.CTkFrame(self.right_container, fg_color="#1e1e1e", corner_radius=15, height=220)
        self.cal_widget.pack(fill="x", pady=10)
        self.cal_widget.pack_propagate(False)
        
        ctk.CTkLabel(self.cal_widget, text="January 2026", text_color="white", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        # Calendar placeholder text
        ctk.CTkLabel(self.cal_widget, text="Calendar Grid Here", text_color="gray70", font=ctk.CTkFont(size=12)).pack(pady=20, expand=True)
        
        ctk.CTkButton(self.cal_widget, text="EXPAND", text_color="white", fg_color="#2980b9", hover_color="#3498db", font=ctk.CTkFont(size=10, weight="bold"), height=25, corner_radius=8, command=lambda: master.select_frame_by_name("calendar")).pack(pady=10)
        
        # Mini Todo
        self.todo_widget = ctk.CTkFrame(self.right_container, fg_color="#1e1e1e", corner_radius=15)
        self.todo_widget.pack(fill="both", expand=True, pady=10)
        ctk.CTkLabel(self.todo_widget, text="To-Do List", text_color="white", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        # To-Do Input Area
        self.todo_input_frame = ctk.CTkFrame(self.todo_widget, fg_color="transparent")
        self.todo_input_frame.pack(fill="x", padx=10, pady=5)
        
        self.todo_entry = ctk.CTkEntry(self.todo_input_frame, placeholder_text="New task...", height=32, corner_radius=8)
        self.todo_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.todo_add_btn = ctk.CTkButton(self.todo_input_frame, text="+", width=32, height=32, corner_radius=8, fg_color="#27ae60", hover_color="#2ecc71", command=self.add_task)
        self.todo_add_btn.pack(side="right")
        
        # To-Do Scrollable List
        self.todo_list_frame = ctk.CTkScrollableFrame(self.todo_widget, fg_color="transparent", height=180)
        self.todo_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.load_data()

    def load_data(self):
        # Clear existing
        for widget in self.scroll_emails.winfo_children():
            widget.destroy()
        
        self.refresh_todo()

        # Load Emails
        service = OutlookService()
        emails = service.fetch_emails()
        
        for email in emails:
            category = EmailParser.categorize(email)
            info = EmailParser.extract_info(email)
            
            e_frame = ctk.CTkFrame(self.scroll_emails, fg_color="transparent")
            e_frame.pack(fill="x", pady=10, padx=5)
            
            title_label = ctk.CTkLabel(e_frame, text=f"{category.upper()}: {info['title']}", text_color="white", font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
            title_label.pack(fill="x")
            
            subtitle_label = ctk.CTkLabel(e_frame, text=f"Priority: {info.get('priority', 'Medium')} | {info['deadline']}", text_color="gray70", font=ctk.CTkFont(size=11), anchor="w")
            subtitle_label.pack(fill="x", pady=(2, 5))
            
            btn_box = ctk.CTkFrame(e_frame, fg_color="transparent")
            btn_box.pack(anchor="w")
            
            ctk.CTkButton(btn_box, text="Add to Calendar", width=100, height=28, fg_color="#2980b9", corner_radius=6, font=ctk.CTkFont(size=11), command=lambda e=email: self.add_to_calendar(e)).pack(side="left", padx=(0, 10))
            ctk.CTkButton(btn_box, text="Go to Mail", width=100, height=28, fg_color="#333333", corner_radius=6, font=ctk.CTkFont(size=11)).pack(side="left")

        # Load small Todo
        tasks = fetch_all("SELECT title FROM tasks LIMIT 5")
        for t in tasks:
            ctk.CTkCheckBox(self.todo_widget, text=t[0], text_color="white", font=ctk.CTkFont(size=12), border_width=2, corner_radius=5).pack(anchor="w", padx=20, pady=5)

    def add_to_todo(self, email):
        info = EmailParser.extract_info(email)
        execute_query("INSERT INTO tasks (title, description, deadline, category) VALUES (?, ?, ?, ?)",
                      (info['title'], email['body'], info['deadline'], 'ToDo'))
        self.load_data() # Refresh

    def add_to_calendar(self, email):
        info = EmailParser.extract_info(email)
        execute_query("INSERT INTO events (title, start_time) VALUES (?, ?)",
                      (info['title'], info['deadline']))
        print(f"Added event: {info['title']}")

    def quick_toggle(self):
        success = toggle_block()
        if not success:
            # Revert switch if failed (e.g. no admin)
            self.update_switch_state()
        else:
            # Sync with settings frame if it's already created
            if hasattr(self.master, 'settings_frame'):
                self.master.settings_frame.refresh_status()

    def update_switch_state(self):
        active = is_block_active()
        if active:
            self.blocker_switch.select()
        else:
            self.blocker_switch.deselect()

    # ===== TODO CRUD =====
    def refresh_todo(self):
        for widget in self.todo_list_frame.winfo_children():
            widget.destroy()
            
        tasks = fetch_all("SELECT id, title, status FROM tasks ORDER BY created_at DESC LIMIT 10")
        for task_id, title, status in tasks:
            item_frame = ctk.CTkFrame(self.todo_list_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=2)
            
            var = ctk.BooleanVar(value=(status == 'completed'))
            cb = ctk.CTkCheckBox(item_frame, text=title, variable=var, text_color="white", font=ctk.CTkFont(size=12), border_width=2, corner_radius=5,
                                 command=lambda i=task_id, v=var: self.toggle_todo(i, v))
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

    def toggle_todo(self, task_id, var):
        new_status = 'completed' if var.get() else 'pending'
        execute_query("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))

