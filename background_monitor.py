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
        
        # Try to import winrt for notification listener
        WINRT_AVAILABLE = False
        UserNotificationListener = None
        UserNotificationListenerAccessStatus = None
        NotificationKinds = None
        KnownNotificationBindings = None
        ApiInformation = None
        
        try:
            import winrt
            import winrt.windows.ui.notifications.management
            import winrt.windows.ui.notifications
            import winrt.windows.foundation.metadata
            
            WINRT_AVAILABLE = True
            print("WinRT loaded successfully!")
        except Exception as e:
            print(f"WinRT import error: {e}")
            print("Falling back to window monitoring")
            
    except ImportError as e:
        print(f"Error: {e}")
        print("\nPlease install: pip install pywin32 psutil")
        print("For better notification support: pip install winrt-Windows.UI.Notifications.Management")
        sys.exit(1)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Console output
        logging.FileHandler('notification_monitor.log', encoding='utf-8')  # File output
    ]
)
logger = logging.getLogger(__name__)

class BackgroundMonitor:
    def __init__(self, ws_url="wss://site--jupiter-system--6qtwyp8fx6v7.code.run"):
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
        self.slack_only_mode = False  # すべての通知を処理
        self.mention_only_mode = False  # すべての通知を表示
        self.notification_listener = None
        self.use_winrt = WINRT_AVAILABLE
        
    async def connect_websocket(self):
        """Connect to WebSocket server"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.ws = await websockets.connect(self.ws_url)
                logger.info(f"Connected to WebSocket: {self.ws_url}")
                print(f"[Connected] WebSocket server connected successfully")
                return True
            except Exception as e:
                logger.error(f"WebSocket connection error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    print(f"[Retry] Connection failed, retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"[Error] Failed to connect to WebSocket server at {self.ws_url}")
                    print(f"[Error] Make sure Discord bot is running on port 8080")
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
        
        # Filter: Slack only mode
        if self.slack_only_mode and not is_slack:
            return
            
        # Filter: Mention only mode (for Slack)
        if is_slack and self.mention_only_mode:
            # Slackのメンション通知パターン
            mention_patterns = [
                # 英語パターン
                'mentioned you',
                'sent a direct message',
                'replied to your thread',
                'reacted to your message',
                '@channel',
                '@here',
                '@everyone',
                'new message in',
                'dm from',
                
                # 日本語パターン
                'メンション',
                'ダイレクトメッセージ',
                'スレッドに返信',
                'リアクション',
                '返信しました',
                'からメッセージ',
                
                # 一般的なパターン
                ':',  # "username: message" format
                '→',  # Arrow indicating direction
            ]
            
            # タイトルとメッセージを結合してチェック
            full_text = f"{title} {message}".lower()
            
            # DMの場合（タイトルに個人名が含まれる）
            is_dm = not any(indicator in full_text for indicator in ['#', 'channel', 'チャンネル'])
            
            # メンションチェック
            has_mention = any(pattern in full_text for pattern in mention_patterns)
            
            # @記号チェック（より厳密に）
            has_at_mention = '@' in message and not '@' in ['@gmail.com', '@outlook.com']  # メールアドレスを除外
            
            # DMまたはメンション通知の場合のみ処理
            if not (is_dm or has_mention or has_at_mention):
                print(f"\n[SKIPPED] Non-mention/DM Slack notification: {title}")
                return
        
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
            
            # Special formatting for Slack mentions
            if is_slack:
                # 通知タイプを判定
                notification_type = "MENTION"
                if 'direct message' in title.lower() or not '#' in title:
                    notification_type = "DM"
                elif 'thread' in title.lower() or 'スレッド' in title:
                    notification_type = "THREAD"
                elif 'reacted' in title.lower() or 'リアクション' in title:
                    notification_type = "REACTION"
                
                print(f"\n{'='*60}")
                print(f"[SLACK {notification_type}] {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*60}")
                print(f"  From: {title}")
                print(f"  Message: {message}")
                print(f"{'='*60}")
                
                # Also log to file
                with open('slack_mentions.log', 'a', encoding='utf-8') as f:
                    f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {notification_type}\n")
                    f.write(f"From: {title}\n")
                    f.write(f"Message: {message}\n")
                    f.write("-" * 50 + "\n")
            else:
                print(f"\n[NOTIFICATION CAPTURED] {datetime.now().strftime('%H:%M:%S')}")
                print(f"  App: {app_name}")
                print(f"  Title: {title}")
                print(f"  Message: {message}")
                print("-" * 50)
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
                    'NativeHWNDHost',
                    'ApplicationFrameWindow',
                    'Windows.UI.Core.CoreComponentsWindowClass',
                    'Action center',
                    'New notification'
                ]
                
                if any(nc in class_name for nc in notification_classes):
                    try:
                        # Get window rectangle
                        rect = win32gui.GetWindowRect(hwnd)
                        screen_width = win32api.GetSystemMetrics(0)
                        screen_height = win32api.GetSystemMetrics(1)
                        
                        # デバッグ: 検出したウィンドウ情報を表示
                        window_text = win32gui.GetWindowText(hwnd)
                        if window_text:  # テキストがある場合のみ
                            print(f"\n[DEBUG] Found window: {class_name}")
                            print(f"  Text: {window_text}")
                            print(f"  Position: {rect}")
                        
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
        # プロセス監視を無効化（ACTIVITYメッセージを削除）
        return []
    
    def background_monitor_loop(self):
        """Background monitoring loop"""
        logger.info("Starting background monitor loop...")
        
        last_check = time.time()
        last_status = time.time()
        check_interval = 1.0  # Check every second
        status_interval = 120.0  # Status update every 2 minutes
        check_count = 0
        notification_count = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Regular interval check
                if current_time - last_check >= check_interval:
                    # Check notification area
                    notifications = self.check_notification_area()
                    
                    for notif in notifications:
                        self.notification_queue.put(notif)
                    
                    # プロセス監視を削除（ACTIVITYログを防ぐ）
                    # process_notifications = self.monitor_active_processes()
                    # for notif in process_notifications:
                    #     self.notification_queue.put(notif)
                    
                    last_check = current_time
                    check_count += 1
                
                # ステータス表示を削除（コメントアウト）
                # if current_time - last_status >= status_interval:
                #     print(f"\n[STATUS] {datetime.now().strftime('%H:%M:%S')} - Monitoring active (Checks: {check_count})")
                #     last_status = current_time
                
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
    
    async def setup_winrt_listener(self):
        """Setup Windows notification listener using WinRT"""
        if not self.use_winrt:
            return False
            
        try:
            # Import here to avoid global scope issues
            from winrt.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus
            from winrt.windows.ui.notifications import NotificationKinds, KnownNotificationBindings
            from winrt.windows.foundation.metadata import ApiInformation
            
            # Check if UserNotificationListener is supported
            if not ApiInformation.is_type_present("Windows.UI.Notifications.Management.UserNotificationListener"):
                print("UserNotificationListener is not supported on this device.")
                return False
            
            # Get the listener instance
            self.notification_listener = UserNotificationListener.get_current()
            
            # Request access permission
            access_status = await self.notification_listener.request_access_async()
            
            if access_status != UserNotificationListenerAccessStatus.ALLOWED:
                print("Access to UserNotificationListener is not allowed.")
                print("Please enable in: Windows Settings > Privacy > Notifications")
                return False
                
            print("[WINRT] Access granted! Using Windows notification listener")
            
            # Handler for notification changes
            def notification_changed_handler(sender, args):
                try:
                    notification = sender.get_notification(args.user_notification_id)
                    
                    app_name = "Unknown"
                    title = ""
                    message = ""
                    
                    # Get app info if available
                    if hasattr(notification, "app_info") and notification.app_info:
                        app_name = notification.app_info.display_info.display_name
                    
                    # Extract notification text
                    try:
                        binding = notification.notification.visual.get_binding(
                            KnownNotificationBindings.get_toast_generic()
                        )
                        if binding:
                            text_elements = binding.get_text_elements()
                            if text_elements:
                                texts = []
                                it = iter(text_elements)
                                if it.current:
                                    texts.append(it.current.text)
                                while True:
                                    next(it, None)
                                    if it.has_current:
                                        texts.append(it.current.text)
                                    else:
                                        break
                                
                                if texts:
                                    title = texts[0]
                                    message = " ".join(texts[1:]) if len(texts) > 1 else ""
                    except Exception as e:
                        logger.debug(f"Error extracting text: {e}")
                    
                    # Queue the notification
                    self.notification_queue.put({
                        'app': app_name,
                        'title': title,
                        'message': message
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing notification: {e}")
            
            # Add the event handler
            self.notification_listener.add_notification_changed(notification_changed_handler)
            
            # Get all current notifications
            notifications = await self.notification_listener.get_notifications_async(NotificationKinds.TOAST)
            print(f"[WINRT] Found {len(notifications)} existing notifications in Action Center")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WinRT listener: {e}")
            print(f"[WINRT] Failed to setup: {e}")
            return False
    
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
        
        # Try to setup WinRT listener
        winrt_success = await self.setup_winrt_listener()
        
        if not winrt_success:
            # Fallback to window monitoring
            print("[FALLBACK] Using window monitoring method")
            monitor_thread = threading.Thread(target=self.background_monitor_loop)
            monitor_thread.daemon = True
            monitor_thread.start()
        
        print("\n[MONITOR ACTIVE] Watching for all notifications...")
        print("=" * 60)
        
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
    
    print("=" * 60)
    print("     NOTIFICATION MONITOR")
    print("=" * 60)
    print("\nMode: All Notifications")
    print("\nFeatures:")
    print("  ✓ Monitors all Windows notifications")
    print("  ✓ Real-time console output")
    print("  ✓ Logs to notification_monitor.log")
    print("\nStatus:")
    print("  → Connecting to WebSocket server...")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    
    # Check platform
    if sys.platform != 'win32':
        print("Error: This program only works on Windows")
        return
    
    # Start monitor
    monitor = BackgroundMonitor()
    
    # Optional: Hide console window after 5 seconds
    # Comment out if you want to keep console visible
    # def hide_console():
    #     time.sleep(5)
    #     kernel32 = ctypes.WinDLL('kernel32')
    #     user32 = ctypes.WinDLL('user32')
    #     
    #     hWnd = kernel32.GetConsoleWindow()
    #     if hWnd:
    #         user32.ShowWindow(hWnd, 6)  # SW_MINIMIZE
    #         print("\nMinimized to background. Check notification_monitor.log for activity.")
    # 
    # hide_thread = threading.Thread(target=hide_console)
    # hide_thread.daemon = True
    # hide_thread.start()
    
    print("\n[Running] Monitor is active. Press Ctrl+C to stop.")
    print("[Logs] Check notification_monitor.log for captured notifications.")
    
    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()

if __name__ == "__main__":
    main()