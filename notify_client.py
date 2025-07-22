#!/usr/bin/env python3
"""
JUPITER NOTIFIER CLIENT
Windows PC向け全画面通知クライアント

Discord BotからのWebSocket経由で通知を受信し、
全画面で通知を表示します。
"""

import asyncio
import websockets
import json
import tkinter as tk
from tkinter import font
import threading
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# 設定
WS_SERVER_URL = os.getenv('WS_SERVER_URL', 'wss://jupiter-system--jupiter-system--r6m10cms-team.p1.northflank.app')
DEFAULT_DURATION = 10000  # 10秒固定
BACKGROUND_COLOR = '#610610'  # 暗い赤色


class FullScreenNotification:
    """全画面通知を表示するクラス"""
    
    def __init__(self):
        self.root = None
        self.is_showing = False
        
    def show_notification(self, title, message, duration=DEFAULT_DURATION, sender=None):
        """
        全画面通知を表示
        
        Args:
            title: 通知タイトル
            message: 通知メッセージ
            duration: 表示時間（ミリ秒）
            sender: 送信者名
        """
        if self.is_showing:
            return
            
        def create_window():
            self.is_showing = True
            self.root = tk.Tk()
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)
            self.root.configure(bg=BACKGROUND_COLOR)
            
            # ウィンドウタイトル
            self.root.title('JUPITER NOTIFICATION')
            
            # メインフレーム
            main_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
            main_frame.pack(expand=True, fill='both')
            
            # 送信者情報
            if sender:
                sender_font = font.Font(size=24)
                sender_label = tk.Label(
                    main_frame,
                    text=f"From: {sender}",
                    font=sender_font,
                    fg='#ff9999',
                    bg=BACKGROUND_COLOR
                )
                sender_label.pack(pady=(100, 20))
            
            # タイトル
            title_font = font.Font(size=72, weight='bold')
            title_label = tk.Label(
                main_frame, 
                text=title, 
                font=title_font,
                fg='white',
                bg=BACKGROUND_COLOR
            )
            title_label.pack(expand=True, pady=(0, 50))
            
            # メッセージ
            msg_font = font.Font(size=48)
            msg_label = tk.Label(
                main_frame,
                text=message,
                font=msg_font,
                fg='white',
                bg=BACKGROUND_COLOR,
                wraplength=1200,
                justify='center'
            )
            msg_label.pack(expand=True)
            
            # 操作説明
            info_font = font.Font(size=16)
            info_label = tk.Label(
                main_frame,
                text="[ESC]キーで閉じる",
                font=info_font,
                fg='#cccccc',
                bg=BACKGROUND_COLOR
            )
            info_label.pack(side='bottom', pady=50)
            
            # 自動的に閉じる
            self.root.after(duration, self.close_notification)
            
            # ESCキーで閉じる
            self.root.bind('<Escape>', lambda e: self.close_notification())
            
            # クリックでも閉じる
            self.root.bind('<Button-1>', lambda e: self.close_notification())
            
            self.root.mainloop()
            
        thread = threading.Thread(target=create_window)
        thread.daemon = True
        thread.start()
    
    def close_notification(self):
        """通知を閉じる"""
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None
            self.is_showing = False


async def connect_to_bot():
    """Discord BotのWebSocketサーバーに接続"""
    notifier = FullScreenNotification()
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] JUPITER NOTIFIER CLIENT 起動")
    print(f"接続先: {WS_SERVER_URL}")
    
    while True:
        try:
            async with websockets.connect(WS_SERVER_URL) as websocket:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] サーバーに接続しました")
                
                # 登録メッセージを送信
                await websocket.send(json.dumps({
                    "type": "register",
                    "client_type": "windows_notifier",
                    "version": "1.0.0"
                }))
                
                # メッセージを受信
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        
                        if data.get('type') == 'registered':
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] サーバーに登録されました: {data.get('clientId')}")
                        
                        elif data.get('type') == 'notification':
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 通知受信: {data.get('title')}")
                            notifier.show_notification(
                                data.get('title', 'Discord通知'),
                                data.get('message', ''),
                                data.get('duration', DEFAULT_DURATION),
                                data.get('sender')
                            )
                            
                    except json.JSONDecodeError as e:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] JSONパースエラー: {e}")
                        
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
        
        asyncio.run(connect_to_bot())
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] アプリケーションを終了します")
        sys.exit(0)


if __name__ == "__main__":
    main()