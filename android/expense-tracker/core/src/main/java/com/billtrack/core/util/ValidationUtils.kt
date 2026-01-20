package com.billtrack.core.util

import java.math.BigDecimal

/**
 * 验证工具
 */
object ValidationUtils {
    /**
     * 验证金额
     */
    fun validateAmount(amount: BigDecimal?): ValidationResult {
        return when {
            amount == null -> ValidationResult.Error("请输入金额")
            amount <= BigDecimal.ZERO -> ValidationResult.Error("金额必须大于0")
            amount.scale() > 2 -> ValidationResult.Error("最多支持两位小数")
            else -> ValidationResult.Success
        }
    }

    /**
     * 验证分类名称
     */
    fun validateCategoryName(name: String?): ValidationResult {
        return when {
            name.isNullOrBlank() -> ValidationResult.Error("请输入分类名称")
            name.length > 10 -> ValidationResult.Error("分类名称不能超过10个字符")
            else -> ValidationResult.Success
        }
    }

    /**
     * 验证备注
     */
    fun validateNote(note: String?): ValidationResult {
        return when {
            note != null && note.length > 50 -> ValidationResult.Error("备注不能超过50个字符")
            else -> ValidationResult.Success
        }
    }
}

/**
 * 验证结果
 */
sealed class ValidationResult {
    object Success : ValidationResult()
    data class Error(val message: String) : ValidationResult()
}
