package com.billtrack.app.ui.statistics

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.billtrack.core.domain.repository.CategoryExpenseStat
import com.billtrack.core.domain.repository.DailyExpenseStat
import com.billtrack.core.domain.usecase.expense.GetStatisticsUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.math.BigDecimal
import java.time.LocalDateTime
import javax.inject.Inject

/**
 * 统计页面ViewModel
 */
@HiltViewModel
class StatisticsViewModel @Inject constructor(
    private val getStatisticsUseCase: GetStatisticsUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(StatisticsUiState())
    val uiState: StateFlow<StatisticsUiState> = _uiState.asStateFlow()

    private val _events = MutableSharedFlow<StatisticsUiEvent>()
    val events: SharedFlow<StatisticsUiEvent> = _events.asSharedFlow()

    init {
        loadStatistics()
    }

    /**
     * 加载统计数据
     */
    fun loadStatistics() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            // 获取本月总支出
            val total = getStatisticsUseCase.getCurrentMonthTotal()
            _uiState.update { it.copy(monthlyTotal = total ?: BigDecimal.ZERO) }

            // 获取分类支出统计
            val categoryStats = getStatisticsUseCase.getCurrentMonthCategoryExpenses()
            _uiState.update { it.copy(categoryStats = categoryStats) }

            // 获取每日支出趋势
            val dailyTrend = getStatisticsUseCase.getCurrentMonthDailyTrend()
            _uiState.update { it.copy(dailyTrend = dailyTrend) }

            _uiState.update { it.copy(isLoading = false) }
        }
    }

    /**
     * 切换到上个月
     */
    fun previousMonth() {
        val currentDate = _uiState.value.selectedDate
        val newDate = currentDate.minusMonths(1)
        _uiState.update { it.copy(selectedDate = newDate) }
        loadStatisticsForDate(newDate)
    }

    /**
     * 切换到下个月
     */
    fun nextMonth() {
        val currentDate = _uiState.value.selectedDate
        val newDate = currentDate.plusMonths(1)
        _uiState.update { it.copy(selectedDate = newDate) }
        loadStatisticsForDate(newDate)
    }

    /**
     * 加载指定日期的统计数据
     */
    private fun loadStatisticsForDate(date: LocalDateTime) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            val startOfMonth = date.withDayOfMonth(1).withHour(0).withMinute(0)
            val endOfMonth = startOfMonth.plusMonths(1)

            // 获取总支出
            val total = getStatisticsUseCase.getTotalExpense(startOfMonth, endOfMonth)
            _uiState.update { it.copy(monthlyTotal = total ?: BigDecimal.ZERO) }

            // 获取分类支出统计
            val categoryStats = getStatisticsUseCase.getCategoryExpenses(startOfMonth, endOfMonth)
            _uiState.update { it.copy(categoryStats = categoryStats) }

            // 获取每日支出趋势
            val dailyTrend = getStatisticsUseCase.getDailyTrend(startOfMonth, endOfMonth)
            _uiState.update { it.copy(dailyTrend = dailyTrend) }

            _uiState.update { it.copy(isLoading = false) }
        }
    }

    /**
     * 刷新数据
     */
    fun refresh() {
        loadStatistics()
    }
}

/**
 * 统计页面UI状态
 */
data class StatisticsUiState(
    val isLoading: Boolean = false,
    val monthlyTotal: BigDecimal = BigDecimal.ZERO,
    val categoryStats: List<CategoryExpenseStat> = emptyList(),
    val dailyTrend: List<DailyExpenseStat> = emptyList(),
    val selectedDate: LocalDateTime = LocalDateTime.now()
)

/**
 * 统计页面UI事件
 */
sealed class StatisticsUiEvent {
    data class ShowError(val message: String) : StatisticsUiEvent()
}
