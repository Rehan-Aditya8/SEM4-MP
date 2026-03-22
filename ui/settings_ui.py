import customtkinter as ctk
from services.blocker_service import toggle_block, is_block_active


class SettingsUI(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#121212", **kwargs)

        # ===== HEADER =====
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.header.pack(fill="x", padx=10, pady=10)
        
        self.back_btn = ctk.CTkButton(
            self.header, 
            text="← Back to Dashboard", 
            width=150, 
            height=35, 
            fg_color="#333333", 
            hover_color="#444444", 
            corner_radius=8,
            command=lambda: parent.select_frame_by_name("dashboard")
        )
        self.back_btn.pack(side="left", padx=15)

        # ===== TITLE =====
        self.title_label = ctk.CTkLabel(
            self,
            text="Website Blocker",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=(20, 10))

        # ===== STATUS LABEL =====
        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Checking...",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=10)

        # ===== TOGGLE BUTTON =====
        self.toggle_button = ctk.CTkButton(
            self,
            text="Loading...",
            command=self.toggle_action,
            width=200,
            height=40
        )
        self.toggle_button.pack(pady=20)

        # ===== REFRESH STATE =====
        self.refresh_status()

    # ===== UPDATE UI BASED ON STATUS =====
    def refresh_status(self):
        active = is_block_active()

        if active:
            self.status_label.configure(text="Status: ON (Websites Blocked)")
            self.toggle_button.configure(text="Disable Blocker")
        else:
            self.status_label.configure(text="Status: OFF (Websites Allowed)")
            self.toggle_button.configure(text="Enable Blocker")

    # ===== BUTTON ACTION =====
    def toggle_action(self):
        success = toggle_block()

        if success:
            self.refresh_status()
            # Sync with dashboard if it's already created
            if hasattr(self.master, 'dashboard_frame'):
                self.master.dashboard_frame.update_focus_button_state()
        else:
            self.status_label.configure(
                text="Error: Run app as Administrator",
                text_color="red"
            )