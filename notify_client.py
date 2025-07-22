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
import winsound
import screeninfo

# .envファイルを読み込み
load_dotenv()

# 設定
WS_SERVER_URL = os.getenv('WS_SERVER_URL', 'wss://site--jupiter-system--6qtwyp8fx6v7.code.run')
DEFAULT_DURATION = 10000  # 10秒固定
BACKGROUND_COLOR = '#610610'  # 暗い赤色


class FullScreenNotification:
    """全画面通知を表示するクラス"""
    
    def __init__(self):
        self.windows = []  # 各モニター用のウィンドウリスト
        self.is_showing = False
        self.close_event = threading.Event()
        self.websocket = None
        self.should_send_dismiss = False
        
    def show_notification(self, title, message, duration=DEFAULT_DURATION, sender=None):
        """
        全画面通知を表示（全モニターに表示）
        
        Args:
            title: 通知タイトル
            message: 通知メッセージ
            duration: 表示時間（ミリ秒）
            sender: 送信者名
        """
        if self.is_showing:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 既に通知を表示中のためスキップします")
            return
            
        def create_windows():
            self.is_showing = True
            self.windows = []
            self.close_event.clear()
            
            # ビープ音を再生（Windowsのみ）
            try:
                winsound.Beep(1000, 100)  # 1000Hzで100ミリ秒
            except:
                pass  # ビープ音が再生できない場合は無視
            
            # 全モニターの情報を取得
            try:
                monitors = screeninfo.get_monitors()
            except:
                # screeninfoが失敗した場合は単一モニターとして処理
                monitors = [None]
            
            # 各モニターにウィンドウを作成
            for i, monitor in enumerate(monitors):
                root = tk.Tk() if i == 0 else tk.Toplevel()
                
                # ウィンドウタイトル（フルスクリーン前に設定）
                root.title('JUPITER NOTIFICATION')
                
                # モニター位置に配置（フルスクリーン前に設定）
                if monitor:
                    root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
                
                # ウィンドウ設定
                root.overrideredirect(True)  # ウィンドウ枠を削除
                root.attributes('-topmost', True)
                root.attributes('-alpha', 0.65)  # 65%の透明度
                root.configure(bg=BACKGROUND_COLOR)
                
                # フルスクリーン設定
                if monitor:
                    # 各モニターの位置とサイズに合わせて配置
                    root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
                else:
                    # モニター情報が取得できない場合は通常のフルスクリーン
                    root.state('zoomed')  # Windows用の最大化
                
                # メインフレーム
                main_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
                main_frame.pack(expand=True, fill='both')
                
                # フレームもクリック可能に
                def on_frame_click(event):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] フレームがクリックされました")
                    self.close_all_notifications(send_dismiss=True)
                main_frame.bind('<Button-1>', on_frame_click)
                
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
                root.bind('<Escape>', lambda e: self.close_all_notifications(send_dismiss=True))
                
                # クリックでも閉じる
                root.bind('<Button-1>', lambda e: self.close_all_notifications(send_dismiss=True))
                
                self.windows.append(root)
            
            # 自動的に閉じるタイマー（最初のウィンドウに設定）
            if self.windows:
                self.windows[0].after(duration, lambda: self.close_all_notifications(send_dismiss=False))
            
            # メインループ（最初のウィンドウで実行）
            if self.windows:
                self.windows[0].mainloop()
            
        thread = threading.Thread(target=create_windows)
        thread.daemon = True
        thread.start()
    
    def close_all_notifications(self, send_dismiss=True):
        """全ての通知ウィンドウを閉じる"""
        # ウィンドウが存在する場合は閉じる
        if self.windows:
            for window in self.windows:
                try:
                    window.quit()
                    window.destroy()
                except:
                    pass
        
        # 状態を必ずリセット
        self.windows = []
        self.is_showing = False
        self.close_event.set()
        
        # 他のクライアントにも消去を通知
        if send_dismiss:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 消去フラグを設定しました")
            self.should_send_dismiss = True


async def connect_to_bot():
    """Discord BotのWebSocketサーバーに接続"""
    notifier = FullScreenNotification()
    
    async def send_dismiss_notification():
        """消去通知を送信"""
        try:
            if notifier.websocket:
                await notifier.websocket.send(json.dumps({
                    "type": "dismiss_notification",
                    "client_type": "windows_notifier"
                }))
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 消去通知を送信しました")
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WebSocket未接続のため消去通知を送信できません")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 消去通知送信中にエラー: {e}")
    
    notifier.send_dismiss_notification = send_dismiss_notification
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] JUPITER NOTIFIER CLIENT 起動")
    print(f"接続先: {WS_SERVER_URL}")
    
    while True:
        try:
            async with websockets.connect(WS_SERVER_URL) as websocket:
                notifier.websocket = websocket
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] サーバーに接続しました")
                
                # 登録メッセージを送信
                await websocket.send(json.dumps({
                    "type": "register",
                    "client_type": "windows_notifier",
                    "version": "1.0.0"
                }))
                
                # メッセージ受信とdismiss送信を並行処理
                async def receive_messages():
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
                            
                            elif data.get('type') == 'dismiss_notification':
                                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 消去通知受信: {data.get('dismissed_by')}")
                                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 現在の状態: is_showing={notifier.is_showing}, windows数={len(notifier.windows)}")
                                notifier.close_all_notifications(send_dismiss=False)
                                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 消去完了: is_showing={notifier.is_showing}")
                                
                        except json.JSONDecodeError as e:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] JSONパースエラー: {e}")
                
                async def check_dismiss():
                    while True:
                        await asyncio.sleep(0.1)
                        if notifier.should_send_dismiss:
                            try:
                                await send_dismiss_notification()
                                notifier.should_send_dismiss = False
                            except Exception as e:
                                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 消去通知送信エラー: {e}")
                                notifier.should_send_dismiss = False
                
                # 両方のタスクを実行
                await asyncio.gather(
                    receive_messages(),
                    check_dismiss()
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
        
        asyncio.run(connect_to_bot())
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] アプリケーションを終了します")
        sys.exit(0)


if __name__ == "__main__":
    main()