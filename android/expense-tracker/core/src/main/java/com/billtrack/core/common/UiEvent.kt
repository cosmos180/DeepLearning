package com.billtrack.core.common

/**
 * 通用UI事件
 */
sealed class UiEvent {
    /**
     * 显示Toast消息
     */
    data class ShowToast(val message: String) : UiEvent()

    /**
     * 显示Snackbar消息
     */
    data class ShowSnackbar(val message: String, val action: String? = null) : UiEvent()

    /**
     * 导航返回
     */
    object NavigateBack : UiEvent()

    /**
     * 显示加载中
     */
    object ShowLoading : UiEvent()

    /**
     * 隐藏加载中
     */
    object HideLoading : UiEvent()
}
