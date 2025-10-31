import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time
from typing import List, Tuple, Any
import colorsys, hashlib

Job = Tuple[str, int, int, int, int]

class JobOptimizerApp:
    def __init__(self, master):
        self.master = master
        master.title("Job Scheduling Optimizer")
        master.configure(bg="#f0f0f0")
        self.jobs: List[Job] = []

        self.main_frame = ttk.Frame(master, padding="15", relief="raised")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_input_section(self.main_frame)
        self.create_output_sections(self.main_frame)

    def create_input_section(self, parent):
        input_frame = ttk.LabelFrame(parent, text="Job Data (ID, Start, Finish, Profit, Deadline)", padding="10")
        input_frame.pack(fill=tk.X, pady=10)

        sample_data = "J1, 0, 3, 50, 2\nJ2, 2, 5, 20, 1\nJ3, 4, 7, 70, 3\nJ4, 6, 8, 40, 3\nJ5, 1, 6, 60, 4\nJ8, 5, 10, 90, 5"
        
        self.job_data_input = scrolledtext.ScrolledText(input_frame, height=8, width=70, font=("Inter", 10), relief="sunken")
        self.job_data_input.insert(tk.INSERT, sample_data)
        self.job_data_input.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(input_frame, text="Run Optimization", command=self.run_optimization).pack(pady=10)

    def create_output_sections(self, parent):
        output_frame = ttk.Frame(parent, padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)

        # Greedy (JSD) Output
        jsd_frame = ttk.LabelFrame(output_frame, text="Greedy: JSD (Deadlines)", padding="10")
        jsd_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.jsd_profit_label = ttk.Label(jsd_frame, text="Max Profit: --", font=("Inter", 12, "bold"), foreground="#d97706")
        self.jsd_profit_label.pack(pady=5)
        self.jsd_schedule_label = ttk.Label(jsd_frame, text="Schedule: --", wraplength=350)
        self.jsd_schedule_label.pack(pady=5)
        self.jsd_time_label = ttk.Label(jsd_frame, text="Time: --s", font=("Inter", 9))
        self.jsd_time_label.pack(pady=2)
        ttk.Label(jsd_frame, text="Timeline (Time Unit Jobs)", font=("Inter", 10, "underline")).pack(pady=5)
        self.jsd_canvas = tk.Canvas(jsd_frame, bg="#ffffff", height=50, width=400, borderwidth=1, relief="sunken")
        self.jsd_canvas.pack(fill=tk.X, expand=True)

        # Dynamic Programming (WIS) Output
        wis_frame = ttk.LabelFrame(output_frame, text="DP: WIS (Intervals)", padding="10")
        wis_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.wis_profit_label = ttk.Label(wis_frame, text="Max Profit: --", font=("Inter", 12, "bold"), foreground="#10b981")
        self.wis_profit_label.pack(pady=5)
        self.wis_schedule_label = ttk.Label(wis_frame, text="Schedule: --", wraplength=350)
        self.wis_schedule_label.pack(pady=5)
        self.wis_time_label = ttk.Label(wis_frame, text="Time: --s", font=("Inter", 9))
        self.wis_time_label.pack(pady=2)
        ttk.Label(wis_frame, text="Timeline (Non-Overlapping Intervals)", font=("Inter", 10, "underline")).pack(pady=5)
        self.wis_canvas = tk.Canvas(wis_frame, bg="#ffffff", height=50, width=400, borderwidth=1, relief="sunken")
        self.wis_canvas.pack(fill=tk.X, expand=True)

    def parse_input(self) -> bool:
        text = self.job_data_input.get("1.0", tk.END).strip()
        self.jobs = []
        if not text:
            messagebox.showerror("Input Error", "Kripya Job Data enter karein.")
            return False
        try:
            for line in text.split('\n'):
                if not line.strip(): continue
                parts = [p.strip() for p in line.split(',')]
                if len(parts) != 5: raise ValueError(f"Har line mein 5 values honi chahiye: {line}")
                job_id = parts[0]
                start, finish, profit, deadline = map(int, parts[1:])
                if start < 0 or finish <= start or profit < 0 or deadline <= 0: raise ValueError(f"Invalid numeric values: {line}")
                self.jobs.append((job_id, start, finish, profit, deadline))
            return True
        except ValueError as e:
            messagebox.showerror("Input Format Error", f"Input data format galat hai: {e}")
            return False

    def run_optimization(self):
        if not self.parse_input(): return

        # JSD (Greedy)
        start_jsd = time.perf_counter()
        max_profit_jsd, schedule_jsd, max_deadline = self.job_sequencing_greedy()
        end_jsd = time.perf_counter()
        self.jsd_profit_label.config(text=f"Max Profit: {max_profit_jsd}")
        self.jsd_schedule_label.config(text=f"Schedule: {', '.join(schedule_jsd)}")
        self.jsd_time_label.config(text=f"Time: {end_jsd - start_jsd:.6f}s")
        self.draw_jsd_timeline(schedule_jsd, max_deadline)

        # WIS (DP)
        start_wis = time.perf_counter()
        max_profit_wis, schedule_wis, max_time = self.weighted_interval_scheduling_dp()
        end_wis = time.perf_counter()
        self.wis_profit_label.config(text=f"Max Profit: {max_profit_wis}")
        self.wis_schedule_label.config(text=f"Schedule: {', '.join(schedule_wis)}")
        self.wis_time_label.config(text=f"Time: {end_wis - start_wis:.6f}s")
        self.draw_wis_timeline(schedule_wis, max_time)

    # ALGORITHM 1: Job Sequencing with Deadlines (Greedy)
    def job_sequencing_greedy(self) -> Tuple[int, List[str], int]:
        jsd_jobs = [(p, d, id) for id, _, _, p, d in self.jobs]
        jsd_jobs.sort(key=lambda x: x[0], reverse=True)

        max_deadline = max(j[1] for j in jsd_jobs) if jsd_jobs else 0
        slots: List[str | None] = [None] * (max_deadline + 1)
        total_profit = 0

        for profit, deadline, job_id in jsd_jobs:
            for t in range(min(deadline, max_deadline), 0, -1):
                if slots[t] is None:
                    slots[t] = job_id
                    total_profit += profit
                    break

        scheduled_jobs = [job for job in slots if job is not None]
        return total_profit, scheduled_jobs, max_deadline

    # ALGORITHM 2: Weighted Interval Scheduling (Dynamic Programming)
    def weighted_interval_scheduling_dp(self) -> Tuple[int, List[str], int]:
        wis_jobs = [(id, s, f, p) for id, s, f, p, _ in self.jobs]
        wis_jobs.sort(key=lambda x: x[2])
        N = len(wis_jobs)
        if N == 0: return 0, [], 0

        job_ids = [job[0] for job in wis_jobs]
        start_times = [job[1] for job in wis_jobs]
        finish_times = [job[2] for job in wis_jobs]
        profits = [job[3] for job in wis_jobs]
        max_time = max(finish_times) if finish_times else 0

        # Precompute p[j]
        p: List[int] = [0] * (N + 1)
        for j in range(1, N + 1):
            current_start = start_times[j - 1]
            for i in range(j - 1, 0, -1):
                if finish_times[i - 1] <= current_start:
                    p[j] = i
                    break

        # DP Calculation
        dp: List[int] = [0] * (N + 1)
        for j in range(1, N + 1):
            include_j = profits[j - 1] + dp[p[j]]
            exclude_j = dp[j - 1]
            dp[j] = max(include_j, exclude_j)

        # Reconstruct schedule
        schedule: List[str] = []
        j = N
        while j > 0:
            if profits[j - 1] + dp[p[j]] > dp[j - 1]:
                schedule.append(job_ids[j - 1])
                j = p[j]
            else:
                j -= 1
        
        schedule.reverse()
        return dp[N], schedule, max_time

    # VISUALIZATION FUNCTIONS
    def get_job_color(self, job_id: str) -> str:
        hash_val = int(hashlib.sha1(job_id.encode('utf-8')).hexdigest(), 16)
        hue = (hash_val % 360) / 360.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.6, 0.85)
        return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))

    def draw_jsd_timeline(self, scheduled_job_ids: List[str], max_time: int):
        canvas = self.jsd_canvas
        canvas.delete("all")
        if max_time == 0: return

        canvas_width = canvas.winfo_width() if canvas.winfo_width() > 1 else 400
        padding = 10
        timeline_width = canvas_width - 2 * padding
        unit_width = timeline_width / max_time
        
        canvas.create_line(padding, 25, canvas_width - padding, 25, fill="black", width=2)
        
        for t in range(1, max_time + 1):
            if t <= len(scheduled_job_ids):
                job_id = scheduled_job_ids[t-1]
                x0 = padding + (t - 1) * unit_width
                x1 = padding + t * unit_width
                job_info = next((job for job in self.jobs if job[0] == job_id), None)
                if job_info:
                    color = self.get_job_color(job_id)
                    canvas.create_rectangle(x0, 15, x1, 35, fill=color, outline=color)
                    canvas.create_text(x0 + unit_width / 2, 25, text=job_id, fill="white", font=("Inter", 8, "bold"))
            
            canvas.create_line(padding + t * unit_width, 25, padding + t * unit_width, 30, fill="black")
            canvas.create_text(padding + t * unit_width, 40, text=str(t), fill="black", font=("Inter", 8))

        canvas.create_text(padding, 40, text="0", fill="black", font=("Inter", 8))

    def draw_wis_timeline(self, scheduled_job_ids: List[str], max_time: int):
        canvas = self.wis_canvas
        canvas.delete("all")
        if max_time == 0: return

        canvas_width = canvas.winfo_width() if canvas.winfo_width() > 1 else 400
        padding = 10
        timeline_width = canvas_width - 2 * padding
        scale_factor = timeline_width / max_time

        canvas.create_line(padding, 25, canvas_width - padding, 25, fill="black", width=2)
        
        for job_id in scheduled_job_ids:
            job_info = next((job for job in self.jobs if job[0] == job_id), None)
            if job_info:
                id, start, finish, profit, _ = job_info
                x0 = padding + start * scale_factor
                x1 = padding + finish * scale_factor
                color = self.get_job_color(job_id)
                
                canvas.create_rectangle(x0, 10, x1, 40, fill=color, outline="#333333", width=1)
                text_x = x0 + (x1 - x0) / 2
                canvas.create_text(text_x, 25, text=f"{id} ({finish-start}h, P{profit})", fill="white", font=("Inter", 8, "bold"))
        
        time_points = [0, max_time]
        if max_time > 2: time_points.append(max_time // 2)
        time_points = sorted(list(set(time_points)))

        for t in time_points:
            x_pos = padding + t * scale_factor
            canvas.create_line(x_pos, 25, x_pos, 30, fill="black")
            canvas.create_text(x_pos, 40, text=str(t), fill="black", font=("Inter", 8))


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam') 
    app = JobOptimizerApp(root)
    root.mainloop()
