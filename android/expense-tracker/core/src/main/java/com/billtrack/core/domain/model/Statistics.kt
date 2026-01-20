package com.billtrack.core.domain.model

import java.math.BigDecimal
import java.time.LocalDate

/**
 * 统计数据领域模型
 *
 * @property totalExpense 总支出
 * @property expenseByCategory 分类支出
 * @property dailyTrend 每日趋势
 * @property budgetUsage 预算使用情况
 */
data class Statistics(
    val totalExpense: BigDecimal,
    val expenseByCategory: List<CategoryExpense>,
    val dailyTrend: List<DailyExpense>,
    val budgetUsage: BudgetUsage? = null
)

/**
 * 分类支出
 */
data class CategoryExpense(
    val category: Category,
    val amount: BigDecimal,
    val percentage: Float,
    val count: Int
)

/**
 * 每日支出
 */
data class DailyExpense(
    val date: LocalDate,
    val amount: BigDecimal,
    val count: Int
)
