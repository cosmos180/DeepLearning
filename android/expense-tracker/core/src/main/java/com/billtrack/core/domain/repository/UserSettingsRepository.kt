package com.billtrack.core.domain.repository

import com.billtrack.core.domain.model.UserSettings
import kotlinx.coroutines.flow.Flow

/**
 * 用户设置Repository接口
 */
interface UserSettingsRepository {
    /**
     * 获取用户设置
     */
    fun getSettings(): Flow<UserSettings>

    /**
     * 更新用户设置
     */
    suspend fun updateSettings(settings: UserSettings): Result<UserSettings>

    /**
     * 更新主题
     */
    suspend fun updateTheme(theme: String): Result<Unit>

    /**
     * 更新货币
     */
    suspend fun updateCurrency(currency: String): Result<Unit>
}
