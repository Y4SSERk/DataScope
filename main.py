"""
DataScope Professional V2 - Main Entry Point
Enterprise-grade composition root with 100% UI parity with original professional version.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont
from typing import List, Tuple

from src.core.context import AppContext
from src.core.exceptions import DataScopeError
from src.data.loaders import load_excel_dataset
from src.ui.theme import Theme
from src.ui.components import PremiumButton
from src.modules.pca.view import PCAView
from src.modules.clustering.view import ClusteringView
from src.modules.ca.view import CAView
from src.modules.cybersecurity.view import SecurityView

class DataScopeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.context = AppContext()
        self.root.title("DataScope Professional V2")
        self.root.state('zoomed')
        self.root.configure(bg=Theme.BG_LIGHT)
        self.root.bind('<Escape>', lambda e: self.root.state('normal'))
        
        self.module_buttons: List[Tuple[PremiumButton, str, str]] = []
        self._build_ui()

    def _build_ui(self):
        self._build_header()
        self._build_main_card()
        self._build_footer()

    def _build_header(self):
        header = tk.Frame(self.root, bg=Theme.BG_DARK, height=160)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Frame(header, bg=Theme.BG_MEDIUM, height=2).pack(fill="x", side="top")
        
        inner_header = tk.Frame(header, bg=Theme.BG_DARK)
        inner_header.pack(expand=True, fill="y", pady=5)
        
        tk.Label(inner_header, text="🔬", font=(Theme.FONT_FAMILY, 42),
                 fg=Theme.PRIMARY, bg=Theme.BG_DARK).pack(side="left", padx=(0, 20))
        
        text_frame = tk.Frame(inner_header, bg=Theme.BG_DARK)
        text_frame.pack(side="left", fill="y", pady=30)
        
        tk.Label(text_frame, text="DataScope", font=(Theme.FONT_FAMILY, 36, "bold"),
                 fg=Theme.TEXT_WHITE, bg=Theme.BG_DARK).pack(anchor="w")
        tk.Label(text_frame, text="Enterprise Data Analysis & Security Suite",
                 font=(Theme.FONT_FAMILY, 13), fg=Theme.TEXT_MUTED,
                 bg=Theme.BG_DARK, pady=2).pack(anchor="w")
        
        border_frame = tk.Frame(header, height=4)
        border_frame.pack(side="bottom", fill="x")
        for color in [Theme.PRIMARY, Theme.SUCCESS, Theme.AFC_PINK, Theme.DANGER]:
            tk.Frame(border_frame, bg=color, width=100).pack(side="left", fill="both", expand=True)

    def _build_main_card(self):
        outer = tk.Frame(self.root, bg=Theme.BG_LIGHT)
        outer.pack(fill="both", expand=True, padx=40, pady=20)
        
        shadow = tk.Frame(outer, bg=Theme.BORDER)
        shadow.pack(fill="both", expand=True, padx=3, pady=3)
        
        card = tk.Frame(shadow, bg=Theme.BG_CARD)
        card.pack(fill="both", expand=True)
        
        content = tk.Frame(card, bg=Theme.BG_CARD)
        content.pack(fill="both", expand=True, padx=40, pady=30)

        # Dataset Section
        self._build_section_header(content, "📁 Dataset Initialization")
        
        load_frame = tk.Frame(content, bg=Theme.BG_CARD)
        load_frame.pack(fill="x", padx=50, pady=10)
        
        self.btn_load = PremiumButton(load_frame, text="📂  Load Master Dataset (Excel)", 
                                     command=self._on_load_click, bg_color=Theme.PRIMARY, 
                                     hover_color=Theme.PRIMARY_HOVER, height=60, font_size=13)
        self.btn_load.pack(fill="x", expand=True)
        
        self.status_lbl = tk.Label(content, text="No data loaded — Select an Excel file to begin",
                                  fg=Theme.TEXT_MUTED, bg=Theme.BG_CARD, font=(Theme.FONT_FAMILY, 10))
        self.status_lbl.pack(pady=(10, 15))

        # Prefix entry
        prefix_frame = tk.Frame(content, bg=Theme.BG_CARD)
        prefix_frame.pack(pady=(0, 20))
        tk.Label(prefix_frame, text="Individual Prefix:", font=(Theme.FONT_FAMILY, 10),
                 fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(side="left", padx=(0, 10))
        
        self.entry_prefix = tk.Entry(prefix_frame, font=(Theme.FONT_FAMILY, 10), width=20,
                                    relief="solid", bd=1, fg=Theme.TEXT_PRIMARY, bg="#f8fafc")
        self.entry_prefix.insert(0, "Individual")
        self.entry_prefix.pack(side="left")
        self.entry_prefix.bind("<KeyRelease>", self._update_prefix)

        # Modules Section
        divider = tk.Frame(content, bg=Theme.BORDER, height=1)
        divider.pack(fill="x", padx=60, pady=20)
        
        self._build_section_header(content, "🧩 Analysis Modules")
        
        btn_frame = tk.Frame(content, bg=Theme.BG_CARD)
        btn_frame.pack(fill="both", expand=True, pady=10, padx=30)
        for i in range(2): btn_frame.grid_columnconfigure(i, weight=1)
        
        modules = [
            ("📈  Data-Analysis PCA (ACP)", lambda: PCAView(self.root, self.context), Theme.PRIMARY, Theme.PRIMARY_HOVER),
            ("🤖  AI Clustering & Forecasting", lambda: ClusteringView(self.root, self.context), Theme.SUCCESS, Theme.SUCCESS_LIGHT),
            ("📊  Data-Analysis CA (AFC)", lambda: CAView(self.root, self.context), Theme.AFC_PINK, Theme.AFC_PINK_LIGHT),
            ("🛡️  Cybersecurity", lambda: SecurityView(self.root, self.context), Theme.DANGER, Theme.DANGER_LIGHT)
        ]
        
        for idx, (name, command, color, hover) in enumerate(modules):
            row, col = divmod(idx, 2)
            btn_container = tk.Frame(btn_frame, bg=Theme.BG_CARD)
            btn_container.grid(row=row, column=col, sticky="nsew", padx=15, pady=10)
            
            btn = PremiumButton(btn_container, text=name, command=command,
                               bg_color=color, hover_color=hover, height=75,
                               font_size=13, disabled=True)
            btn.pack(fill="both", expand=True)
            self.module_buttons.append((btn, color, hover))

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=Theme.BG_LIGHT, height=100)
        footer.pack(side="bottom", fill="x")
        tk.Frame(footer, height=1, bg=Theme.BORDER).pack(fill="x")
        
        credits = tk.Frame(footer, bg=Theme.BG_LIGHT)
        credits.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Left: Student
        s_frame = tk.Frame(credits, bg=Theme.BG_LIGHT)
        s_frame.pack(side="left", padx=30)
        tk.Label(s_frame, text="DEVELOPED BY", font=(Theme.FONT_FAMILY, 9, "bold"),
                 fg=Theme.TEXT_MUTED, bg=Theme.BG_LIGHT).pack(anchor="w")
        tk.Label(s_frame, text="Yasser KHATTACH", font=(Theme.FONT_FAMILY, 14, "bold"),
                 fg=Theme.PRIMARY_DARK, bg=Theme.BG_LIGHT).pack(anchor="w")
        
        # Right: Professor
        p_frame = tk.Frame(credits, bg=Theme.BG_LIGHT)
        p_frame.pack(side="right", padx=30)
        tk.Label(p_frame, text="SUPERVISED BY PROFESSOR", font=(Theme.FONT_FAMILY, 9, "bold"),
                 fg=Theme.TEXT_MUTED, bg=Theme.BG_LIGHT).pack(anchor="e")
        tk.Label(p_frame, text="DR. EL MKHALET MOUNA", font=(Theme.FONT_FAMILY, 14, "bold"),
                 fg=Theme.TEXT_PRIMARY, bg=Theme.BG_LIGHT).pack(anchor="e")
        
        tk.Label(footer, text="© 2025 DataScope Project  •  Professional Edition",
                 font=(Theme.FONT_FAMILY, 9), fg=Theme.TEXT_MUTED, bg=Theme.BG_LIGHT).pack(side="bottom", pady=(0, 15))

    def _build_section_header(self, parent, text):
        f = tk.Frame(parent, bg=Theme.BG_CARD)
        f.pack(pady=(20, 10))
        tk.Label(f, text=text, font=(Theme.FONT_FAMILY, 14, "bold"),
                 fg=Theme.TEXT_PRIMARY, bg=Theme.BG_CARD).pack()

    def _update_prefix(self, event=None):
        prefix = self.entry_prefix.get().strip()
        if prefix: self.context.set_individual_prefix(prefix)

    def _on_load_click(self):
        filepath = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if not filepath: return
        try:
            raw_df, scaled_df = load_excel_dataset(filepath)
            self.context.set_data(raw_df, scaled_df)
            self.status_lbl.config(text=f"✓ Loaded {len(raw_df)} records", fg=Theme.SUCCESS,
                                  font=(Theme.FONT_FAMILY, 10, "bold"))
            for btn, color, hover in self.module_buttons: btn.enable(color, hover)
        except DataScopeError as e:
            messagebox.showerror("System Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = DataScopeApp(root)
    root.mainloop()
