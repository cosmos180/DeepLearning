package com.billtrack.app.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.billtrack.core.domain.model.Category
import com.billtrack.core.domain.model.Expense
import com.billtrack.core.domain.usecase.category.GetCategoriesUseCase
import com.billtrack.core.domain.usecase.expense.GetExpensesUseCase
import com.billtrack.core.domain.usecase.expense.GetStatisticsUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.math.BigDecimal
import javax.inject.Inject

/**
 * 首页ViewModel
 */
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val getExpensesUseCase: GetExpensesUseCase,
    private val getCategoriesUseCase: GetCategoriesUseCase,
    private val getStatisticsUseCase: GetStatisticsUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    private val _events = MutableSharedFlow<HomeUiEvent>()
    val events: SharedFlow<HomeUiEvent> = _events.asSharedFlow()

    init {
        loadHomeData()
    }

    /**
     * 加载首页数据
     */
    private fun loadHomeData() {
        viewModelScope.launch {
            // 加载本月总支出
            val total = getStatisticsUseCase.getCurrentMonthTotal()
            _uiState.update { it.copy(monthlyTotal = total ?: BigDecimal.ZERO) }

            // 加载最近消费记录
            getExpensesUseCase.getCurrentMonthExpenses()
                .take(1)
                .map { expenses -> expenses.take(10) }
                .collect { recentExpenses ->
                    _uiState.update { it.copy(recentExpenses = recentExpenses) }
                }

            // 加载分类数据
            getCategoriesUseCase.getRootCategories()
                .take(1)
                .collect { categories ->
                    _uiState.update { it.copy(categories = categories) }
                }
        }
    }

    /**
     * 刷新数据
     */
    fun refresh() {
        loadHomeData()
    }

    /**
     * 删除消费记录
     */
    fun deleteExpense(expenseId: String) {
        viewModelScope.launch {
            try {
                // 这里需要注入 DeleteExpenseUseCase
                _events.emit(HomeUiEvent.ShowMessage("Expense deleted"))
                refresh()
            } catch (e: Exception) {
                _events.emit(HomeUiEvent.ShowError(e.message ?: "Failed to delete expense"))
            }
        }
    }

    /**
     * 显示快速记账对话框
     */
    fun showQuickAddDialog() {
        viewModelScope.launch {
            _events.emit(HomeUiEvent.ShowQuickAddDialog)
        }
    }
}

/**
 * 首页UI状态
 */
data class HomeUiState(
    val isLoading: Boolean = false,
    val monthlyTotal: BigDecimal = BigDecimal.ZERO,
    val recentExpenses: List<Expense> = emptyList(),
    val categories: List<Category> = emptyList()
)

/**
 * 首页UI事件
 */
sealed class HomeUiEvent {
    data class ShowError(val message: String) : HomeUiEvent()
    data class ShowMessage(val message: String) : HomeUiEvent()
    object ShowQuickAddDialog : HomeUiEvent()
    object NavigateToStatistics : HomeUiEvent()
    object NavigateToSettings : HomeUiEvent()
}
