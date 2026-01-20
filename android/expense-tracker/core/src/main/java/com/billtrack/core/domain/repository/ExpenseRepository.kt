package com.billtrack.core.domain.repository

import com.billtrack.core.domain.model.Expense
import kotlinx.coroutines.flow.Flow

/**
 * 消费记录Repository接口
 */
interface ExpenseRepository {
    /**
     * 获取所有消费记录
     */
    fun getAllExpenses(): Flow<List<Expense>>

    /**
     * 根据ID获取消费记录
     */
    suspend fun getExpenseById(id: String): Expense?

    /**
     * 根据日期范围获取消费记录
     */
    fun getExpensesByDateRange(startDate: java.time.LocalDateTime, endDate: java.time.LocalDateTime): Flow<List<Expense>>

    /**
     * 根据分类获取消费记录
     */
    fun getExpensesByCategory(categoryId: String): Flow<List<Expense>>

    /**
     * 搜索消费记录
     */
    fun searchExpenses(keyword: String): Flow<List<Expense>>

    /**
     * 插入消费记录
     */
    suspend fun insertExpense(expense: Expense): Result<Expense>

    /**
     * 更新消费记录
     */
    suspend fun updateExpense(expense: Expense): Result<Expense>

    /**
     * 删除消费记录
     */
    suspend fun deleteExpense(id: String): Result<Unit>

    /**
     * 批量删除消费记录
     */
    suspend fun deleteExpenses(ids: List<String>): Result<Unit>

    /**
     * 获取总支出
     */
    suspend fun getTotalExpense(startDate: java.time.LocalDateTime, endDate: java.time.LocalDateTime): java.math.BigDecimal?

    /**
     * 获取分类支出统计
     */
    suspend fun getExpenseByCategory(startDate: java.time.LocalDateTime, endDate: java.time.LocalDateTime): List<CategoryExpenseStat>

    /**
     * 获取每日趋势
     */
    suspend fun getDailyTrend(startDate: java.time.LocalDateTime, endDate: java.time.LocalDateTime): List<DailyExpenseStat>
}

/**
 * 分类支出统计
 */
data class CategoryExpenseStat(
    val categoryId: String,
    val total: java.math.BigDecimal,
    val count: Int
)

/**
 * 每日支出统计
 */
data class DailyExpenseStat(
    val date: java.time.LocalDateTime,
    val total: java.math.BigDecimal,
    val count: Int
)
