package com.billtrack.app

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * 账单通应用类
 */
@HiltAndroidApp
class BillTrackApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        // 初始化工作在ApplicationModule中完成
    }
}
