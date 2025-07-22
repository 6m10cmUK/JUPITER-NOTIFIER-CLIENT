package com.jupiter.notifier

import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.Vibrator
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.widget.TextView
import androidx.core.content.getSystemService
import android.media.AudioManager
import android.media.ToneGenerator
import android.media.MediaPlayer
import android.media.AudioAttributes
import android.util.Log

class OverlayService : Service() {
    
    private lateinit var windowManager: WindowManager
    private var overlayView: View? = null
    private val handler = Handler(Looper.getMainLooper())
    private var toneGenerator: ToneGenerator? = null
    private var mediaPlayer: MediaPlayer? = null
    private var originalAlarmVolume: Int = 0
    
    companion object {
        private const val TAG = "OverlayService"
        private const val DISPLAY_DURATION = 0L // 0 = 無制限（タップするまで表示）
        var instance: OverlayService? = null
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        instance = this
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        intent?.let {
            val title = it.getStringExtra("title") ?: "Discord通知"
            val message = it.getStringExtra("message") ?: ""
            val sender = it.getStringExtra("sender")
            
            showOverlay(title, message, sender)
        }
        
        return START_NOT_STICKY
    }
    
    private fun showOverlay(title: String, message: String, sender: String?) {
        // 既存のオーバーレイを削除
        removeOverlay()
        
        // オーバーレイビューを作成
        val inflater = getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
        overlayView = inflater.inflate(R.layout.overlay_notification, null)
        
        // ビューの設定
        overlayView?.apply {
            findViewById<TextView>(R.id.overlayMessageText).text = message
            
            val senderTextView = findViewById<TextView>(R.id.overlaySenderText)
            if (sender != null) {
                senderTextView.text = "From: $sender"
                senderTextView.visibility = View.VISIBLE
            } else {
                senderTextView.visibility = View.GONE
            }
            
            // クリックで閉じる
            setOnClickListener {
                Log.d(TAG, "Overlay clicked, closing with dismiss notification")
                removeOverlay(sendDismiss = true)
            }
            
            // 透明度設定
            alpha = 0.65f
        }
        
        // WindowManagerのパラメータ設定
        val params = WindowManager.LayoutParams().apply {
            width = WindowManager.LayoutParams.MATCH_PARENT
            height = WindowManager.LayoutParams.MATCH_PARENT
            type = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
            } else {
                WindowManager.LayoutParams.TYPE_SYSTEM_ALERT
            }
            flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                    WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN or
                    WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS or
                    WindowManager.LayoutParams.FLAG_TRANSLUCENT_NAVIGATION or
                    WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON or
                    WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or
                    WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON
            format = PixelFormat.TRANSLUCENT
            gravity = Gravity.CENTER
        }
        
        // オーバーレイを表示
        windowManager.addView(overlayView, params)
        
        // バイブレーションとアラーム音
        vibrate()
        startAlarmSound()
        
        // 自動的に閉じるタイマーを設定（DISPLAY_DURATION = 0の場合は設定しない）
        if (DISPLAY_DURATION > 0) {
            handler.postDelayed({
                removeOverlay()
            }, DISPLAY_DURATION)
        }
    }
    
    private fun removeOverlay(sendDismiss: Boolean = false) {
        Log.d(TAG, "removeOverlay called: sendDismiss=$sendDismiss")
        overlayView?.let {
            windowManager.removeView(it)
            overlayView = null
        }
        handler.removeCallbacksAndMessages(null)
        stopAlarmSound()
        
        // 他のクライアントにも消去を通知
        if (sendDismiss) {
            Log.d(TAG, "Sending dismiss notification via WebSocketService")
            val wsInstance = WebSocketService.instance
            if (wsInstance != null) {
                wsInstance.sendDismissNotification()
            } else {
                Log.e(TAG, "WebSocketService.instance is null!")
            }
        }
    }
    
    fun dismissFromRemote() {
        Log.d(TAG, "dismissFromRemote called")
        removeOverlay(sendDismiss = false)
    }
    
    private fun startAlarmSound() {
        try {
            // アラーム音量で再生
            val audioManager = getSystemService(Context.AUDIO_SERVICE) as AudioManager
            val alarmVolume = audioManager.getStreamVolume(AudioManager.STREAM_ALARM)
            val maxVolume = audioManager.getStreamMaxVolume(AudioManager.STREAM_ALARM)
            val volumePercent = (alarmVolume.toFloat() / maxVolume.toFloat() * 100).toInt()
            
            // 音量が0の場合は音を鳴らさない
            if (volumePercent == 0) {
                Log.d(TAG, "アラーム音量が0のため、音を鳴らしません")
                return
            }
            
            // MediaPlayerを使用してシステムのアラーム音を再生
            mediaPlayer = MediaPlayer().apply {
                setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_ALARM)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                        .build()
                )
                
                // システムのデフォルトアラーム音を使用
                val alarmUri = android.media.RingtoneManager.getDefaultUri(
                    android.media.RingtoneManager.TYPE_ALARM
                ) ?: android.media.RingtoneManager.getDefaultUri(
                    android.media.RingtoneManager.TYPE_NOTIFICATION
                )
                
                setDataSource(applicationContext, alarmUri)
                isLooping = true  // ループ再生
                
                // 音量をブースト（1.5倍のゲイン）
                val gainFactor = 1.5f
                setVolume(gainFactor, gainFactor)
                
                prepare()
                start()
            }
            
            // バックアップとしてToneGeneratorも使用
            // 音量に1.5倍のゲインをかける（最大100）
            val adjustedVolume = minOf(100, (volumePercent * 1.5).toInt())
            toneGenerator = ToneGenerator(AudioManager.STREAM_ALARM, adjustedVolume)
            
            handler.post(object : Runnable {
                override fun run() {
                    toneGenerator?.startTone(ToneGenerator.TONE_CDMA_EMERGENCY_RINGBACK, 1000)
                    handler.postDelayed(this, 1050)
                }
            })
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    private fun stopAlarmSound() {
        // MediaPlayerを停止
        mediaPlayer?.let {
            if (it.isPlaying) {
                it.stop()
            }
            it.release()
        }
        mediaPlayer = null
        
        // ToneGeneratorを停止
        toneGenerator?.release()
        toneGenerator = null
    }
    
    private fun vibrate() {
        val vibrator = getSystemService<Vibrator>()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator?.vibrate(android.os.VibrationEffect.createOneShot(100, android.os.VibrationEffect.DEFAULT_AMPLITUDE))
        } else {
            @Suppress("DEPRECATION")
            vibrator?.vibrate(100)
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        removeOverlay()
        instance = null
    }
}