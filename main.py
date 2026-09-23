"""
ColorGrabber - entry point.

No tray icon - the app runs as a single background instance, reachable
through the global keyboard shortcuts:

  Ctrl+Alt+C  - save the color under the cursor
  Ctrl+Alt+V  - open the saved colors window
  Ctrl+Alt+Q  - hide the window (does NOT quit the app - same as the X
                button). Use the "Exit" button inside the window to
                actually quit.

The window can also be opened from the Start menu (see create_shortcut.ps1)
- if the app is already running in the background, this just brings the
existing window to the front instead of starting a second instance.

Launch flags:
  --hidden    Starts the window hidden (used by autostart - see
              setup_autostart.ps1). Without it the window shows immediately.
"""
import sys

from colorgrab import storage, singleton
from colorgrab.grabber import grab_color_at_cursor
from colorgrab.context import get_active_window_info
from colorgrab.hotkey import register_hotkey, DEFAULT_HOTKEY, SHOW_WINDOW_HOTKEY, QUIT_HOTKEY
from gui import ColorGrabberApp

app: ColorGrabberApp = None  # type: ignore


def on_hotkey_triggered():
    """Runs when the color-grab hotkey is pressed - on a DIFFERENT thread, not the GUI thread."""
    entry = grab_color_at_cursor()
    context = get_active_window_info()
    saved_entry = storage.add_color(
        entry["hex"], entry["rgb"], entry["x"], entry["y"],
        app_name=context["app_name"], window_title=context["window_title"],
    )
    if app is not None:
        app.notify_color_grabbed(saved_entry)


def on_show_window_hotkey():
    if app is not None:
        app.request_show_window()


def on_quit_hotkey():
    """This no longer quits the app - it only hides the window (like the X button).
    Actually quitting is done via the "Exit" button inside the window."""
    if app is not None:
        app.request_hide_window()


def main():
    global app

    start_hidden = "--hidden" in sys.argv

    if singleton.is_already_running():
        # An instance is already running - just tell it to show itself, then exit.
        singleton.request_show()
        return

    singleton.acquire_lock()

    app = ColorGrabberApp()
    if start_hidden:
        app.withdraw()

    register_hotkey(on_hotkey_triggered, DEFAULT_HOTKEY)
    register_hotkey(on_show_window_hotkey, SHOW_WINDOW_HOTKEY)
    register_hotkey(on_quit_hotkey, QUIT_HOTKEY)

    try:
        app.mainloop()
    finally:
        singleton.release_lock()


if __name__ == "__main__":
    main()
