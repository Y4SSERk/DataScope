"""
DataScope Chart Engine
Centralized Matplotlib configuration and embedding.
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from src.ui.theme import Theme

class ZoomManager:
    """Handles professional mouse wheel zooming and panning with performance optimizations."""
    def __init__(self, fig, ax, canvas):
        self.fig = fig
        self.ax = ax
        self.canvas = canvas
        self.base_scale = 1.25
        
        # Initial limits
        self.init_xlim = None
        self.init_ylim = None
        
        self.press = None
        self._throttling = False
        self._interaction_active = False
        
        self.cids = [
            self.canvas.mpl_connect('scroll_event', self.on_scroll),
            self.canvas.mpl_connect('button_press_event', self.on_press),
            self.canvas.mpl_connect('button_release_event', self.on_release),
            self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        ]
        self.canvas.zoom_manager = self

    def _capture_limits(self):
        if self.init_xlim is None:
            self.init_xlim = self.ax.get_xlim()
            self.init_ylim = self.ax.get_ylim()

    def _set_fast_mode(self, enabled: bool):
        """Hides heavy elements (like text annotations) during active interaction."""
        if self._interaction_active == enabled:
            return
        
        self._interaction_active = enabled
        # Hide/Show all text elements to speed up rendering during pan/zoom
        for text in self.ax.texts:
            text.set_visible(not enabled)

    def _request_draw(self):
        """Throttled draw request for smoother UI."""
        if not self._throttling:
            self.canvas.draw_idle()
            self._throttling = True
            # ~60fps cap (16ms delay)
            self.canvas.get_tk_widget().after(16, self._reset_throttling)

    def _reset_throttling(self):
        self._throttling = False

    def on_scroll(self, event):
        if event.inaxes != self.ax: return
        self._capture_limits()
        self._set_fast_mode(True)
        
        x, y = event.xdata, event.ydata
        if x is None or y is None: return

        if event.button == 'up':
            scale_factor = 1.0 / self.base_scale
        elif event.button == 'down':
            scale_factor = self.base_scale
        else:
            try:
                scale_factor = 1.0 / self.base_scale if event.step > 0 else self.base_scale
            except: return

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        new_width = (xlim[1] - xlim[0]) * scale_factor
        new_height = (ylim[1] - ylim[0]) * scale_factor
        
        rel_x = (xlim[1] - x) / (xlim[1] - xlim[0])
        rel_y = (ylim[1] - y) / (ylim[1] - ylim[0])
        
        self.ax.set_xlim([x - new_width * (1 - rel_x), x + new_width * rel_x])
        self.ax.set_ylim([y - new_height * (1 - rel_y), y + new_height * rel_y])
        
        self._request_draw()
        
        # Reset fast mode after a short delay if no more scroll events
        if hasattr(self, '_scroll_timer'):
            self.canvas.get_tk_widget().after_cancel(self._scroll_timer)
        self._scroll_timer = self.canvas.get_tk_widget().after(200, lambda: self._set_fast_mode(False) or self.canvas.draw_idle())

    def on_press(self, event):
        if event.inaxes != self.ax: return
        self._capture_limits()
        
        if event.dblclick:
            if self.init_xlim:
                self.ax.set_xlim(self.init_xlim)
                self.ax.set_ylim(self.init_ylim)
                self._set_fast_mode(False)
                self.canvas.draw_idle()
            return

        if event.button == 1:
            self._set_fast_mode(True)
            # Store initial pixel coordinates, data limits, and the inverse transform
            inv = self.ax.transData.inverted()
            self.press = event.x, event.y, self.ax.get_xlim(), self.ax.get_ylim(), inv

    def on_motion(self, event):
        if self.press is None or event.inaxes != self.ax: return
        xpress, ypress, xlim, ylim, inv = self.press
        
        if event.x is None or event.y is None: return
        
        # Use the inverse transform from the moment of 'press' to avoid jitter
        p0 = inv.transform((xpress, ypress))
        p1 = inv.transform((event.x, event.y))
        
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        
        self.ax.set_xlim([xlim[0] - dx, xlim[1] - dx])
        self.ax.set_ylim([ylim[0] - dy, ylim[1] - dy])
        self._request_draw()

    def on_release(self, event):
        self.press = None
        self._set_fast_mode(False)
        self.canvas.draw_idle()

def setup_chart_style():
    """Applies universal styling to all matplotlib charts."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Inter', 'Segoe UI', 'Arial'],
        'figure.facecolor': '#ffffff',
        'axes.facecolor': '#fcfcfc',
        'axes.edgecolor': '#e2e8f0',
        'grid.color': '#f1f5f9',
        'grid.linewidth': 1.0,
        'axes.labelcolor': '#475569',
        'xtick.color': '#64748b',
        'ytick.color': '#64748b',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'legend.frameon': True,
        'legend.facecolor': 'white',
        'legend.edgecolor': '#e2e8f0',
    })

def create_embedded_chart(parent: tk.Widget, figsize=(5, 4), toolbar: bool = False) -> tuple:
    """Creates a Figure and Axis embedded in a Tkinter parent, with custom interaction."""
    fig = Figure(figsize=figsize, dpi=100)
    fig.patch.set_facecolor('white')
    ax = fig.add_subplot(111)
    
    # Clean up axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Canvas
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.config(highlightthickness=0)
    
    # Initialize interaction
    ZoomManager(fig, ax, canvas)
    
    if toolbar:
        # Create a frame for the toolbar to keep it neat
        tb_frame = tk.Frame(parent, bg='white')
        tb_frame.pack(side="bottom", fill="x")
        nav_toolbar = NavigationToolbar2Tk(canvas, tb_frame)
        nav_toolbar.update()
        canvas_widget.pack(fill="both", expand=True, side="top")
    else:
        canvas_widget.pack(fill="both", expand=True)
        
    return fig, ax, canvas


