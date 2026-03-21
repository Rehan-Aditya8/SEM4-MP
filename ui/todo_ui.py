import customtkinter as ctk
from database.db import fetch_all, execute_query

class TodoFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#121212", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.back_btn = ctk.CTkButton(self.header_frame, text="← Back to Dashboard", width=150, height=30, fg_color="#333333", corner_radius=8, command=lambda: master.select_frame_by_name("dashboard"))
        self.back_btn.pack(side="left")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Daily Checklist", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        self.title_label.pack(side="left", padx=20)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="#1e1e1e", corner_radius=15)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.refresh()

    def refresh(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        tasks = fetch_all("SELECT id, title, deadline, status FROM tasks ORDER BY created_at DESC")
        for task_id, title, deadline, status in tasks:
            frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#252525", corner_radius=8)
            frame.pack(fill="x", padx=10, pady=5)
            
            var = ctk.BooleanVar(value=(status == 'completed'))
            cb = ctk.CTkCheckBox(frame, text=f"{title} (Due: {deadline})", variable=var, text_color="white", border_width=2, corner_radius=5,
                                 command=lambda i=task_id, v=var: self.toggle_task(i, v))
            cb.pack(side="left", padx=10, pady=5)
            
            btn_del = ctk.CTkButton(frame, text="X", width=30, fg_color="red", command=lambda i=task_id: self.delete_task(i))
            btn_del.pack(side="right", padx=10, pady=5)

    def toggle_task(self, task_id, var):
        new_status = 'completed' if var.get() else 'pending'
        execute_query("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))

    def delete_task(self, task_id):
        execute_query("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.refresh()
