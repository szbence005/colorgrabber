"""
ColorGrabber main window: lists saved colors, lets you copy the hex code
or delete an entry, and shows the active keyboard shortcuts.
"""
import queue
import keyboard
import pyperclip
import customtkinter as ctk

from colorgrab import storage, singleton
from colorgrab.hotkey import DEFAULT_HOTKEY, SHOW_WINDOW_HOTKEY, QUIT_HOTKEY

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT = "#2E8AE6"
ACCENT_HOVER = "#2571C4"
SURFACE = "#1E1F22"
SURFACE_ALT = "#26282C"
BORDER = "#33353A"
TEXT_MUTED = "#9BA1AA"
DANGER = "#8A2E2E"
DANGER_HOVER = "#6E2424"


def _contrasting_text_color(hex_color: str) -> str:
    """Returns black or white, whichever reads better on the given background color."""
    h = hex_color.lstrip("#")
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except (ValueError, IndexError):
        return "#FFFFFF"
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#1A1A1A" if luminance > 150 else "#FFFFFF"


def _format_hotkey(hotkey: str) -> str:
    """"ctrl+alt+c" -> "Ctrl + Alt + C" """
    return " + ".join(part.capitalize() for part in hotkey.split("+"))


class FlashOverlay(ctk.CTkToplevel):
    """
    Short, fading bubble that appears next to the cursor when a color is
    grabbed, showing the saved hex code - quick visual feedback. Doesn't
    steal focus, and disappears on its own after a fraction of a second.
    """

    def __init__(self, master, x: int, y: int, hex_color: str):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        try:
            self.attributes("-alpha", 0.0)
        except Exception:
            pass

        width, height = 104, 42
        self.geometry(f"{width}x{height}+{x + 18}+{y + 18}")
        self.configure(fg_color=hex_color)

        label = ctk.CTkLabel(
            self,
            text=hex_color,
            text_color=_contrasting_text_color(hex_color),
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        label.place(relx=0.5, rely=0.5, anchor="center")

        self._alpha = 0.0
        self.after(0, self._fade_in)

    def _fade_in(self):
        self._alpha = min(1.0, self._alpha + 0.25)
        try:
            self.attributes("-alpha", self._alpha)
        except Exception:
            self.destroy()
            return
        if self._alpha < 1.0:
            self.after(12, self._fade_in)
        else:
            self.after(450, self._fade_out)

    def _fade_out(self):
        self._alpha = max(0.0, self._alpha - 0.18)
        try:
            self.attributes("-alpha", self._alpha)
        except Exception:
            self.destroy()
            return
        if self._alpha > 0.0:
            self.after(12, self._fade_out)
        else:
            self.destroy()


class HotkeyBadge(ctk.CTkFrame):
    """Small pill showing one action and the key combo that triggers it."""

    def __init__(self, master, action: str, hotkey: str):
        super().__init__(master, corner_radius=10, fg_color=SURFACE_ALT,
                          border_width=1, border_color=BORDER)
        self.grid_columnconfigure(0, weight=1)

        action_label = ctk.CTkLabel(
            self, text=action.upper(), font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_MUTED,
        )
        action_label.pack(anchor="w", padx=12, pady=(8, 0))

        key_label = ctk.CTkLabel(
            self, text=_format_hotkey(hotkey),
            font=ctk.CTkFont(size=13, weight="bold"), text_color=ACCENT,
        )
        key_label.pack(anchor="w", padx=12, pady=(0, 8))


class ColorRow(ctk.CTkFrame):
    """One row in the list: swatch + hex code + timestamp + buttons."""

    def __init__(self, master, entry: dict, index: int, on_delete, **kwargs):
        super().__init__(master, corner_radius=10, fg_color=SURFACE_ALT,
                          border_width=1, border_color=BORDER)
        self.entry = entry
        self.index = index
        self.on_delete = on_delete

        self.grid_columnconfigure(1, weight=1)

        swatch = ctk.CTkLabel(
            self, text="", width=44, height=44, corner_radius=8,
            fg_color=entry["hex"],
        )
        swatch.grid(row=0, column=0, padx=(10, 14), pady=10)

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="w", pady=10)

        hex_label = ctk.CTkLabel(
            info_frame, text=entry["hex"], font=ctk.CTkFont(size=15, weight="bold")
        )
        hex_label.pack(anchor="w")

        rgb_text = "RGB({}, {}, {})".format(*entry["rgb"])
        meta_label = ctk.CTkLabel(
            info_frame,
            text=f"{rgb_text}   ·   {entry['timestamp']}",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
        )
        meta_label.pack(anchor="w")

        app_name = entry.get("app_name", "Unknown")
        window_title = entry.get("window_title", "")
        source_text = f"📍 {app_name}"
        if window_title:
            source_text += f" — {window_title}"
        source_label = ctk.CTkLabel(
            info_frame,
            text=source_text,
            font=ctk.CTkFont(size=11),
            text_color="#6FA8DC",
            wraplength=250,
            justify="left",
            anchor="w",
        )
        source_label.pack(anchor="w")

        copy_btn = ctk.CTkButton(
            self, text="Copy", width=80, fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=self._copy,
        )
        copy_btn.grid(row=0, column=2, padx=6, pady=10)

        delete_btn = ctk.CTkButton(
            self, text="Delete", width=70, fg_color=DANGER,
            hover_color=DANGER_HOVER, command=self._delete
        )
        delete_btn.grid(row=0, column=3, padx=(0, 10), pady=10)

    def _copy(self):
        pyperclip.copy(self.entry["hex"])

    def _delete(self):
        self.on_delete(self.index)


class ColorGrabberApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Color Grabber")
        self.geometry("480x620")
        self.minsize(380, 340)
        self.configure(fg_color=SURFACE)

        self.event_queue: "queue.Queue[dict]" = queue.Queue()
        self.command_queue: "queue.Queue[str]" = queue.Queue()

        # --- Header -------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(18, 6))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame, text="🎨 Color Grabber",
            font=ctk.CTkFont(size=19, weight="bold"),
        )
        title_label.grid(row=0, column=0, sticky="w")

        quit_btn = ctk.CTkButton(
            header_frame, text="Exit", width=70, fg_color=DANGER,
            hover_color=DANGER_HOVER, command=self._real_quit,
        )
        quit_btn.grid(row=0, column=1, sticky="e")

        subheader = ctk.CTkLabel(
            self,
            text="Press a shortcut anywhere on your screen — no need to focus this window.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
            wraplength=440,
            justify="left",
        )
        subheader.pack(fill="x", padx=16, pady=(0, 12), anchor="w")

        # --- Hotkeys strip -------------------------------------------
        hotkeys_frame = ctk.CTkFrame(self, fg_color="transparent")
        hotkeys_frame.pack(fill="x", padx=16, pady=(0, 14))
        hotkeys_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="hk")

        HotkeyBadge(hotkeys_frame, "Grab color", DEFAULT_HOTKEY).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        HotkeyBadge(hotkeys_frame, "Show window", SHOW_WINDOW_HOTKEY).grid(
            row=0, column=1, sticky="ew", padx=6
        )
        HotkeyBadge(hotkeys_frame, "Hide window", QUIT_HOTKEY).grid(
            row=0, column=2, sticky="ew", padx=(6, 0)
        )

        # --- Saved colors list -----------------------------------------
        list_header = ctk.CTkLabel(
            self, text="Saved colors", font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_MUTED,
        )
        list_header.pack(anchor="w", padx=18, pady=(4, 4))

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text="No colors saved yet.",
            text_color=TEXT_MUTED,
        )

        # Closing the window doesn't quit the app, it just hides it (runs in the background)
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

        self.refresh()
        self.after(200, self._poll_queue)

    def refresh(self):
        """Reloads the saved colors and redraws the list."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        colors = storage.load_colors()

        if not colors:
            self.empty_label = ctk.CTkLabel(
                self.scroll_frame,
                text="No colors saved yet.",
                text_color=TEXT_MUTED,
            )
            self.empty_label.pack(pady=20)
            return

        for i, entry in enumerate(colors):
            row = ColorRow(self.scroll_frame, entry, i, self._delete_by_index)
            row.pack(fill="x", pady=5)

    def _delete_by_index(self, index: int):
        storage.delete_color(index)
        self.refresh()

    def notify_color_grabbed(self, entry: dict):
        """Thread-safe: callable from the hotkey-listener thread, just queues the event."""
        self.event_queue.put(entry)

    def request_show_window(self):
        """Thread-safe: callable from any thread - queues the 'show window' command."""
        self.command_queue.put("show")

    def request_hide_window(self):
        """Thread-safe: callable from any thread - queues the 'hide window' command.
        This does NOT quit the app, it just hides the window (same as the X button)."""
        self.command_queue.put("hide")

    def _poll_queue(self):
        """Runs on the main (GUI) thread - drains queued events, flashes the overlay and refreshes."""
        had_events = False
        while not self.event_queue.empty():
            entry = self.event_queue.get()
            had_events = True
            try:
                FlashOverlay(self, entry["x"], entry["y"], entry["hex"])
            except Exception:
                pass  # the animation should never be allowed to break saving
        if had_events:
            self.refresh()

        # If the Start menu shortcut (or another launch attempt) asked us to
        # show the window, do it now.
        if singleton.consume_show_request():
            self.show_window()

        # The Show/Hide hotkeys run the command from here, on the GUI thread -
        # this is safe, unlike calling into tkinter directly from the
        # hotkey-listener thread.
        while not self.command_queue.empty():
            cmd = self.command_queue.get()
            if cmd == "show":
                self.show_window()
            elif cmd == "hide":
                self.withdraw()

        self.after(50, self._poll_queue)

    def _real_quit(self):
        """Runs on the GUI thread - this is the ACTUAL exit (called by the 'Exit' button):
        stops the hotkey listener, releases the lock, then closes the app."""
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        singleton.release_lock()
        self.destroy()

    def show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()
