package com.billtrack.core.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey
import com.billtrack.core.domain.model.Expense
import java.math.BigDecimal
import java.time.LocalDateTime

/**
 * 消费记录数据库实体
 */
@Entity(
    tableName = "expenses",
    foreignKeys = [
        ForeignKey(
            entity = CategoryEntity::class,
            parentColumns = ["id"],
            childColumns = ["category_id"],
            onDelete = ForeignKey.RESTRICT
        )
    ],
    indices = [
        Index(value = ["category_id"]),
        Index(value = ["date"]),
        Index(value = ["created_at"])
    ]
)
data class ExpenseEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String,

    @ColumnInfo(name = "amount")
    val amount: BigDecimal,

    @ColumnInfo(name = "category_id")
    val categoryId: String,

    @ColumnInfo(name = "date")
    val date: LocalDateTime,

    @ColumnInfo(name = "note")
    val note: String? = null,

    @ColumnInfo(name = "payment_method")
    val paymentMethod: String? = null,

    @ColumnInfo(name = "created_at")
    val createdAt: LocalDateTime,

    @ColumnInfo(name = "updated_at")
    val updatedAt: LocalDateTime
) {
    fun toDomainModel(): Expense {
        return Expense(
            id = id,
            amount = amount,
            categoryId = categoryId,
            category = null,
            date = date,
            note = note,
            paymentMethod = paymentMethod,
            createdAt = createdAt,
            updatedAt = updatedAt
        )
    }

    companion object {
        fun fromDomainModel(expense: Expense): ExpenseEntity {
            return ExpenseEntity(
                id = expense.id,
                amount = expense.amount,
                categoryId = expense.categoryId,
                date = expense.date,
                note = expense.note,
                paymentMethod = expense.paymentMethod,
                createdAt = expense.createdAt,
                updatedAt = expense.updatedAt
            )
        }
    }
}

/**
 * 分类数据库实体
 */
@Entity(
    tableName = "categories",
    foreignKeys = [
        ForeignKey(
            entity = CategoryEntity::class,
            parentColumns = ["id"],
            childColumns = ["parent_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["parent_id"]),
        Index(value = ["name"], unique = true)
    ]
)
data class CategoryEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String,

    @ColumnInfo(name = "name")
    val name: String,

    @ColumnInfo(name = "parent_id")
    val parentId: String? = null,

    @ColumnInfo(name = "icon")
    val icon: String,

    @ColumnInfo(name = "color")
    val color: String,

    @ColumnInfo(name = "is_custom")
    val isCustom: Boolean = false,

    @ColumnInfo(name = "sort_order")
    val sortOrder: Int = 0,

    @ColumnInfo(name = "created_at")
    val createdAt: LocalDateTime
) {
    fun toDomainModel(): com.billtrack.core.domain.model.Category {
        return com.billtrack.core.domain.model.Category(
            id = id,
            name = name,
            parentId = parentId,
            parent = null,
            children = null,
            icon = icon,
            color = color,
            isCustom = isCustom,
            sortOrder = sortOrder,
            createdAt = createdAt
        )
    }

    companion object {
        fun fromDomainModel(category: com.billtrack.core.domain.model.Category): CategoryEntity {
            return CategoryEntity(
                id = category.id,
                name = category.name,
                parentId = category.parentId,
                icon = category.icon,
                color = category.color,
                isCustom = category.isCustom,
                sortOrder = category.sortOrder,
                createdAt = category.createdAt
            )
        }
    }
}

/**
 * 预算数据库实体
 */
@Entity(
    tableName = "budgets",
    foreignKeys = [
        ForeignKey(
            entity = CategoryEntity::class,
            parentColumns = ["id"],
            childColumns = ["category_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["category_id"]),
        Index(value = ["month"], unique = true)
    ]
)
data class BudgetEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String,

    @ColumnInfo(name = "category_id")
    val categoryId: String? = null,

    @ColumnInfo(name = "amount")
    val amount: BigDecimal,

    @ColumnInfo(name = "month")
    val month: String,

    @ColumnInfo(name = "created_at")
    val createdAt: LocalDateTime,

    @ColumnInfo(name = "updated_at")
    val updatedAt: LocalDateTime
) {
    fun toDomainModel(): com.billtrack.core.domain.model.Budget {
        return com.billtrack.core.domain.model.Budget(
            id = id,
            categoryId = categoryId,
            category = null,
            amount = amount,
            month = java.time.YearMonth.parse(month),
            createdAt = createdAt,
            updatedAt = updatedAt
        )
    }

    companion object {
        fun fromDomainModel(budget: com.billtrack.core.domain.model.Budget): BudgetEntity {
            return BudgetEntity(
                id = budget.id,
                categoryId = budget.categoryId,
                amount = budget.amount,
                month = budget.month.toString(),
                createdAt = budget.createdAt,
                updatedAt = budget.updatedAt
            )
        }
    }
}

/**
 * 用户设置数据库实体
 */
@Entity(tableName = "user_settings")
data class UserSettingsEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String = "default",

    @ColumnInfo(name = "currency")
    val currency: String = "CNY",

    @ColumnInfo(name = "decimal_places")
    val decimalPlaces: Int = 2,

    @ColumnInfo(name = "month_start_day")
    val monthStartDay: Int = 1,

    @ColumnInfo(name = "theme")
    val theme: String = "light",

    @ColumnInfo(name = "language")
    val language: String = "zh-CN",

    @ColumnInfo(name = "reminder_enabled")
    val reminderEnabled: Boolean = true,

    @ColumnInfo(name = "reminder_time")
    val reminderTime: String = "21:00"
) {
    fun toDomainModel(): com.billtrack.core.domain.model.UserSettings {
        return com.billtrack.core.domain.model.UserSettings(
            id = id,
            currency = currency,
            decimalPlaces = decimalPlaces,
            monthStartDay = monthStartDay,
            theme = theme,
            language = language,
            reminderEnabled = reminderEnabled,
            reminderTime = reminderTime
        )
    }

    companion object {
        fun fromDomainModel(settings: com.billtrack.core.domain.model.UserSettings): UserSettingsEntity {
            return UserSettingsEntity(
                id = settings.id,
                currency = settings.currency,
                decimalPlaces = settings.decimalPlaces,
                monthStartDay = settings.monthStartDay,
                theme = settings.theme,
                language = settings.language,
                reminderEnabled = settings.reminderEnabled,
                reminderTime = settings.reminderTime
            )
        }
    }
}
