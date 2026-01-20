package com.billtrack.core.domain.usecase.expense

import com.billtrack.core.domain.model.Expense
import com.billtrack.core.domain.repository.ExpenseRepository
import kotlinx.coroutines.flow.Flow
import java.time.LocalDateTime
import javax.inject.Inject

/**
 * 获取消费记录用例
 */
class GetExpensesUseCase @Inject constructor(
    private val expenseRepository: ExpenseRepository
) {
    /**
     * 获取所有消费记录
     */
    fun getAllExpenses(): Flow<List<Expense>> {
        return expenseRepository.getAllExpenses()
    }

    /**
     * 根据ID获取消费记录
     */
    suspend fun getExpenseById(id: String): Expense? {
        return expenseRepository.getExpenseById(id)
    }

    /**
     * 根据日期范围获取消费记录
     */
    fun getExpensesByDateRange(startDate: LocalDateTime, endDate: LocalDateTime): Flow<List<Expense>> {
        return expenseRepository.getExpensesByDateRange(startDate, endDate)
    }

    /**
     * 根据分类获取消费记录
     */
    fun getExpensesByCategory(categoryId: String): Flow<List<Expense>> {
        return expenseRepository.getExpensesByCategory(categoryId)
    }

    /**
     * 搜索消费记录
     */
    fun searchExpenses(keyword: String): Flow<List<Expense>> {
        return expenseRepository.searchExpenses(keyword)
    }

    /**
     * 获取本月消费记录
     */
    fun getCurrentMonthExpenses(): Flow<List<Expense>> {
        val now = LocalDateTime.now()
        val startOfMonth = now.withDayOfMonth(1).withHour(0).withMinute(0).withSecond(0)
        val endOfMonth = startOfMonth.plusMonths(1)
        return expenseRepository.getExpensesByDateRange(startOfMonth, endOfMonth)
    }
}
