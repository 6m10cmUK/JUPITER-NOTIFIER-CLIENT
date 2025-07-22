#!/usr/bin/env python3
"""
JUPITER NOTIFIER CLIENT V2
Windows PC向け全画面通知クライアント（改良版）

スレッド管理を改善し、安定した通知表示を実現
"""

import asyncio
import websockets
import json
import tkinter as tk
from tkinter import font
import queue
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import winsound
import screeninfo

# .envファイルを読み込み
load_dotenv()

# 設定
WS_SERVER_URL = os.getenv('WS_SERVER_URL', 'wss://site--jupiter-system--6qtwyp8fx6v7.code.run')
DEFAULT_DURATION = 10000  # 10秒固定
BACKGROUND_COLOR = '#610610'  # 暗い赤色


class NotificationManager:
    """通知の表示を管理するクラス（シングルスレッドで動作）"""
    
    def __init__(self):
        self.root = None
        self.windows = []
        self.is_showing = False
        self.auto_close_id = None
        
    def setup(self):
        """Tkinterのセットアップ（メインスレッドで実行）"""
        self.root = tk.Tk()
        self.root.withdraw()  # メインウィンドウは非表示
        
    def show_notification(self, title, message, duration=DEFAULT_DURATION, sender=None, send_dismiss_callback=None):
        """通知を表示"""
        if self.is_showing:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 既に通知を表示中のため、先に閉じます")
            self.close_all_notifications(send_dismiss=False)
            
        self.is_showing = True
        self.send_dismiss_callback = send_dismiss_callback
        
        # ビープ音を再生（Windowsのみ）
        try:
            winsound.Beep(1000, 100)  # 1000Hzで100ミリ秒
        except:
            pass
            
        # 全モニターの情報を取得
        try:
            monitors = screeninfo.get_monitors()
        except:
            monitors = [None]
            
        # 各モニターにウィンドウを作成
        for i, monitor in enumerate(monitors):
            window = tk.Toplevel(self.root)
            
            # ウィンドウタイトル
            window.title('JUPITER NOTIFICATION')
            
            # モニター位置に配置
            if monitor:
                window.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
            
            # ウィンドウ設定
            window.overrideredirect(True)  # ウィンドウ枠を削除
            window.attributes('-topmost', True)
            window.attributes('-alpha', 0.65)  # 65%の透明度
            window.configure(bg=BACKGROUND_COLOR)
            
            # フルスクリーン設定
            if monitor:
                window.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
            else:
                window.state('zoomed')  # Windows用の最大化
            
            # メインフレーム
            main_frame = tk.Frame(window, bg=BACKGROUND_COLOR)
            main_frame.pack(expand=True, fill='both')
            
            # フレームもクリック可能に
            main_frame.bind('<Button-1>', lambda e: self.close_all_notifications(send_dismiss=True))
            
            # 送信者情報
            if sender:
                sender_font = font.Font(size=24)
                sender_label = tk.Label(
                    main_frame,
                    text=f"From: {sender}",
                    font=sender_font,
                    fg='#ff9999',
                    bg=BACKGROUND_COLOR,
                    cursor='hand2'
                )
                sender_label.pack(pady=(100, 20))
                sender_label.bind('<Button-1>', lambda e: self.close_all_notifications(send_dismiss=True))
            
            # メッセージ（大きく表示）
            msg_font = font.Font(size=96, weight='bold')
            msg_label = tk.Label(
                main_frame,
                text=message,
                font=msg_font,
                fg='white',
                bg=BACKGROUND_COLOR,
                wraplength=1600,
                justify='center',
                cursor='hand2'
            )
            msg_label.pack(expand=True, pady=(0, 50))
            msg_label.bind('<Button-1>', lambda e: self.close_all_notifications(send_dismiss=True))
            
            # 操作説明
            info_font = font.Font(size=16)
            info_label = tk.Label(
                main_frame,
                text="画面をクリックまたは[ESC]キーで閉じる",
                font=info_font,
                fg='#cccccc',
                bg=BACKGROUND_COLOR,
                cursor='hand2'
            )
            info_label.pack(side='bottom', pady=50)
            info_label.bind('<Button-1>', lambda e: self.close_all_notifications(send_dismiss=True))
            
            # ESCキーで閉じる
            window.bind('<Escape>', lambda e: self.close_all_notifications(send_dismiss=True))
            
            # クリックでも閉じる
            window.bind('<Button-1>', lambda e: self.close_all_notifications(send_dismiss=True))
            
            self.windows.append(window)
        
        # 自動的に閉じるタイマー
        if self.windows:
            self.auto_close_id = self.root.after(duration, lambda: self.close_all_notifications(send_dismiss=False))
    
    def close_all_notifications(self, send_dismiss=True):
        """全ての通知ウィンドウを閉じる"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 通知を閉じます: send_dismiss={send_dismiss}")
        
        # タイマーをキャンセル
        if self.auto_close_id:
            self.root.after_cancel(self.auto_close_id)
            self.auto_close_id = None
            
        # ウィンドウを閉じる
        for window in self.windows:
            try:
                window.destroy()
            except:
                pass
                
        self.windows = []
        self.is_showing = False
        
        # 消去通知を送信
        if send_dismiss and self.send_dismiss_callback:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 消去通知をキューに追加")
            self.send_dismiss_callback()
    
    def process_events(self):
        """Tkinterのイベントを処理（定期的に呼び出す）"""
        if self.root:
            self.root.update()


async def websocket_handler(notification_queue, dismiss_queue):
    """WebSocket通信を処理"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] JUPITER NOTIFIER CLIENT V2 起動")
    print(f"接続先: {WS_SERVER_URL}")
    
    while True:
        try:
            async with websockets.connect(WS_SERVER_URL) as websocket:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] サーバーに接続しました")
                
                # 登録メッセージを送信
                await websocket.send(json.dumps({
                    "type": "register",
                    "client_type": "windows_notifier",
                    "version": "2.0.0"
                }))
                
                # 受信と送信を並行処理
                async def receive_messages():
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            
                            if data.get('type') == 'registered':
                                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] サーバーに登録されました: {data.get('clientId')}")
                            
                            elif data.get('type') == 'notification':
                                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 通知受信: {data.get('title')}")
                                notification_queue.put(data)
                            
                            elif data.get('type') == 'dismiss_notification':
                                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 消去通知受信: {data.get('dismissed_by')}")
                                notification_queue.put({'type': 'dismiss'})
                                
                        except json.JSONDecodeError as e:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] JSONパースエラー: {e}")
                
                async def send_dismisses():
                    while True:
                        try:
                            # キューから消去通知を取得（非同期）
                            await asyncio.sleep(0.1)
                            if not dismiss_queue.empty():
                                dismiss_queue.get()
                                await websocket.send(json.dumps({
                                    "type": "dismiss_notification",
                                    "client_type": "windows_notifier"
                                }))
                                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 消去通知を送信しました")
                        except Exception as e:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 消去通知送信エラー: {e}")
                
                # 両方のタスクを実行
                await asyncio.gather(
                    receive_messages(),
                    send_dismisses()
                )
                        
        except websockets.ConnectionClosed:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] サーバーとの接続が切断されました")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 接続エラー: {e}")
            
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 5秒後に再接続します...")
        await asyncio.sleep(5)


def main():
    """メイン関数"""
    try:
        # Windowsプラットフォームチェック
        if sys.platform != 'win32':
            print("[警告] このアプリケーションはWindows向けに設計されています")
        
        # キューを作成
        notification_queue = queue.Queue()
        dismiss_queue = queue.Queue()
        
        # 通知マネージャーを作成
        manager = NotificationManager()
        manager.setup()
        
        # WebSocketハンドラーを非同期で起動
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        websocket_task = loop.create_task(websocket_handler(notification_queue, dismiss_queue))
        
        # メインループ
        try:
            while True:
                # Tkinterのイベントを処理
                manager.process_events()
                
                # キューから通知を取得
                try:
                    notification = notification_queue.get_nowait()
                    
                    if notification.get('type') == 'dismiss':
                        manager.close_all_notifications(send_dismiss=False)
                    elif notification.get('type') == 'notification':
                        manager.show_notification(
                            notification.get('title', 'Discord通知'),
                            notification.get('message', ''),
                            notification.get('duration', DEFAULT_DURATION),
                            notification.get('sender'),
                            lambda: dismiss_queue.put(True)
                        )
                except queue.Empty:
                    pass
                
                # 少し待機
                loop.run_until_complete(asyncio.sleep(0.01))
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] アプリケーションを終了します")
            websocket_task.cancel()
            
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] アプリケーションを終了します")
        sys.exit(0)


if __name__ == "__main__":
    main()