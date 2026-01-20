package com.billtrack.app.ui.statistics

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.billtrack.core.util.CurrencyUtils.formatCurrency
import java.text.NumberFormat
import java.util.Locale

/**
 * 统计页面屏幕
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StatisticsScreen(
    onNavigateBack: () -> Unit = {},
    viewModel: StatisticsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("统计") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 月份选择器
            item {
                MonthSelector(
                    currentMonth = uiState.selectedDate,
                    onPreviousMonth = { viewModel.previousMonth() },
                    onNextMonth = { viewModel.nextMonth() }
                )
            }

            // 本月总支出
            item {
                MonthlyTotalCard(
                    total = uiState.monthlyTotal,
                    isLoading = uiState.isLoading
                )
            }

            // 分类支出统计
            item {
                Text(
                    text = "分类支出",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
            }

            items(uiState.categoryStats) { stat ->
                CategoryExpenseItem(stat = stat)
            }

            // 每日趋势
            item {
                Text(
                    text = "每日趋势",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                DailyTrendChart(
                    dailyTrend = uiState.dailyTrend,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                )
            }
        }
    }
}

/**
 * 月份选择器
 */
@Composable
fun MonthSelector(
    currentMonth: java.time.LocalDateTime,
    onPreviousMonth: () -> Unit,
    onNextMonth: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onPreviousMonth) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Previous Month")
            }

            Text(
                text = currentMonth.format(java.time.format.DateTimeFormatter.ofPattern("yyyy年MM月")),
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )

            IconButton(onClick = onNextMonth) {
                Icon(Icons.Default.ArrowForward, contentDescription = "Next Month")
            }
        }
    }
}

/**
 * 本月总支出卡片
 */
@Composable
fun MonthlyTotalCard(
    total: java.math.BigDecimal,
    isLoading: Boolean
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(24.dp)
        ) {
            Text(
                text = "本月总支出",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
            )
            Spacer(modifier = Modifier.height(8.dp))
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(32.dp),
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
            } else {
                Text(
                    text = formatCurrency(total),
                    style = MaterialTheme.typography.displaySmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }
        }
    }
}

/**
 * 分类支出项
 */
@Composable
fun CategoryExpenseItem(stat: com.billtrack.core.domain.repository.CategoryExpenseStat) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "分类 ${stat.categoryId.take(8)}",
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "${stat.count} 笔消费",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
            Text(
                text = formatCurrency(stat.total),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.error
            )
        }
    }
}

/**
 * 每日趋势图（简化版）
 */
@Composable
fun DailyTrendChart(
    dailyTrend: List<com.billtrack.core.domain.repository.DailyExpenseStat>,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            contentAlignment = Alignment.Center
        ) {
            if (dailyTrend.isEmpty()) {
                Text(
                    text = "暂无数据",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            } else {
                // 简单的条形图表示
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    dailyTrend.takeLast(7).forEach { stat ->
                        DailyTrendBar(
                            date = stat.date,
                            amount = stat.total,
                            maxAmount = dailyTrend.maxOfOrNull { it.total } ?: stat.total
                        )
                    }
                }
            }
        }
    }
}

/**
 * 每日趋势条
 */
@Composable
fun DailyTrendBar(
    date: java.time.LocalDateTime,
    amount: java.math.BigDecimal,
    maxAmount: java.math.BigDecimal
) {
    val progress = if (maxAmount > java.math.BigDecimal.ZERO) {
        amount.toFloat() / maxAmount.toFloat()
    } else {
        0f
    }

    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = date.format(java.time.format.DateTimeFormatter.ofPattern("MM-dd")),
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.width(50.dp)
        )
        Box(
            modifier = Modifier
                .weight(1f)
                .height(24.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(progress)
                    .fillMaxHeight()
                    .background(MaterialTheme.colorScheme.primary)
            )
        }
        Text(
            text = formatCurrency(amount),
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.width(80.dp)
        )
    }
}
