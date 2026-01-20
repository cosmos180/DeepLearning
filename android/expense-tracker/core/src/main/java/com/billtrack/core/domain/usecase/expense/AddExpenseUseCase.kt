package com.billtrack.core.domain.usecase.expense

import com.billtrack.core.domain.model.Expense
import com.billtrack.core.domain.repository.ExpenseRepository
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.UUID
import javax.inject.Inject

/**
 * 添加消费记录用例
 */
class AddExpenseUseCase @Inject constructor(
    private val expenseRepository: ExpenseRepository
) {
    suspend operator fun invoke(
        amount: BigDecimal,
        categoryId: String,
        date: LocalDateTime = LocalDateTime.now(),
        note: String? = null,
        paymentMethod: String? = null
    ): Result<Expense> {
        // 验证金额
        if (amount <= BigDecimal.ZERO) {
            return Result.failure(IllegalArgumentException("Amount must be greater than zero"))
        }

        // 创建消费记录
        val expense = Expense.create(
            amount = amount,
            categoryId = categoryId,
            date = date,
            note = note,
            paymentMethod = paymentMethod
        )

        return expenseRepository.insertExpense(expense)
    }
}
