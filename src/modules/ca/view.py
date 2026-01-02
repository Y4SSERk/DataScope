"""
CA Module View - Professional Edition
Full-fidelity dashboard for Correspondence Analysis with heatmaps and biplots.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from src.ui.theme import Theme
from src.ui.components import StyledCard, PremiumButton
from src.ui.charts import create_embedded_chart, setup_chart_style
from src.modules.ca.engine import CAEngine
from src.core.context import AppContext

class CAView(tk.Toplevel):
    def __init__(self, parent, context: AppContext):
        super().__init__(parent)
        self.context = context
        self.title("DATA ANALYSIS • CA - Correspondence Analysis")
        self.state("zoomed")
        self.configure(bg=Theme.BG_PRIMARY)
        self.bind('<Escape>', lambda e: self.destroy())
        
        setup_chart_style()
        self._build_ui()

    def _build_ui(self):
        # Header
        self.header = tk.Frame(self, bg=Theme.AFC_PINK, height=70)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.header_content = tk.Frame(self.header, bg=Theme.AFC_PINK)
        self.header_content.pack(expand=True, fill="both")
        
        self.title_label = tk.Label(self.header_content, text="DATA-ANALYSIS - CA (AFC)", 
                                   font=(Theme.FONT_FAMILY, 22, "bold"), 
                                   fg=Theme.TEXT_WHITE, bg=Theme.AFC_PINK)
        self.title_label.pack(side="left", padx=20)

        # Content Area
        self.content_container = tk.Frame(self, bg=Theme.BG_PRIMARY)
        self.content_container.pack(fill="both", expand=True, padx=20, pady=20)

        self._render_dashboard()

    def _render_dashboard(self):
        # Clear current content
        for widget in self.content_container.winfo_children():
            widget.destroy()
        
        # Reset header
        for widget in self.header_content.winfo_children():
            if getattr(widget, 'is_back_btn', False): widget.destroy()

        # Dashboard Grid
        dashboard = tk.Frame(self.content_container, bg=Theme.BG_PRIMARY)
        dashboard.pack(expand=True)

        # Top Row: Data Controls
        controls_frame = tk.Frame(dashboard, bg=Theme.BG_PRIMARY)
        controls_frame.grid(row=0, column=0, columnspan=2, pady=(0, 30))

        tk.Button(controls_frame, text="📂 Load Table", command=self._on_load,
                  bg="#475569", fg=Theme.TEXT_WHITE, relief="flat", padx=25, pady=12,
                  font=(Theme.FONT_FAMILY, 10, "bold")).pack(side="left", padx=10)
        
        tk.Button(controls_frame, text="🎲 Generate Demo", command=self._on_demo,
                  bg="#475569", fg=Theme.TEXT_WHITE, relief="flat", padx=25, pady=12,
                  font=(Theme.FONT_FAMILY, 10, "bold")).pack(side="left", padx=10)

        # Analysis Cluster
        menu_items = [
            ("📋 Frequencies & Stats", "stats", Theme.AFC_PINK, Theme.AFC_PINK_LIGHT),
            ("🔥 Contingency Heatmap", "heatmap", Theme.AFC_PINK, Theme.AFC_PINK_LIGHT),
            ("🎯 Factorial Biplot", "biplot", Theme.AFC_PINK, Theme.AFC_PINK_LIGHT),
            ("📉 Chi² Analysis", "chi2", Theme.DANGER, Theme.DANGER_LIGHT)
        ]

        for i, (text, view_id, color, hover) in enumerate(menu_items):
            r, c = divmod(i, 2)
            btn = PremiumButton(dashboard, text=text, 
                                command=lambda v=view_id: self._switch_view(v),
                                bg_color=color, hover_color=hover, width=300, height=90)
            btn.grid(row=r+1, column=c, padx=15, pady=15)

    def _switch_view(self, view_id):
        if not hasattr(self, 'current_df'):
            messagebox.showinfo("Note", "Please load or generate data first.")
            return

        for widget in self.content_container.winfo_children():
            widget.destroy()

        # Add Back Button to Header - Clear existing ones first to prevent duplication
        for widget in self.header_content.winfo_children():
            if getattr(widget, 'is_back_btn', False): widget.destroy()

        back_btn = tk.Button(self.header_content, text="⬅️ Back to Menu", 
                             font=(Theme.FONT_FAMILY, 10, "bold"),
                             bg="#475569", fg=Theme.TEXT_WHITE, bd=0, padx=15, pady=5,
                             cursor="hand2", command=self._render_dashboard)
        back_btn.is_back_btn = True
        back_btn.pack(side="right", padx=20)

        if view_id == "stats":
            self._render_stats()
        elif view_id == "heatmap":
            self._render_heatmap()
        elif view_id == "biplot":
            self._render_biplot()
        elif view_id == "chi2":
            self._render_chi2()

    def _on_load(self):
        path = filedialog.askopenfilename(filetypes=[("Excel/CSV", "*.xlsx *.csv")])
        if not path: return
        try:
            df = pd.read_csv(path, index_col=0) if path.endswith('.csv') else pd.read_excel(path, index_col=0)
            df = df.select_dtypes(include=[np.number])
            self._update_data(df)
        except Exception as e: messagebox.showerror("Error", str(e))

    def _on_demo(self):
        if not self.context.features:
            messagebox.showerror("Error", "Please load the Master Dataset first to sync features.")
            return
            
        np.random.seed(42)
        n_rows = 8
        n_cols = len(self.context.features)
        
        # Row labels with prefix
        row_labels = [f"{self.context.individual_prefix}_{i+1}" for i in range(n_rows)]
        
        # Values between 1 and 10
        data = np.random.randint(1, 11, size=(n_rows, n_cols))
        
        df = pd.DataFrame(data, index=row_labels, columns=self.context.features)
        self._update_data(df)

    def _update_data(self, df):
        self.current_df = df
        engine = CAEngine(df)
        self.results = engine.run()
        self._switch_view("stats")

    def _render_stats(self):
        card = StyledCard(self.content_container, "Frequency Matrix", "📋")
        card.pack(fill="both", expand=True)
        t = tk.Text(card.content, bg="#fdf2f8", font=(Theme.FONT_MONO, 10), relief="flat")
        content = "FREQUENCY MATRIX\n" + "="*30 + "\n" + self.current_df.to_string() + "\n\n"
        content += f"Chi2: {self.results['chi2']:.4f}\nP-Value: {self.results['p_value']:.4e}\nDOF: {self.results['dof']}"
        t.insert("1.0", content)
        t.config(state="disabled")
        t.pack(fill="both", expand=True, padx=10, pady=10)

    def _render_heatmap(self):
        card = StyledCard(self.content_container, "Contingency Heatmap", "🔥")
        card.pack(fill="both", expand=True)
        fig, ax, canvas = create_embedded_chart(card.content)
        sns.heatmap(self.current_df, annot=True, fmt="d", cmap="PuRd", ax=ax, cbar=False)
        canvas.draw()

    def _render_biplot(self):
        card = StyledCard(self.content_container, "Factorial Biplot", "🎯")
        card.pack(fill="both", expand=True)
        fig, ax, canvas = create_embedded_chart(card.content)
        r = self.results
        ax.scatter(r['row_coords'][:,0], r['row_coords'][:,1], c=Theme.CHART_BLUE, label="Rows", s=60)
        ax.scatter(r['col_coords'][:,0], r['col_coords'][:,1], c=Theme.AFC_PINK, label="Cols", s=60, marker="^")
        for i, txt in enumerate(r['row_names']): ax.annotate(txt, (r['row_coords'][i,0], r['row_coords'][i,1]), color=Theme.CHART_BLUE)
        for i, txt in enumerate(r['col_names']): ax.annotate(txt, (r['col_coords'][i,0], r['col_coords'][i,1]), color=Theme.AFC_PINK)
        ax.axhline(0, color='gray', lw=0.5); ax.axvline(0, color='gray', lw=0.5)
        ax.legend()
        canvas.draw()

    def _render_chi2(self):
        card = StyledCard(self.content_container, "Chi² Independence Analysis", "📉")
        card.pack(fill="both", expand=True)
        t = tk.Text(card.content, bg="#fdf2f8", font=(Theme.FONT_MONO, 9), relief="flat")
        t.insert("1.0", "CONTRIBUTION TO CHI2\n" + "="*30 + "\n" + self.results['res_df'].to_string())
        t.config(state="disabled")
        t.pack(fill="both", expand=True, padx=10, pady=10)
