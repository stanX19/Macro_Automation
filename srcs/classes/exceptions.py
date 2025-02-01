import pyautogui


class GameConnectionError(RuntimeError):
    pass


class BattleLostError(RuntimeError):
    pass


class DomainNotSpecifiedError(KeyError):
    pass


class ScreenCaptureFailedError(OSError):
    pass


# =============================Function overrides===============================
_original_screenshot = pyautogui.screenshot

def _screenshot_with_error():
    try:
        return _original_screenshot()
    except OSError:
        raise ScreenCaptureFailedError()

pyautogui.screenshot = _screenshot_with_error