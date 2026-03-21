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
        
        self.chart_container = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=15)
        self.chart_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.refresh_btn = ctk.CTkButton(self, text="Refresh Charts", fg_color="#2980b9", corner_radius=8, command=self.show_charts)
        self.refresh_btn.grid(row=2, column=0, padx=20, pady=20)
        
        self.show_charts()

    def show_charts(self):
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        # Fetch today's logs with timestamps and titles
        query = "SELECT timestamp, is_productive, app_name, window_title FROM logs WHERE date(timestamp, 'localtime') = date('now', 'localtime') ORDER BY timestamp ASC"
        logs = fetch_all(query)
        
        if not logs:
            ctk.CTkLabel(self.chart_container, text="No tracking data for today. Keep working!", text_color="white", font=ctk.CTkFont(size=14)).pack(expand=True)
            return

        df = pd.DataFrame(logs, columns=['timestamp', 'is_productive', 'app_name', 'window_title'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Combine App Name and Window Title for better accuracy
        def format_name(row):
            app = row['app_name'].replace(".exe", "").capitalize()
            title = row['window_title']
            if not title or title == "N/A":
                return app
            # Truncate title if too long
            if len(title) > 20:
                title = title[:17] + "..."
            return f"{app}: {title}"

        df['display_name'] = df.apply(format_name, axis=1)
        
        # Calculate duration
        df['duration'] = df['timestamp'].diff().shift(-1).dt.total_seconds()
        
        if not df.empty:
            last_log_time = df['timestamp'].iloc[-1]
            now = pd.Timestamp.now()
            if last_log_time.date() == now.date():
                diff = (now - last_log_time).total_seconds()
                df.loc[df.index[-1], 'duration'] = min(diff, 60) 
            else:
                df.loc[df.index[-1], 'duration'] = 15
        
        df['duration'] = df['duration'].fillna(15)

        # Style matplotlib for dark theme
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), facecolor='#1e1e1e')
        ax1.set_facecolor('#1e1e1e')
        ax2.set_facecolor('#1e1e1e')
        
        # Pie Chart (Productivity)
        prod_time = df.groupby('is_productive')['duration'].sum()
        labels = ['Productive' if i==1 else 'Distraction' for i in prod_time.index]
        ax1.pie(prod_time, labels=labels, autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], textprops={'color':"w"})
        ax1.set_title("Today's Productivity", color="white", fontdict={'fontsize': 12, 'fontweight': 'bold'})
        
        # Bar Chart (Time Spent per App: Title)
        app_time = df.groupby('display_name')['duration'].sum().sort_values(ascending=False).head(5)
        app_time.plot(kind='bar', ax=ax2, color='#2980b9')
        ax2.set_title("Top 5 Activities (Time Spent)", color="white")
        ax2.set_ylabel("Seconds", color="white")
        plt.xticks(rotation=45, ha='right', color="white", fontsize=8)
        plt.yticks(color="white")
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

