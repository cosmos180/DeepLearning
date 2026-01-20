package com.billtrack.core.data.local.converter

import androidx.room.TypeConverter
import java.math.BigDecimal
import java.time.LocalDateTime
import java.time.YearMonth

/**
 * Room类型转换器
 * 用于处理Room不直接支持的类型
 */
class Converters {
    /**
     * LocalDateTime ↔ Long
     */
    @TypeConverter
    fun fromLocalDateTime(dateTime: LocalDateTime?): Long? {
        return dateTime?.atZone(java.time.ZoneId.systemDefault())?.toEpochSecond()
    }

    @TypeConverter
    fun toLocalDateTime(epochSecond: Long?): LocalDateTime? {
        return epochSecond?.let {
            LocalDateTime.ofInstant(
                java.time.Instant.ofEpochSecond(it),
                java.time.ZoneId.systemDefault()
            )
        }
    }

    /**
     * BigDecimal ↔ String
     */
    @TypeConverter
    fun fromBigDecimal(bigDecimal: BigDecimal?): String? {
        return bigDecimal?.toString()
    }

    @TypeConverter
    fun toBigDecimal(string: String?): BigDecimal? {
        return string?.let { BigDecimal(it) }
    }

    /**
     * YearMonth ↔ String
     */
    @TypeConverter
    fun fromYearMonth(yearMonth: YearMonth?): String? {
        return yearMonth?.toString()
    }

    @TypeConverter
    fun toYearMonth(string: String?): YearMonth? {
        return string?.let { YearMonth.parse(it) }
    }
}
