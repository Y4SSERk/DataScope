"""
PCA Module View - Professional Edition
Exact replication of the 5-tab original architecture with premium styling.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from src.ui.theme import Theme
from src.ui.components import StyledCard, PremiumButton
from src.ui.charts import create_embedded_chart, setup_chart_style
from src.modules.pca.engine import PCAEngine
from src.core.context import AppContext

class PCAView(tk.Toplevel):
    def __init__(self, parent, context: AppContext):
        super().__init__(parent)
        self.context = context
        self.title("DATA ANALYSIS • PCA - Principal Component Analysis")
        self.state("zoomed")
        self.configure(bg=Theme.BG_PRIMARY)
        self.bind('<Escape>', lambda e: self.destroy())
        
        if self.context.scaled_data is None:
            messagebox.showerror("Error", "No dataset loaded.")
            self.destroy()
            return
            
        self.engine = PCAEngine(self.context.raw_data, self.context.scaled_data)
        setup_chart_style()
        self._build_ui()
        self._run_analysis()

    def _build_ui(self):
        # Premium Header
        self.header = tk.Frame(self, bg=Theme.HEADER_COLOR, height=70)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        
        self.header_content = tk.Frame(self.header, bg=Theme.HEADER_COLOR)
        self.header_content.pack(expand=True, fill="both")
        
        self.title_label = tk.Label(self.header_content, text="DATA-ANALYSIS - PCA (ACP)", 
                                    font=(Theme.FONT_FAMILY, 22, "bold"),
                                    fg=Theme.TEXT_WHITE, bg=Theme.HEADER_COLOR)
        self.title_label.pack(side="left", padx=20)

        # Content Container
        self.content_container = tk.Frame(self, bg=Theme.BG_PRIMARY)
        self.content_container.pack(fill="both", expand=True, padx=20, pady=20)

        self._render_dashboard()

    def _render_dashboard(self):
        # Clear current content
        for widget in self.content_container.winfo_children():
            widget.destroy()
        
        # Reset header (remove back button if any)
        for widget in self.header_content.winfo_children():
            if getattr(widget, 'is_back_btn', False): widget.destroy()

        # Dashboard Grid Area
        dashboard = tk.Frame(self.content_container, bg=Theme.BG_PRIMARY)
        dashboard.pack(expand=True)

        menu_items = [
            ("📋 Descriptive Statistics", "stats", Theme.PRIMARY, Theme.PRIMARY_HOVER),
            ("🔢 Centered-Reduced Matrix", "matrix", Theme.PRIMARY, Theme.PRIMARY_HOVER),
            ("🔥 Correlation Matrix", "corr", Theme.PRIMARY, Theme.PRIMARY_HOVER),
            ("⚡ Inertia (Scree Plot)", "inertia", Theme.SUCCESS, Theme.SUCCESS_LIGHT),
            ("🔄 Circle of Correlations", "circle", Theme.SUCCESS, Theme.SUCCESS_LIGHT),
            ("🎯 Factorial Plan", "plan", Theme.AFC_PINK, Theme.AFC_PINK_LIGHT),
            ("✨ Quality of Representation", "quality", Theme.PRIMARY, Theme.PRIMARY_HOVER),
            ("📈 Individual Contributions", "contrib", Theme.PRIMARY, Theme.PRIMARY_HOVER)
        ]

        # 3 columns grid
        for i, (text, view_id, color, hover) in enumerate(menu_items):
            r, c = divmod(i, 3)
            btn = PremiumButton(dashboard, text=text, 
                                command=lambda v=view_id: self._switch_view(v),
                                bg_color=color, hover_color=hover, width=280, height=80)
            btn.grid(row=r, column=c, padx=15, pady=15)

    def _run_analysis(self):
        try:
            self.results = self.engine.run()
            # Do not switch view automatically, let user pick from dashboard
        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))

    def _switch_view(self, view_id):
        # Clear current content
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

        # Render selected view
        if view_id == "stats":
            self._render_stats()
        elif view_id == "matrix":
            self._render_matrix()
        elif view_id == "corr":
            self._render_corr()
        elif view_id == "inertia":
            self._render_inertia()
        elif view_id == "circle":
            self._render_circle()
        elif view_id == "plan":
            self._render_plan()
        elif view_id == "quality":
            self._render_quality()
        elif view_id == "contrib":
            self._render_contrib()

    def _create_text_card(self, parent, title, icon, content, font_size=9):
        card = StyledCard(parent, title, icon)
        txt = tk.Text(card.content, bg="#f8fafc", fg=Theme.TEXT_PRIMARY,
                     font=(Theme.FONT_MONO, font_size), relief="flat", wrap="none",
                     padx=15, pady=10)
        sy = tk.Scrollbar(card.content, orient="vertical", command=txt.yview)
        sx = tk.Scrollbar(card.content, orient="horizontal", command=txt.xview)
        txt.config(yscrollcommand=sy.set, xscrollcommand=sx.set)
        txt.insert("1.0", content)
        txt.config(state="disabled")
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        txt.pack(side="left", fill="both", expand=True)
        return card

    def _render_stats(self):
        stats_text = "         MEAN & STANDARD DEVIATION\n" + "═" * 50 + "\n\n"
        stats_text += self.results['desc_stats'].T.to_string()
        self._create_text_card(self.content_container, "Descriptive Statistics", "📊", stats_text, 10).pack(fill="both", expand=True)

    def _render_matrix(self):
        labels = self.context.get_individual_labels()
        df_display = self.results['scaled_data'].copy()
        df_display.index = labels
        matrix_text = df_display.round(4).to_string()
        self._create_text_card(self.content_container, "Centered-Reduced Matrix (Z-Scores)", "🔢", matrix_text, 9).pack(fill="both", expand=True)

    def _render_corr(self):
        card = StyledCard(self.content_container, "Correlation Matrix Heatmap", "🔥")
        card.pack(fill="both", expand=True)
        fig, ax, canvas = create_embedded_chart(card.content)
        sns.heatmap(self.results['corr_matrix'], annot=True, cmap='RdYlBu_r', fmt=".2f", ax=ax,
                    linewidths=0.8, cbar_kws={"shrink": 0.8}, annot_kws={"size": 9, "weight": "bold"})
        ax.tick_params(labelsize=9, rotation=45)
        canvas.draw()

    def _render_inertia(self):
        card = StyledCard(self.content_container, "Explained Variance (Scree Plot)", "⚡")
        card.pack(fill="both", expand=True)
        fig, ax, canvas = create_embedded_chart(card.content)
        inertia = self.results['inertia']
        n_comp = min(10, len(inertia))
        bars = ax.bar([f'PC{i+1}' for i in range(n_comp)], inertia[:n_comp], color=Theme.CHART_BLUE, alpha=0.9)
        for bar, val in zip(bars, inertia[:n_comp]):
            ax.annotate(f'{val:.1f}%', (bar.get_x() + bar.get_width()/2, bar.get_height()), ha='center', va='bottom', fontsize=9)
        ax.set_ylabel("Explained Variance (%)")
        canvas.draw()

    def _render_plan(self):
        card = StyledCard(self.content_container, "Projection of Individuals (PC1 vs PC2)", "🎯")
        card.pack(fill="both", expand=True)
        fig, ax, canvas = create_embedded_chart(card.content, figsize=(10, 7))
        ax.scatter(self.results['components'][:, 0], self.results['components'][:, 1], c=Theme.CHART_BLUE, s=80, alpha=0.85, zorder=3)
        labels = self.context.get_individual_labels()
        for i, txt in enumerate(labels):
            ax.annotate(txt, (self.results['components'][i, 0], self.results['components'][i, 1]), fontsize=8, alpha=0.8, xytext=(5, 5), textcoords='offset points')
        ax.axhline(0, color='#94a3b8', linestyle='--', alpha=0.7)
        ax.axvline(0, color='#94a3b8', linestyle='--', alpha=0.7)
        ax.set_xlabel(f"PC1 ({self.results['inertia'][0]:.1f}%)")
        ax.set_ylabel(f"PC2 ({self.results['inertia'][1]:.1f}%)")
        canvas.draw()

    def _render_circle(self):
        card = StyledCard(self.content_container, "Variables Factor Map", "🔄")
        card.pack(fill="both", expand=True)
        fig, ax, canvas = create_embedded_chart(card.content, figsize=(8, 7))
        loadings = self.results['loadings']
        for i, feat in enumerate(self.results['features']):
            ax.arrow(0, 0, loadings[i, 0], loadings[i, 1], head_width=0.05, head_length=0.04, fc=Theme.CHART_RED, ec=Theme.CHART_RED, lw=2)
            ax.text(loadings[i, 0] * 1.15, loadings[i, 1] * 1.15, feat, ha='center', fontweight='bold')
        ax.add_artist(plt.Circle((0,0), 1, color=Theme.CHART_BLUE, fill=False, lw=2))
        ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25)
        ax.set_aspect('equal')
        canvas.draw()

    def _render_quality(self):
        labels = self.context.get_individual_labels()
        data = pd.DataFrame(self.results['cos2'], columns=['PC1', 'PC2'], index=labels).round(4)
        self._create_text_card(self.content_container, "QUALITY OF REPRESENTATION (COS²)", "✨", data.to_string(), 10).pack(fill="both", expand=True)

    def _render_contrib(self):
        labels = self.context.get_individual_labels()
        data = pd.DataFrame(self.results['contrib'], columns=['PC1', 'PC2'], index=labels).round(2)
        self._create_text_card(self.content_container, "CONTRIBUTIONS (%)", "📈", data.to_string(), 10).pack(fill="both", expand=True)
