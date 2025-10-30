# Interactive Sales Analysis Dashboard (Tkinter)

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class SalesDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Sales Analysis Dashboard")
        self.root.geometry("1000x700")
        self.root.configure(bg="#F4F6F7")

        self.data = None

        # Title
        tk.Label(root, text="📊 Interactive Sales Analysis Dashboard",
                 font=("Helvetica", 18, "bold"), bg="#2E86C1", fg="white", pady=10).pack(fill="x")

        # Upload Button
        tk.Button(root, text="Upload Sales CSV", font=("Helvetica", 12),
                  bg="#28B463", fg="white", command=self.load_data).pack(pady=10)

        # Filter Frame
        filter_frame = tk.Frame(root, bg="#F4F6F7")
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Filter by Region:", bg="#F4F6F7").grid(row=0, column=0, padx=5)
        self.region_cb = ttk.Combobox(filter_frame, state="readonly")
        self.region_cb.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Filter by Product:", bg="#F4F6F7").grid(row=0, column=2, padx=5)
        self.product_cb = ttk.Combobox(filter_frame, state="readonly")
        self.product_cb.grid(row=0, column=3, padx=5)

        tk.Button(filter_frame, text="Apply Filter", bg="#3498DB", fg="white",
                  command=self.apply_filter).grid(row=0, column=4, padx=10)

        # KPI Labels
        self.kpi_frame = tk.Frame(root, bg="#F4F6F7")
        self.kpi_frame.pack(pady=10)

        self.total_sales_label = tk.Label(self.kpi_frame, text="Total Sales: -", font=("Helvetica", 12, "bold"), bg="#F4F6F7")
        self.total_sales_label.grid(row=0, column=0, padx=20)

        self.avg_profit_label = tk.Label(self.kpi_frame, text="Average Profit: -", font=("Helvetica", 12, "bold"), bg="#F4F6F7")
        self.avg_profit_label.grid(row=0, column=1, padx=20)

        # Chart Frame
        self.chart_frame = tk.Frame(root, bg="#F4F6F7")
        self.chart_frame.pack(fill="both", expand=True)

    def load_data(self):
        """Load CSV file"""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            self.data = pd.read_csv(file_path)
            messagebox.showinfo("Success", "Dataset loaded successfully!")

            # Prepare filters
            if 'Region' in self.data.columns:
                self.region_cb['values'] = ['All'] + sorted(self.data['Region'].dropna().unique().tolist())
            if 'Product' in self.data.columns:
                self.product_cb['values'] = ['All'] + sorted(self.data['Product'].dropna().unique().tolist())

            self.region_cb.set('All')
            self.product_cb.set('All')

            self.update_dashboard(self.data)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def apply_filter(self):
        """Filter data and update dashboard"""
        if self.data is None:
            messagebox.showwarning("Warning", "Please upload a dataset first.")
            return

        df = self.data.copy()

        # Apply region filter
        if self.region_cb.get() != 'All' and 'Region' in df.columns:
            df = df[df['Region'] == self.region_cb.get()]

        # Apply product filter
        if self.product_cb.get() != 'All' and 'Product' in df.columns:
            df = df[df['Product'] == self.product_cb.get()]

        self.update_dashboard(df)

    def update_dashboard(self, df):
        """Update KPIs and charts"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if 'Sales' not in df.columns or 'Profit' not in df.columns:
            messagebox.showerror("Error", "Dataset must include 'Sales' and 'Profit' columns.")
            return

        # --- KPIs ---
        total_sales = df['Sales'].sum()
        avg_profit = df['Profit'].mean()

        self.total_sales_label.config(text=f"Total Sales: {total_sales:,.2f}")
        self.avg_profit_label.config(text=f"Average Profit: {avg_profit:,.2f}")

        # --- Charts ---
        fig, axs = plt.subplots(1, 3, figsize=(13, 4))

        # Bar chart: Sales by Product
        if 'Product' in df.columns:
            product_sales = df.groupby('Product')['Sales'].sum().nlargest(5)
            axs[0].bar(product_sales.index, product_sales.values)
            axs[0].set_title("Top 5 Products by Sales")
            axs[0].tick_params(axis='x', rotation=45)

        # Line chart: Sales Trend
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            date_sales = df.groupby('Date')['Sales'].sum().sort_index()
            axs[1].plot(date_sales.index, date_sales.values, marker='o')
            axs[1].set_title("Sales Over Time")

        # Pie chart: Sales by Region
        if 'Region' in df.columns:
            region_sales = df.groupby('Region')['Sales'].sum()
            axs[2].pie(region_sales.values, labels=region_sales.index, autopct='%1.1f%%')
            axs[2].set_title("Sales by Region")

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


# --- Run App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SalesDashboard(root)
    root.mainloop()
