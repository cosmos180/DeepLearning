package com.billtrack.core.domain.usecase.expense

import com.billtrack.core.domain.repository.CategoryExpenseStat
import com.billtrack.core.domain.repository.DailyExpenseStat
import com.billtrack.core.domain.repository.ExpenseRepository
import java.math.BigDecimal
import java.time.LocalDateTime
import javax.inject.Inject

/**
 * 获取统计数据用例
 */
class GetStatisticsUseCase @Inject constructor(
    private val expenseRepository: ExpenseRepository
) {
    /**
     * 获取总支出
     */
    suspend fun getTotalExpense(
        startDate: LocalDateTime = LocalDateTime.now().withDayOfMonth(1).withHour(0).withMinute(0),
        endDate: LocalDateTime = startDate.plusMonths(1)
    ): BigDecimal? {
        return expenseRepository.getTotalExpense(startDate, endDate)
    }

    /**
     * 获取本月总支出
     */
    suspend fun getCurrentMonthTotal(): BigDecimal? {
        val now = LocalDateTime.now()
        val startOfMonth = now.withDayOfMonth(1).withHour(0).withMinute(0)
        val endOfMonth = startOfMonth.plusMonths(1)
        return expenseRepository.getTotalExpense(startOfMonth, endOfMonth)
    }

    /**
     * 获取分类支出统计
     */
    suspend fun getCategoryExpenses(
        startDate: LocalDateTime = LocalDateTime.now().withDayOfMonth(1).withHour(0).withMinute(0),
        endDate: LocalDateTime = startDate.plusMonths(1)
    ): List<CategoryExpenseStat> {
        return expenseRepository.getExpenseByCategory(startDate, endDate)
    }

    /**
     * 获取本月分类支出统计
     */
    suspend fun getCurrentMonthCategoryExpenses(): List<CategoryExpenseStat> {
        val now = LocalDateTime.now()
        val startOfMonth = now.withDayOfMonth(1).withHour(0).withMinute(0)
        val endOfMonth = startOfMonth.plusMonths(1)
        return expenseRepository.getExpenseByCategory(startOfMonth, endOfMonth)
    }

    /**
     * 获取每日支出趋势
     */
    suspend fun getDailyTrend(
        startDate: LocalDateTime = LocalDateTime.now().withDayOfMonth(1).withHour(0).withMinute(0),
        endDate: LocalDateTime = startDate.plusMonths(1)
    ): List<DailyExpenseStat> {
        return expenseRepository.getDailyTrend(startDate, endDate)
    }

    /**
     * 获取本月每日支出趋势
     */
    suspend fun getCurrentMonthDailyTrend(): List<DailyExpenseStat> {
        val now = LocalDateTime.now()
        val startOfMonth = now.withDayOfMonth(1).withHour(0).withMinute(0)
        val endOfMonth = startOfMonth.plusMonths(1)
        return expenseRepository.getDailyTrend(startOfMonth, endOfMonth)
    }
}
