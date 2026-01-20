package com.billtrack.app.navigation

/**
 * 应用页面路由
 */
sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Statistics : Screen("statistics")
    object Settings : Screen("settings")
    object ExpenseDetail : Screen("expense_detail/{expenseId}") {
        fun createRoute(expenseId: String) = "expense_detail/$expenseId"
    }
}
