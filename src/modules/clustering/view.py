"""
Clustering Module View - Professional Edition
Dashboard with cluster viz, pie charts, metrics, and interactive forms.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

from src.ui.theme import Theme
from src.ui.components import StyledCard, PremiumButton, ModernSlider
from src.ui.charts import create_embedded_chart, setup_chart_style
from src.modules.clustering.engine import ClusteringEngine
from src.core.context import AppContext

class ClusteringView(tk.Toplevel):
    def __init__(self, parent, context: AppContext):
        super().__init__(parent)
        self.context = context
        self.title("AI ANALYTICS • CLUSTERING - Machine Learning Forecast")
        self.state("zoomed")
        self.configure(bg=Theme.BG_PRIMARY)
        self.bind('<Escape>', lambda e: self.destroy())
        
        self.engine = ClusteringEngine(self.context.scaled_data)
        setup_chart_style()
        self._build_ui()
        self._run_analysis()

    def _build_ui(self):
        # Header
        self.header = tk.Frame(self, bg=Theme.SUCCESS, height=70)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        
        self.header_content = tk.Frame(self.header, bg=Theme.SUCCESS)
        self.header_content.pack(expand=True, fill="both")
        
        self.title_label = tk.Label(self.header_content, text="AI CLUSTERING & FORECASTING", 
                                   font=(Theme.FONT_FAMILY, 22, "bold"), 
                                   fg=Theme.TEXT_WHITE, bg=Theme.SUCCESS)
        self.title_label.pack(side="left", padx=20)

        # Content Area
        self.content_container = tk.Frame(self, bg=Theme.BG_PRIMARY)
        self.content_container.pack(fill="both", expand=True, padx=20, pady=20)

        self._render_dashboard()

    def _run_analysis(self):
        try:
            self.results = self.engine.run_clustering_flow()
            # No initial view switch here, dashboard is default
        except Exception as e:
            messagebox.showerror("ML Error", str(e))

    def _render_dashboard(self):
        # Clear current content
        for widget in self.content_container.winfo_children():
            widget.destroy()
        
        # Reset header
        for widget in self.header_content.winfo_children():
            if getattr(widget, 'is_back_btn', False): widget.destroy()
        self.title_label.config(text="AI CLUSTERING & FORECASTING") # Reset title if it was changed

        # Dashboard Grid Area
        dashboard = tk.Frame(self.content_container, bg=Theme.BG_PRIMARY)
        dashboard.pack(expand=True)

        menu_items = [
            ("🎨 Cluster Visualization", "viz", Theme.SUCCESS, Theme.SUCCESS_LIGHT),
            ("📊 Cluster Distribution", "dist", Theme.SUCCESS, Theme.SUCCESS_LIGHT),
            ("🚀 AI Performance", "perf", Theme.PRIMARY, Theme.PRIMARY_HOVER),
            ("🔮 Predict Individual", "pred", Theme.AFC_PINK, Theme.AFC_PINK_LIGHT)
        ]

        # 2 columns grid
        for i, (text, view_id, color, hover) in enumerate(menu_items):
            r, c = divmod(i, 2)
            btn = PremiumButton(dashboard, text=text, 
                                command=lambda v=view_id: self._switch_view(v),
                                bg_color=color, hover_color=hover, width=320, height=100)
            btn.grid(row=r, column=c, padx=20, pady=20)

    def _switch_view(self, view_id):
        # Clear current content
        for widget in self.content_container.winfo_children():
            widget.destroy()

        # Add Back Button to Header
        # Remove existing back button if any
        for widget in self.header_content.winfo_children():
            if getattr(widget, 'is_back_btn', False):
                widget.destroy()

        back_btn = tk.Button(self.header_content, text="⬅️ Back to Menu", 
                             font=(Theme.FONT_FAMILY, 10, "bold"),
                             bg="#475569", fg=Theme.TEXT_WHITE, bd=0, padx=15, pady=5,
                             cursor="hand2", command=self._render_dashboard)
        back_btn.is_back_btn = True # Custom attribute to identify the back button
        back_btn.pack(side="right", padx=20)

        # Update title based on view
        view_titles = {
            "viz": "🎨 Cluster Visualization",
            "dist": "📊 Cluster Distribution",
            "perf": "🚀 AI Performance",
            "pred": "🔮 Predict Individual"
        }
        self.title_label.config(text=view_titles.get(view_id, "AI CLUSTERING & FORECASTING"))

        if view_id == "viz":
            self._render_viz()
        elif view_id == "dist":
            self._render_dist()
        elif view_id == "perf":
            self._render_perf()
        elif view_id == "pred":
            self._render_pred()

    def _render_viz(self):
        card = StyledCard(self.content_container, "Cluster Visualization (PCA)", "🎨")
        card.pack(fill="both", expand=True)

        # Control Panel for Slider
        controls = tk.Frame(card.content, bg=Theme.BG_CARD)
        controls.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(controls, text="Number of clusters (K):", font=(Theme.FONT_FAMILY, 10, "bold"),
                 bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(side="left", padx=(0, 10))

        self.cluster_slider = ModernSlider(controls, min_val=2, max_val=10, 
                                          initial_val=self.results.get('n_clusters', 4),
                                          callback=self._on_slider_change)
        self.cluster_slider.pack(side="left", fill="x", expand=True)

        # Plot Area
        self.viz_fig, self.viz_ax, self.viz_canvas = create_embedded_chart(card.content)
        self._update_viz_chart()

    def _on_slider_change(self, val):
        try:
            k = int(val)
            # Re-run analysis with new K
            self.results = self.engine.run_clustering_flow(n_clusters=k)
            self._update_viz_chart()
        except Exception as e:
            print(f"Slider update error: {e}")

    def _update_viz_chart(self):
        self.viz_ax.clear()
        r = self.results
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(self.context.scaled_data)
        
        # Extended color palette for more clusters
        colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316', '#84cc16', '#a855f7']
        k_colors = colors[:r['n_clusters']]
        
        self.viz_ax.scatter(X_pca[:, 0], X_pca[:, 1], c=[k_colors[c] for c in r['labels']], s=70, edgecolor='white', alpha=0.8)
        
        labels = self.context.get_individual_labels()
        for i, txt in enumerate(labels):
            self.viz_ax.annotate(txt, (X_pca[i, 0], X_pca[i, 1]), fontsize=7, alpha=0.7, xytext=(4, 4), textcoords='offset points')

        for i, color in enumerate(k_colors):
            self.viz_ax.scatter([],[], c=color, label=f"Cluster {i}")
        
        self.viz_ax.legend(loc='upper right', fontsize=8)
        self.viz_ax.set_title(f"Clustering with K={r['n_clusters']}", fontsize=10, fontweight='bold')
        self.viz_canvas.draw()

    def _render_dist(self):
        card = StyledCard(self.content_container, "Cluster Distribution", "📊")
        card.pack(fill="both", expand=True)
        fig, ax, canvas = create_embedded_chart(card.content)
        dist = self.results['distribution']
        colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'][:len(dist)]
        ax.pie(dist, labels=[f'Cluster {i}' for i in dist.index], autopct='%1.1f%%', colors=colors, startangle=90, wedgeprops={'edgecolor':'white'})
        canvas.draw()

    def _render_perf(self):
        card = StyledCard(self.content_container, "Model Performance", "📈")
        card.pack(fill="both", expand=True)
        txt = tk.Text(card.content, bg="#f0fdf4", font=(Theme.FONT_MONO, 10), relief="flat", padx=15, pady=10)
        txt.insert("1.0", f"Accuracy: {self.results['accuracy']*100:.2f}%\n\nREPORT:\n{self.results['report']}")
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True)

    def _render_pred(self):
        card = StyledCard(self.content_container, "Predict New Individual", "🔮")
        card.pack(fill="both", expand=True)
        
        # Scrollable Area
        canvas = tk.Canvas(card.content, bg=Theme.BG_CARD, highlightthickness=0)
        sb = tk.Scrollbar(card.content, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Centering Wrapper
        wrapper = tk.Frame(canvas, bg=Theme.BG_CARD)
        window_id = canvas.create_window((0,0), window=wrapper, anchor="n")
        
        def _on_canvas_configure(event):
            # Center the wrapper horizontally and limit its width
            width = min(event.width - 40, 600)
            canvas.itemconfig(window_id, width=width)
            canvas.coords(window_id, event.width // 2, 20)
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _on_canvas_configure)

        # Form Content
        form = tk.Frame(wrapper, bg=Theme.BG_CARD)
        form.pack(fill="x", padx=20, pady=20)

        self.entries = {}
        for feat in self.context.features:
            f = tk.Frame(form, bg=Theme.BG_CARD)
            f.pack(fill="x", pady=5)
            tk.Label(f, text=feat, width=25, anchor="w", font=(Theme.FONT_FAMILY, 10, "bold"), bg=Theme.BG_CARD).pack(side="left")
            e = tk.Entry(f, font=(Theme.FONT_FAMILY, 10), relief="solid", bd=1)
            e.pack(side="left", fill="x", expand=True)
            self.entries[feat] = e

        btn_frame = tk.Frame(form, bg=Theme.BG_CARD)
        btn_frame.pack(fill="x", pady=25)

        tk.Button(btn_frame, text="🚀  Predict Cluster", command=self._on_predict,
                  bg=Theme.SUCCESS, fg=Theme.TEXT_WHITE, font=(Theme.FONT_FAMILY, 11, "bold"),
                  relief="flat", pady=10).pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(btn_frame, text="🧹", command=self._clear_pred,
                  bg=Theme.BG_PRIMARY, fg=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, 11, "bold"),
                  relief="flat", pady=10, width=5).pack(side="left")

        # Result Container
        self.res_card = tk.Frame(form, bg=Theme.BG_CARD, highlightthickness=0)
        self.res_card.pack(fill="x", pady=(0, 20))
        
        self.res_inner = tk.Frame(self.res_card, bg=Theme.BG_CARD, padx=20, pady=15)
        self.res_inner.pack(fill="x")
        
        self.res_icon = tk.Label(self.res_inner, text="", font=(Theme.FONT_FAMILY, 24), bg=Theme.BG_CARD)
        self.res_icon.pack(side="left", padx=(0, 15))
        
        self.res_text = tk.Label(self.res_inner, text="", font=(Theme.FONT_FAMILY, 11), 
                                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, justify="left", anchor="w")
        self.res_text.pack(side="left", fill="x")

    def _clear_pred(self):
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.res_inner.config(bg=Theme.BG_CARD)
        self.res_icon.config(text="", bg=Theme.BG_CARD)
        self.res_text.config(text="", bg=Theme.BG_CARD)

    def _on_predict(self):
        try:
            vals = [float(self.entries[f].get()) for f in self.context.features]
            pred = self.engine.predict(vals)
            
            # Modern Result Display
            colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
            cluster_color = colors[pred % len(colors)]
            
            self.res_inner.config(bg=cluster_color)
            self.res_icon.config(text="🏷️", bg=cluster_color, fg="white")
            self.res_text.config(text=f"PREDICTION COMPLETED\nThis individual belongs to: Cluster {pred}", 
                                bg=cluster_color, fg="white", font=(Theme.FONT_FAMILY, 10, "bold"))
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for all fields.")
