"""
Simple test using alternative notification capture methods
"""
import time
import ctypes
from ctypes import wintypes
import win32gui
import win32con

# Windows constants
WM_DWMCOLORIZATIONCOLORCHANGED = 0x0320

class NotificationMonitor:
    def __init__(self):
        self.notifications = []
        
    def enum_windows_callback(self, hwnd, lParam):
        """Callback for enumerating windows"""
        if win32gui.IsWindowVisible(hwnd):
            class_name = win32gui.GetClassName(hwnd)
            window_text = win32gui.GetWindowText(hwnd)
            
            # Look for toast notifications
            if class_name in ['Windows.UI.Core.CoreWindow', 'ToastChildWindowClass', 'Shell_ToastWnd']:
                if window_text and window_text not in ['Windows 入力エクスペリエンス', '設定', 'Program Manager']:
                    print(f"\n[POTENTIAL NOTIFICATION]")
                    print(f"  Class: {class_name}")
                    print(f"  Title: {window_text}")
                    
                    # Try to get more info
                    try:
                        rect = win32gui.GetWindowRect(hwnd)
                        print(f"  Position: {rect}")
                        
                        # Check if it's in notification area (typically top-right)
                        screen_width = win32gui.GetSystemMetrics(0)
                        if rect[0] > screen_width - 500:
                            print("  ✓ In notification area!")
                            self.notifications.append({
                                'hwnd': hwnd,
                                'class': class_name,
                                'text': window_text,
                                'rect': rect
                            })
                    except:
                        pass
        return True
    
    def check_notifications(self):
        """Check for notifications"""
        self.notifications = []
        win32gui.EnumWindows(self.enum_windows_callback, None)
        return self.notifications

print("=== Simple Notification Monitor ===")
print("This will monitor for Windows toast notifications")
print("Try triggering a notification (e.g., from Slack)")
print("Press Ctrl+C to stop\n")

monitor = NotificationMonitor()
last_count = 0

try:
    while True:
        notifications = monitor.check_notifications()
        if len(notifications) != last_count:
            print(f"\nFound {len(notifications)} potential notifications")
            last_count = len(notifications)
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopped")