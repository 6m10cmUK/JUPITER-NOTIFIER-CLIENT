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
import subprocess
import logging
import platform

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
DEFAULT_DURATION = 30000  # 30秒固定
BACKGROUND_COLOR = '#610610'  # 暗い赤色
MAIN_LOOP_INTERVAL = 0.01  # 10ms (レスポンス向上のため短縮)


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
        
        # macOSのダークモード対応 & Dockアイコン非表示
        if platform.system() == 'Darwin':
            try:
                self.root.tk.call('tk', 'windowingsystem')  # aquaを返すはず
                # Dockにアイコンを表示しない（バックグラウンドアプリ化）
                import AppKit
                AppKit.NSApp.setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)
            except ImportError:
                logger.warning("AppKitが利用できません。Dockアイコンが表示されます。")
            except Exception as e:
                logger.warning(f"Dock非表示設定に失敗: {e}")
                
        logger.info("NotificationManager initialized")
        
    def play_notification_sound(self):
        """通知サウンドを再生"""
        try:
            # macOSのシステムサウンドを再生
            subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
        except Exception as e:
            logger.warning(f"サウンドの再生に失敗: {e}")
        
    def show_notification(self, title, message, duration=DEFAULT_DURATION, sender=None, send_dismiss_callback=None):
        """通知を表示（メインディスプレイにオーバーレイ）"""
        if self.is_showing:
            logger.info("既に通知を表示中のため、先に閉じます")
            self.close_all_notifications(send_dismiss=False)
            
        self.is_showing = True
        self.send_dismiss_callback = send_dismiss_callback
        
        # メインディスプレイにオーバーレイを作成（サウンドより先に）
        try:
            window = tk.Toplevel(self.root)
            
            # ウィンドウタイトル
            window.title('JUPITER NOTIFICATION')
            
            # メインディスプレイのサイズを取得
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            
            # フルスクリーンサイズに設定
            window_width = screen_width
            window_height = screen_height
            
            # ウィンドウを画面全体に配置
            window.geometry(f'{window_width}x{window_height}+0+0')
            
            # macOS固有の設定
            if platform.system() == 'Darwin':
                # ウィンドウを最前面に保持
                window.attributes('-topmost', True)
                # 透明度設定（Windows版と同じ0.65に）
                window.attributes('-alpha', 0.65)
                # オーバーライドリダイレクトを使用（フルスクリーンではなく）
                window.overrideredirect(True)
                # ウィンドウレベルを設定
                try:
                    # フローティングウィンドウレベル（全デスクトップで表示）
                    window.tk.call('wm', 'attributes', window._w, '-level', '3')
                except:
                    pass
            
            window.configure(bg=BACKGROUND_COLOR)
            
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
            
            # メッセージ（Windows版と同じ96サイズ）
            msg_font = font.Font(size=96, weight='bold')
            msg_label = tk.Label(
                main_frame,
                text=message,
                font=msg_font,
                fg='white',
                bg=BACKGROUND_COLOR,
                wraplength=window_width - 100,  # ウィンドウ幅に合わせて調整
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
            
            # macOSのCmd+Qでも閉じる
            window.bind('<Command-q>', lambda e: self.close_all_notifications(send_dismiss=True))
            
            self.windows.append(window)
            
            # ウィンドウを最前面に持ってくる（即座に表示）
            window.lift()
            window.focus_force()
            window.update_idletasks()  # 即座に描画を更新
            
        except Exception as e:
            logger.error(f"ウィンドウ作成エラー: {e}")
        
        # 自動的に閉じるタイマー
        if self.windows:
            self.auto_close_id = self.root.after(duration, lambda: self.close_all_notifications(send_dismiss=False))
            logger.info(f"通知を表示: {message}")
            
        # サウンドを最後に再生（表示を優先）
        self.play_notification_sound()
    
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
    logger.info("JUPITER NOTIFIER CLIENT for macOS 起動")
    logger.info(f"接続先: {WS_SERVER_URL}")
    
    while True:
        try:
            async with websockets.connect(WS_SERVER_URL) as websocket:
                logger.info("サーバーに接続しました")
                
                # 登録メッセージを送信
                await websocket.send(json.dumps({
                    "type": "register",
                    "client_type": "macos_notifier",
                    "version": "1.0.0"
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
                                    "client_type": "macos_notifier"
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


def check_permissions():
    """macOSの権限をチェック"""
    if platform.system() != 'Darwin':
        return
        
    logger.info("macOSの権限をチェックしています...")
    
    # tkinterのみを使用するため、特別な権限チェックは不要
    logger.info("tkinterベースの通知システムを使用します")


def main():
    """メイン関数"""
    try:
        # macOSプラットフォームチェック
        if platform.system() != 'Darwin':
            logger.warning("このアプリケーションはmacOS向けに設計されています")
            response = input("続行しますか？ (y/n): ")
            if response.lower() != 'y':
                sys.exit(0)
        
        # 権限チェック
        check_permissions()
        
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
                    else:
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