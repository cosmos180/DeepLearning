package com.billtrack.core.util

import java.math.BigDecimal
import java.math.RoundingMode

/**
 * 货币格式化工具
 */
object CurrencyUtils {
    /**
     * 格式化金额
     */
    fun formatAmount(
        amount: BigDecimal,
        currencySymbol: String = "¥",
        decimalPlaces: Int = 2
    ): String {
        val formattedAmount = amount.setScale(decimalPlaces, RoundingMode.HALF_UP)
        val pattern = if (decimalPlaces > 0) {
            "###,##0.${"0".repeat(decimalPlaces)}"
        } else {
            "###,##0"
        }
        val formatter = java.text.DecimalFormat(pattern)
        return "$currencySymbol${formatter.format(formattedAmount)}"
    }

    /**
     * 格式化金额（别名）
     */
    fun formatCurrency(amount: BigDecimal): String = formatAmount(amount)

    /**
     * 解析金额字符串
     */
    fun parseAmount(amountStr: String): BigDecimal? {
        return try {
            val cleanStr = amountStr.replace("[^0-9.]".toRegex(), "")
            if (cleanStr.isEmpty()) null
            else BigDecimal(cleanStr)
        } catch (e: Exception) {
            null
        }
    }
}
