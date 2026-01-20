package com.billtrack.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// 主色调
private val Primary = Color(0xFF4CAF50)
private val PrimaryDark = Color(0xFF388E3C)
private val Secondary = Color(0xFFFF6B6B)

// 颜色方案
private val LightColors = lightColorScheme(
    primary = Primary,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFC8E6C9),
    onPrimaryContainer = PrimaryDark,
    secondary = Secondary,
    onSecondary = Color.White,
    background = Color(0xFFFFFBFE),
    onBackground = Color(0xFF1C1B1F),
    surface = Color(0xFFFFFBFE),
    onSurface = Color(0xFF1C1B1F),
    error = Color(0xFFBA1A1A),
    onError = Color.White
)

/**
 * 应用主题
 */
@Composable
fun BillTrackTheme(
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = LightColors,
        typography = Typography,
        content = content
    )
}
