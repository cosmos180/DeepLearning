# 数据模型设计

## 1. 数据模型概述

### 1.1 数据模型架构

```
┌─────────────────────────────────────────────────────────┐
│                    数据模型分层                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Domain Layer (领域层)                           │  │
│  │  - 纯Kotlin数据类                                │  │
│  │  - 业务逻辑封装                                  │  │
│  │  - 无Android依赖                                 │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓ 转换                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Data Layer (数据层)                             │  │
│  │  - Room Entity (@Entity)                        │  │
│  │  - 数据库表结构                                  │  │
│  │  - Room注解                                      │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓ 存储                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Database (SQLite)                               │  │
│  │  - 表结构定义                                    │  │
│  │  - 索引优化                                      │  │
│  │  - 关系约束                                      │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 数据模型命名规范

| 类型 | 命名 | 示例 |
|------|------|------|
| Domain Model | 简单名词 | `Expense`, `Category`, `Budget` |
| Entity | Model + Entity | `ExpenseEntity`, `CategoryEntity` |
| DAO | 接口名 + Dao | `ExpenseDao`, `CategoryDao` |
| Repository | 接口名 + Repository | `ExpenseRepository` |

---

## 2. 领域模型设计 (Domain Layer)

### 2.1 核心领域模型

#### Expense (消费记录)

```kotlin
/**
 * 消费记录领域模型
 *
 * @property id 唯一标识
 * @property amount 金额
 * @property categoryId 分类ID
 * @property category 分类(关联查询时填充)
 * @property date 消费日期时间
 * @property note 备注
 * @property paymentMethod 支付方式
 * @property createdAt 创建时间
 * @property updatedAt 更新时间
 */
data class Expense(
    val id: String,
    val amount: BigDecimal,
    val categoryId: String,
    val category: Category? = null,  // 关联查询时填充
    val date: LocalDateTime,
    val note: String? = null,
    val paymentMethod: String? = null,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime
) {
    companion object {
        fun create(
            amount: BigDecimal,
            categoryId: String,
            date: LocalDateTime,
            note: String? = null,
            paymentMethod: String? = null
        ): Expense {
            val now = LocalDateTime.now()
            return Expense(
                id = UUID.randomUUID().toString(),
                amount = amount,
                categoryId = categoryId,
                date = date,
                note = note,
                paymentMethod = paymentMethod,
                createdAt = now,
                updatedAt = now
            )
        }
    }
}
```

#### Category (分类)

```kotlin
/**
 * 分类领域模型
 *
 * @property id 唯一标识
 * @property name 分类名称
 * @property parentId 父分类ID (null表示一级分类)
 * @property parent 父分类(关联查询时填充)
 * @property children 子分类列表(关联查询时填充)
 * @property icon 图标名称
 * @property color 颜色值 (HEX)
 * @property isCustom 是否自定义分类
 * @property sortOrder 排序序号
 * @property createdAt 创建时间
 */
data class Category(
    val id: String,
    val name: String,
    val parentId: String? = null,
    val parent: Category? = null,
    val children: List<Category>? = null,
    val icon: String,
    val color: String,
    val isCustom: Boolean = false,
    val sortOrder: Int = 0,
    val createdAt: LocalDateTime
) {
    val isRootCategory: Boolean
        get() = parentId == null

    val fullName: String
        get() = if (parent != null) "${parent.name} - $name" else name
}
```

#### Budget (预算)

```kotlin
/**
 * 预算领域模型
 *
 * @property id 唯一标识
 * @property categoryId 分类ID (null表示总预算)
 * @property category 分类(关联查询时填充)
 * @property amount 预算金额
 * @property month 月份 (格式: YYYY-MM)
 * @property createdAt 创建时间
 * @property updatedAt 更新时间
 */
data class Budget(
    val id: String,
    val categoryId: String? = null,
    val category: Category? = null,
    val amount: BigDecimal,
    val month: YearMonth,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime
) {
    val isTotalBudget: Boolean
        get() = categoryId == null

    companion object {
        fun createTotalBudget(
            amount: BigDecimal,
            month: YearMonth
        ): Budget {
            val now = LocalDateTime.now()
            return Budget(
                id = UUID.randomUUID().toString(),
                categoryId = null,
                amount = amount,
                month = month,
                createdAt = now,
                updatedAt = now
            )
        }

        fun createCategoryBudget(
            categoryId: String,
            amount: BigDecimal,
            month: YearMonth
        ): Budget {
            val now = LocalDateTime.now()
            return Budget(
                id = UUID.randomUUID().toString(),
                categoryId = categoryId,
                amount = amount,
                month = month,
                createdAt = now,
                updatedAt = now
            )
        }
    }
}
```

#### UserSettings (用户设置)

```kotlin
/**
 * 用户设置领域模型
 *
 * @property id 唯一标识 (固定为"default")
 * @property currency 货币代码 (CNY, USD, EUR等)
 * @property decimalPlaces 小数位数 (0, 1, 2)
 * @property monthStartDay 每月起始日期 (1-31)
 * @property theme 主题 (light, dark, system)
 * @property language 语言 (zh-CN, en)
 * @property reminderEnabled 是否启用提醒
 * @property reminderTime 提醒时间 (HH:mm格式)
 */
data class UserSettings(
    val id: String = "default",
    val currency: String = "CNY",
    val decimalPlaces: Int = 2,
    val monthStartDay: Int = 1,
    val theme: String = "light",
    val language: String = "zh-CN",
    val reminderEnabled: Boolean = true,
    val reminderTime: String = "21:00"
) {
    fun formatAmount(amount: BigDecimal): String {
        val formatter = DecimalFormat().apply {
            minimumFractionDigits = decimalPlaces
            maximumFractionDigits = decimalPlaces
            groupingSize = 3
            isGroupingUsed = true
        }
        return "${getCurrencySymbol()}${formatter.format(amount)}"
    }

    private fun getCurrencySymbol(): String {
        return when (currency) {
            "CNY" -> "¥"
            "USD" -> "$"
            "EUR" -> "€"
            else -> ""
        }
    }
}
```

#### Statistics (统计数据)

```kotlin
/**
 * 统计数据领域模型
 *
 * @property totalExpense 总支出
 * @property expenseByCategory 分类支出
 * @property dailyTrend 每日趋势
 * @property budgetUsage 预算使用情况
 */
data class Statistics(
    val totalExpense: BigDecimal,
    val expenseByCategory: List<CategoryExpense>,
    val dailyTrend: List<DailyExpense>,
    val budgetUsage: BudgetUsage? = null
)

/**
 * 分类支出
 */
data class CategoryExpense(
    val category: Category,
    val amount: BigDecimal,
    val percentage: Float,
    val count: Int
)

/**
 * 每日支出
 */
data class DailyExpense(
    val date: LocalDate,
    val amount: BigDecimal,
    val count: Int
)

/**
 * 预算使用情况
 */
data class BudgetUsage(
    val budget: Budget,
    val used: BigDecimal,
    val remaining: BigDecimal,
    val percentage: Float,
    val status: BudgetStatus
)

/**
 * 预算状态
 */
enum class BudgetStatus {
    HEALTHY,    // < 50%
    ATTENTION,  // 50% - 80%
    WARNING,    // 80% - 100%
    OVERBUDGET  // > 100%
}
```

---

## 3. 数据库实体设计 (Data Layer)

### 3.1 Room Entity定义

#### ExpenseEntity

```kotlin
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
            category = null,  // 关联查询时填充
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
```

#### CategoryEntity

```kotlin
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
    fun toDomainModel(): Category {
        return Category(
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
        fun fromDomainModel(category: Category): CategoryEntity {
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
```

#### BudgetEntity

```kotlin
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
    val month: String,  // 格式: YYYY-MM

    @ColumnInfo(name = "created_at")
    val createdAt: LocalDateTime,

    @ColumnInfo(name = "updated_at")
    val updatedAt: LocalDateTime
) {
    fun toDomainModel(): Budget {
        return Budget(
            id = id,
            categoryId = categoryId,
            category = null,
            amount = amount,
            month = YearMonth.parse(month),
            createdAt = createdAt,
            updatedAt = updatedAt
        )
    }

    companion object {
        fun fromDomainModel(budget: Budget): BudgetEntity {
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
```

#### UserSettingsEntity

```kotlin
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
    fun toDomainModel(): UserSettings {
        return UserSettings(
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
        fun fromDomainModel(settings: UserSettings): UserSettingsEntity {
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
```

### 3.2 TypeConverter (类型转换器)

```kotlin
/**
 * Room类型转换器
 * 用于处理Room不直接支持的类型
 */
class Converters {
    // LocalDateTime ↔ Long
    @TypeConverter
    fun fromLocalDateTime(dateTime: LocalDateTime?): Long? {
        return dateTime?.atZone(ZoneId.systemDefault())?.toEpochSecond()
    }

    @TypeConverter
    fun toLocalDateTime(epochSecond: Long?): LocalDateTime? {
        return epochSecond?.let {
            LocalDateTime.ofInstant(
                Instant.ofEpochSecond(it),
                ZoneId.systemDefault()
            )
        }
    }

    // BigDecimal ↔ String
    @TypeConverter
    fun fromBigDecimal(bigDecimal: BigDecimal?): String? {
        return bigDecimal?.toString()
    }

    @TypeConverter
    fun toBigDecimal(string: String?): BigDecimal? {
        return string?.let { BigDecimal(it) }
    }

    // YearMonth ↔ String
    @TypeConverter
    fun fromYearMonth(yearMonth: YearMonth?): String? {
        return yearMonth?.toString()
    }

    @TypeConverter
    fun toYearMonth(string: String?): YearMonth? {
        return string?.let { YearMonth.parse(it) }
    }
}
```

---

## 4. 数据库设计 (Database Schema)

### 4.1 Room Database定义

```kotlin
@Database(
    entities = [
        ExpenseEntity::class,
        CategoryEntity::class,
        BudgetEntity::class,
        UserSettingsEntity::class
    ],
    version = 1,
    exportSchema = true
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun expenseDao(): ExpenseDao
    abstract fun categoryDao(): CategoryDao
    abstract fun budgetDao(): BudgetDao
    abstract fun userSettingsDao(): UserSettingsDao

    companion object {
        const val DATABASE_NAME = "billtrack_db"
    }
}
```

### 4.2 表结构SQL

#### expenses表

```sql
CREATE TABLE expenses (
    id TEXT PRIMARY KEY NOT NULL,
    amount TEXT NOT NULL,
    category_id TEXT NOT NULL,
    date INTEGER NOT NULL,
    note TEXT,
    payment_method TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

CREATE INDEX idx_expenses_category_id ON expenses(category_id);
CREATE INDEX idx_expenses_date ON expenses(date);
CREATE INDEX idx_expenses_created_at ON expenses(created_at);
```

#### categories表

```sql
CREATE TABLE categories (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL UNIQUE,
    parent_id TEXT,
    icon TEXT NOT NULL,
    color TEXT NOT NULL,
    is_custom INTEGER NOT NULL DEFAULT 0,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE UNIQUE INDEX idx_categories_name ON categories(name);
```

#### budgets表

```sql
CREATE TABLE budgets (
    id TEXT PRIMARY KEY NOT NULL,
    category_id TEXT,
    amount TEXT NOT NULL,
    month TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE INDEX idx_budgets_category_id ON budgets(category_id);
CREATE UNIQUE INDEX idx_budgets_month ON budgets(month);
```

#### user_settings表

```sql
CREATE TABLE user_settings (
    id TEXT PRIMARY KEY NOT NULL,
    currency TEXT NOT NULL DEFAULT 'CNY',
    decimal_places INTEGER NOT NULL DEFAULT 2,
    month_start_day INTEGER NOT NULL DEFAULT 1,
    theme TEXT NOT NULL DEFAULT 'light',
    language TEXT NOT NULL DEFAULT 'zh-CN',
    reminder_enabled INTEGER NOT NULL DEFAULT 1,
    reminder_time TEXT NOT NULL DEFAULT '21:00'
);
```

### 4.3 数据库关系图 (ER Diagram)

```
┌─────────────────┐
│  user_settings  │ (1:1)
│  ─────────────  │
└────────┬────────┘
         │
         │ 1:N
         ↓
┌─────────────────┐         ┌─────────────────┐
│    expenses     │ ──N:1──>│   categories    │
│  ─────────────  │         │  ─────────────  │
└─────────────────┘         │  parent_id      │
                            │     ↓           │
                            └─────────────────┘
                                   ↓ 1:N
                            ┌─────────────────┐
                            │    budgets      │
                            │  ─────────────  │
                            └─────────────────┘
```

---

## 5. DAO设计

### 5.1 ExpenseDao

```kotlin
@Dao
interface ExpenseDao {
    // 基础CRUD
    @Query("SELECT * FROM expenses ORDER BY date DESC")
    fun getAllExpenses(): Flow<List<ExpenseEntity>>

    @Query("SELECT * FROM expenses WHERE id = :id")
    suspend fun getExpenseById(id: String): ExpenseEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertExpense(expense: ExpenseEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertExpenses(expenses: List<ExpenseEntity>)

    @Update
    suspend fun updateExpense(expense: ExpenseEntity)

    @Delete
    suspend fun deleteExpense(expense: ExpenseEntity)

    @Query("DELETE FROM expenses WHERE id = :id")
    suspend fun deleteExpenseById(id: String)

    @Query("DELETE FROM expenses")
    suspend fun deleteAllExpenses()

    // 查询方法
    @Query("SELECT * FROM expenses WHERE date >= :startDate AND date < :endDate ORDER BY date DESC")
    fun getExpensesByDateRange(startDate: LocalDateTime, endDate: LocalDateTime): Flow<List<ExpenseEntity>>

    @Query("SELECT * FROM expenses WHERE category_id = :categoryId ORDER BY date DESC")
    fun getExpensesByCategory(categoryId: String): Flow<List<ExpenseEntity>>

    @Query("SELECT * FROM expenses WHERE note LIKE '%' || :keyword || '%' ORDER BY date DESC")
    fun searchExpenses(keyword: String): Flow<List<ExpenseEntity>>

    // 统计方法
    @Query("SELECT SUM(amount) FROM expenses WHERE date >= :startDate AND date < :endDate")
    suspend fun getTotalExpense(startDate: LocalDateTime, endDate: LocalDateTime): BigDecimal?

    @Query("""
        SELECT category_id, SUM(amount) as total, COUNT(*) as count
        FROM expenses
        WHERE date >= :startDate AND date < :endDate
        GROUP BY category_id
        ORDER BY total DESC
    """)
    suspend fun getExpenseByCategory(startDate: LocalDateTime, endDate: LocalDateTime): List<CategoryExpenseStat>

    @Query("""
        SELECT date, SUM(amount) as total, COUNT(*) as count
        FROM expenses
        WHERE date >= :startDate AND date < :endDate
        GROUP BY date
        ORDER BY date ASC
    """)
    suspend fun getDailyTrend(startDate: LocalDateTime, endDate: LocalDateTime): List<DailyExpenseStat>
}

// 统计结果类
data class CategoryExpenseStat(
    val categoryId: String,
    val total: BigDecimal,
    val count: Int
)

data class DailyExpenseStat(
    val date: LocalDateTime,
    val total: BigDecimal,
    val count: Int
)
```

### 5.2 CategoryDao

```kotlin
@Dao
interface CategoryDao {
    @Query("SELECT * FROM categories ORDER BY sort_order ASC")
    fun getAllCategories(): Flow<List<CategoryEntity>>

    @Query("SELECT * FROM categories WHERE id = :id")
    suspend fun getCategoryById(id: String): CategoryEntity?

    @Query("SELECT * FROM categories WHERE parent_id IS NULL ORDER BY sort_order ASC")
    fun getRootCategories(): Flow<List<CategoryEntity>>

    @Query("SELECT * FROM categories WHERE parent_id = :parentId ORDER BY sort_order ASC")
    fun getChildCategories(parentId: String): Flow<List<CategoryEntity>>

    @Query("SELECT * FROM categories WHERE is_custom = 1 ORDER BY sort_order ASC")
    fun getCustomCategories(): Flow<List<CategoryEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCategory(category: CategoryEntity)

    @Update
    suspend fun updateCategory(category: CategoryEntity)

    @Delete
    suspend fun deleteCategory(category: CategoryEntity)

    @Query("DELETE FROM categories WHERE id = :id")
    suspend fun deleteCategoryById(id: String)
}
```

### 5.3 BudgetDao

```kotlin
@Dao
interface BudgetDao {
    @Query("SELECT * FROM budgets WHERE month = :month")
    fun getBudgetsByMonth(month: String): Flow<List<BudgetEntity>>

    @Query("SELECT * FROM budgets WHERE month = :month AND category_id IS NULL")
    suspend fun getTotalBudget(month: String): BudgetEntity?

    @Query("SELECT * FROM budgets WHERE month = :month AND category_id = :categoryId")
    suspend fun getCategoryBudget(month: String, categoryId: String): BudgetEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBudget(budget: BudgetEntity)

    @Update
    suspend fun updateBudget(budget: BudgetEntity)

    @Delete
    suspend fun deleteBudget(budget: BudgetEntity)
}
```

---

## 6. 数据模型转换

### 6.1 Entity Mapper

```kotlin
/**
 * Entity与Domain Model之间的转换器
 */
object ExpenseMapper {
    fun toDomainModel(entity: ExpenseEntity): Expense {
        return entity.toDomainModel()
    }

    fun toEntity(model: Expense): ExpenseEntity {
        return ExpenseEntity.fromDomainModel(model)
    }

    fun toDomainModelList(entities: List<ExpenseEntity>): List<Expense> {
        return entities.map { it.toDomainModel() }
    }
}

object CategoryMapper {
    fun toDomainModel(entity: CategoryEntity): Category {
        return entity.toDomainModel()
    }

    fun toEntity(model: Category): CategoryEntity {
        return CategoryEntity.fromDomainModel(model)
    }
}
```

### 6.2 扩展函数 (关联查询)

```kotlin
/**
 * 关联查询扩展
 * 为Expense添加Category信息
 */
fun ExpenseEntity.toDomainModelWithCategory(category: Category?): Expense {
    return Expense(
        id = id,
        amount = amount,
        categoryId = categoryId,
        category = category,
        date = date,
        note = note,
        paymentMethod = paymentMethod,
        createdAt = createdAt,
        updatedAt = updatedAt
    )
}
```

---

## 7. 数据库初始化

### 7.1 预设数据初始化

```kotlin
/**
 * 数据库初始化类
 * 用于创建预设分类数据
 */
class DatabaseInitializer @Inject constructor(
    private val database: AppDatabase,
    private val categoryDao: CategoryDao
) {
    suspend fun initialize() {
        // 检查是否已初始化
        val categories = categoryDao.getAllCategories().first()
        if (categories.isNotEmpty()) return

        // 插入预设分类
        val presetCategories = getPresetCategories()
        presetCategories.forEach { category ->
            categoryDao.insertCategory(category)
        }
    }

    private fun getPresetCategories(): List<CategoryEntity> {
        val now = LocalDateTime.now()
        return listOf(
            // 餐饮
            CategoryEntity("cat_1", "餐饮", null, "restaurant", "#FF6B6B", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_1_1", "早餐", "cat_1", "breakfast", "#FF8E8E", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_1_2", "午餐", "cat_1", "lunch", "#FF8E8E", isCustom = false, sortOrder = 2, now),
            CategoryEntity("cat_1_3", "晚餐", "cat_1", "dinner", "#FF8E8E", isCustom = false, sortOrder = 3, now),
            CategoryEntity("cat_1_4", "零食", "cat_1", "snack", "#FF8E8E", isCustom = false, sortOrder = 4, now),

            // 交通
            CategoryEntity("cat_2", "交通", null, "transport", "#4ECDC4", isCustom = false, sortOrder = 2, now),
            CategoryEntity("cat_2_1", "公交地铁", "cat_2", "subway", "#7EDDD5", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_2_2", "打车", "cat_2", "taxi", "#7EDDD5", isCustom = false, sortOrder = 2, now),

            // 购物
            CategoryEntity("cat_3", "购物", null, "shopping", "#95E1D3", isCustom = false, sortOrder = 3, now),
            CategoryEntity("cat_3_1", "服饰", "cat_3", "clothing", "#B8E8DE", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_3_2", "日用品", "cat_3", "daily", "#B8E8DE", isCustom = false, sortOrder = 2, now),

            // 娱乐
            CategoryEntity("cat_4", "娱乐", null, "entertainment", "#F38181", isCustom = false, sortOrder = 4, now),
            CategoryEntity("cat_4_1", "电影", "cat_4", "movie", "#F5A3A3", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_4_2", "游戏", "cat_4", "game", "#F5A3A3", isCustom = false, sortOrder = 2, now),

            // 居住
            CategoryEntity("cat_5", "居住", null, "home", "#AA96DA", isCustom = false, sortOrder = 5, now),
            CategoryEntity("cat_5_1", "房租", "cat_5", "rent", "#C5B7E6", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_5_2", "水电燃气", "cat_5", "utility", "#C5B7E6", isCustom = false, sortOrder = 2, now),

            // 医疗
            CategoryEntity("cat_6", "医疗", null, "medical", "#FCBAD3", isCustom = false, sortOrder = 6, now),
            CategoryEntity("cat_6_1", "门诊", "cat_6", "clinic", "#FDCDE0", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_6_2", "药品", "cat_6", "medicine", "#FDCDE0", isCustom = false, sortOrder = 2, now),

            // 教育
            CategoryEntity("cat_7", "教育", null, "education", "#FFFFD2", isCustom = false, sortOrder = 7, now),
            CategoryEntity("cat_7_1", "书籍", "cat_7", "book", "#FFFFE5", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_7_2", "课程", "cat_7", "course", "#FFFFE5", isCustom = false, sortOrder = 2, now),

            // 其他
            CategoryEntity("cat_8", "其他", null, "other", "#A8D8EA", isCustom = false, sortOrder = 8, now)
        )
    }
}
```

---

*文档版本: v1.0*
*创建日期: 2025-01-16*
*架构师: Claude (Software Architecture Agent)*
