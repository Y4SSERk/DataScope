import tkinter as tk
from tkinter import messagebox, filedialog
from src.ui.theme import Theme
from src.ui.components import StyledCard, PremiumButton
from src.ui.charts import create_embedded_chart, setup_chart_style
from src.modules.cybersecurity.engine import SecurityEngine
from src.core.context import AppContext
from src.data.loaders import load_excel_dataset

class SecurityView(tk.Toplevel):
    def __init__(self, parent, context: AppContext):
        super().__init__(parent)
        self.context = context
        self.title("CYBER-SECURITY - Anomaly Detection")
        self.state("zoomed")
        self.configure(bg=Theme.BG_PRIMARY)
        self.bind('<Escape>', lambda e: self.destroy())
        
        setup_chart_style()
        self._build_ui()

    def _build_ui(self):
        # Header
        self.header = tk.Frame(self, bg=Theme.DANGER, height=70)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        
        self.header_content = tk.Frame(self.header, bg=Theme.DANGER)
        self.header_content.pack(expand=True, fill="both")
        
        self.title_label = tk.Label(self.header_content, text="CYBERSECURITY ANALYSIS", 
                                   font=(Theme.FONT_FAMILY, 22, "bold"), 
                                   fg=Theme.TEXT_WHITE, bg=Theme.DANGER)
        self.title_label.pack(side="left", padx=20, pady=15)

        # Content Area
        self.content_container = tk.Frame(self, bg=Theme.BG_PRIMARY)
        self.content_container.pack(fill="both", expand=True, padx=20, pady=20)

        self._render_dashboard()

    def _render_dashboard(self):
        # Clear current content
        for widget in self.content_container.winfo_children():
            widget.destroy()
        
        # Reset header (remove back button)
        for widget in self.header_content.winfo_children():
            if getattr(widget, 'is_back_btn', False): widget.destroy()
        self.title_label.config(text="CYBERSECURITY ANALYSIS")

        # Dashboard Area
        dashboard = tk.Frame(self.content_container, bg=Theme.BG_PRIMARY)
        dashboard.pack(expand=True)

        # 1. Dataset Initialization Section
        load_card = tk.Frame(dashboard, bg=Theme.BG_PRIMARY)
        load_card.pack(pady=(0, 40))
        
        tk.Label(load_card, text="Import security data for analysis.",
                 font=(Theme.FONT_FAMILY, 10, "italic"), bg=Theme.BG_PRIMARY, fg=Theme.TEXT_SECONDARY).pack(pady=5)
        
        self.load_btn = PremiumButton(load_card, text="📁 LOAD DATASET", 
                                      command=self._handle_import,
                                      bg_color=Theme.DANGER, hover_color=Theme.DANGER_LIGHT,
                                      width=320, height=65)
        self.load_btn.pack(pady=10)
        
        status_text = f"✅ {len(self.engine.data)} Stations loaded" if hasattr(self, 'engine') else "Status: Waiting"
        self.status_label = tk.Label(load_card, text=status_text, 
                                    font=(Theme.FONT_FAMILY, 10, "bold" if hasattr(self, 'engine') else "italic"),
                                    bg=Theme.BG_PRIMARY, fg=Theme.SUCCESS if hasattr(self, 'engine') else Theme.TEXT_MUTED)
        self.status_label.pack()

        # 2. Module Buttons Grid
        btn_frame = tk.Frame(dashboard, bg=Theme.BG_PRIMARY)
        btn_frame.pack()
        
        menu_items = [
            ("🌲 Isolation Forest Analysis", "iso", Theme.DANGER, Theme.DANGER_LIGHT),
            ("📍 LOF Algorithm Results", "lof", Theme.DANGER, Theme.DANGER_LIGHT),
            ("⚠️ Risk Profile Interpretation", "risk", Theme.WARNING, Theme.WARNING_LIGHT),
            ("🛡️ Security Protocol", "protocol", Theme.PRIMARY, Theme.PRIMARY_HOVER)
        ]

        is_disabled = not hasattr(self, 'res')

        for i, (text, view_id, color, hover) in enumerate(menu_items):
            r, c = divmod(i, 2)
            btn = PremiumButton(btn_frame, text=text, 
                                command=lambda v=view_id: self._switch_view(v),
                                bg_color=color, hover_color=hover, width=320, height=90,
                                disabled=is_disabled)
            btn.grid(row=r, column=c, padx=20, pady=20)

    def _handle_import(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path: return
        
        try:
            raw_df, _ = load_excel_dataset(file_path)
            self.engine = SecurityEngine(raw_df)
            self.res = self.engine.run_scan()
            self._render_dashboard()
        except Exception as e:
            messagebox.showerror("Import Error", f"Unable to load file: {str(e)}")

    def _switch_view(self, view_id):
        # Clear current content
        for widget in self.content_container.winfo_children():
            widget.destroy()

        # Add Back Button to Header
        back_btn = tk.Button(self.header_content, text="⬅️ Back to Menu", 
                             font=(Theme.FONT_FAMILY, 10, "bold"),
                             bg="#475569", fg=Theme.TEXT_WHITE, bd=0, padx=15, pady=5,
                             cursor="hand2", command=self._render_dashboard)
        back_btn.is_back_btn = True
        back_btn.pack(side="right", padx=20)

        # Update title based on view
        titles = {
            "iso": "🌲 Isolation Forest Analysis",
            "lof": "📍 LOF Algorithm Results",
            "risk": "⚠️ Risk Profiles & Interpretation",
            "protocol": "🛡️ Security Protocol"
        }
        self.title_label.config(text=titles.get(view_id, "CYBERSECURITY ANALYSIS"))

        if view_id == "iso":
            self._render_iso_full()
        elif view_id == "lof":
            self._render_lof_full()
        elif view_id == "risk":
            self._render_risk_full()
        elif view_id == "protocol":
            self._render_protocol_full()

    def _render_iso_full(self):
        card = StyledCard(self.content_container, "Isolation Forest Results", "🌲")
        card.pack(fill="both", expand=True)
        fig, ax, canvas = create_embedded_chart(card.content)
        r = self.res
        colors = [Theme.DANGER if x == -1 else Theme.PRIMARY for x in r['y_iso']]
        ax.scatter(r['X_pca'][:,0], r['X_pca'][:,1], c=colors, s=80, alpha=0.9, edgecolor='white')
        
        for i, txt in enumerate(r['labels']):
            is_anomaly = r['y_iso'][i] == -1
            ax.annotate(txt, (r['X_pca'][i, 0], r['X_pca'][i, 1]), 
                        color=Theme.DANGER if is_anomaly else Theme.TEXT_SECONDARY, 
                        fontweight='bold' if is_anomaly else 'normal', 
                        fontsize=7, alpha=0.9 if is_anomaly else 0.4)

        ax.set_title(f"Visualizing {r['iso_count']} Detected Global Anomalies")
        canvas.draw()

    def _render_lof_full(self):
        card = StyledCard(self.content_container, "LOF (Local Outlier Factor) Results", "📍")
        card.pack(fill="both", expand=True)
        fig, ax, canvas = create_embedded_chart(card.content)
        r = self.res
        colors = [Theme.WARNING if x == -1 else Theme.PRIMARY for x in r['y_lof']]
        ax.scatter(r['X_pca'][:,0], r['X_pca'][:,1], c=colors, s=80, alpha=0.9, edgecolor='white')
        
        for i, txt in enumerate(r['labels']):
            is_outlier = r['y_lof'][i] == -1
            ax.annotate(txt, (r['X_pca'][i, 0], r['X_pca'][i, 1]), 
                        color=Theme.WARNING if is_outlier else Theme.TEXT_SECONDARY, 
                        fontweight='bold' if is_outlier else 'normal', 
                        fontsize=7, alpha=0.9 if is_outlier else 0.4)

        ax.set_title(f"Visualizing {r['lof_count']} Density-based Outliers")
        canvas.draw()

    def _render_risk_full(self):
        card = StyledCard(self.content_container, "Risk Interpretation & Solutions", "⚠️")
        card.pack(fill="both", expand=True)
        r = self.res
        t = tk.Text(card.content, bg="#fef2f2", font=(Theme.FONT_MONO, 11), relief="flat", padx=25, pady=20)
        content = "🚨 CRITICAL RISK ANALYSIS REPORT\n" + "═"*45 + "\n\n"
        
        if r['high_risk_ids']:
            content += "The following stations present high security risks (Algorithmic Consensus):\n\n"
            for rid in r['high_risk_ids']:
                content += f"  ❌ {rid} -> HIGH PRIORITY INVESTIGATION\n"
        else:
            content += "  ✅ No high-risk anomalies detected by algorithmic consensus.\n"
            
        content += "\n\n🛡️ RECOMMENDED MITIGATION STRATEGIES:\n"
        content += "• Inspect network access logs for stations flagged as anomalies.\n"
        content += "• Update firewall configuration and station-specific security rules.\n"
        content += "• Temporarily isolate suspicious platforms or IoT devices.\n"
        content += "• Execute a complete vulnerability audit on target station networks.\n"
        
        t.insert("1.0", content)
        t.config(state="disabled")
        t.pack(fill="both", expand=True)

    def _render_protocol_full(self):
        card = StyledCard(self.content_container, "Cybersecurity Standard Protocol", "🛡️")
        card.pack(fill="both", expand=True)
        protocol = """
1. 🔍 INVESTIGATION PHASE
   - Cross-reference flagged Station IDs with physical activity logs.
   - Analyze specific indicator spikes (Suspect Attempts, Connection Speed).

2. 🔐 LOCKDOWN PHASE
   - Flagged stations should be isolated from the main production network.
   - Initiate multi-factor authentication for all platform access roles.

3. 📊 MONITORING PHASE
   - Increase LOF sensitivity for real-time traffic monitoring.
   - Compare behavioral drift over 24-hour cycles.

💡 PRO TIP: 
   Always validate the vulnerability score before deploying new station software.
"""
        tk.Label(card.content, text=protocol, font=(Theme.FONT_MONO, 11), 
                 justify="left", bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                 padx=40, pady=30, anchor="nw").pack(fill="both", expand=True)


