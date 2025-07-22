package com.jupiter.notifier

import android.app.Activity
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.Vibrator
import android.view.View
import android.view.WindowManager
import android.widget.TextView
import androidx.core.content.getSystemService

class OverlayActivity : Activity() {
    
    private lateinit var messageTextView: TextView
    private lateinit var senderTextView: TextView
    private lateinit var infoTextView: TextView
    
    companion object {
        private const val DISPLAY_DURATION = 10000L // 10秒
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // フルスクリーン設定
        window.apply {
            setFlags(
                WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
                WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS
            )
            // 透明度設定 (65%)
            attributes.alpha = 0.65f
        }
        
        setContentView(R.layout.activity_overlay)
        
        // ビューの初期化
        messageTextView = findViewById(R.id.messageTextView)
        senderTextView = findViewById(R.id.senderTextView)
        infoTextView = findViewById(R.id.infoTextView)
        
        // インテントからデータを取得
        val message = intent.getStringExtra("message") ?: ""
        val sender = intent.getStringExtra("sender")
        
        // データを表示
        messageTextView.text = message
        
        if (sender != null) {
            senderTextView.text = "From: $sender"
            senderTextView.visibility = View.VISIBLE
        } else {
            senderTextView.visibility = View.GONE
        }
        
        // バイブレーション（ビープ音の代わり）
        vibrate()
        
        // クリックで閉じる
        findViewById<View>(R.id.rootLayout).setOnClickListener {
            finish()
        }
        
        // 10秒後に自動的に閉じる
        Handler(Looper.getMainLooper()).postDelayed({
            finish()
        }, DISPLAY_DURATION)
    }
    
    private fun vibrate() {
        val vibrator = getSystemService<Vibrator>()
        vibrator?.vibrate(100) // 100ミリ秒のバイブレーション
    }
    
    override fun onBackPressed() {
        // バックボタンでも閉じる
        finish()
    }
}