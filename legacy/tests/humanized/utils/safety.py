"""Safety utilities for UI automation - allows user to interrupt."""

import platform
import time

# Try multiple methods for keyboard interrupt detection
KEYBOARD_METHOD = None

# Method 1: pynput (cross-platform, works even when GUI has focus, no admin needed)
# Prefer this as it's more reliable on Windows without admin rights
try:
    from pynput import keyboard as pynput_keyboard

    # Global listener for any key press
    _esc_pressed = False
    _listener = None


    def _on_press(key):
        global _esc_pressed
        # Any key press will trigger stop
        try:
            _esc_pressed = True
        except:
            pass


    # Start listener in daemon mode so it doesn't block program exit
    # DISABLED: pynput listener causes hangs/timeouts on Windows
    # TODO: Fix keyboard interrupt detection
    _listener = None
    KEYBOARD_METHOD = None
except ImportError:
    pass
except Exception:
    pass

# Method 2: keyboard module (works on Windows/Linux/Mac, but may need admin on Windows)
# Use hook-based approach for better reliability
if KEYBOARD_METHOD is None:
    try:
        import keyboard

        _keyboard_esc_pressed = False


        def _keyboard_on_any_key(event):
            global _keyboard_esc_pressed
            # Any key press will trigger stop (not just ESC)
            _keyboard_esc_pressed = True


        # Try to hook any key press
        try:
            keyboard.on_press(_keyboard_on_any_key)
            KEYBOARD_METHOD = 'keyboard'
        except:
            # keyboard might need admin rights, skip it
            pass
    except ImportError:
        pass

# Method 3: msvcrt (Windows only, only works when console has focus)
if KEYBOARD_METHOD is None and platform.system() == 'Windows':
    try:
        import msvcrt

        KEYBOARD_METHOD = 'msvcrt'
    except ImportError:
        pass

try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


def check_user_interrupt(main_window_bounds=None):
    """
    Check if user wants to interrupt (mouse outside main window or mouse in corner).
    Raises KeyboardInterrupt if user wants to stop.
    
    Args:
        main_window_bounds: Tuple of (left, top, width, height) for main app window.
                          If None, only corner check is performed.
    
    TODO: Keyboard interrupt (any key press) is not working reliably on Windows.
          Currently only mouse-based interrupts work:
          - Mouse in screen corner (FAILSAFE)
          - Mouse outside main application window
    """
    # TODO: Keyboard interrupt - not working reliably on Windows
    # Check if any key was pressed using available method
    # if KEYBOARD_METHOD == 'keyboard':
    #     try:
    #         global _keyboard_esc_pressed
    #         if _keyboard_esc_pressed:
    #             _keyboard_esc_pressed = False
    #             raise KeyboardInterrupt("User pressed a key to stop")
    #     except KeyboardInterrupt:
    #         raise
    #     except Exception:
    #         pass  # Ignore errors
    # elif KEYBOARD_METHOD == 'msvcrt':
    #     try:
    #         import msvcrt
    #         if msvcrt.kbhit():
    #             key = msvcrt.getch()
    #             # Any key press will trigger stop (not just ESC)
    #             raise KeyboardInterrupt("User pressed a key to stop")
    #     except KeyboardInterrupt:
    #         raise
    #     except Exception:
    #         pass
    # elif KEYBOARD_METHOD == 'pynput':
    #     try:
    #         global _esc_pressed, _listener
    #         # Check if any key was pressed
    #         if _esc_pressed:
    #             _esc_pressed = False
    #             raise KeyboardInterrupt("User pressed a key to stop")
    #         # Also check if listener is still running, restart if needed
    #         if _listener and not _listener.running:
    #             try:
    #                 from pynput import keyboard as pynput_keyboard
    #                 _listener = pynput_keyboard.Listener(on_press=_on_press, daemon=True)
    #                 _listener.start()
    #             except:
    #                 pass
    #     except KeyboardInterrupt:
    #         raise
    #     except Exception:
    #         pass

    # Mouse-based interrupt checks
    if PYAUTOGUI_AVAILABLE and pyautogui.FAILSAFE:
        try:
            # Get mouse position
            x, y = pyautogui.position()
            screen_width, screen_height = pyautogui.size()

            # Check 1: Mouse in any corner (FAILSAFE zone)
            corner_size = 10
            in_corner = (
                    (x < corner_size and y < corner_size) or  # Top-left
                    (x >= screen_width - corner_size and y < corner_size) or  # Top-right
                    (x < corner_size and y >= screen_height - corner_size) or  # Bottom-left
                    (x >= screen_width - corner_size and y >= screen_height - corner_size)  # Bottom-right
            )

            if in_corner:
                raise KeyboardInterrupt("Mouse moved to corner (FAILSAFE triggered)")

            # Check 2: Mouse outside main application window
            if main_window_bounds is not None:
                win_left, win_top, win_width, win_height = main_window_bounds
                win_right = win_left + win_width
                win_bottom = win_top + win_height

                # Check if mouse is outside main window
                outside_window = (
                        x < win_left or x > win_right or
                        y < win_top or y > win_bottom
                )

                if outside_window:
                    # But check if it's in a dialog window (Add Item dialog, etc.)
                    # Only check dialogs occasionally to avoid performance issues
                    # Cache dialog check result for a short time
                    import time
                    if not hasattr(check_user_interrupt, '_last_dialog_check'):
                        check_user_interrupt._last_dialog_check = 0
                        check_user_interrupt._cached_dialogs = []

                    current_time = time.time()
                    # Re-check dialogs every 0.5 seconds
                    if current_time - check_user_interrupt._last_dialog_check > 0.5:
                        try:
                            import pygetwindow as gw
                            dialog_windows = gw.getWindowsWithTitle("Add Item")
                            check_user_interrupt._cached_dialogs = []
                            for dialog in dialog_windows:
                                try:
                                    d_left = dialog.left
                                    d_top = dialog.top
                                    d_width = dialog.width if hasattr(dialog, 'width') else 0
                                    d_height = dialog.height if hasattr(dialog, 'height') else 0
                                    if d_width > 0 and d_height > 0:
                                        check_user_interrupt._cached_dialogs.append({
                                            'left': d_left,
                                            'top': d_top,
                                            'right': d_left + d_width,
                                            'bottom': d_top + d_height
                                        })
                                except:
                                    pass
                            check_user_interrupt._last_dialog_check = current_time
                        except:
                            check_user_interrupt._cached_dialogs = []

                    # Check if mouse is in any cached dialog
                    in_dialog = False
                    for dialog in check_user_interrupt._cached_dialogs:
                        if (dialog['left'] <= x <= dialog['right'] and
                                dialog['top'] <= y <= dialog['bottom']):
                            in_dialog = True
                            break

                    # If mouse is outside main window and not in dialog, stop
                    if not in_dialog:
                        raise KeyboardInterrupt("Mouse moved outside application window")
        except KeyboardInterrupt:
            raise
        except Exception:
            pass  # Ignore other errors


def safe_sleep(duration: float, main_window_bounds=None):
    """
    Sleep with periodic interrupt checks.
    Allows user to stop by moving mouse outside window or to corner.
    
    Args:
        duration: Sleep duration in seconds
        main_window_bounds: Tuple of (left, top, width, height) for main app window
    """
    check_interval = 0.1  # Check every 100ms
    elapsed = 0.0

    while elapsed < duration:
        check_user_interrupt(main_window_bounds)
        sleep_time = min(check_interval, duration - elapsed)
        time.sleep(sleep_time)
        elapsed += sleep_time
