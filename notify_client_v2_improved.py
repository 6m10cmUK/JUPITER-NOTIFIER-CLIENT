#!/usr/bin/env python3
"""
JUPITER NOTIFIER CLIENT V2 (Improved)
Windows PC向け全画面通知クライアント（改良版）

レビューで見つかった問題を修正した改善版
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
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# .envファイルを読み込み
load_dotenv()

# 設定
WS_SERVER_URL = os.getenv('WS_SERVER_URL', 'wss://site--jupiter-system--6qtwyp8fx6v7.code.run')
DEFAULT_DURATION = 10000  # 10秒固定
BACKGROUND_COLOR = '#610610'  # 暗い赤色
MAIN_LOOP_INTERVAL = 0.05  # 50ms (CPU使用率を抑える)


class NotificationManager:
    """通知の表示を管理するクラス（シングルスレッドで動作）"""
    
    def __init__(self):
        self.root = None
        self.windows = []
        self.is_showing = False
        self.auto_close_id = None
        self.send_dismiss_callback = None
        
    def setup(self):
        """Tkinterのセットアップ（メインスレッドで実行）"""
        self.root = tk.Tk()
        self.root.withdraw()  # メインウィンドウは非表示
        logger.info("NotificationManager initialized")
        
    def show_notification(self, title, message, duration=DEFAULT_DURATION, sender=None, send_dismiss_callback=None):
        """通知を表示"""
        if self.is_showing:
            logger.info("既に通知を表示中のため、先に閉じます")
            self.close_all_notifications(send_dismiss=False)
            
        self.is_showing = True
        self.send_dismiss_callback = send_dismiss_callback
        
        # ビープ音を再生（Windowsのみ）
        try:
            winsound.Beep(1000, 100)  # 1000Hzで100ミリ秒
        except Exception as e:
            logger.warning(f"ビープ音の再生に失敗: {e}")
            
        # 全モニターの情報を取得
        try:
            monitors = screeninfo.get_monitors()
            logger.info(f"{len(monitors)}個のモニターを検出")
        except Exception as e:
            logger.warning(f"モニター情報の取得に失敗: {e}")
            monitors = [None]
            
        # 各モニターにウィンドウを作成
        for i, monitor in enumerate(monitors):
            try:
                window = tk.Toplevel(self.root)
                
                # ウィンドウタイトル
                window.title('JUPITER NOTIFICATION')
                
                # ウィンドウ設定
                window.overrideredirect(True)  # ウィンドウ枠を削除
                window.attributes('-topmost', True)
                window.attributes('-alpha', 0.65)  # 65%の透明度
                window.configure(bg=BACKGROUND_COLOR)
                
                # モニター位置に配置
                if monitor:
                    geometry = f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}"
                    window.geometry(geometry)
                    logger.debug(f"モニター{i}: {geometry}")
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
                
            except Exception as e:
                logger.error(f"ウィンドウ作成エラー (モニター{i}): {e}")
        
        # 自動的に閉じるタイマー
        if self.windows:
            self.auto_close_id = self.root.after(duration, lambda: self.close_all_notifications(send_dismiss=False))
            logger.info(f"通知を表示: {message}")
    
    def close_all_notifications(self, send_dismiss=True):
        """全ての通知ウィンドウを閉じる"""
        logger.info(f"通知を閉じます: send_dismiss={send_dismiss}")
        
        # タイマーをキャンセル
        if self.auto_close_id:
            try:
                self.root.after_cancel(self.auto_close_id)
                self.auto_close_id = None
            except Exception as e:
                logger.warning(f"タイマーキャンセルエラー: {e}")
                
        # ウィンドウを閉じる
        for i, window in enumerate(self.windows):
            try:
                window.destroy()
                logger.debug(f"ウィンドウ{i}を破棄")
            except Exception as e:
                logger.warning(f"ウィンドウ{i}の破棄エラー: {e}")
                
        self.windows = []
        self.is_showing = False
        
        # 消去通知を送信
        if send_dismiss and self.send_dismiss_callback:
            logger.info("消去通知をキューに追加")
            try:
                self.send_dismiss_callback()
            except Exception as e:
                logger.error(f"消去通知コールバックエラー: {e}")
    
    def process_events(self):
        """Tkinterのイベントを処理（定期的に呼び出す）"""
        if self.root:
            try:
                self.root.update()
            except Exception as e:
                logger.error(f"Tkinterイベント処理エラー: {e}")


async def websocket_handler(notification_queue, dismiss_queue):
    """WebSocket通信を処理"""
    logger.info("JUPITER NOTIFIER CLIENT V2 (Improved) 起動")
    logger.info(f"接続先: {WS_SERVER_URL}")
    
    while True:
        try:
            async with websockets.connect(WS_SERVER_URL) as websocket:
                logger.info("サーバーに接続しました")
                
                # 登録メッセージを送信
                await websocket.send(json.dumps({
                    "type": "register",
                    "client_type": "windows_notifier",
                    "version": "2.1.0"
                }))
                
                # 受信と送信を並行処理
                async def receive_messages():
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            
                            if data.get('type') == 'registered':
                                logger.info(f"サーバーに登録されました: {data.get('clientId')}")
                            
                            elif data.get('type') == 'notification':
                                logger.info(f"通知受信: {data.get('title')}")
                                notification_queue.put(data)
                            
                            elif data.get('type') == 'dismiss_notification':
                                logger.info(f"消去通知受信: {data.get('dismissed_by')}")
                                notification_queue.put({'type': 'dismiss'})
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"JSONパースエラー: {e}")
                
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
                                logger.info("消去通知を送信しました")
                        except Exception as e:
                            logger.error(f"消去通知送信エラー: {e}")
                
                # 両方のタスクを実行
                await asyncio.gather(
                    receive_messages(),
                    send_dismisses()
                )
                        
        except websockets.ConnectionClosed:
            logger.warning("サーバーとの接続が切断されました")
        except Exception as e:
            logger.error(f"接続エラー: {e}")
            
        logger.info("5秒後に再接続します...")
        await asyncio.sleep(5)


def main():
    """メイン関数"""
    try:
        # Windowsプラットフォームチェック
        if sys.platform != 'win32':
            logger.warning("このアプリケーションはWindows向けに設計されています")
        
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
                
                # CPU使用率を抑えるため少し待機
                loop.run_until_complete(asyncio.sleep(MAIN_LOOP_INTERVAL))
                
        except KeyboardInterrupt:
            logger.info("アプリケーションを終了します")
            websocket_task.cancel()
            
    except KeyboardInterrupt:
        logger.info("アプリケーションを終了します")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"致命的なエラー: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()