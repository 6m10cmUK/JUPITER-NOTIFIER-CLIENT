#!/usr/bin/env python3
"""
Background Notification Monitor
Runs continuously in background, monitoring all notifications
"""

import asyncio
import websockets
import json
import logging
import time
from datetime import datetime
import sys
import os
import threading
import queue

# Windows specific imports
if sys.platform == 'win32':
    try:
        import win32gui
        import win32con
        import win32api
        import win32event
        import win32process
        import win32clipboard
        import psutil
        import ctypes
        from ctypes import wintypes
        import pythoncom
        import win32com.client
    except ImportError as e:
        print(f"Error: {e}")
        print("\nPlease install: pip install pywin32 psutil")
        sys.exit(1)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('notification_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

class BackgroundMonitor:
    def __init__(self, ws_url="ws://localhost:8080"):
        self.ws_url = ws_url
        self.ws = None
        self.running = False
        self.notification_queue = queue.Queue()
        self.processed_notifications = set()
        self.known_apps = {
            'slack.exe': 'Slack',
            'teams.exe': 'Microsoft Teams',
            'outlook.exe': 'Outlook',
            'discord.exe': 'Discord',
            'skype.exe': 'Skype',
            'chrome.exe': 'Chrome',
            'firefox.exe': 'Firefox',
            'thunderbird.exe': 'Thunderbird'
        }
        
    async def connect_websocket(self):
        """Connect to WebSocket server"""
        try:
            self.ws = await websockets.connect(self.ws_url)
            logger.info(f"Connected to WebSocket: {self.ws_url}")
            return True
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            return False
    
    async def send_notification(self, app_name, title, message):
        """Send notification to WebSocket server"""
        if not self.ws:
            if not await self.connect_websocket():
                return
                
        # Create unique ID for this notification
        notif_id = f"{app_name}:{title}:{message[:50]}"
        
        # Skip if already processed
        if notif_id in self.processed_notifications:
            return
            
        self.processed_notifications.add(notif_id)
        
        # Clean up old notifications
        if len(self.processed_notifications) > 1000:
            self.processed_notifications = set(list(self.processed_notifications)[-500:])
        
        # Check if Slack notification
        is_slack = "slack" in app_name.lower() or "slack" in title.lower()
        
        notification_data = {
            "type": "notification",
            "title": title,
            "message": message,
            "sender": f"Windows ({app_name})",
            "source": "background_monitor",
            "app": app_name,
            "is_slack": is_slack,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            await self.ws.send(json.dumps(notification_data))
            logger.info(f"Sent: [{app_name}] {title} - {message}")
        except Exception as e:
            logger.error(f"Send error: {e}")
            self.ws = None
    
    def check_notification_area(self):
        """Check Windows notification area for new notifications"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                class_name = win32gui.GetClassName(hwnd)
                
                # Check for notification-related windows
                notification_classes = [
                    'Windows.UI.Core.CoreWindow',
                    'Shell_ToastWnd',
                    'ToastChildWindowClass',
                    'NativeHWNDHost'
                ]
                
                if any(nc in class_name for nc in notification_classes):
                    try:
                        # Get window rectangle
                        rect = win32gui.GetWindowRect(hwnd)
                        screen_width = win32api.GetSystemMetrics(0)
                        screen_height = win32api.GetSystemMetrics(1)
                        
                        # Check if in notification area (bottom-right)
                        if rect[0] > screen_width - 600 and rect[1] > screen_height - 600:
                            # Get window text
                            window_text = win32gui.GetWindowText(hwnd)
                            
                            # Get process info
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            process = psutil.Process(pid)
                            app_name = process.name()
                            
                            # Get all text from window
                            texts = self.get_all_window_text(hwnd)
                            
                            if texts:
                                windows.append({
                                    'app': self.known_apps.get(app_name.lower(), app_name),
                                    'title': texts[0] if texts else window_text,
                                    'message': ' '.join(texts[1:]) if len(texts) > 1 else '',
                                    'hwnd': hwnd
                                })
                    except Exception as e:
                        logger.debug(f"Error processing window: {e}")
            return True
        
        windows = []
        try:
            win32gui.EnumWindows(callback, windows)
        except Exception as e:
            logger.error(f"EnumWindows error: {e}")
            
        return windows
    
    def get_all_window_text(self, hwnd):
        """Extract all text from a window and its children"""
        texts = []
        
        def enum_child_proc(child_hwnd, lparam):
            try:
                # Get window text
                length = win32gui.GetWindowTextLength(child_hwnd)
                if length > 0:
                    text = win32gui.GetWindowText(child_hwnd)
                    if text and text not in texts:
                        texts.append(text)
                
                # Try WM_GETTEXT
                buf_size = 512
                buffer = ctypes.create_unicode_buffer(buf_size)
                result = win32api.SendMessage(child_hwnd, win32con.WM_GETTEXT, buf_size, buffer)
                if result and buffer.value and buffer.value not in texts:
                    texts.append(buffer.value)
                    
            except Exception:
                pass
            return True
        
        # Get main window text
        try:
            main_text = win32gui.GetWindowText(hwnd)
            if main_text:
                texts.append(main_text)
        except:
            pass
            
        # Enumerate child windows
        try:
            win32gui.EnumChildWindows(hwnd, enum_child_proc, None)
        except:
            pass
            
        return texts
    
    def monitor_active_processes(self):
        """Monitor active processes for notification activity"""
        notifications = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    # Check known messaging apps
                    if any(app in proc_name for app in ['slack', 'teams', 'discord', 'skype']):
                        # Check for CPU/memory spikes (might indicate new notification)
                        if proc.info['cpu_percent'] > 5 or proc.info['memory_percent'] > 0.5:
                            logger.debug(f"Activity detected in {proc_name}")
                            
                            # Try to find associated windows
                            def window_callback(hwnd, pid):
                                try:
                                    _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                                    if window_pid == pid and win32gui.IsWindowVisible(hwnd):
                                        texts = self.get_all_window_text(hwnd)
                                        if texts:
                                            notifications.append({
                                                'app': self.known_apps.get(proc_name, proc_name),
                                                'title': texts[0] if texts else proc_name,
                                                'message': ' '.join(texts[1:]) if len(texts) > 1 else 'New activity'
                                            })
                                except:
                                    pass
                                return True
                                
                            win32gui.EnumWindows(window_callback, proc.info['pid'])
                            
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(f"Process monitoring error: {e}")
            
        return notifications
    
    def background_monitor_loop(self):
        """Background monitoring loop"""
        logger.info("Starting background monitor loop...")
        
        last_check = time.time()
        check_interval = 1.0  # Check every second
        
        while self.running:
            try:
                current_time = time.time()
                
                # Regular interval check
                if current_time - last_check >= check_interval:
                    # Check notification area
                    notifications = self.check_notification_area()
                    
                    for notif in notifications:
                        self.notification_queue.put(notif)
                    
                    # Check active processes
                    process_notifications = self.monitor_active_processes()
                    
                    for notif in process_notifications:
                        self.notification_queue.put(notif)
                    
                    last_check = current_time
                
                # Small sleep to prevent CPU overuse
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(1)
    
    async def process_queue(self):
        """Process notification queue"""
        while self.running:
            try:
                # Process all queued notifications
                processed = 0
                while not self.notification_queue.empty() and processed < 10:
                    try:
                        notif = self.notification_queue.get_nowait()
                        await self.send_notification(
                            notif['app'],
                            notif['title'],
                            notif['message']
                        )
                        processed += 1
                    except queue.Empty:
                        break
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(5)
    
    async def start(self):
        """Start monitoring"""
        self.running = True
        
        # Connect to WebSocket
        if not await self.connect_websocket():
            logger.error("Failed to connect to WebSocket")
            return
        
        # Send test notification
        await self.send_notification(
            "Background Monitor",
            "Monitor Started",
            "Background monitoring is active"
        )
        
        # Start background monitor in thread
        monitor_thread = threading.Thread(target=self.background_monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        logger.info("Background monitor is running...")
        logger.info("The program will continue running in the background")
        logger.info("Check notification_monitor.log for activity")
        
        try:
            # Process queue asynchronously
            await self.process_queue()
        except KeyboardInterrupt:
            logger.info("Stopping monitor...")
        finally:
            self.running = False
            if self.ws:
                await self.ws.close()
            logger.info("Monitor stopped")

def main():
    """Main entry point"""
    print("=== Background Notification Monitor ===")
    print("Runs continuously in background")
    print("\nFeatures:")
    print("- Monitors all notification windows")
    print("- Tracks process activity")
    print("- Runs silently in background")
    print("- Logs to notification_monitor.log")
    print("\nThe program will minimize to background after starting")
    print("Press Ctrl+C to stop\n")
    
    # Check platform
    if sys.platform != 'win32':
        print("Error: This program only works on Windows")
        return
    
    # Start monitor
    monitor = BackgroundMonitor()
    
    # Hide console window after 5 seconds
    def hide_console():
        time.sleep(5)
        # Get console window handle
        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')
        
        hWnd = kernel32.GetConsoleWindow()
        if hWnd:
            # Minimize to tray
            user32.ShowWindow(hWnd, 6)  # SW_MINIMIZE
            print("\nMinimized to background. Check notification_monitor.log for activity.")
    
    # Start hide thread
    hide_thread = threading.Thread(target=hide_console)
    hide_thread.daemon = True
    hide_thread.start()
    
    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        print("\nStopping...")

if __name__ == "__main__":
    main()