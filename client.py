#!/usr/bin/env python3
"""
JUPITER-NOTIFIER-CLIENT
Windows notification client for JUPITER SYSTEM
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime
from typing import Optional, Dict, Any

# Third-party imports
import requests
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Windows-specific imports
if sys.platform == 'win32':
    from plyer import notification
    import pystray
    from PIL import Image, ImageDraw
    from win10toast import ToastNotifier
    import win32gui
    import win32con

# Initialize colorama for colored console output
init(autoreset=True)

# Load environment variables
load_dotenv()

# Configuration
class Config:
    # Server settings
    SERVER_URL = os.getenv('JUPITER_SERVER_URL', 'http://localhost:3000')
    WEBHOOK_PORT = int(os.getenv('JUPITER_WEBHOOK_PORT', '8080'))
    API_KEY = os.getenv('API_KEY', '')
    
    # Discord settings
    DISCORD_USER_ID = os.getenv('DISCORD_USER_ID', '')
    DISCORD_GUILD_ID = os.getenv('DISCORD_GUILD_ID', '')
    
    # Notification settings
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'
    NOTIFICATION_SOUND = os.getenv('NOTIFICATION_SOUND', 'true').lower() == 'true'
    NOTIFICATION_TIMEOUT = int(os.getenv('NOTIFICATION_TIMEOUT', '10'))
    NOTIFICATION_TYPES = os.getenv('NOTIFICATION_TYPES', 'all').split(',')
    
    # Connection settings
    RECONNECT_INTERVAL = int(os.getenv('RECONNECT_INTERVAL', '5'))
    MAX_RECONNECT_ATTEMPTS = int(os.getenv('MAX_RECONNECT_ATTEMPTS', '10'))
    HEARTBEAT_INTERVAL = int(os.getenv('HEARTBEAT_INTERVAL', '30'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'jupiter_notifier.log')
    
    # System tray
    ENABLE_SYSTEM_TRAY = os.getenv('ENABLE_SYSTEM_TRAY', 'true').lower() == 'true'
    START_MINIMIZED = os.getenv('START_MINIMIZED', 'false').lower() == 'true'
    
    # Windows specific
    APP_ID = os.getenv('WINDOWS_NOTIFICATION_APP_ID', 'JUPITER.Notifier')

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class JupiterNotifierClient:
    def __init__(self):
        self.running = False
        self.connected = False
        self.reconnect_attempts = 0
        self.icon = None
        self.toaster = ToastNotifier() if sys.platform == 'win32' else None
        
        # Validate configuration
        self._validate_config()
        
    def _validate_config(self):
        """Validate required configuration"""
        if not Config.DISCORD_USER_ID:
            logger.error("DISCORD_USER_ID not configured in .env file")
            sys.exit(1)
            
        if not Config.SERVER_URL:
            logger.error("JUPITER_SERVER_URL not configured in .env file")
            sys.exit(1)
            
        logger.info(f"Configuration loaded - User ID: {Config.DISCORD_USER_ID}")
        
    def _create_icon(self):
        """Create system tray icon"""
        # Create a simple icon
        image = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(image)
        draw.ellipse([8, 8, 56, 56], fill='#333333', outline='white')
        draw.text((24, 24), "J", fill='white')
        
        return image
        
    def _setup_system_tray(self):
        """Setup system tray icon"""
        if not Config.ENABLE_SYSTEM_TRAY or not sys.platform == 'win32':
            return
            
        menu = pystray.Menu(
            pystray.MenuItem("Show Console", self._show_console),
            pystray.MenuItem("Settings", self._open_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Reconnect", self._reconnect),
            pystray.MenuItem("Exit", self._quit)
        )
        
        self.icon = pystray.Icon(
            "jupiter_notifier",
            self._create_icon(),
            "JUPITER Notifier",
            menu
        )
        
        # Run icon in separate thread
        icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        icon_thread.start()
        
    def _show_console(self, icon, item):
        """Show console window"""
        # Windows-specific console showing
        if sys.platform == 'win32':
            import ctypes
            kernel32 = ctypes.WinDLL('kernel32')
            user32 = ctypes.WinDLL('user32')
            SW_SHOW = 5
            
            hWnd = kernel32.GetConsoleWindow()
            if hWnd:
                user32.ShowWindow(hWnd, SW_SHOW)
                
    def _open_settings(self, icon, item):
        """Open settings file"""
        os.startfile('.env')
        
    def _reconnect(self, icon, item):
        """Force reconnection"""
        logger.info("Manual reconnection requested")
        self.connected = False
        
    def _quit(self, icon, item):
        """Quit application"""
        self.running = False
        if self.icon:
            self.icon.stop()
        sys.exit(0)
        
    def show_notification(self, title: str, message: str, notification_type: str = "info"):
        """Show Windows notification"""
        if not Config.ENABLE_NOTIFICATIONS:
            return
            
        try:
            if self.toaster:
                # Use Windows 10 toast notifications
                self.toaster.show_toast(
                    title,
                    message,
                    icon_path=None,
                    duration=Config.NOTIFICATION_TIMEOUT,
                    threaded=True
                )
            else:
                # Fallback to plyer
                notification.notify(
                    title=title,
                    message=message,
                    app_name="JUPITER Notifier",
                    timeout=Config.NOTIFICATION_TIMEOUT
                )
                
            logger.info(f"Notification shown: {title}")
            
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
            
    def connect_to_server(self):
        """Connect to JUPITER server"""
        try:
            # Register client
            register_url = f"{Config.SERVER_URL}/api/notifier/register"
            data = {
                "user_id": Config.DISCORD_USER_ID,
                "guild_id": Config.DISCORD_GUILD_ID,
                "client_type": "windows",
                "notification_types": Config.NOTIFICATION_TYPES
            }
            
            headers = {}
            if Config.API_KEY:
                headers['Authorization'] = f"Bearer {Config.API_KEY}"
                
            response = requests.post(register_url, json=data, headers=headers)
            
            if response.status_code == 200:
                self.connected = True
                self.reconnect_attempts = 0
                logger.info("Successfully connected to JUPITER server")
                self.show_notification("JUPITER Notifier", "Connected to server", "success")
                return True
            else:
                logger.error(f"Failed to connect: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
            
    def poll_notifications(self):
        """Poll for new notifications"""
        poll_url = f"{Config.SERVER_URL}/api/notifier/poll/{Config.DISCORD_USER_ID}"
        
        headers = {}
        if Config.API_KEY:
            headers['Authorization'] = f"Bearer {Config.API_KEY}"
            
        try:
            response = requests.get(poll_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                notifications = response.json()
                
                for notif in notifications:
                    self.handle_notification(notif)
                    
            elif response.status_code == 204:
                # No new notifications
                pass
            else:
                logger.warning(f"Poll failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.debug("Poll timeout (normal)")
        except Exception as e:
            logger.error(f"Poll error: {e}")
            self.connected = False
            
    def handle_notification(self, notification: Dict[str, Any]):
        """Handle incoming notification"""
        notif_type = notification.get('type', 'unknown')
        
        # Check if we should handle this notification type
        if Config.NOTIFICATION_TYPES != ['all'] and notif_type not in Config.NOTIFICATION_TYPES:
            logger.debug(f"Ignoring notification type: {notif_type}")
            return
            
        title = notification.get('title', 'JUPITER Notification')
        message = notification.get('message', '')
        
        # Format based on type
        if notif_type == 'mention':
            title = "📌 " + title
        elif notif_type == 'direct_message':
            title = "💬 " + title
        elif notif_type == 'role_mention':
            title = "👥 " + title
            
        self.show_notification(title, message, notif_type)
        
        # Log notification
        logger.info(f"Notification received: {notif_type} - {title}")
        
    def run(self):
        """Main run loop"""
        self.running = True
        
        # Setup system tray
        if Config.ENABLE_SYSTEM_TRAY:
            self._setup_system_tray()
            
        logger.info("JUPITER Notifier Client started")
        print(f"{Fore.GREEN}JUPITER Notifier Client v1.0.0{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Monitoring notifications for user: {Config.DISCORD_USER_ID}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}\n")
        
        while self.running:
            try:
                # Connect if not connected
                if not self.connected:
                    if self.reconnect_attempts >= Config.MAX_RECONNECT_ATTEMPTS:
                        logger.error("Max reconnection attempts reached")
                        self.show_notification(
                            "Connection Failed",
                            "Unable to connect to JUPITER server",
                            "error"
                        )
                        time.sleep(60)  # Wait longer before retrying
                        self.reconnect_attempts = 0
                        continue
                        
                    logger.info(f"Attempting to connect... (attempt {self.reconnect_attempts + 1})")
                    if self.connect_to_server():
                        self.connected = True
                    else:
                        self.reconnect_attempts += 1
                        time.sleep(Config.RECONNECT_INTERVAL)
                        continue
                        
                # Poll for notifications
                self.poll_notifications()
                
                # Small delay between polls
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Shutdown requested")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(5)
                
        # Cleanup
        if self.icon:
            self.icon.stop()
            
        logger.info("JUPITER Notifier Client stopped")

def main():
    """Main entry point"""
    client = JupiterNotifierClient()
    
    try:
        client.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()