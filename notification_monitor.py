#!/usr/bin/env python3
"""
Windows通知センター監視プログラム
Slackを含むすべてのWindows通知をキャプチャしてWebSocketサーバーに転送
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

# Windows固有のインポート
if sys.platform == 'win32':
    import win32gui
    import win32con
    import win32api
    import win32event
    import ctypes
    from ctypes import wintypes
    import comtypes
    from comtypes import GUID
    
    # UI Automation用
    import comtypes.client
    from comtypes.automation import VARIANT
    
    # Windows Runtime
    try:
        import winrt
        from winrt.windows.ui.notifications import ToastNotificationManager
        from winrt.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus
    except ImportError:
        print("winrt モジュールが必要です: pip install winrt")
        sys.exit(1)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NotificationMonitor:
    def __init__(self, ws_url="ws://localhost:8080"):
        self.ws_url = ws_url
        self.ws = None
        self.running = False
        self.notification_queue = queue.Queue()
        self.processed_ids = set()  # 処理済み通知のID
        
    async def connect_websocket(self):
        """WebSocketサーバーに接続"""
        try:
            self.ws = await websockets.connect(self.ws_url)
            logger.info(f"WebSocketサーバーに接続しました: {self.ws_url}")
            return True
        except Exception as e:
            logger.error(f"WebSocket接続エラー: {e}")
            return False
    
    async def send_notification(self, app_name, title, message):
        """WebSocketサーバーに通知を送信"""
        if not self.ws:
            if not await self.connect_websocket():
                return
                
        # Slack通知を特別扱い
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
            logger.info(f"通知を転送: [{app_name}] {title} - {message}")
        except Exception as e:
            logger.error(f"通知送信エラー: {e}")
            self.ws = None
    
    async def request_notification_access(self):
        """通知へのアクセス許可をリクエスト"""
        try:
            # 通知リスナーのアクセス許可をリクエスト
            listener = UserNotificationListener.get_current()
            access_status = await listener.request_access_async()
            
            if access_status == UserNotificationListenerAccessStatus.ALLOWED:
                logger.info("通知へのアクセスが許可されました")
                return True
            else:
                logger.error(f"通知へのアクセスが拒否されました: {access_status}")
                return False
        except Exception as e:
            logger.error(f"アクセス許可リクエストエラー: {e}")
            return False
    
    async def get_notifications(self):
        """現在の通知を取得"""
        try:
            listener = UserNotificationListener.get_current()
            notifications = await listener.get_notifications_async(
                UserNotificationListenerAccessStatus.ALLOWED
            )
            
            for notification in notifications:
                try:
                    # 通知IDを取得
                    notif_id = notification.id
                    
                    # 既に処理済みならスキップ
                    if notif_id in self.processed_ids:
                        continue
                    
                    # アプリ情報を取得
                    app_info = notification.app_info
                    app_name = app_info.display_info.display_name if app_info else "Unknown"
                    
                    # 通知内容を取得
                    notification_binding = notification.notification
                    if notification_binding:
                        visual = notification_binding.visual
                        if visual:
                            # テキスト要素を取得
                            bindings = visual.bindings
                            if bindings and len(bindings) > 0:
                                binding = bindings[0]
                                text_elements = binding.get_text_elements()
                                
                                title = ""
                                message = ""
                                
                                if len(text_elements) > 0:
                                    title = text_elements[0].text
                                if len(text_elements) > 1:
                                    message = text_elements[1].text
                                
                                # 通知をキューに追加
                                self.notification_queue.put({
                                    'app_name': app_name,
                                    'title': title,
                                    'message': message
                                })
                                
                                # 処理済みとしてマーク
                                self.processed_ids.add(notif_id)
                                
                                # メモリ管理のため、古いIDを削除
                                if len(self.processed_ids) > 1000:
                                    self.processed_ids = set(list(self.processed_ids)[-500:])
                    
                except Exception as e:
                    logger.error(f"通知処理エラー: {e}")
                    
        except Exception as e:
            logger.error(f"通知取得エラー: {e}")
    
    async def monitor_notifications(self):
        """通知を定期的に監視"""
        logger.info("通知監視を開始します")
        
        while self.running:
            try:
                # 通知を取得
                await self.get_notifications()
                
                # キューから通知を処理
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
                
                # 1秒待機
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"監視エラー: {e}")
                await asyncio.sleep(5)
    
    async def start(self):
        """監視を開始"""
        self.running = True
        
        # アクセス許可をリクエスト
        if not await self.request_notification_access():
            logger.error("通知へのアクセス許可が必要です")
            logger.info("設定 > プライバシー > 通知 でこのアプリを許可してください")
            return
        
        # WebSocketに接続
        if not await self.connect_websocket():
            logger.error("WebSocket接続に失敗しました")
            return
        
        # テスト通知
        await self.send_notification(
            "Notification Monitor",
            "監視開始",
            "Windows通知の監視を開始しました"
        )
        
        try:
            # 監視を開始
            await self.monitor_notifications()
        except KeyboardInterrupt:
            logger.info("監視を終了します")
        finally:
            self.running = False
            if self.ws:
                await self.ws.close()

def setup_windows_manifest():
    """Windows用のマニフェストファイルを生成"""
    manifest_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="*"
    name="JupiterNotificationMonitor"
    type="win32"
  />
  <description>Jupiter Notification Monitor</description>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>"""
    
    with open("notification_monitor.exe.manifest", "w") as f:
        f.write(manifest_content)
    logger.info("マニフェストファイルを作成しました")

def main():
    """メインエントリーポイント"""
    print("=== Windows通知監視システム ===")
    print("すべてのWindows通知をWebSocketサーバーに転送します")
    print("特にSlackの通知を識別して転送します")
    print("\n必要な設定:")
    print("1. Windows 10/11 バージョン1809以降")
    print("2. 設定 > プライバシー > 通知 でアクセスを許可")
    print("3. Slackデスクトップアプリがインストールされていること")
    print("\nCtrl+C で終了します\n")
    
    # Windows以外では動作しない
    if sys.platform != 'win32':
        print("エラー: このプログラムはWindowsでのみ動作します")
        return
    
    # マニフェストファイルを作成
    if not os.path.exists("notification_monitor.exe.manifest"):
        setup_windows_manifest()
    
    # 監視を開始
    monitor = NotificationMonitor()
    
    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        print("\n終了します")

if __name__ == "__main__":
    main()