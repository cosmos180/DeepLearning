package com.billtrack.app.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.billtrack.app.ui.home.HomeScreen
import com.billtrack.app.ui.quickadd.QuickAddDialog
import com.billtrack.app.ui.statistics.StatisticsScreen

/**
 * 应用导航图
 */
@Composable
fun BillTrackNavGraph(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    var showQuickAddDialog by remember { mutableStateOf(false) }

    NavHost(
        navController = navController,
        startDestination = Screen.Home.route,
        modifier = modifier
    ) {
        // 首页
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToStatistics = {
                    navController.navigate(Screen.Statistics.route)
                },
                onNavigateToSettings = {
                    navController.navigate(Screen.Settings.route)
                },
                onExpenseClick = { expenseId ->
                    navController.navigate(Screen.ExpenseDetail.createRoute(expenseId))
                }
            )

            // 快速记账对话框
            if (showQuickAddDialog) {
                QuickAddDialog(
                    onDismiss = { showQuickAddDialog = false }
                )
            }
        }

        // 统计页面
        composable(Screen.Statistics.route) {
            StatisticsScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }

        // 设置页面
        composable(Screen.Settings.route) {
            // TODO: Implement SettingsScreen
            SettingsScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }

        // 消费详情页面
        composable(
            route = Screen.ExpenseDetail.route,
            arguments = listOf(
                navArgument("expenseId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val expenseId = backStackEntry.arguments?.getString("expenseId") ?: return@composable
            // TODO: Implement ExpenseDetailScreen
            ExpenseDetailScreen(
                expenseId = expenseId,
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
    }
}

// 临时的占位屏幕
@Composable
fun SettingsScreen(onNavigateBack: () -> Unit) {
    androidx.compose.material3.Text("设置页面 - 开发中")
}

@Composable
fun ExpenseDetailScreen(expenseId: String, onNavigateBack: () -> Unit) {
    androidx.compose.material3.Text("消费详情 - 开发中: $expenseId")
}
