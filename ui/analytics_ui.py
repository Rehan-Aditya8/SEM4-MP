import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db import fetch_all
import pandas as pd

class AnalyticsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#121212", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.back_btn = ctk.CTkButton(self.header_frame, text="← Back to Dashboard", width=150, height=30, fg_color="#333333", corner_radius=8, command=lambda: master.select_frame_by_name("dashboard"))
        self.back_btn.pack(side="left")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Productivity Analytics", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        self.title_label.pack(side="left", padx=20)
        
        # Filtering dropdown
        self.filter_var = ctk.StringVar(value="Today")
        self.filter_dropdown = ctk.CTkComboBox(self.header_frame, values=["Today", "Last 7 Days", "Last 30 Days"], 
                                             variable=self.filter_var, command=lambda _: self.show_charts(),
                                             width=150, corner_radius=8, fg_color="#333333", border_color="#444444")
        self.filter_dropdown.pack(side="right", padx=10)
        
        self.summary_container = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_container.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        self.chart_container = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=15)
        self.chart_container.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        self.refresh_btn = ctk.CTkButton(self, text="Refresh Charts", fg_color="#2980b9", hover_color="#3498db", corner_radius=8, command=self.show_charts)
        self.refresh_btn.grid(row=3, column=0, padx=20, pady=(0, 20))
        
        self.show_charts()

    def show_charts(self):
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        for widget in self.summary_container.winfo_children():
            widget.destroy()
            
        filter_type = self.filter_var.get()
        if filter_type == "Today":
            date_filter = "date(timestamp, 'localtime') = date('now', 'localtime')"
            title_prefix = "Today's"
        elif filter_type == "Last 7 Days":
            date_filter = "date(timestamp, 'localtime') >= date('now', 'localtime', '-7 days')"
            title_prefix = "Last 7 Days"
        else:
            date_filter = "date(timestamp, 'localtime') >= date('now', 'localtime', '-30 days')"
            title_prefix = "Last 30 Days"
            
        query = f"SELECT timestamp, is_productive, app_name, window_title FROM logs WHERE {date_filter} ORDER BY timestamp ASC"
        logs = fetch_all(query)
        
        # Exclude our own app from analytics
        app_exclusions = ["python.exe", "pythonw.exe", "focusdesk.exe"]
        logs = [log for log in logs if log[2].lower() not in app_exclusions]
        
        if not logs:
            ctk.CTkLabel(self.chart_container, text=f"No tracking data for {filter_type.lower()}. Keep working!", 
                        text_color="#888888", font=ctk.CTkFont(size=14)).pack(expand=True)
            return

        df = pd.DataFrame(logs, columns=['timestamp', 'is_productive', 'app_name', 'window_title'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Combine App Name and Window Title for better accuracy
        def format_name(row):
            app = str(row['app_name']).replace(".exe", "").capitalize()
            title = str(row['window_title'])
            
            # Browser special handling
            if app in ["Chrome", "Brave", "Msedge"]:
                if "youtube" in title.lower(): return "YouTube"
                if "spotify" in title.lower(): return "Spotify"
                if "netflix" in title.lower(): return "Netflix"
                if "github" in title.lower(): return "GitHub"
            
            if not title or title == "N/A" or title == "None":
                return app
            
            # Truncate title if too long
            if len(title) > 20:
                title = title[:17] + "..."
            return f"{app}: {title}"

        df['display_name'] = df.apply(format_name, axis=1)
        
        # Calculate duration
        # We assume each log entry represents activity until the next log entry
        df['duration'] = df['timestamp'].diff().shift(-1).dt.total_seconds()
        
        # Cap duration at 15 minutes (900s) to avoid huge gaps if computer was off/asleep
        # Since tracker logs every 10s on change, gaps usually mean inactivity or sleep
        df['duration'] = df['duration'].clip(upper=900)
        
        if not df.empty:
            last_log_time = df['timestamp'].iloc[-1]
            now = pd.Timestamp.now()
            # If the last log was very recent (within 5 mins), add current duration
            if (now - last_log_time).total_seconds() < 300:
                df.loc[df.index[-1], 'duration'] = (now - last_log_time).total_seconds()
            else:
                df.loc[df.index[-1], 'duration'] = 10 # Default small value for single logs

        df['duration'] = df['duration'].fillna(10)

        # --- Summary Section ---
        total_seconds = df['duration'].sum()
        h = int(total_seconds // 3600)
        m = int((total_seconds % 3600) // 60)
        total_time_str = f"{h}h {m}m" if h > 0 else f"{m}m"
        
        most_used = df.groupby('display_name')['duration'].sum().idxmax() if not df.empty else "N/A"
        if len(most_used) > 15: most_used = most_used[:12] + "..."
        
        prod_time_total = df[df['is_productive'] == 1]['duration'].sum()
        dist_time_total = df[df['is_productive'] == 0]['duration'].sum()
        prod_pct = (prod_time_total / total_seconds * 100) if total_seconds > 0 else 0
        
        self.create_summary_card("Total Time", total_time_str, "#3498db", 0)
        self.create_summary_card("Most Used", most_used, "#9b59b6", 1)
        self.create_summary_card("Productive", f"{prod_pct:.1f}%", "#2ecc71", 2)
        self.create_summary_card("Distraction", f"{(100-prod_pct):.1f}%", "#e74c3c", 3)

        # --- Matplotlib Styling ---
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(12, 5), facecolor='#1e1e1e')
        gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.5])
        
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        
        ax1.set_facecolor('#1e1e1e')
        ax2.set_facecolor('#1e1e1e')
        
        # Donut Chart (Productivity)
        prod_time = df.groupby('is_productive')['duration'].sum()
        labels = []
        colors = []
        # Ensure correct order and presence
        vals = []
        if 1 in prod_time.index:
            labels.append('Productive')
            colors.append('#2ecc71')
            vals.append(prod_time[1])
        if 0 in prod_time.index:
            labels.append('Distraction')
            colors.append('#e74c3c')
            vals.append(prod_time[0])
            
        if not vals: # Fallback if no data
            vals = [1]
            labels = ["No Data"]
            colors = ["#333333"]

        ax1.pie(vals, labels=labels, autopct='%1.1f%%', colors=colors, 
                textprops={'color':"w", 'fontsize': 10, 'weight': 'bold'}, startangle=90, pctdistance=0.8)
        
        # Draw circle for donut effect
        centre_circle = plt.Circle((0,0), 0.70, fc='#1e1e1e')
        ax1.add_artist(centre_circle)
        
        # Add center text
        ax1.text(0, 0, f"{prod_pct:.0f}%\nProductive", ha='center', va='center', 
                color='#2ecc71', fontsize=12, fontweight='bold')
        
        ax1.set_title(f"{title_prefix} Productivity", color="white", fontdict={'fontsize': 14, 'fontweight': 'bold'}, pad=20)
        
        # Horizontal Bar Chart (Top 10 Activities)
        app_time_all = df.groupby('display_name')['duration'].sum().sort_values(ascending=True)
        app_time = app_time_all.tail(10) # Get top 10 (sorted ascending for barh)
        
        # Convert seconds to minutes for display
        app_mins = app_time / 60
        
        # Determine colors for each bar
        colors = []
        for name in app_mins.index:
            is_prod = df[df['display_name'] == name]['is_productive'].iloc[0]
            colors.append('#3498db' if is_prod == 1 else '#e74c3c')
            
        bars = ax2.barh(app_mins.index, app_mins.values, color=colors, edgecolor='none', alpha=0.8)
        ax2.set_title(f"Top 10 Activities (Minutes)", color="white", fontdict={'fontsize': 14, 'fontweight': 'bold'}, pad=20)
        ax2.set_xlabel("Minutes", color="#aaaaaa", fontsize=10)
        
        # Remove spines for cleaner look
        for spine in ax2.spines.values():
            spine.set_visible(False)
        ax2.grid(axis='x', linestyle='--', alpha=0.3)
        
        # Format labels
        ax2.tick_params(axis='both', colors='#bbbbbb', labelsize=9)
        
        # Add value labels at the end of each bar
        for bar in bars:
            width = bar.get_width()
            label = f'{width:.1f}m'
            ax2.text(width + (app_mins.max() * 0.02), bar.get_y() + bar.get_height()/2., label,
                    ha='left', va='center', color='white', fontsize=9, fontweight='bold')

        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_summary_card(self, title, value, color, col):
        card = ctk.CTkFrame(self.summary_container, fg_color="#1e1e1e", corner_radius=12, border_width=1, border_color="#333333")
        card.grid(row=0, column=col, padx=10, pady=10, sticky="ew")
        self.summary_container.grid_columnconfigure(col, weight=1)
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="normal"), text_color="#888888").pack(pady=(10, 0))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"), text_color=color).pack(pady=(0, 10))

