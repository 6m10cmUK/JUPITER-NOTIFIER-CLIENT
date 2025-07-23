package com.jupiter.notifier

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.EditText
import android.widget.Switch
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.NotificationManagerCompat
import android.Manifest
import android.content.pm.PackageManager
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import android.os.PowerManager

class MainActivity : AppCompatActivity() {
    
    private lateinit var urlEditText: EditText
    private lateinit var serviceSwitch: Switch
    private lateinit var overlayPermissionButton: Button
    
    companion object {
        private const val OVERLAY_PERMISSION_REQUEST_CODE = 1001
        private const val NOTIFICATION_PERMISSION_REQUEST_CODE = 1002
        private const val BATTERY_OPTIMIZATION_REQUEST_CODE = 1003
        private const val PREFS_NAME = "JupiterNotifierPrefs"
        private const val KEY_WS_URL = "ws_url"
        private const val DEFAULT_WS_URL = "wss://site--jupiter-system--6qtwyp8fx6v7.code.run"
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // ビューの初期化
        urlEditText = findViewById(R.id.urlEditText)
        serviceSwitch = findViewById(R.id.serviceSwitch)
        overlayPermissionButton = findViewById(R.id.overlayPermissionButton)
        
        // 保存されたURLを読み込む
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        urlEditText.setText(prefs.getString(KEY_WS_URL, DEFAULT_WS_URL))
        
        // サービスの状態を確認
        updateServiceSwitch()
        
        // オーバーレイ権限ボタン
        overlayPermissionButton.setOnClickListener {
            requestOverlayPermission()
        }
        
        // サービススイッチ
        serviceSwitch.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                startWebSocketService()
            } else {
                stopWebSocketService()
            }
        }
        
        // 権限の確認
        checkPermissions()
    }
    
    private fun checkPermissions() {
        var allPermissionsGranted = true
        
        // オーバーレイ権限
        if (!Settings.canDrawOverlays(this)) {
            overlayPermissionButton.isEnabled = true
            allPermissionsGranted = false
            Toast.makeText(this, "オーバーレイ権限が必要です", Toast.LENGTH_LONG).show()
        } else {
            overlayPermissionButton.isEnabled = false
        }
        
        // 通知権限（Android 13以上）
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) 
                != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                    NOTIFICATION_PERMISSION_REQUEST_CODE
                )
                allPermissionsGranted = false
            }
        }
        
        // バッテリー最適化の無効化を確認
        checkBatteryOptimization()
        
        serviceSwitch.isEnabled = allPermissionsGranted
    }
    
    private fun checkBatteryOptimization() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val powerManager = getSystemService(POWER_SERVICE) as PowerManager
            if (!powerManager.isIgnoringBatteryOptimizations(packageName)) {
                // バッテリー最適化を無効にするダイアログを表示
                val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
                    data = Uri.parse("package:$packageName")
                }
                startActivityForResult(intent, BATTERY_OPTIMIZATION_REQUEST_CODE)
            }
        }
    }
    
    private fun requestOverlayPermission() {
        val intent = Intent(
            Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
            Uri.parse("package:$packageName")
        )
        startActivityForResult(intent, OVERLAY_PERMISSION_REQUEST_CODE)
    }
    
    private fun startWebSocketService() {
        // URLと自動起動フラグを保存
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        prefs.edit()
            .putString(KEY_WS_URL, urlEditText.text.toString())
            .putBoolean("auto_start_service", true)
            .apply()
        
        // サービスを開始
        val intent = Intent(this, WebSocketService::class.java).apply {
            putExtra("ws_url", urlEditText.text.toString())
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        
        Toast.makeText(this, "通知サービスを開始しました", Toast.LENGTH_SHORT).show()
    }
    
    private fun stopWebSocketService() {
        // 自動起動フラグをクリア
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        prefs.edit().putBoolean("auto_start_service", false).apply()
        
        stopService(Intent(this, WebSocketService::class.java))
        Toast.makeText(this, "通知サービスを停止しました", Toast.LENGTH_SHORT).show()
    }
    
    private fun updateServiceSwitch() {
        // サービスが実行中かチェックする実装
        serviceSwitch.isChecked = WebSocketService.isRunning
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == OVERLAY_PERMISSION_REQUEST_CODE) {
            checkPermissions()
        }
    }
    
    override fun onResume() {
        super.onResume()
        checkPermissions()
        updateServiceSwitch()
        
        // サービスが停止していたら自動で再起動
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        val shouldAutoStart = prefs.getBoolean("auto_start_service", false)
        if (shouldAutoStart && !WebSocketService.isRunning && serviceSwitch.isEnabled) {
            startWebSocketService()
        }
    }
    
    override fun onBackPressed() {
        // バックボタンでアプリを閉じても、サービスは継続
        if (WebSocketService.isRunning) {
            Toast.makeText(this, "通知サービスはバックグラウンドで継続します", Toast.LENGTH_SHORT).show()
        }
        super.onBackPressed()
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == NOTIFICATION_PERMISSION_REQUEST_CODE) {
            checkPermissions()
        }
    }
}