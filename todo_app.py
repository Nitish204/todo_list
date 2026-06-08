"""
╔══════════════════════════════════════════════════════════╗
║           AURORA TODO  —  A Premium Task Manager          ║
║        Single-file Python App  |  tkinter + ttk           ║
╚══════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import json, os, time, threading
from datetime import datetime, date
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import math, random

# ─────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.expanduser("~"), ".aurora_todos.json")

PRIORITIES = {"HIGH": "#FF4757", "MEDIUM": "#FFA502", "LOW": "#2ED573"}
CATEGORIES = ["Work", "Personal", "Health", "Learning", "Finance", "Other"]

@dataclass
class Todo:
    id: int
    title: str
    done: bool = False
    priority: str = "MEDIUM"
    category: str = "Personal"
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    due: Optional[str] = None
    note: str = ""

def load_todos() -> List[Todo]:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return [Todo(**t) for t in json.load(f)]
        except Exception:
            return []
    return []

def save_todos(todos: List[Todo]):
    with open(DATA_FILE, "w") as f:
        json.dump([asdict(t) for t in todos], f, indent=2)

# ─────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────
class Theme:
    BG          = "#0D0F1A"
    SURFACE     = "#161827"
    SURFACE2    = "#1E2235"
    BORDER      = "#2A2D45"
    ACCENT      = "#7C6FFF"
    ACCENT2     = "#FF6B9D"
    TEXT        = "#E8EAFF"
    TEXT_MUTED  = "#6B6F8E"
    SUCCESS     = "#2ED573"
    WARNING     = "#FFA502"
    DANGER      = "#FF4757"
    DONE_BG     = "#131520"
    DONE_TEXT   = "#3A3F5C"

# ─────────────────────────────────────────────
# ANIMATED CANVAS BACKGROUND
# ─────────────────────────────────────────────
class ParticleCanvas(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, bg=Theme.BG, highlightthickness=0, **kw)
        self._particles = []
        self._running = True
        self._init_particles()
        self._animate()

    def _init_particles(self):
        for _ in range(28):
            x = random.randint(0, 1200)
            y = random.randint(0, 800)
            r = random.uniform(1, 3.5)
            speed = random.uniform(0.15, 0.6)
            angle = random.uniform(0, 2 * math.pi)
            alpha = random.uniform(0.2, 0.8)
            colors = ["#7C6FFF", "#FF6B9D", "#2ED573", "#FFA502", "#5edfff"]
            color = random.choice(colors)
            oid = self.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
            self._particles.append({
                "id": oid, "x": x, "y": y, "r": r,
                "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed,
                "color": color, "alpha": alpha
            })

    def _animate(self):
        if not self._running:
            return
        w = self.winfo_width() or 1200
        h = self.winfo_height() or 800
        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] < 0: p["x"] = w
            if p["x"] > w: p["x"] = 0
            if p["y"] < 0: p["y"] = h
            if p["y"] > h: p["y"] = 0
            x, y, r = p["x"], p["y"], p["r"]
            self.coords(p["id"], x-r, y-r, x+r, y+r)
        self.after(40, self._animate)

    def stop(self):
        self._running = False

# ─────────────────────────────────────────────
# CUSTOM WIDGETS
# ─────────────────────────────────────────────
class RoundedButton(tk.Canvas):
    def __init__(self, master, text="", command=None, bg=Theme.ACCENT,
                 fg=Theme.TEXT, width=120, height=36, radius=18, font_size=11, **kw):
        super().__init__(master, width=width, height=height,
                         bg=master.cget("bg") if hasattr(master, "cget") else Theme.BG,
                         highlightthickness=0, cursor="hand2", **kw)
        self._bg = bg
        self._bg_hover = self._lighten(bg)
        self._fg = fg
        self._text = text
        self._cmd = command
        self._r = radius
        self._w = width
        self._h = height
        self._font_size = font_size
        self._draw(self._bg)
        self.bind("<Enter>", lambda e: self._draw(self._bg_hover))
        self.bind("<Leave>", lambda e: self._draw(self._bg))
        self.bind("<Button-1>", lambda e: self._click())
        self.bind("<ButtonRelease-1>", lambda e: self._draw(self._bg_hover))

    def _lighten(self, hex_color):
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        r = min(255, r + 30); g = min(255, g + 30); b = min(255, b + 30)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self, color):
        self.delete("all")
        r = self._r; w = self._w; h = self._h
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=color, outline=color)
        self.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=color, outline=color)
        self.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=color, outline=color)
        self.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(r, 0, w-r, h, fill=color, outline=color)
        self.create_rectangle(0, r, w, h-r, fill=color, outline=color)
        self.create_text(w//2, h//2, text=self._text, fill=self._fg,
                         font=("Helvetica", self._font_size, "bold"))

    def _click(self):
        self._draw(self._bg)
        if self._cmd:
            self._cmd()

    def configure_text(self, text):
        self._text = text
        self._draw(self._bg)


class GlowEntry(tk.Frame):
    def __init__(self, master, placeholder="", width=300, **kw):
        super().__init__(master, bg=Theme.SURFACE, **kw)
        self._placeholder = placeholder
        self._focused = False
        self.configure(highlightthickness=1, highlightbackground=Theme.BORDER,
                       highlightcolor=Theme.ACCENT)
        self._entry = tk.Entry(self, bg=Theme.SURFACE, fg=Theme.TEXT,
                               insertbackground=Theme.ACCENT,
                               relief="flat", font=("Helvetica", 12),
                               width=width)
        self._entry.pack(padx=12, pady=8, fill="both", expand=True)
        self._set_placeholder()
        self._entry.bind("<FocusIn>",  self._on_focus_in)
        self._entry.bind("<FocusOut>", self._on_focus_out)

    def _set_placeholder(self):
        self._entry.insert(0, self._placeholder)
        self._entry.config(fg=Theme.TEXT_MUTED)
        self._is_placeholder = True

    def _on_focus_in(self, e):
        self.configure(highlightbackground=Theme.ACCENT)
        if self._is_placeholder:
            self._entry.delete(0, "end")
            self._entry.config(fg=Theme.TEXT)
            self._is_placeholder = False

    def _on_focus_out(self, e):
        self.configure(highlightbackground=Theme.BORDER)
        if not self._entry.get():
            self._set_placeholder()

    def get(self):
        if self._is_placeholder:
            return ""
        return self._entry.get()

    def set(self, value):
        self._entry.delete(0, "end")
        if value:
            self._entry.insert(0, value)
            self._entry.config(fg=Theme.TEXT)
            self._is_placeholder = False
        else:
            self._set_placeholder()

    def clear(self):
        self.set("")

    def bind_entry(self, event, callback):
        self._entry.bind(event, callback)


# ─────────────────────────────────────────────
# TOAST NOTIFICATION
# ─────────────────────────────────────────────
class Toast:
    def __init__(self, root, message, kind="success"):
        color = {"success": Theme.SUCCESS, "error": Theme.DANGER, "info": Theme.ACCENT}.get(kind, Theme.ACCENT)
        self._win = tk.Toplevel(root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.attributes("-alpha", 0.0)
        rw = root.winfo_width(); rx = root.winfo_x()
        ry = root.winfo_y(); rh = root.winfo_height()
        w, h = 320, 50
        x = rx + rw//2 - w//2
        y = ry + rh - 80
        self._win.geometry(f"{w}x{h}+{x}+{y}")
        frame = tk.Frame(self._win, bg=color)
        frame.pack(fill="both", expand=True)
        icons = {"success": "✓", "error": "✗", "info": "ℹ"}
        icon = icons.get(kind, "•")
        tk.Label(frame, text=f"  {icon}  {message}", bg=color, fg="white",
                 font=("Helvetica", 11, "bold"), anchor="w").pack(fill="x", padx=10, pady=10)
        self._fade_in()

    def _fade_in(self):
        def _step(alpha=0.0):
            if alpha <= 1.0:
                self._win.attributes("-alpha", alpha)
                self._win.after(20, lambda: _step(alpha + 0.08))
            else:
                self._win.after(1800, self._fade_out)
        _step()

    def _fade_out(self):
        def _step(alpha=1.0):
            if alpha >= 0:
                self._win.attributes("-alpha", alpha)
                self._win.after(20, lambda: _step(alpha - 0.08))
            else:
                self._win.destroy()
        _step()

# ─────────────────────────────────────────────
# TODO CARD
# ─────────────────────────────────────────────
class TodoCard(tk.Frame):
    def __init__(self, master, todo: Todo, on_toggle, on_delete, on_edit, **kw):
        bg = Theme.DONE_BG if todo.done else Theme.SURFACE2
        super().__init__(master, bg=bg, padx=0, pady=0, **kw)
        self.todo = todo
        self._on_toggle = on_toggle
        self._on_delete = on_delete
        self._on_edit = on_edit
        self._build()
        self.bind("<Enter>", self._hover_on)
        self.bind("<Leave>", self._hover_off)

    def _hover_on(self, e=None):
        if not self.todo.done:
            self.configure(bg=Theme.BORDER)
            for w in self.winfo_children():
                try: w.configure(bg=Theme.BORDER)
                except: pass

    def _hover_off(self, e=None):
        bg = Theme.DONE_BG if self.todo.done else Theme.SURFACE2
        self.configure(bg=bg)
        for w in self.winfo_children():
            try: w.configure(bg=bg)
            except: pass

    def _build(self):
        bg = self.cget("bg")
        pri_color = PRIORITIES.get(self.todo.priority, Theme.TEXT_MUTED)
        text_color = Theme.DONE_TEXT if self.todo.done else Theme.TEXT
        title_font = ("Helvetica", 13)
        if self.todo.done:
            title_font = ("Helvetica", 13, "overstrike")

        # Priority strip
        strip = tk.Frame(self, bg=pri_color, width=4)
        strip.pack(side="left", fill="y")

        # Main body
        body = tk.Frame(self, bg=bg)
        body.pack(side="left", fill="both", expand=True, padx=12, pady=10)

        # Top row
        top = tk.Frame(body, bg=bg)
        top.pack(fill="x")

        # Checkbox
        cb_var = tk.BooleanVar(value=self.todo.done)
        cb_text = "✓" if self.todo.done else "○"
        cb_color = Theme.SUCCESS if self.todo.done else Theme.TEXT_MUTED
        self._cb_label = tk.Label(top, text=cb_text, fg=cb_color, bg=bg,
                                   font=("Helvetica", 15), cursor="hand2")
        self._cb_label.pack(side="left", padx=(0, 8))
        self._cb_label.bind("<Button-1>", lambda e: self._on_toggle(self.todo.id))

        # Title
        title = tk.Label(top, text=self.todo.title, fg=text_color, bg=bg,
                         font=title_font, anchor="w", wraplength=380, justify="left")
        title.pack(side="left", fill="x", expand=True)

        # Category badge
        cat_frame = tk.Frame(top, bg=Theme.ACCENT, padx=6, pady=2)
        cat_frame.pack(side="right", padx=4)
        tk.Label(cat_frame, text=self.todo.category, fg="white",
                 bg=Theme.ACCENT, font=("Helvetica", 8, "bold")).pack()

        # Priority badge
        pri_frame = tk.Frame(top, bg=pri_color, padx=6, pady=2)
        pri_frame.pack(side="right", padx=4)
        tk.Label(pri_frame, text=self.todo.priority, fg="white",
                 bg=pri_color, font=("Helvetica", 8, "bold")).pack()

        # Bottom row (meta)
        bot = tk.Frame(body, bg=bg)
        bot.pack(fill="x", pady=(4, 0))
        created = datetime.fromisoformat(self.todo.created).strftime("%b %d, %Y")
        meta = f"Created {created}"
        if self.todo.due:
            meta += f"   •   Due {self.todo.due}"
        if self.todo.note:
            meta += f"   •   📝 {self.todo.note[:40]}{'…' if len(self.todo.note) > 40 else ''}"
        tk.Label(bot, text=meta, fg=Theme.TEXT_MUTED, bg=bg,
                 font=("Helvetica", 9)).pack(side="left")

        # Action buttons
        edit_btn = tk.Label(top, text="✎", fg=Theme.ACCENT, bg=bg,
                            font=("Helvetica", 14), cursor="hand2")
        edit_btn.pack(side="right", padx=4)
        edit_btn.bind("<Button-1>", lambda e: self._on_edit(self.todo.id))

        del_btn = tk.Label(top, text="🗑", fg=Theme.DANGER, bg=bg,
                           font=("Helvetica", 13), cursor="hand2")
        del_btn.pack(side="right", padx=4)
        del_btn.bind("<Button-1>", lambda e: self._on_delete(self.todo.id))


# ─────────────────────────────────────────────
# ADD / EDIT DIALOG
# ─────────────────────────────────────────────
class TodoDialog(tk.Toplevel):
    def __init__(self, master, on_save, todo: Optional[Todo] = None):
        super().__init__(master)
        self.title("Edit Task" if todo else "New Task")
        self.resizable(False, False)
        self.configure(bg=Theme.SURFACE)
        self.attributes("-topmost", True)
        self._todo = todo
        self._on_save = on_save
        w, h = 480, 420
        mx = master.winfo_x() + master.winfo_width()//2 - w//2
        my = master.winfo_y() + master.winfo_height()//2 - h//2
        self.geometry(f"{w}x{h}+{mx}+{my}")
        self._build()
        if todo:
            self._populate(todo)
        self.grab_set()
        self.lift()

    def _build(self):
        pad = dict(padx=24, pady=8)
        header_text = "Edit Task" if self._todo else "✦  New Task"
        tk.Label(self, text=header_text, fg=Theme.TEXT, bg=Theme.SURFACE,
                 font=("Helvetica", 16, "bold")).pack(pady=(20, 4))
        tk.Frame(self, bg=Theme.ACCENT, height=2).pack(fill="x", padx=24, pady=(0, 16))

        # Title
        tk.Label(self, text="Task Title *", fg=Theme.TEXT_MUTED, bg=Theme.SURFACE,
                 font=("Helvetica", 10)).pack(anchor="w", padx=24)
        self._title_entry = GlowEntry(self, placeholder="What needs to be done?", width=36)
        self._title_entry.pack(fill="x", padx=24, pady=(4, 8))

        # Row: Priority + Category
        row = tk.Frame(self, bg=Theme.SURFACE)
        row.pack(fill="x", padx=24, pady=4)

        # Priority
        pl = tk.Frame(row, bg=Theme.SURFACE)
        pl.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(pl, text="Priority", fg=Theme.TEXT_MUTED, bg=Theme.SURFACE,
                 font=("Helvetica", 10)).pack(anchor="w")
        self._pri_var = tk.StringVar(value="MEDIUM")
        pri_cb = ttk.Combobox(pl, textvariable=self._pri_var,
                              values=list(PRIORITIES.keys()), state="readonly", width=14)
        pri_cb.pack(fill="x")
        self._style_combo(pri_cb)

        # Category
        cl = tk.Frame(row, bg=Theme.SURFACE)
        cl.pack(side="left", fill="x", expand=True)
        tk.Label(cl, text="Category", fg=Theme.TEXT_MUTED, bg=Theme.SURFACE,
                 font=("Helvetica", 10)).pack(anchor="w")
        self._cat_var = tk.StringVar(value="Personal")
        cat_cb = ttk.Combobox(cl, textvariable=self._cat_var,
                              values=CATEGORIES, state="readonly", width=14)
        cat_cb.pack(fill="x")
        self._style_combo(cat_cb)

        # Due date
        tk.Label(self, text="Due Date (YYYY-MM-DD, optional)", fg=Theme.TEXT_MUTED,
                 bg=Theme.SURFACE, font=("Helvetica", 10)).pack(anchor="w", padx=24, pady=(4,0))
        self._due_entry = GlowEntry(self, placeholder="e.g. 2025-12-31", width=36)
        self._due_entry.pack(fill="x", padx=24, pady=(4, 4))

        # Note
        tk.Label(self, text="Note (optional)", fg=Theme.TEXT_MUTED, bg=Theme.SURFACE,
                 font=("Helvetica", 10)).pack(anchor="w", padx=24)
        note_frame = tk.Frame(self, bg=Theme.SURFACE, highlightthickness=1,
                              highlightbackground=Theme.BORDER)
        note_frame.pack(fill="x", padx=24, pady=(4, 16))
        self._note_text = tk.Text(note_frame, bg=Theme.SURFACE, fg=Theme.TEXT,
                                  insertbackground=Theme.ACCENT, relief="flat",
                                  height=3, font=("Helvetica", 11), wrap="word")
        self._note_text.pack(padx=8, pady=6, fill="both")

        # Buttons
        btn_row = tk.Frame(self, bg=Theme.SURFACE)
        btn_row.pack(fill="x", padx=24, pady=(0, 20))
        RoundedButton(btn_row, text="Cancel", command=self.destroy,
                      bg=Theme.BORDER, width=110).pack(side="left", padx=(0, 8))
        RoundedButton(btn_row, text="Save Task ✦", command=self._save,
                      bg=Theme.ACCENT, width=150).pack(side="left")

    def _style_combo(self, cb):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=Theme.SURFACE2,
                        background=Theme.SURFACE2, foreground=Theme.TEXT,
                        selectbackground=Theme.ACCENT, bordercolor=Theme.BORDER,
                        arrowcolor=Theme.ACCENT)

    def _populate(self, todo: Todo):
        self._title_entry.set(todo.title)
        self._pri_var.set(todo.priority)
        self._cat_var.set(todo.category)
        if todo.due:
            self._due_entry.set(todo.due)
        if todo.note:
            self._note_text.insert("1.0", todo.note)

    def _save(self):
        title = self._title_entry.get().strip()
        if not title:
            Toast(self.master, "Title is required!", kind="error")
            return
        due = self._due_entry.get().strip() or None
        if due:
            try: datetime.strptime(due, "%Y-%m-%d")
            except ValueError:
                Toast(self.master, "Invalid date format!", kind="error")
                return
        note = self._note_text.get("1.0", "end-1c").strip()
        self._on_save(title, self._pri_var.get(), self._cat_var.get(), due, note)
        self.destroy()


# ─────────────────────────────────────────────
# STATS PANEL
# ─────────────────────────────────────────────
class StatsPanel(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg=Theme.SURFACE, **kw)
        self._labels = {}
        self._build()

    def _build(self):
        stats = [
            ("TOTAL",     "0", Theme.ACCENT),
            ("DONE",      "0", Theme.SUCCESS),
            ("PENDING",   "0", Theme.WARNING),
            ("HIGH PRI",  "0", Theme.DANGER),
        ]
        for i, (name, val, color) in enumerate(stats):
            card = tk.Frame(self, bg=Theme.SURFACE2, padx=14, pady=10)
            card.grid(row=0, column=i, padx=6, pady=6, sticky="nsew")
            self.columnconfigure(i, weight=1)
            num_lbl = tk.Label(card, text=val, fg=color, bg=Theme.SURFACE2,
                               font=("Helvetica", 22, "bold"))
            num_lbl.pack()
            tk.Label(card, text=name, fg=Theme.TEXT_MUTED, bg=Theme.SURFACE2,
                     font=("Helvetica", 8, "bold")).pack()
            self._labels[name] = num_lbl

    def update_stats(self, todos: List[Todo]):
        total   = len(todos)
        done    = sum(1 for t in todos if t.done)
        pending = total - done
        high    = sum(1 for t in todos if t.priority == "HIGH" and not t.done)
        self._labels["TOTAL"].config(text=str(total))
        self._labels["DONE"].config(text=str(done))
        self._labels["PENDING"].config(text=str(pending))
        self._labels["HIGH PRI"].config(text=str(high))


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
class AuroraApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aurora — Task Manager")
        self.root.geometry("860x720")
        self.root.minsize(680, 500)
        self.root.configure(bg=Theme.BG)
        self._next_id = 1
        self._todos: List[Todo] = []
        self._filter_done  = None   # None=all, True=done, False=pending
        self._filter_cat   = "All"
        self._filter_pri   = "All"
        self._search_term  = ""
        self._load()
        self._build_ui()
        self._refresh()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _load(self):
        self._todos = load_todos()
        self._next_id = max((t.id for t in self._todos), default=0) + 1

    def _on_close(self):
        if hasattr(self, "_particle_canvas"):
            self._particle_canvas.stop()
        save_todos(self._todos)
        self.root.destroy()

    # ──────────────────── UI BUILD ────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=Theme.SURFACE, pady=0)
        header.pack(fill="x")
        inner_h = tk.Frame(header, bg=Theme.SURFACE)
        inner_h.pack(fill="x", padx=24, pady=12)
        title_frame = tk.Frame(inner_h, bg=Theme.SURFACE)
        title_frame.pack(side="left")
        tk.Label(title_frame, text="✦ AURORA", fg=Theme.ACCENT,
                 bg=Theme.SURFACE, font=("Helvetica", 22, "bold")).pack(side="left")
        tk.Label(title_frame, text="  Task Manager", fg=Theme.TEXT_MUTED,
                 bg=Theme.SURFACE, font=("Helvetica", 14)).pack(side="left", pady=4)
        RoundedButton(inner_h, text="+ New Task", command=self._open_add_dialog,
                      bg=Theme.ACCENT, width=130, height=38, font_size=12).pack(side="right")

        # Stats
        self._stats = StatsPanel(self.root)
        self._stats.pack(fill="x", padx=16, pady=(10, 0))

        # Filter bar
        fbar = tk.Frame(self.root, bg=Theme.SURFACE, pady=0)
        fbar.pack(fill="x", padx=16, pady=8)
        inner_f = tk.Frame(fbar, bg=Theme.SURFACE)
        inner_f.pack(fill="x", padx=8, pady=8)

        # Search
        self._search_entry = GlowEntry(inner_f, placeholder="Search tasks…", width=22)
        self._search_entry.pack(side="left", padx=(0, 10))
        self._search_entry.bind_entry("<KeyRelease>", self._on_search)

        # Status filter
        tk.Label(inner_f, text="Status:", fg=Theme.TEXT_MUTED, bg=Theme.SURFACE,
                 font=("Helvetica", 10)).pack(side="left")
        self._status_var = tk.StringVar(value="All")
        for val in ["All", "Pending", "Done"]:
            rb = tk.Radiobutton(inner_f, text=val, variable=self._status_var, value=val,
                                command=self._on_filter_change,
                                bg=Theme.SURFACE, fg=Theme.TEXT, selectcolor=Theme.SURFACE2,
                                activebackground=Theme.SURFACE, activeforeground=Theme.ACCENT,
                                font=("Helvetica", 10))
            rb.pack(side="left", padx=4)

        # Category filter
        tk.Label(inner_f, text="  Cat:", fg=Theme.TEXT_MUTED, bg=Theme.SURFACE,
                 font=("Helvetica", 10)).pack(side="left")
        self._cat_filter_var = tk.StringVar(value="All")
        cat_cb = ttk.Combobox(inner_f, textvariable=self._cat_filter_var,
                              values=["All"] + CATEGORIES, state="readonly", width=9)
        cat_cb.pack(side="left", padx=4)
        cat_cb.bind("<<ComboboxSelected>>", self._on_filter_change)

        # Priority filter
        tk.Label(inner_f, text="  Pri:", fg=Theme.TEXT_MUTED, bg=Theme.SURFACE,
                 font=("Helvetica", 10)).pack(side="left")
        self._pri_filter_var = tk.StringVar(value="All")
        pri_cb = ttk.Combobox(inner_f, textvariable=self._pri_filter_var,
                              values=["All"] + list(PRIORITIES.keys()), state="readonly", width=8)
        pri_cb.pack(side="left", padx=4)
        pri_cb.bind("<<ComboboxSelected>>", self._on_filter_change)

        # Clear done
        RoundedButton(inner_f, text="Clear Done", command=self._clear_done,
                      bg=Theme.DANGER, width=110, height=30, font_size=9).pack(side="right")

        # Scrollable list
        container = tk.Frame(self.root, bg=Theme.BG)
        container.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self._canvas = tk.Canvas(container, bg=Theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                  command=self._canvas.yview)
        self._list_frame = tk.Frame(self._canvas, bg=Theme.BG)
        self._list_frame.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.create_window((0, 0), window=self._list_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=scrollbar.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Empty state label
        self._empty_label = tk.Label(self._list_frame, text="",
                                     fg=Theme.TEXT_MUTED, bg=Theme.BG,
                                     font=("Helvetica", 14))

        # Footer
        footer = tk.Frame(self.root, bg=Theme.SURFACE)
        footer.pack(fill="x")
        today_str = date.today().strftime("%A, %B %d %Y")
        tk.Label(footer, text=f"  {today_str}", fg=Theme.TEXT_MUTED,
                 bg=Theme.SURFACE, font=("Helvetica", 9)).pack(side="left", pady=6)
        tk.Label(footer, text="Aurora Task Manager  ✦  ", fg=Theme.TEXT_MUTED,
                 bg=Theme.SURFACE, font=("Helvetica", 9)).pack(side="right", pady=6)

    # ──────────────────── LOGIC ────────────────────
    def _filtered_todos(self) -> List[Todo]:
        todos = list(self._todos)
        s = self._search_entry.get().strip().lower()
        if s:
            todos = [t for t in todos if s in t.title.lower() or s in t.note.lower()]
        status = self._status_var.get()
        if status == "Done":
            todos = [t for t in todos if t.done]
        elif status == "Pending":
            todos = [t for t in todos if not t.done]
        cat = self._cat_filter_var.get()
        if cat != "All":
            todos = [t for t in todos if t.category == cat]
        pri = self._pri_filter_var.get()
        if pri != "All":
            todos = [t for t in todos if t.priority == pri]
        # Sort: pending high → medium → low, then done
        pri_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        todos.sort(key=lambda t: (t.done, pri_order.get(t.priority, 1)))
        return todos

    def _refresh(self):
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._stats.update_stats(self._todos)
        todos = self._filtered_todos()
        if not todos:
            msg = "No tasks yet — add one above! ✦" if not self._todos else "No tasks match the filter."
            tk.Label(self._list_frame, text=msg, fg=Theme.TEXT_MUTED, bg=Theme.BG,
                     font=("Helvetica", 14)).pack(pady=60)
            return
        for i, todo in enumerate(todos):
            card = TodoCard(self._list_frame, todo,
                            on_toggle=self._toggle_todo,
                            on_delete=self._delete_todo,
                            on_edit=self._open_edit_dialog)
            card.pack(fill="x", padx=4, pady=(0, 2))
            sep = tk.Frame(self._list_frame, bg=Theme.BORDER, height=1)
            sep.pack(fill="x", padx=4)
        save_todos(self._todos)

    def _on_search(self, event=None):
        self._refresh()

    def _on_filter_change(self, event=None):
        self._refresh()

    def _toggle_todo(self, todo_id: int):
        for t in self._todos:
            if t.id == todo_id:
                t.done = not t.done
                msg = "Task completed! 🎉" if t.done else "Task reopened"
                Toast(self.root, msg, kind="success" if t.done else "info")
                break
        self._refresh()

    def _delete_todo(self, todo_id: int):
        if messagebox.askyesno("Delete Task", "Delete this task permanently?",
                               parent=self.root):
            self._todos = [t for t in self._todos if t.id != todo_id]
            Toast(self.root, "Task deleted", kind="error")
            self._refresh()

    def _clear_done(self):
        done_count = sum(1 for t in self._todos if t.done)
        if done_count == 0:
            Toast(self.root, "No completed tasks to clear", kind="info")
            return
        if messagebox.askyesno("Clear Done", f"Remove {done_count} completed task(s)?",
                               parent=self.root):
            self._todos = [t for t in self._todos if not t.done]
            Toast(self.root, f"Cleared {done_count} tasks", kind="success")
            self._refresh()

    def _open_add_dialog(self):
        TodoDialog(self.root, on_save=self._save_new_todo)

    def _save_new_todo(self, title, priority, category, due, note):
        todo = Todo(id=self._next_id, title=title, priority=priority,
                    category=category, due=due, note=note)
        self._next_id += 1
        self._todos.append(todo)
        Toast(self.root, "Task added ✦", kind="success")
        self._refresh()

    def _open_edit_dialog(self, todo_id: int):
        todo = next((t for t in self._todos if t.id == todo_id), None)
        if todo:
            TodoDialog(self.root, on_save=lambda *a: self._save_edit(todo_id, *a), todo=todo)

    def _save_edit(self, todo_id, title, priority, category, due, note):
        for t in self._todos:
            if t.id == todo_id:
                t.title, t.priority, t.category = title, priority, category
                t.due, t.note = due, note
                break
        Toast(self.root, "Task updated", kind="info")
        self._refresh()

# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    AuroraApp()
