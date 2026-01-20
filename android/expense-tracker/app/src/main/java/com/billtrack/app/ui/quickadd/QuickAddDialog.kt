package com.billtrack.app.ui.quickadd

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.hilt.navigation.compose.hiltViewModel
import com.billtrack.core.domain.model.Category
import java.text.NumberFormat
import java.util.Locale

/**
 * 快速记账对话框
 */
@Composable
fun QuickAddDialog(
    onDismiss: () -> Unit = {},
    viewModel: QuickAddViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is QuickAddUiEvent.ShowError -> {
                    // Show error message (could use Snackbar)
                }
                QuickAddUiEvent.SaveSuccess -> {
                    onDismiss()
                }
                QuickAddUiEvent.Dismiss -> {
                    onDismiss()
                }
            }
        }
    }

    Dialog(onDismissRequest = onDismiss) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp)
            ) {
                // 标题
                Text(
                    text = "记一笔",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(24.dp))

                // 金额输入
                OutlinedTextField(
                    value = uiState.amount,
                    onValueChange = { viewModel.updateAmount(it) },
                    label = { Text("金额") },
                    leadingIcon = {
                        Text(
                            text = "¥",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                    },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )

                Spacer(modifier = Modifier.height(16.dp))

                // 分类选择
                Text(
                    text = "选择分类",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
                Spacer(modifier = Modifier.height(8.dp))
                CategorySelector(
                    categories = uiState.categories,
                    selectedCategory = uiState.selectedCategory,
                    onCategorySelected = { viewModel.selectCategory(it) }
                )

                Spacer(modifier = Modifier.height(16.dp))

                // 备注输入
                OutlinedTextField(
                    value = uiState.note,
                    onValueChange = { viewModel.updateNote(it) },
                    label = { Text("备注（可选）") },
                    modifier = Modifier.fillMaxWidth(),
                    maxLines = 2,
                    singleLine = false
                )

                Spacer(modifier = Modifier.height(24.dp))

                // 操作按钮
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    OutlinedButton(
                        onClick = { viewModel.cancel() },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("取消")
                    }
                    Button(
                        onClick = { viewModel.saveExpense() },
                        modifier = Modifier.weight(1f),
                        enabled = !uiState.isSaving
                    ) {
                        if (uiState.isSaving) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp),
                                color = MaterialTheme.colorScheme.onPrimary,
                                strokeWidth = 2.dp
                            )
                        } else {
                            Text("保存")
                        }
                    }
                }
            }
        }
    }
}

/**
 * 分类选择器
 */
@Composable
fun CategorySelector(
    categories: List<Category>,
    selectedCategory: Category?,
    onCategorySelected: (Category) -> Unit
) {
    LazyRow(
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(categories) { category ->
            CategoryItem(
                category = category,
                isSelected = selectedCategory?.id == category.id,
                onClick = { onCategorySelected(category) }
            )
        }
    }
}

/**
 * 分类项
 */
@Composable
fun CategoryItem(
    category: Category,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .background(
                if (isSelected) {
                    MaterialTheme.colorScheme.primaryContainer
                } else {
                    MaterialTheme.colorScheme.surfaceVariant
                }
            )
            .padding(12.dp)
    ) {
        Box(
            modifier = Modifier
                .size(48.dp)
                .clip(CircleShape)
                .background(Color(android.graphics.Color.parseColor(category.color))),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = category.icon.take(1),
                style = MaterialTheme.typography.titleLarge,
                color = Color.White
            )
        }

        if (isSelected) {
            Spacer(modifier = Modifier.height(4.dp))
            Icon(
                imageVector = Icons.Default.Check,
                contentDescription = "Selected",
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(16.dp)
            )
        }

        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = category.name,
            style = MaterialTheme.typography.bodySmall,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
        )
    }
}
