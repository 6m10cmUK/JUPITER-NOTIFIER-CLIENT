#!/usr/bin/env python3
"""
通知テストスクリプト
ローカルで通知の表示/非表示をテストする
"""

import time
from notify_client import FullScreenNotification

def test_notifications():
    notifier = FullScreenNotification()
    
    print("テスト1: 最初の通知")
    notifier.show_notification("テスト1", "最初の通知です", 5000)
    time.sleep(2)
    
    print("\nテスト2: 手動で閉じる")
    notifier.close_all_notifications(send_dismiss=False)
    time.sleep(1)
    
    print("\nテスト3: 2回目の通知")
    notifier.show_notification("テスト2", "2回目の通知です", 5000)
    time.sleep(2)
    
    print("\nテスト4: 再度手動で閉じる")
    notifier.close_all_notifications(send_dismiss=False)
    time.sleep(1)
    
    print("\nテスト5: 3回目の通知")
    notifier.show_notification("テスト3", "3回目の通知です", 5000)
    time.sleep(6)
    
    print("\nテスト完了")

if __name__ == "__main__":
    test_notifications()