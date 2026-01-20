package com.billtrack.core.domain.repository

import com.billtrack.core.domain.model.Budget
import kotlinx.coroutines.flow.Flow

/**
 * 预算Repository接口
 */
interface BudgetRepository {
    /**
     * 获取月份预算列表
     */
    fun getBudgetsByMonth(month: java.time.YearMonth): Flow<List<Budget>>

    /**
     * 获取总预算
     */
    suspend fun getTotalBudget(month: java.time.YearMonth): Budget?

    /**
     * 获取分类预算
     */
    suspend fun getCategoryBudget(month: java.time.YearMonth, categoryId: String): Budget?

    /**
     * 设置总预算
     */
    suspend fun setTotalBudget(amount: java.math.BigDecimal, month: java.time.YearMonth): Result<Budget>

    /**
     * 设置分类预算
     */
    suspend fun setCategoryBudget(categoryId: String, amount: java.math.BigDecimal, month: java.time.YearMonth): Result<Budget>

    /**
     * 更新预算
     */
    suspend fun updateBudget(budget: Budget): Result<Budget>

    /**
     * 删除预算
     */
    suspend fun deleteBudget(id: String): Result<Unit>
}
