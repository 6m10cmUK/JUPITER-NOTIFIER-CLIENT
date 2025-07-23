"""
Test using winsdk instead of winrt
"""
import asyncio
import sys

print("Testing winsdk package for Windows notifications...")
print("-" * 60)

# Test 1: Try winsdk package
try:
    from winsdk.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus
    from winsdk.windows.ui.notifications import NotificationKinds, KnownNotificationBindings
    print("✓ winsdk import successful!")
    
    async def test_notification_access():
        try:
            # Get listener
            listener = UserNotificationListener.get_current()
            print("✓ Got UserNotificationListener instance")
            
            # Request access
            access_status = await listener.request_access_async()
            print(f"Access status: {access_status}")
            
            if access_status == UserNotificationListenerAccessStatus.ALLOWED:
                print("✓ Access granted!")
                
                # Get current notifications
                notifications = await listener.get_notifications_async(NotificationKinds.TOAST)
                print(f"Found {len(notifications)} notifications in Action Center")
                
                # Set up handler
                def handler(sender, args):
                    try:
                        notification = sender.get_notification(args.user_notification_id)
                        print("\n[NEW NOTIFICATION]")
                        if hasattr(notification, "app_info") and notification.app_info:
                            print(f"  App: {notification.app_info.display_info.display_name}")
                        
                        # Get text
                        binding = notification.notification.visual.get_binding(
                            KnownNotificationBindings.get_toast_generic()
                        )
                        if binding:
                            text_elements = binding.get_text_elements()
                            texts = []
                            it = iter(text_elements)
                            while it.has_current:
                                texts.append(it.current.text)
                                it.move_next()
                            
                            if texts:
                                print(f"  Title: {texts[0]}")
                                if len(texts) > 1:
                                    print(f"  Message: {' '.join(texts[1:])}")
                    except Exception as e:
                        print(f"Handler error: {e}")
                
                listener.add_notification_changed(handler)
                print("\n✓ Notification handler registered")
                print("Listening for notifications... (Press Ctrl+C to stop)")
                
                # Keep running
                while True:
                    await asyncio.sleep(1)
                    
            else:
                print("✗ Access denied. Please check Windows Settings > Privacy > Notifications")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Run the test
    asyncio.run(test_notification_access())
    
except ImportError as e:
    print(f"✗ winsdk not installed: {e}")
    print("\nTo install winsdk:")
    print("  pip install winsdk")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()