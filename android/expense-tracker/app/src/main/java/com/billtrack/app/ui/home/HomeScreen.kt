package com.billtrack.app.ui.home

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.billtrack.core.domain.model.Expense
import com.billtrack.core.util.CurrencyUtils.formatCurrency
import com.billtrack.core.util.DateUtils.formatDate
import com.billtrack.app.ui.quickadd.QuickAddDialog
import java.text.NumberFormat
import java.util.Locale

/**
 * 首页屏幕
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToStatistics: () -> Unit = {},
    onNavigateToSettings: () -> Unit = {},
    onExpenseClick: (String) -> Unit = {},
    viewModel: HomeViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var showQuickAddDialog by remember { mutableStateOf(false) }
    val scaffoldState = rememberBottomSheetScaffoldState(
        bottomSheetState = rememberStandardBottomSheetState(
            initialValue = SheetValue.Hidden,
            skipHiddenState = false
        )
    )

    // Handle events
    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is HomeUiEvent.ShowQuickAddDialog -> {
                    showQuickAddDialog = true
                }
                HomeUiEvent.NavigateToStatistics -> onNavigateToStatistics()
                HomeUiEvent.NavigateToSettings -> onNavigateToSettings()
                else -> {}
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("账单通") },
                actions = {
                    IconButton(onClick = onNavigateToStatistics) {
                        Icon(
                            imageVector = Icons.Default.Add,
                            contentDescription = "Statistics"
                        )
                    }
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(
                            imageVector = Icons.Default.Add,
                            contentDescription = "Settings"
                        )
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { viewModel.showQuickAddDialog() }
            ) {
                Icon(Icons.Default.Add, contentDescription = "Add Expense")
            }
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 本月支出卡片
            item {
                MonthlyExpenseCard(
                    total = uiState.monthlyTotal,
                    onClick = onNavigateToStatistics
                )
            }

            // 最近记录标题
            item {
                Text(
                    text = "最近记录",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
            }

            // 最近记录列表
            items(uiState.recentExpenses) { expense ->
                ExpenseItem(
                    expense = expense,
                    onClick = { onExpenseClick(expense.id) },
                    onDelete = { viewModel.deleteExpense(expense.id) }
                )
            }
        }
    }

    // 快速记账对话框
    if (showQuickAddDialog) {
        QuickAddDialog(
            onDismiss = {
                showQuickAddDialog = false
                viewModel.refresh()
            }
        )
    }
}

/**
 * 本月支出卡片
 */
@Composable
fun MonthlyExpenseCard(
    total: java.math.BigDecimal,
    onClick: () -> Unit = {}
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = "本月支出",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = formatCurrency(total),
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
        }
    }
}

/**
 * 消费记录项
 */
@Composable
fun ExpenseItem(
    expense: Expense,
    onClick: () -> Unit = {},
    onDelete: () -> Unit = {}
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 分类图标
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(Color(android.graphics.Color.parseColor(expense.category?.color ?: "#FF6B6B"))),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = expense.category?.icon?.take(1) ?: "E",
                    style = MaterialTheme.typography.titleLarge,
                    color = Color.White
                )
            }

            Spacer(modifier = Modifier.width(12.dp))

            // 详情
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = expense.category?.name ?: "未知分类",
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Medium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Text(
                    text = formatDate(expense.date),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
                val note = expense.note
                if (!note.isNullOrBlank()) {
                    Text(
                        text = note,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }

            Spacer(modifier = Modifier.width(12.dp))

            // 金额和删除按钮
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = formatCurrency(expense.amount),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.error
                )
                IconButton(
                    onClick = onDelete,
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = "Delete",
                        tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f),
                        modifier = Modifier.size(20.dp)
                    )
                }
            }
        }
    }
}

/**
 * 货币格式化工具
 */
object CurrencyUtils {
    fun formatCurrency(amount: java.math.BigDecimal): String {
        val format = NumberFormat.getCurrencyInstance(Locale.CHINA)
        return format.format(amount)
    }
}

/**
 * 日期格式化工具
 */
object DateUtils {
    fun formatDate(date: java.time.LocalDateTime): String {
        val now = java.time.LocalDateTime.now()
        return when {
            date.toLocalDate() == now.toLocalDate() -> "今天 ${date.format(java.time.format.DateTimeFormatter.ofPattern("HH:mm"))}"
            date.toLocalDate() == now.minusDays(1).toLocalDate() -> "昨天 ${date.format(java.time.format.DateTimeFormatter.ofPattern("HH:mm"))}"
            else -> date.format(java.time.format.DateTimeFormatter.ofPattern("MM-dd HH:mm"))
        }
    }
}
