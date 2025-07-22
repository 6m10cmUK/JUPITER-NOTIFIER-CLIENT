package com.jupiter.notifier

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log

class BootReceiver : BroadcastReceiver() {
    
    companion object {
        private const val TAG = "BootReceiver"
    }
    
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            Log.d(TAG, "Boot completed, checking auto-start preference")
            
            val prefs = context.getSharedPreferences("JupiterNotifierPrefs", Context.MODE_PRIVATE)
            val autoStart = prefs.getBoolean("auto_start_service", false)
            
            if (autoStart) {
                Log.d(TAG, "Auto-start enabled, starting service")
                
                // 権限チェック
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && 
                    !android.provider.Settings.canDrawOverlays(context)) {
                    Log.e(TAG, "Overlay permission not granted, cannot start service")
                    return
                }
                
                val serviceIntent = Intent(context, WebSocketService::class.java)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    context.startForegroundService(serviceIntent)
                } else {
                    context.startService(serviceIntent)
                }
            } else {
                Log.d(TAG, "Auto-start disabled")
            }
        }
    }
}