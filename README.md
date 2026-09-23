# Color Grabber

A lightweight Windows background app: press **Ctrl+Alt+C** anywhere and it
saves the color of the pixel under your cursor (hex + RGB), along with which
app and window it was grabbed from. No tray icon - it runs entirely in the
background, reachable through global keyboard shortcuts and a Start menu
shortcut.

## Shortcuts

| Combo          | What it does                                        |
|----------------|------------------------------------------------------|
| `Ctrl+Alt+C`   | Save the color at the current cursor position         |
| `Ctrl+Alt+V`   | Open the saved colors window                          |
| `Ctrl+Alt+Q`   | Hide the window (same as the X button - does NOT quit) |

## Quick install (recommended)

**Option A - just download it:** grab the latest `ColorGrabber.exe` from the
[Releases page](../../releases) - no Python required. Then optionally run
`create_shortcut.ps1` (see step 5 below) for a Start menu entry.

**Option B - install from source, one command:**

Requires Python 3.10+ ([python.org](https://python.org), not the Microsoft
Store version).

```
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

This creates a virtual environment, installs dependencies, builds
`ColorGrabber.exe` and adds a Start menu shortcut - all in one go. See below
for what each step does individually, and for autostart-on-login setup.

## 1. Manual install

```
pip install -r requirements.txt
```

If `pip` doesn't run directly (e.g. blocked by "Device Guard" or a similar
policy), try: `python -m pip install -r requirements.txt`.

## 2. Running during development

> **Important:** the `keyboard` package needs admin rights on Windows for
> the global hotkey listener, so launch it from a terminal opened with
> "Run as administrator".

```
python main.py
```

Without any flag the window shows immediately. To start it hidden (running
only in the background), add the `--hidden` flag:

```
python main.py --hidden
```

If the app is already running in the background and you launch it again
(with or without `--hidden`), the new launch attempt doesn't open a second
instance - it just brings the existing window to the front and exits.

When you press `Ctrl+Alt+C`, the app:
1. reads the cursor position and the pixel color underneath it,
2. reads the title of the currently active window and its owning app name,
3. flashes a short, fading bubble next to the cursor with the hex code
   (quick visual feedback),
4. saves all of this to `%APPDATA%\ColorGrabber\colors.json`,
5. refreshes the window if it's currently open.

Closing the window (X button) does NOT quit the app, it just hides it - the
app keeps running in the background. `Ctrl+Alt+Q` does the same. To actually
quit, use the red "Exit" button inside the window.

## 3. Changing the shortcuts

`colorgrab/hotkey.py` has three constants (`DEFAULT_HOTKEY`,
`SHOW_WINDOW_HOTKEY`, `QUIT_HOTKEY`) - any of them can be changed to any
combo supported by the `keyboard` package.

## 4. Building a standalone .exe

```
pyinstaller --noconfirm --onefile --windowed --name ColorGrabber --icon assets\icon.ico main.py
```

The finished .exe is created at `dist\ColorGrabber.exe`, already carrying
its own eyedropper icon.

Pushing a tag like `v1.0.0` also triggers a GitHub Actions workflow
(`.github/workflows/build.yml`) that builds this exe on a Windows runner and
attaches it to a GitHub Release automatically.

## 5. Start menu shortcut

Doesn't require admin rights:

```
powershell -ExecutionPolicy Bypass -File .\create_shortcut.ps1
```

This creates a "Color Grabber" shortcut in the Start menu. If the app is
already running in the background (e.g. via autostart), clicking it just
brings the existing window forward - it doesn't start a second instance.

## 6. Autostart on login

Since the app needs admin rights (for the global hotkey), the plain
"Startup" folder isn't enough - it wouldn't launch with elevated rights, so
the hotkey wouldn't work. Instead, this sets up a Task Scheduler entry that
silently starts the app (hidden, with `--hidden`) with admin rights, with no
UAC prompt.

**Steps:**

1. Build the .exe first (see step 4).
2. Open PowerShell **as administrator** (Start menu → type "PowerShell" →
   right-click → "Run as administrator").
3. cd into the project folder, then run:

```
powershell -ExecutionPolicy Bypass -File .\setup_autostart.ps1
```

This creates a "ColorGrabber" entry in Task Scheduler that automatically
starts the app, hidden, with admin rights, on every logon - from then on,
`Ctrl+Alt+V` or the Start menu shortcut brings up the window whenever you
need it.

**Uninstall** (if you no longer want it to start automatically):

```
powershell -ExecutionPolicy Bypass -File .\uninstall_autostart.ps1
```

Check/manage manually: Start menu → "Task Scheduler" → "Task Scheduler
Library" → look for the "ColorGrabber" entry.

## 7. Project structure

```
main.py                       - entry point: single-instance check, hotkeys, GUI
gui.py                        - CustomTkinter window, color list, flash animation
colorgrab/
  grabber.py                  - reads the pixel color at the cursor position
  context.py                  - gets the active window / source app name
  hotkey.py                   - registers the global keyboard shortcuts
  storage.py                  - saves/loads colors to/from a JSON file
  singleton.py                 - single-instance enforcement + "show window" signal
  icon.py                       - draws the eyedropper icon from code (PIL)
assets/
  icon.ico                       - pre-generated icon for the .exe build
install.ps1                       - one-command setup (venv, deps, build, shortcut)
setup_autostart.ps1                - sets up autostart (admin required)
uninstall_autostart.ps1             - removes autostart (admin required)
create_shortcut.ps1                  - creates the Start menu shortcut (no admin needed)
.github/workflows/build.yml           - builds the exe and publishes a GitHub Release on tag push
```

## Known limitations / ideas for further work

- The `keyboard` package can look suspicious to some antivirus/EDR software
  (it uses a low-level keyboard hook) - if that's an issue,
  `pynput.keyboard.GlobalHotKeys` is an alternative.
- Currently only saves a single pixel's color; easy to extend to average a
  small square (e.g. 5x5 px) for a less "noisy" result.
- Exporting (e.g. `.ase` Adobe Swatch Exchange, or a `.css`/`.txt` list) can
  easily be added to `gui.py` with a new button.
- The source window name can sometimes return "Unknown" for system windows -
  thanks to the error handling in `context.py` this doesn't stop the save,
  it just leaves the source info empty.

## License

MIT - see [LICENSE](LICENSE).
