package com.billtrack.core.common

/**
 * UI文本封装
 * 支持字符串资源和动态字符串
 */
sealed class UiText {
    /**
     * 动态字符串
     */
    data class DynamicString(val value: String) : UiText()

    /**
     * 字符串资源
     */
    data class StringResource(val resId: Int) : UiText()

    /**
     * 格式化字符串资源
     */
    data class PluralResource(val resId: Int, val count: Int) : UiText()
}
