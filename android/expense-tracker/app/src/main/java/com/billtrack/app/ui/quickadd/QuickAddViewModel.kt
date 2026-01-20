package com.billtrack.app.ui.quickadd

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.billtrack.core.domain.model.Category
import com.billtrack.core.domain.usecase.category.GetCategoriesUseCase
import com.billtrack.core.domain.usecase.expense.AddExpenseUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.math.BigDecimal
import java.time.LocalDateTime
import javax.inject.Inject

/**
 * 快速记账ViewModel
 */
@HiltViewModel
class QuickAddViewModel @Inject constructor(
    private val addExpenseUseCase: AddExpenseUseCase,
    private val getCategoriesUseCase: GetCategoriesUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(QuickAddUiState())
    val uiState: StateFlow<QuickAddUiState> = _uiState.asStateFlow()

    private val _events = MutableSharedFlow<QuickAddUiEvent>()
    val events: SharedFlow<QuickAddUiEvent> = _events.asSharedFlow()

    init {
        loadCategories()
    }

    /**
     * 加载分类列表
     */
    private fun loadCategories() {
        viewModelScope.launch {
            getCategoriesUseCase.getRootCategories()
                .collect { categories ->
                    _uiState.update { it.copy(categories = categories) }
                }
        }
    }

    /**
     * 更新金额
     */
    fun updateAmount(amount: String) {
        _uiState.update { it.copy(amount = amount) }
    }

    /**
     * 选择分类
     */
    fun selectCategory(category: Category) {
        _uiState.update { it.copy(selectedCategory = category) }
    }

    /**
     * 更新备注
     */
    fun updateNote(note: String) {
        _uiState.update { it.copy(note = note) }
    }

    /**
     * 更新日期
     */
    fun updateDate(date: LocalDateTime) {
        _uiState.update { it.copy(date = date) }
    }

    /**
     * 更新支付方式
     */
    fun updatePaymentMethod(method: String) {
        _uiState.update { it.copy(paymentMethod = method) }
    }

    /**
     * 保存消费记录
     */
    fun saveExpense() {
        val state = _uiState.value

        // 验证输入
        if (state.amount.isBlank()) {
            viewModelScope.launch {
                _events.emit(QuickAddUiEvent.ShowError("请输入金额"))
            }
            return
        }

        val amount = try {
            BigDecimal(state.amount)
        } catch (e: NumberFormatException) {
            viewModelScope.launch {
                _events.emit(QuickAddUiEvent.ShowError("金额格式不正确"))
            }
            return
        }

        if (amount <= BigDecimal.ZERO) {
            viewModelScope.launch {
                _events.emit(QuickAddUiEvent.ShowError("金额必须大于0"))
            }
            return
        }

        if (state.selectedCategory == null) {
            viewModelScope.launch {
                _events.emit(QuickAddUiEvent.ShowError("请选择分类"))
            }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }

            addExpenseUseCase(
                amount = amount,
                categoryId = state.selectedCategory.id,
                date = state.date,
                note = state.note.ifBlank { null },
                paymentMethod = state.paymentMethod.ifBlank { null }
            )
                .onSuccess {
                    _events.emit(QuickAddUiEvent.SaveSuccess)
                    resetForm()
                }
                .onFailure { error ->
                    _events.emit(QuickAddUiEvent.ShowError(error.message ?: "保存失败"))
                }

            _uiState.update { it.copy(isSaving = false) }
        }
    }

    /**
     * 重置表单
     */
    private fun resetForm() {
        _uiState.update {
            QuickAddUiState(
                categories = it.categories,
                date = LocalDateTime.now()
            )
        }
    }

    /**
     * 取消
     */
    fun cancel() {
        viewModelScope.launch {
            _events.emit(QuickAddUiEvent.Dismiss)
        }
    }
}

/**
 * 快速记账UI状态
 */
data class QuickAddUiState(
    val isLoading: Boolean = false,
    val isSaving: Boolean = false,
    val amount: String = "",
    val selectedCategory: Category? = null,
    val categories: List<Category> = emptyList(),
    val note: String = "",
    val date: LocalDateTime = LocalDateTime.now(),
    val paymentMethod: String = ""
)

/**
 * 快速记账UI事件
 */
sealed class QuickAddUiEvent {
    data class ShowError(val message: String) : QuickAddUiEvent()
    object SaveSuccess : QuickAddUiEvent()
    object Dismiss : QuickAddUiEvent()
}
