#!/usr/bin/env python3
"""
Simplified Windows Notification Monitor
Using Windows 10 Toast Notification History
"""

import asyncio
import websockets
import json
import logging
import time
from datetime import datetime
import sys
import os

# Windows specific imports
if sys.platform == 'win32':
    import win32gui
    import win32api
    import xml.etree.ElementTree as ET
    try:
        from winrt.windows.ui.notifications.management import UserNotificationListener
        from winrt.windows.ui.notifications import ToastNotificationManager
    except ImportError:
        print("Error: winrt module required")
        print("Install: pip install winrt-runtime")
        print("Also try: pip install winrt")
        sys.exit(1)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleNotificationMonitor:
    def __init__(self, ws_url="ws://localhost:8080"):
        self.ws_url = ws_url
        self.ws = None
        self.running = False
        self.processed_ids = set()
        
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
        is_slack = "slack" in app_name.lower()
        
        notification_data = {
            "type": "notification",
            "title": title if title else app_name,
            "message": message,
            "sender": f"Windows ({app_name})",
            "source": "notification_monitor",
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
    
    def get_notification_history(self):
        """Get notification history using simpler approach"""
        try:
            # Try to get notification history
            history = ToastNotificationManager.get_for_user().history()
            logger.info(f"Found {len(history)} notifications in history")
            
            for notification in history:
                try:
                    # Get app info
                    app_id = notification.application_id if hasattr(notification, 'application_id') else "Unknown"
                    
                    # Parse notification XML
                    xml_content = notification.content.get_xml() if hasattr(notification.content, 'get_xml') else ""
                    
                    if xml_content:
                        root = ET.fromstring(xml_content)
                        
                        # Extract text elements
                        texts = []
                        for text_elem in root.findall(".//text"):
                            if text_elem.text:
                                texts.append(text_elem.text)
                        
                        title = texts[0] if len(texts) > 0 else ""
                        message = texts[1] if len(texts) > 1 else ""
                        
                        # Create unique ID
                        notif_id = f"{app_id}_{title}_{message}"
                        
                        if notif_id not in self.processed_ids:
                            self.processed_ids.add(notif_id)
                            
                            # Send notification
                            asyncio.create_task(self.send_notification(app_id, title, message))
                            
                            # Keep memory usage low
                            if len(self.processed_ids) > 1000:
                                self.processed_ids = set(list(self.processed_ids)[-500:])
                
                except Exception as e:
                    logger.debug(f"Error processing notification: {e}")
                    
        except Exception as e:
            logger.error(f"Error getting notification history: {e}")
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting notification monitoring...")
        
        while self.running:
            try:
                # Check for new notifications
                self.get_notification_history()
                
                # Wait 2 seconds
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
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
            "Notification Monitor",
            "Monitor Started",
            "Windows notification monitoring is active"
        )
        
        try:
            # Start monitoring
            await self.monitor_loop()
        except KeyboardInterrupt:
            logger.info("Stopping monitor...")
        finally:
            self.running = False
            if self.ws:
                await self.ws.close()

def main():
    """Main entry point"""
    print("=== Simple Windows Notification Monitor ===")
    print("Monitoring Windows notifications and forwarding to WebSocket")
    print("\nRequirements:")
    print("- Windows 10/11")
    print("- Discord bot running on port 8080")
    print("- Slack desktop app (for Slack notifications)")
    print("\nPress Ctrl+C to stop\n")
    
    # Check platform
    if sys.platform != 'win32':
        print("Error: This program only works on Windows")
        return
    
    # Start monitor
    monitor = SimpleNotificationMonitor()
    
    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        print("\nStopping...")

if __name__ == "__main__":
    main()