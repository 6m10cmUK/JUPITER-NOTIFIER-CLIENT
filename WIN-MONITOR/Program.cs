using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Windows.Foundation.Metadata;
using Windows.UI.Notifications;
using Windows.UI.Notifications.Management;
using System.Net.WebSockets;
using System.Text;
using Newtonsoft.Json;
using System.Threading;

namespace NotificationMonitor
{
    class Program
    {
        private static ClientWebSocket? webSocket;
        private static readonly string wsUrl = "wss://site--jupiter-system--6qtwyp8fx6v7.code.run";
        private static HashSet<uint> knownNotificationIds = new HashSet<uint>();

        static async Task Main(string[] args)
        {
            Console.WriteLine("================================");
            Console.WriteLine("Windows Notification Monitor");
            Console.WriteLine("================================");
            Console.WriteLine();

            // Check if API is available
            if (!ApiInformation.IsTypePresent("Windows.UI.Notifications.Management.UserNotificationListener"))
            {
                Console.WriteLine("UserNotificationListener API is not available on this system.");
                return;
            }

            // Request access
            var listener = UserNotificationListener.Current;
            var accessStatus = await listener.RequestAccessAsync();

            Console.WriteLine($"Access status: {accessStatus}");

            if (accessStatus != UserNotificationListenerAccessStatus.Allowed)
            {
                Console.WriteLine("Access denied. Please enable notification access in Windows Settings:");
                Console.WriteLine("Settings > Privacy > Notifications");
                return;
            }

            // Connect to WebSocket
            await ConnectWebSocket();

            Console.WriteLine("\nMonitoring notifications...");
            Console.WriteLine("Press Ctrl+C to exit\n");

            // Initial scan
            await CheckNotifications(listener);

            // Monitor loop
            while (true)
            {
                await Task.Delay(1000); // Check every second
                await CheckNotifications(listener);
            }
        }

        static async Task CheckNotifications(UserNotificationListener listener)
        {
            try
            {
                // Get all toast notifications
                var notifications = await listener.GetNotificationsAsync(NotificationKinds.Toast);
                var currentIds = new HashSet<uint>();

                foreach (var notification in notifications)
                {
                    currentIds.Add(notification.Id);

                    // Check if this is a new notification
                    if (!knownNotificationIds.Contains(notification.Id))
                    {
                        knownNotificationIds.Add(notification.Id);

                        // Get app info
                        string appName = "Unknown";
                        string appId = "";
                        
                        if (notification.AppInfo != null)
                        {
                            appName = notification.AppInfo.DisplayInfo.DisplayName;
                            appId = notification.AppInfo.AppUserModelId;
                        }

                        // Only process Slack/Discord notifications
                        if (appId.Contains("slack", StringComparison.OrdinalIgnoreCase) || 
                            appId.Contains("discord", StringComparison.OrdinalIgnoreCase))
                        {
                            // Extract notification content
                            var (title, message) = ExtractNotificationContent(notification);

                            // Filter for specific mentions only
                            if (message.Contains("@木林ユピテル") || 
                                message.Contains("@濱出拓海_Takumi Hamade"))
                            {
                                // Display notification
                                Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] NEW NOTIFICATION");
                                Console.WriteLine($"  App: {appName} ({appId})");
                                Console.WriteLine($"  Title: {title}");
                                Console.WriteLine($"  Message: {message}");
                                Console.WriteLine($"  Time: {notification.CreationTime}");
                                Console.WriteLine("--------------------------------");

                                // Determine notification type
                                var notificationType = DetermineNotificationType(title, message);

                                // Send to WebSocket
                                await SendToWebSocket(appName, title, message, notificationType);
                            }
                        }
                    }
                }

                // Remove notifications that no longer exist
                knownNotificationIds.RemoveWhere(id => !currentIds.Contains(id));
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error checking notifications: {ex.Message}");
            }
        }

        static (string title, string message) ExtractNotificationContent(UserNotification notification)
        {
            string title = "";
            string message = "";

            try
            {
                // Get the toast binding
                var toastBinding = notification.Notification.Visual.GetBinding(KnownNotificationBindings.ToastGeneric);
                
                if (toastBinding != null)
                {
                    // Get text elements
                    var textElements = toastBinding.GetTextElements();
                    
                    // First text element is usually the title
                    var titleElement = textElements.FirstOrDefault();
                    if (titleElement != null)
                    {
                        title = titleElement.Text;
                    }

                    // Remaining elements are the body
                    var bodyElements = textElements.Skip(1);
                    message = string.Join("\n", bodyElements.Select(e => e.Text));
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error extracting content: {ex.Message}");
            }

            return (title, message);
        }

        static string DetermineNotificationType(string title, string message)
        {
            string fullText = $"{title} {message}".ToLower();

            // Check for DM patterns
            if (fullText.Contains("direct message") || 
                fullText.Contains("dm from") || 
                fullText.Contains("sent you") ||
                fullText.Contains("ダイレクトメッセージ"))
            {
                return "DM";
            }

            // Check for mention patterns
            if (fullText.Contains("mentioned") || 
                fullText.Contains("@") || 
                fullText.Contains("pinged") ||
                fullText.Contains("メンション"))
            {
                return "MENTION";
            }

            // Check for thread patterns
            if (fullText.Contains("thread") || 
                fullText.Contains("replied") ||
                fullText.Contains("スレッド"))
            {
                return "THREAD";
            }

            return "MESSAGE";
        }

        static async Task ConnectWebSocket()
        {
            try
            {
                webSocket = new ClientWebSocket();
                await webSocket.ConnectAsync(new Uri(wsUrl), CancellationToken.None);
                Console.WriteLine("Connected to WebSocket server");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"WebSocket connection failed: {ex.Message}");
                webSocket = null;
            }
        }

        static async Task SendToWebSocket(string app, string title, string message, string notificationType)
        {
            if (webSocket == null || webSocket.State != WebSocketState.Open)
            {
                await ConnectWebSocket();
            }

            if (webSocket != null && webSocket.State == WebSocketState.Open)
            {
                var data = new
                {
                    type = "notification",
                    app = app,
                    title = title,
                    message = message,
                    notification_type = notificationType,
                    timestamp = DateTime.Now.ToString("o"),
                    source = "windows_notification_listener"
                };

                var json = JsonConvert.SerializeObject(data);
                var bytes = Encoding.UTF8.GetBytes(json);

                try
                {
                    await webSocket.SendAsync(
                        new ArraySegment<byte>(bytes),
                        WebSocketMessageType.Text,
                        true,
                        CancellationToken.None
                    );
                    Console.WriteLine("[WebSocket] Notification sent");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[WebSocket] Send failed: {ex.Message}");
                    webSocket = null;
                }
            }
        }
    }
}