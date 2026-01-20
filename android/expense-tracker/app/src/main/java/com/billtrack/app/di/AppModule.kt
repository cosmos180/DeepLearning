package com.billtrack.app.di

import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent

/**
 * 应用模块
 * 提供应用级别的依赖
 */
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    // Hilt will automatically provide all dependencies marked with @Inject
    // DatabaseInitializer is already injectable via its @Inject constructor
}
