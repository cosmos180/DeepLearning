package com.billtrack.data.repository

import com.billtrack.core.data.local.dao.UserSettingsDao
import com.billtrack.core.data.local.entity.UserSettingsEntity
import com.billtrack.core.domain.model.UserSettings
import com.billtrack.core.domain.repository.UserSettingsRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

/**
 * 用户设置Repository实现
 */
class UserSettingsRepositoryImpl @Inject constructor(
    private val userSettingsDao: UserSettingsDao
) : UserSettingsRepository {

    override fun getSettings(): Flow<UserSettings> {
        return userSettingsDao.getSettings().map { entity ->
            entity?.toDomainModel() ?: UserSettingsEntity().toDomainModel()
        }
    }

    override suspend fun updateSettings(settings: UserSettings): Result<UserSettings> {
        return try {
            val entity = UserSettingsEntity.fromDomainModel(settings)
            userSettingsDao.updateSettings(entity)
            Result.success(settings)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateTheme(theme: String): Result<Unit> {
        return try {
            userSettingsDao.updateTheme("default", theme)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateCurrency(currency: String): Result<Unit> {
        return try {
            userSettingsDao.updateCurrency("default", currency)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
