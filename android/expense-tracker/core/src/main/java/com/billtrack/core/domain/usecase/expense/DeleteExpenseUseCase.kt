package com.billtrack.core.domain.usecase.expense

import com.billtrack.core.domain.repository.ExpenseRepository
import javax.inject.Inject

/**
 * 删除消费记录用例
 */
class DeleteExpenseUseCase @Inject constructor(
    private val expenseRepository: ExpenseRepository
) {
    /**
     * 删除单条消费记录
     */
    suspend operator fun invoke(id: String): Result<Unit> {
        if (id.isBlank()) {
            return Result.failure(IllegalArgumentException("Expense ID cannot be blank"))
        }
        return expenseRepository.deleteExpense(id)
    }

    /**
     * 批量删除消费记录
     */
    suspend fun deleteMultiple(ids: List<String>): Result<Unit> {
        if (ids.isEmpty()) {
            return Result.failure(IllegalArgumentException("Expense IDs cannot be empty"))
        }
        return expenseRepository.deleteExpenses(ids)
    }
}
