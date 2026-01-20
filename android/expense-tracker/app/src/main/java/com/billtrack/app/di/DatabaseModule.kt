package com.billtrack.app.di

import android.content.Context
import com.billtrack.data.local.AppDatabase
import com.billtrack.data.local.DatabaseInitializer
import com.billtrack.core.data.local.dao.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * 数据库模块
 */
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideAppDatabase(
        @ApplicationContext context: Context
    ): AppDatabase {
        return AppDatabase.getInstance(context)
    }

    @Provides
    fun provideExpenseDao(database: AppDatabase): ExpenseDao {
        return database.expenseDao()
    }

    @Provides
    fun provideCategoryDao(database: AppDatabase): CategoryDao {
        return database.categoryDao()
    }

    @Provides
    fun provideBudgetDao(database: AppDatabase): BudgetDao {
        return database.budgetDao()
    }

    @Provides
    fun provideUserSettingsDao(database: AppDatabase): UserSettingsDao {
        return database.userSettingsDao()
    }

    @Provides
    @Singleton
    fun provideDatabaseInitializer(
        database: AppDatabase,
        categoryDao: CategoryDao
    ): DatabaseInitializer {
        return DatabaseInitializer(database, categoryDao)
    }
}
