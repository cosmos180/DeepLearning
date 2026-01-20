package com.billtrack.core.domain.usecase.expense

import com.billtrack.core.domain.model.Expense
import com.billtrack.core.domain.repository.ExpenseRepository
import java.math.BigDecimal
import javax.inject.Inject

/**
 * 更新消费记录用例
 */
class UpdateExpenseUseCase @Inject constructor(
    private val expenseRepository: ExpenseRepository
) {
    suspend operator fun invoke(
        id: String,
        amount: BigDecimal? = null,
        categoryId: String? = null,
        date: java.time.LocalDateTime? = null,
        note: String? = null,
        paymentMethod: String? = null
    ): Result<Expense> {
        // 获取现有记录
        val existingExpense = expenseRepository.getExpenseById(id)
            ?: return Result.failure(IllegalArgumentException("Expense not found"))

        // 验证金额
        val newAmount = amount ?: existingExpense.amount
        if (newAmount <= BigDecimal.ZERO) {
            return Result.failure(IllegalArgumentException("Amount must be greater than zero"))
        }

        // 创建更新后的记录
        val updatedExpense = existingExpense.copy(
            amount = newAmount,
            categoryId = categoryId ?: existingExpense.categoryId,
            date = date ?: existingExpense.date,
            note = note,
            paymentMethod = paymentMethod ?: existingExpense.paymentMethod,
            updatedAt = java.time.LocalDateTime.now()
        )

        return expenseRepository.updateExpense(updatedExpense)
    }

    /**
     * 直接更新消费记录
     */
    suspend fun update(expense: Expense): Result<Expense> {
        if (expense.amount <= BigDecimal.ZERO) {
            return Result.failure(IllegalArgumentException("Amount must be greater than zero"))
        }
        return expenseRepository.updateExpense(expense)
    }
}
