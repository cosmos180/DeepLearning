package com.billtrack.app.di

import com.billtrack.core.domain.repository.CategoryRepository
import com.billtrack.core.domain.repository.BudgetRepository
import com.billtrack.core.domain.repository.ExpenseRepository
import com.billtrack.core.domain.repository.UserSettingsRepository
import com.billtrack.data.repository.CategoryRepositoryImpl
import com.billtrack.data.repository.BudgetRepositoryImpl
import com.billtrack.data.repository.ExpenseRepositoryImpl
import com.billtrack.data.repository.UserSettingsRepositoryImpl
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Repository依赖注入模块
 */
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindExpenseRepository(
        expenseRepositoryImpl: ExpenseRepositoryImpl
    ): ExpenseRepository

    @Binds
    @Singleton
    abstract fun bindCategoryRepository(
        categoryRepositoryImpl: CategoryRepositoryImpl
    ): CategoryRepository

    @Binds
    @Singleton
    abstract fun bindBudgetRepository(
        budgetRepositoryImpl: BudgetRepositoryImpl
    ): BudgetRepository

    @Binds
    @Singleton
    abstract fun bindUserSettingsRepository(
        userSettingsRepositoryImpl: UserSettingsRepositoryImpl
    ): UserSettingsRepository
}
