package com.billtrack.core.domain.model

import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.UUID

/**
 * 消费记录领域模型
 *
 * @property id 唯一标识
 * @property amount 金额
 * @property categoryId 分类ID
 * @property category 分类(关联查询时填充)
 * @property date 消费日期时间
 * @property note 备注
 * @property paymentMethod 支付方式
 * @property createdAt 创建时间
 * @property updatedAt 更新时间
 */
data class Expense(
    val id: String,
    val amount: BigDecimal,
    val categoryId: String,
    val category: Category? = null,
    val date: LocalDateTime,
    val note: String? = null,
    val paymentMethod: String? = null,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime
) {
    companion object {
        fun create(
            amount: BigDecimal,
            categoryId: String,
            date: LocalDateTime = LocalDateTime.now(),
            note: String? = null,
            paymentMethod: String? = null
        ): Expense {
            val now = LocalDateTime.now()
            return Expense(
                id = UUID.randomUUID().toString(),
                amount = amount,
                categoryId = categoryId,
                date = date,
                note = note,
                paymentMethod = paymentMethod,
                createdAt = now,
                updatedAt = now
            )
        }
    }
}
