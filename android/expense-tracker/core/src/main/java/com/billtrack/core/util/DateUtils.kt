package com.billtrack.core.util

import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

/**
 * 日期时间工具
 */
object DateUtils {
    private val dateFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd")
    private val timeFormatter = DateTimeFormatter.ofPattern("HH:mm")
    private val dateTimeFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")
    private val monthFormatter = DateTimeFormatter.ofPattern("yyyy-MM")

    /**
     * 格式化日期
     */
    fun formatDate(dateTime: LocalDateTime): String {
        return dateTime.format(dateFormatter)
    }

    /**
     * 格式化时间
     */
    fun formatTime(dateTime: LocalDateTime): String {
        return dateTime.format(timeFormatter)
    }

    /**
     * 格式化日期时间
     */
    fun formatDateTime(dateTime: LocalDateTime): String {
        return dateTime.format(dateTimeFormatter)
    }

    /**
     * 格式化月份
     */
    fun formatMonth(dateTime: LocalDateTime): String {
        return dateTime.format(monthFormatter)
    }

    /**
     * 获取今日开始时间
     */
    fun getTodayStart(): LocalDateTime {
        return LocalDateTime.now().toLocalDate().atStartOfDay()
    }

    /**
     * 获取本月开始时间
     */
    fun getMonthStart(): LocalDateTime {
        val now = LocalDateTime.now()
        return now.withDayOfMonth(1).withHour(0).withMinute(0).withSecond(0)
    }

    /**
     * 获取本月结束时间
     */
    fun getMonthEnd(): LocalDateTime {
        val now = LocalDateTime.now()
        return now.withDayOfMonth(now.toLocalDate().lengthOfMonth())
            .withHour(23).withMinute(59).withSecond(59)
    }

    /**
     * 判断是否今天
     */
    fun isToday(dateTime: LocalDateTime): Boolean {
        return dateTime.toLocalDate() == LocalDateTime.now().toLocalDate()
    }

    /**
     * 判断是否昨天
     */
    fun isYesterday(dateTime: LocalDateTime): Boolean {
        return dateTime.toLocalDate() == LocalDateTime.now().minusDays(1).toLocalDate()
    }

    /**
     * 获取友好的日期描述
     */
    fun getFriendlyDate(dateTime: LocalDateTime): String {
        return when {
            isToday(dateTime) -> "今天"
            isYesterday(dateTime) -> "昨天"
            else -> formatDate(dateTime)
        }
    }
}
