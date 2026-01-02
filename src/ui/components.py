"""
DataScope UI Components - Premium Edition
Reusable widgets with specific original styling (shadows, rounded corners).
"""

import tkinter as tk
from typing import Callable, Optional
from src.ui.theme import Theme

class PremiumButton(tk.Canvas):
    """Refined premium button with exact shadow offset and rounding."""
    
    def __init__(self, parent, text: str, command: Callable, 
                 bg_color: str, hover_color: str, height: int = 60,
                 font_size: int = 12, disabled: bool = False, **kwargs):
        super().__init__(parent, height=height, bg=parent["bg"] if "bg" in parent.keys() else Theme.BG_CARD, 
                        highlightthickness=0, **kwargs)
        
        self.command = command
        self.text = text
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.disabled = disabled
        self.font_size = font_size
        
        self.current_color = self.bg_color if not disabled else "#d1d5db"
        
        self.bind("<Configure>", self._on_resize)
        if not disabled:
            self._bind_events()

    def _bind_events(self):
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_resize(self, event):
        self._draw_button(self.current_color)

    def _draw_button(self, color: str):
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        if width < 10 or height < 10: return
            
        # Draw Shadow (offset 4,4)
        if not self.disabled:
            self._round_rect(4, 4, width - 2, height - 2, 12, fill=Theme.SHADOW, outline="")
        
        # Draw Body (size -6)
        self._round_rect(0, 0, width - 6, height - 6, 12, fill=color, outline="")
        
        # Draw Text
        text_color = Theme.TEXT_WHITE if not self.disabled else Theme.TEXT_MUTED
        self.create_text(
            (width - 6) // 2, (height - 6) // 2,
            text=self.text, 
            fill=text_color,
            font=(Theme.FONT_FAMILY, self.font_size, "bold")
        )
        
    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        self._draw_button(self.hover_color)
        self.config(cursor="hand2")
        
    def _on_leave(self, event):
        self._draw_button(self.bg_color)
        self.config(cursor="")
        
    def _on_click(self, event):
        if self.command and not self.disabled:
            self.command()

    def enable(self, new_color=None, new_hover=None):
        self.disabled = False
        if new_color: self.bg_color = new_color
        if new_hover: self.hover_color = new_hover
        self._bind_events()
        self._draw_button(self.bg_color)

class StyledCard(tk.Frame):
    """Premium container with title and separator."""
    def __init__(self, parent, title: str, icon: str = "📋", **kwargs):
        super().__init__(parent, bg=Theme.BG_CARD, highlightthickness=1, 
                         highlightbackground=Theme.BORDER, **kwargs)
        
        # Title section
        title_frame = tk.Frame(self, bg=Theme.BG_CARD)
        title_frame.pack(fill="x", padx=15, pady=(15, 8))
        
        tk.Label(
            title_frame,
            text=f"{icon}  {title}",
            font=(Theme.FONT_FAMILY, 12, "bold"),
            fg=Theme.TEXT_PRIMARY,
            bg=Theme.BG_CARD
        ).pack(anchor="w")
        
        tk.Frame(title_frame, height=1, bg=Theme.BORDER).pack(fill="x", pady=(8, 0))
        
        # Content section
        self.content = tk.Frame(self, bg=Theme.BG_CARD)
        self.content.pack(fill="both", expand=True)

class ModernSlider(tk.Canvas):
    """Custom premium slider with smooth interaction and clean design."""
    def __init__(self, parent, min_val, max_val, initial_val, callback, 
                 active_color=Theme.SUCCESS, **kwargs):
        super().__init__(parent, height=60, bg=parent["bg"], highlightthickness=0, **kwargs)
        
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = initial_val
        self.callback = callback
        self.active_color = active_color
        
        self.padding = 30
        self.track_height = 6
        self.thumb_radius = 6
        
        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Enter>", lambda e: self.config(cursor="hand2"))
        self.bind("<Leave>", lambda e: self.config(cursor=""))

    def _draw(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 50: return
        
        x_start = self.padding
        x_end = width - self.padding
        y_center = height // 2
        
        # Draw Track (Background) - Use high-quality rounded line
        self.create_line(x_start, y_center, x_end, y_center, 
                        fill=Theme.BORDER, width=self.track_height, capstyle='round')
        
        # Calculate Thumb Position
        ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        thumb_x = x_start + ratio * (x_end - x_start)
        
        # Draw Active Track - Use high-quality rounded line
        self.create_line(x_start, y_center, thumb_x, y_center, 
                        fill=self.active_color, width=self.track_height, capstyle='round')
        
        # Draw Thumb Shadow (subtle)
        self.create_oval(thumb_x - self.thumb_radius, y_center - self.thumb_radius + 1,
                         thumb_x + self.thumb_radius, y_center + self.thumb_radius + 1,
                         fill="#e2e8f0", outline="")
        
        # Draw Thumb (Outer ring)
        self.create_oval(thumb_x - self.thumb_radius, y_center - self.thumb_radius,
                         thumb_x + self.thumb_radius, y_center + self.thumb_radius,
                         fill="white", outline=self.active_color, width=2)
        
        # Value Label (Floating) - Positioned for smaller thumb
        self.create_text(thumb_x, y_center - 18, text=str(self.current_val),
                        font=(Theme.FONT_FAMILY, 11, "bold"), fill=Theme.TEXT_PRIMARY)

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_click(self, event):
        self._update_val(event.x)

    def _on_drag(self, event):
        self._update_val(event.x)

    def _update_val(self, x):
        width = self.winfo_width()
        x_start = self.padding
        x_end = width - self.padding
        
        # Clamp X
        x = max(x_start, min(x, x_end))
        
        # Calculate Value
        ratio = (x - x_start) / (x_end - x_start)
        new_val = round(self.min_val + ratio * (self.max_val - self.min_val))
        
        if new_val != self.current_val:
            self.current_val = new_val
            self._draw()
            if self.callback:
                self.callback(new_val)
