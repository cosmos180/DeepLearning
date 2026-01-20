package com.billtrack.core.domain.model

import java.math.BigDecimal
import java.text.DecimalFormat

/**
 * 用户设置领域模型
 *
 * @property id 唯一标识 (固定为"default")
 * @property currency 货币代码 (CNY, USD, EUR等)
 * @property decimalPlaces 小数位数 (0, 1, 2)
 * @property monthStartDay 每月起始日期 (1-31)
 * @property theme 主题 (light, dark, system)
 * @property language 语言 (zh-CN, en)
 * @property reminderEnabled 是否启用提醒
 * @property reminderTime 提醒时间 (HH:mm格式)
 */
data class UserSettings(
    val id: String = "default",
    val currency: String = "CNY",
    val decimalPlaces: Int = 2,
    val monthStartDay: Int = 1,
    val theme: String = "light",
    val language: String = "zh-CN",
    val reminderEnabled: Boolean = true,
    val reminderTime: String = "21:00"
) {
    fun formatAmount(amount: BigDecimal): String {
        val formatter = DecimalFormat().apply {
            minimumFractionDigits = decimalPlaces
            maximumFractionDigits = decimalPlaces
            groupingSize = 3
            isGroupingUsed = true
        }
        return "${getCurrencySymbol()}${formatter.format(amount)}"
    }

    private fun getCurrencySymbol(): String {
        return when (currency) {
            "CNY" -> "¥"
            "USD" -> "$"
            "EUR" -> "€"
            else -> ""
        }
    }
}
