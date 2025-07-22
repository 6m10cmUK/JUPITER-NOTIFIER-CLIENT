package com.jupiter.notifier

import android.app.*
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import okhttp3.*
import okio.ByteString
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class WebSocketService : Service() {
    
    private var webSocket: WebSocket? = null
    private lateinit var client: OkHttpClient
    private var wsUrl: String = ""
    
    companion object {
        private const val TAG = "WebSocketService"
        private const val CHANNEL_ID = "jupiter_notifier_channel"
        private const val NOTIFICATION_ID = 1
        var isRunning = false
            private set
        var instance: WebSocketService? = null
    }
    
    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Service created")
        createNotificationChannel()
        instance = this
        
        client = OkHttpClient.Builder()
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "Service started")
        
        wsUrl = intent?.getStringExtra("ws_url") ?: ""
        if (wsUrl.isEmpty()) {
            val prefs = getSharedPreferences("JupiterNotifierPrefs", MODE_PRIVATE)
            wsUrl = prefs.getString("ws_url", "wss://site--jupiter-system--6qtwyp8fx6v7.code.run") ?: ""
        }
        
        // Android 13以降の通知権限チェック
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) 
                != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                Log.e(TAG, "Notification permission not granted")
                stopSelf()
                return START_NOT_STICKY
            }
        }
        
        startForeground(NOTIFICATION_ID, createNotification())
        isRunning = true
        
        connectWebSocket()
        
        return START_STICKY
    }
    
    private fun connectWebSocket() {
        Log.d(TAG, "Connecting to: $wsUrl")
        
        val request = Request.Builder()
            .url(wsUrl)
            .build()
        
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.d(TAG, "WebSocket connected")
                
                // 登録メッセージを送信
                val registerMessage = JSONObject().apply {
                    put("type", "register")
                    put("client_type", "android_notifier")
                    put("version", "1.0.0")
                }
                webSocket.send(registerMessage.toString())
            }
            
            override fun onMessage(webSocket: WebSocket, text: String) {
                Log.d(TAG, "Message received: $text")
                handleMessage(text)
            }
            
            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                Log.d(TAG, "Bytes received")
            }
            
            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                Log.d(TAG, "WebSocket closing: $code / $reason")
                webSocket.close(1000, null)
            }
            
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e(TAG, "WebSocket error", t)
                // 5秒後に再接続
                Thread.sleep(5000)
                connectWebSocket()
            }
        })
    }
    
    private fun handleMessage(message: String) {
        try {
            val json = JSONObject(message)
            val type = json.optString("type")
            
            when (type) {
                "registered" -> {
                    Log.d(TAG, "Registered with server: ${json.optString("clientId")}")
                }
                "notification" -> {
                    val title = json.optString("title", "Discord通知")
                    val msg = json.optString("message", "")
                    val sender = json.optString("sender", null)
                    
                    showOverlayNotification(title, msg, sender)
                }
                "dismiss_notification" -> {
                    Log.d(TAG, "Dismiss notification from: ${json.optString("dismissed_by")}")
                    OverlayService.instance?.dismissFromRemote()
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error handling message", e)
        }
    }
    
    private fun showOverlayNotification(title: String, message: String, sender: String?) {
        val intent = Intent(this, OverlayService::class.java).apply {
            putExtra("title", title)
            putExtra("message", message)
            putExtra("sender", sender)
        }
        startService(intent)
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Jupiter Notifier Service",
                NotificationManager.IMPORTANCE_MIN  // 最小の重要度で静かに
            ).apply {
                description = "WebSocket接続を維持するための通知"
                setShowBadge(false)
            }
            
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 
            0, 
            intent, 
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Jupiter Notifier")
            .setContentText("Discord通知を待機中...")
            .setSmallIcon(android.R.drawable.ic_menu_info_details)
            .setPriority(NotificationCompat.PRIORITY_MIN)
            .setOngoing(true)  // 消せない通知
            .setContentIntent(pendingIntent)  // タップでアプリを開く
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .build()
    }
    
    fun sendDismissNotification() {
        try {
            val message = JSONObject().apply {
                put("type", "dismiss_notification")
                put("client_type", "android_notifier")
            }
            webSocket?.send(message.toString())
            Log.d(TAG, "Sent dismiss notification")
        } catch (e: Exception) {
            Log.e(TAG, "Error sending dismiss notification", e)
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "Service destroyed - attempting restart")
        isRunning = false
        instance = null
        webSocket?.close(1000, "Service stopped")
        
        // サービスが強制終了された場合、自動で再起動
        val prefs = getSharedPreferences("JupiterNotifierPrefs", MODE_PRIVATE)
        val shouldAutoStart = prefs.getBoolean("auto_start_service", false)
        if (shouldAutoStart) {
            val restartIntent = Intent(this, WebSocketService::class.java)
            val pendingIntent = PendingIntent.getService(
                this,
                1,
                restartIntent,
                PendingIntent.FLAG_ONE_SHOT or PendingIntent.FLAG_IMMUTABLE
            )
            
            val alarmManager = getSystemService(Context.ALARM_SERVICE) as AlarmManager
            alarmManager.set(
                AlarmManager.RTC_WAKEUP,
                System.currentTimeMillis() + 1000,  // 1秒後に再起動
                pendingIntent
            )
        }
    }
    
    override fun onTaskRemoved(rootIntent: Intent?) {
        super.onTaskRemoved(rootIntent)
        Log.d(TAG, "Task removed - service will continue running")
        // タスクが削除されても、サービスは継続
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
}