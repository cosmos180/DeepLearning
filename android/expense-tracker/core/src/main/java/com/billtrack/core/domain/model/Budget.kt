package com.billtrack.core.domain.model

import java.math.BigDecimal
import java.time.LocalDateTime
import java.time.YearMonth
import java.util.UUID

/**
 * 预算领域模型
 *
 * @property id 唯一标识
 * @property categoryId 分类ID (null表示总预算)
 * @property category 分类(关联查询时填充)
 * @property amount 预算金额
 * @property month 月份
 * @property createdAt 创建时间
 * @property updatedAt 更新时间
 */
data class Budget(
    val id: String,
    val categoryId: String? = null,
    val category: Category? = null,
    val amount: BigDecimal,
    val month: YearMonth,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime
) {
    val isTotalBudget: Boolean
        get() = categoryId == null

    companion object {
        fun createTotalBudget(
            amount: BigDecimal,
            month: YearMonth
        ): Budget {
            val now = LocalDateTime.now()
            return Budget(
                id = UUID.randomUUID().toString(),
                categoryId = null,
                amount = amount,
                month = month,
                createdAt = now,
                updatedAt = now
            )
        }

        fun createCategoryBudget(
            categoryId: String,
            amount: BigDecimal,
            month: YearMonth
        ): Budget {
            val now = LocalDateTime.now()
            return Budget(
                id = UUID.randomUUID().toString(),
                categoryId = categoryId,
                amount = amount,
                month = month,
                createdAt = now,
                updatedAt = now
            )
        }
    }
}

/**
 * 预算使用情况
 */
data class BudgetUsage(
    val budget: Budget,
    val used: BigDecimal,
    val remaining: BigDecimal,
    val percentage: Float,
    val status: BudgetStatus
)

/**
 * 预算状态
 */
enum class BudgetStatus {
    HEALTHY,    // < 50%
    ATTENTION,  // 50% - 80%
    WARNING,    // 80% - 100%
    OVERBUDGET  // > 100%
}
