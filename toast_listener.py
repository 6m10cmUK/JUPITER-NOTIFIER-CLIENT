#!/usr/bin/env python3
"""
Windows Toast Notification Listener
Alternative approach using Windows 10 Toast library
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
        from win10toast import ToastNotifier
        import psutil
        import win32gui
        import win32con
        import win32api
        import win32process
    except ImportError as e:
        print(f"Error: {e}")
        print("\nPlease install required packages:")
        print("pip install win10toast")
        print("pip install psutil")
        print("pip install pywin32")
        sys.exit(1)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ToastListener:
    def __init__(self, ws_url="ws://localhost:8080"):
        self.ws_url = ws_url
        self.ws = None
        self.running = False
        self.notification_queue = queue.Queue()
        self.last_titles = []  # Store recent notification titles
        
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
                
        # Check if Slack notification
        is_slack = "slack" in app_name.lower() or "slack" in title.lower()
        
        notification_data = {
            "type": "notification",
            "title": title,
            "message": message,
            "sender": f"Windows ({app_name})",
            "source": "toast_listener",
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
    
    def find_notification_windows(self):
        """Find notification windows using Win32 API"""
        notifications = []
        
        def enum_windows_callback(hwnd, lparam):
            try:
                # Get window class name
                class_name = win32gui.GetClassName(hwnd)
                
                # Check for notification-related classes
                if any(name in class_name.lower() for name in ['toast', 'notification', 'windows.ui.core']):
                    # Get window text
                    window_text = win32gui.GetWindowText(hwnd)
                    
                    if window_text and win32gui.IsWindowVisible(hwnd):
                        # Get process info
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        
                        try:
                            process = psutil.Process(pid)
                            app_name = process.name()
                            
                            # Store notification info
                            notifications.append({
                                'app': app_name,
                                'title': window_text,
                                'class': class_name
                            })
                        except:
                            pass
            except:
                pass
            
            return True
        
        # Enumerate all windows
        win32gui.EnumWindows(enum_windows_callback, None)
        
        return notifications
    
    def monitor_active_window(self):
        """Monitor active window for notification popups"""
        try:
            # Get foreground window
            hwnd = win32gui.GetForegroundWindow()
            
            if hwnd:
                # Get window title
                window_title = win32gui.GetWindowText(hwnd)
                
                # Get process info
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                
                try:
                    process = psutil.Process(pid)
                    app_name = process.name()
                    
                    # Check if it's a notification from known apps
                    notification_apps = ['slack.exe', 'teams.exe', 'outlook.exe', 'discord.exe']
                    
                    if app_name.lower() in notification_apps:
                        # Check if this is a new notification
                        if window_title and window_title not in self.last_titles:
                            self.last_titles.append(window_title)
                            
                            # Keep only last 20 titles
                            if len(self.last_titles) > 20:
                                self.last_titles = self.last_titles[-20:]
                            
                            # Queue notification
                            self.notification_queue.put({
                                'app_name': app_name,
                                'title': window_title,
                                'message': f"New notification from {app_name}"
                            })
                except:
                    pass
        except:
            pass
    
    def check_slack_process(self):
        """Check if Slack is running and monitor its activity"""
        slack_found = False
        
        for process in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if 'slack' in process.info['name'].lower():
                    slack_found = True
                    
                    # Check CPU usage spike (might indicate new notification)
                    if process.info['cpu_percent'] > 5:
                        logger.debug(f"Slack activity detected: CPU {process.info['cpu_percent']}%")
            except:
                pass
        
        return slack_found
    
    def monitor_loop_sync(self):
        """Synchronous monitoring loop"""
        logger.info("Starting synchronous monitor loop...")
        
        while self.running:
            try:
                # Check for notification windows
                notifications = self.find_notification_windows()
                
                for notif in notifications:
                    if notif['title'] not in self.last_titles:
                        self.last_titles.append(notif['title'])
                        
                        # Queue notification
                        self.notification_queue.put({
                            'app_name': notif['app'],
                            'title': notif['title'],
                            'message': f"Notification from {notif['app']}"
                        })
                
                # Monitor active window
                self.monitor_active_window()
                
                # Check Slack process
                self.check_slack_process()
                
                # Small delay
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(5)
    
    async def process_queue(self):
        """Process notification queue"""
        while self.running:
            try:
                # Check queue for notifications
                while not self.notification_queue.empty():
                    try:
                        notif = self.notification_queue.get_nowait()
                        await self.send_notification(
                            notif['app_name'],
                            notif['title'],
                            notif['message']
                        )
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
            "Toast Listener",
            "Monitor Started",
            "Monitoring Windows notifications"
        )
        
        # Start synchronous monitor in thread
        monitor_thread = threading.Thread(target=self.monitor_loop_sync)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            # Process queue asynchronously
            await self.process_queue()
        except KeyboardInterrupt:
            logger.info("Stopping monitor...")
        finally:
            self.running = False
            if self.ws:
                await self.ws.close()

def main():
    """Main entry point"""
    print("=== Windows Toast Notification Listener ===")
    print("Alternative approach using Win32 API")
    print("\nRequirements:")
    print("- Windows 10/11")
    print("- Discord bot running on port 8080")
    print("- Slack desktop app (for Slack notifications)")
    print("\nNote: This monitors window titles and processes")
    print("Some notifications might be missed or duplicated")
    print("\nPress Ctrl+C to stop\n")
    
    # Check platform
    if sys.platform != 'win32':
        print("Error: This program only works on Windows")
        return
    
    # Start monitor
    monitor = ToastListener()
    
    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        print("\nStopping...")

if __name__ == "__main__":
    main()