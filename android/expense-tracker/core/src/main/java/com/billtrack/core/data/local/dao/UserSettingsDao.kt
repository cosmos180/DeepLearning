package com.billtrack.core.data.local.dao

import androidx.room.*
import com.billtrack.core.data.local.entity.UserSettingsEntity
import kotlinx.coroutines.flow.Flow

/**
 * 用户设置DAO
 */
@Dao
interface UserSettingsDao {
    @Query("SELECT * FROM user_settings WHERE id = :id")
    fun getSettings(id: String = "default"): Flow<UserSettingsEntity?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSettings(settings: UserSettingsEntity)

    @Update
    suspend fun updateSettings(settings: UserSettingsEntity)

    @Query("UPDATE user_settings SET theme = :theme WHERE id = :id")
    suspend fun updateTheme(id: String, theme: String)

    @Query("UPDATE user_settings SET currency = :currency WHERE id = :id")
    suspend fun updateCurrency(id: String, currency: String)
}
