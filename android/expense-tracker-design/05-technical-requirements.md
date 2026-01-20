# 技术需求文档

## 1. 技术架构概述

本文档定义"账单通"产品的技术架构、技术选型、数据模型、API设计和实现规范。

---

## 2. 技术栈选型

### 2.1 移动端技术栈

#### 方案一：原生开发（推荐用于1.0版本）

**Android**：
- **语言**：Kotlin
- **最低SDK**：API 24 (Android 7.0)
- **目标SDK**：API 34 (Android 14)
- **构建工具**：Gradle 8.x
- **架构模式**：MVVM + Clean Architecture
- **依赖注入**：Hilt
- **异步处理**：Kotlin Coroutines + Flow
- **本地存储**：Room Database
- **图表库**：MPAndroidChart
- **UI框架**：Jetpack Compose（推荐）或传统XML

**关键依赖**：
```gradle
// Core
implementation("androidx.core:core-ktx:1.12.0")
implementation("androidx.appcompat:appcompat:1.6.1")

// Lifecycle
implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.7.0")

// Room Database
implementation("androidx.room:room-runtime:2.6.1")
implementation("androidx.room:room-ktx:2.6.1")
kapt("androidx.room:room-compiler:2.6.1")

// Coroutines
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

// Hilt
implementation("com.google.dagger:hilt-android:2.48")
kapt("com.google.dagger:hilt-compiler:2.48")

// Chart
implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")

// UI
implementation("androidx.compose.ui:ui:1.5.4")
implementation("androidx.compose.material3:material3:1.1.2")
```

**iOS**（后续版本）：
- **语言**：Swift
- **最低版本**：iOS 12.0
- **架构模式**：MVVM
- **UI框架**：SwiftUI
- **数据存储**：Core Data
- **图表库**：Charts

---

#### 方案二：跨平台开发（考虑用于2.0版本）

**Flutter**：
- **语言**：Dart
- **最低版本**：Android 5.0+、iOS 10+
- **状态管理**：Provider/Riverpod
- **本地存储**：sqflite、Hive
- **图表库**：fl_chart

**React Native**：
- **语言**：TypeScript
- **最低版本**：Android 5.0+、iOS 10+
- **状态管理**：Redux/MobX
- **本地存储**：AsyncStorage、Realm
- **图表库**：react-native-chart-kit

**1.0版本建议**：
- 优先选择Android原生开发
- 快速验证MVP
- 后续考虑跨平台

---

### 2.2 后端技术栈（预留）

**未来版本可能需要**：
- **服务端**：Node.js + Express / Python + FastAPI
- **数据库**：PostgreSQL / MongoDB
- **缓存**：Redis
- **对象存储**：AWS S3 / 阿里云OSS
- **推送服务**：Firebase Cloud Messaging

**1.0版本**：
- 无需后端
- 所有数据本地存储
- 预留API接口设计

---

### 2.3 开发工具

| 工具类型 | 工具名称 | 用途 |
|----------|----------|------|
| IDE | Android Studio | Android开发 |
| 版本控制 | Git | 代码管理 |
| 项目管理 | Jira / Trello | 任务管理 |
| 设计工具 | Figma | UI设计 |
| API测试 | Postman | API测试（未来） |
| 性能分析 | Android Profiler | 性能监控 |
| 崩溃收集 | Firebase Crashlytics | 崩溃分析 |

---

## 3. 系统架构设计

### 3.1 整体架构

```
┌─────────────────────────────────────────────────┐
│                  Presentation Layer              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Activity │  │ Fragment │  │  Widget  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
                       ↕
┌─────────────────────────────────────────────────┐
│                   Domain Layer                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ViewModel │  │ Use Case │  │  Model   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
                       ↕
┌─────────────────────────────────────────────────┐
│                    Data Layer                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Repository│  │   DAO    │  │ Database │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
                       ↕
┌─────────────────────────────────────────────────┐
│                  Local Storage                   │
│              (Room Database)                     │
└─────────────────────────────────────────────────┘
```

### 3.2 分层说明

**Presentation Layer（表现层）**：
- **职责**：UI展示、用户交互
- **组件**：Activity、Fragment、Compose Widget
- **原则**：不包含业务逻辑，只处理UI相关

**Domain Layer（领域层）**：
- **职责**：业务逻辑、用例编排
- **组件**：ViewModel、Use Case、Domain Model
- **原则**：独立于UI和数据层，可复用

**Data Layer（数据层）**：
- **职责**：数据获取、存储、转换
- **组件**：Repository、DAO、Database
- **原则**：对外暴露统一接口，隐藏数据源细节

---

## 4. 数据模型设计

### 4.1 数据库设计

#### Room Database Schema

```kotlin
@Database(
    entities = [
        Expense::class,
        Category::class,
        Budget::class,
        UserSettings::class
    ],
    version = 1,
    exportSchema = true
)
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

---

### 4.2 实体定义

#### Expense（消费记录）

```kotlin
@Entity(
    tableName = "expenses",
    foreignKeys = [
        ForeignKey(
            entity = Category::class,
            parentColumns = ["id"],
            childColumns = ["category_id"],
            onDelete = ForeignKey.RESTRICT
        )
    ],
    indices = [
        Index(value = ["category_id"]),
        Index(value = ["date"]),
        Index(value = ["amount"])
    ]
)
data class Expense(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String = UUID.randomUUID().toString(),

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
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @ColumnInfo(name = "updated_at")
    val updatedAt: LocalDateTime = LocalDateTime.now()
)
```

#### Category（分类）

```kotlin
@Entity(
    tableName = "categories",
    foreignKeys = [
        ForeignKey(
            entity = Category::class,
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
data class Category(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String = UUID.randomUUID().toString(),

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
    val createdAt: LocalDateTime = LocalDateTime.now()
)
```

#### Budget（预算）

```kotlin
@Entity(
    tableName = "budgets",
    foreignKeys = [
        ForeignKey(
            entity = Category::class,
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
data class Budget(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String = UUID.randomUUID().toString(),

    @ColumnInfo(name = "category_id")
    val categoryId: String? = null, // null表示总预算

    @ColumnInfo(name = "amount")
    val amount: BigDecimal,

    @ColumnInfo(name = "month")
    val month: YearMonth, // 格式: YYYY-MM

    @ColumnInfo(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @ColumnInfo(name = "updated_at")
    val updatedAt: LocalDateTime = LocalDateTime.now()
)
```

#### UserSettings（用户设置）

```kotlin
@Entity(tableName = "user_settings")
data class UserSettings(
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
)
```

---

### 4.3 DAO（数据访问对象）

#### ExpenseDao

```kotlin
@Dao
interface ExpenseDao {
    @Query("SELECT * FROM expenses ORDER BY date DESC")
    fun getAllExpenses(): Flow<List<Expense>>

    @Query("SELECT * FROM expenses WHERE id = :id")
    suspend fun getExpenseById(id: String): Expense?

    @Query("SELECT * FROM expenses WHERE date >= :startDate AND date < :endDate ORDER BY date DESC")
    fun getExpensesByDateRange(startDate: LocalDateTime, endDate: LocalDateTime): Flow<List<Expense>>

    @Query("SELECT * FROM expenses WHERE category_id = :categoryId ORDER BY date DESC")
    fun getExpensesByCategory(categoryId: String): Flow<List<Expense>>

    @Query("SELECT * FROM expenses WHERE note LIKE '%' || :keyword || '%' OR category_id IN (SELECT id FROM categories WHERE name LIKE '%' || :keyword || '%') ORDER BY date DESC")
    fun searchExpenses(keyword: String): Flow<List<Expense>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertExpense(expense: Expense)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertExpenses(expenses: List<Expense>)

    @Update
    suspend fun updateExpense(expense: Expense)

    @Delete
    suspend fun deleteExpense(expense: Expense)

    @Query("DELETE FROM expenses WHERE id IN (:ids)")
    suspend fun deleteExpenses(ids: List<String>)

    @Query("DELETE FROM expenses")
    suspend fun deleteAllExpenses()

    @Query("SELECT SUM(amount) FROM expenses WHERE date >= :startDate AND date < :endDate")
    suspend fun getTotalExpense(startDate: LocalDateTime, endDate: LocalDateTime): BigDecimal?

    @Query("SELECT category_id, SUM(amount) as total FROM expenses WHERE date >= :startDate AND date < :endDate GROUP BY category_id ORDER BY total DESC")
    suspend fun getExpenseByCategory(startDate: LocalDateTime, endDate: LocalDateTime): List<CategoryExpense>
}
```

---

## 5. 业务逻辑设计

### 5.1 Use Cases

#### AddExpenseUseCase

```kotlin
class AddExpenseUseCase(
    private val expenseRepository: ExpenseRepository,
    private val categoryRepository: CategoryRepository
) {
    suspend operator fun invoke(
        amount: BigDecimal,
        categoryId: String,
        date: LocalDateTime,
        note: String? = null,
        paymentMethod: String? = null
    ): Result<Expense> {
        // 验证
        if (amount <= BigDecimal.ZERO) {
            return Result.failure(ValidationException("金额必须大于0"))
        }

        val category = categoryRepository.getCategoryById(categoryId)
            ?: return Result.failure(NotFoundException("分类不存在"))

        // 创建记录
        val expense = Expense(
            amount = amount,
            categoryId = categoryId,
            date = date,
            note = note,
            paymentMethod = paymentMethod
        )

        // 保存
        return try {
            expenseRepository.insertExpense(expense)
            Result.success(expense)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

#### GetStatisticsUseCase

```kotlin
class GetStatisticsUseCase(
    private val expenseRepository: ExpenseRepository,
    private val budgetRepository: BudgetRepository,
    private val userSettingsRepository: UserSettingsRepository
) {
    suspend operator fun invoke(
        startDate: LocalDateTime,
        endDate: LocalDateTime
    ): Statistics {
        // 获取总支出
        val totalExpense = expenseRepository.getTotalExpense(startDate, endDate)
            ?: BigDecimal.ZERO

        // 获取分类支出
        val expenseByCategory = expenseRepository.getExpenseByCategory(startDate, endDate)

        // 获取预算
        val month = YearMonth.from(startDate)
        val budget = budgetRepository.getBudgetByMonth(month)

        // 获取设置
        val settings = userSettingsRepository.getSettings()

        return Statistics(
            totalExpense = totalExpense,
            expenseByCategory = expenseByCategory,
            budget = budget,
            currency = settings.currency
        )
    }
}
```

---

### 5.2 ViewModel

#### HomeViewModel

```kotlin
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val getStatisticsUseCase: GetStatisticsUseCase,
    private val getRecentExpensesUseCase: GetRecentExpensesUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow<HomeUiState>(HomeUiState.Loading)
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            _uiState.value = HomeUiState.Loading

            try {
                val now = LocalDateTime.now()
                val monthStart = now.withDayOfMonth(1).withHour(0).withMinute(0).withSecond(0)
                val monthEnd = monthStart.plusMonths(1)

                val statistics = getStatisticsUseCase(monthStart, monthEnd)
                val recentExpenses = getRecentExpensesUseCase(5)

                _uiState.value = HomeUiState.Success(
                    statistics = statistics,
                    recentExpenses = recentExpenses
                )
            } catch (e: Exception) {
                _uiState.value = HomeUiState.Error(e.message ?: "加载失败")
            }
        }
    }

    fun refresh() {
        loadData()
    }
}

sealed class HomeUiState {
    object Loading : HomeUiState()
    data class Success(
        val statistics: Statistics,
        val recentExpenses: List<Expense>
    ) : HomeUiState()
    data class Error(val message: String) : HomeUiState()
}
```

---

## 6. API设计（预留）

### 6.1 RESTful API设计（未来版本）

**基础URL**：`https://api.billtrack.com/v1`

**认证**：JWT Token

#### 认证接口

```
POST   /auth/register        # 注册
POST   /auth/login           # 登录
POST   /auth/refresh         # 刷新Token
POST   /auth/logout          # 登出
```

#### 消费记录接口

```
GET    /expenses             # 获取记录列表
POST   /expenses             # 创建记录
GET    /expenses/:id         # 获取记录详情
PUT    /expenses/:id         # 更新记录
DELETE /expenses/:id         # 删除记录
GET    /expenses/statistics  # 获取统计数据
```

#### 分类接口

```
GET    /categories           # 获取分类列表
POST   /categories           # 创建分类
GET    /categories/:id       # 获取分类详情
PUT    /categories/:id       # 更新分类
DELETE /categories/:id       # 删除分类
```

#### 预算接口

```
GET    /budgets              # 获取预算列表
POST   /budgets              # 创建预算
GET    /budgets/:id          # 获取预算详情
PUT    /budgets/:id          # 更新预算
DELETE /budgets/:id          # 删除预算
```

#### 用户设置接口

```
GET    /settings             # 获取设置
PUT    /settings             # 更新设置
```

#### 数据同步接口

```
GET    /sync/pull            # 拉取数据
POST   /sync/push            # 推送数据
```

---

### 6.2 数据模型（API版本）

#### Expense（API版本）

```json
{
  "id": "uuid",
  "amount": 28.50,
  "category": {
    "id": "uuid",
    "name": "餐饮",
    "icon": "restaurant",
    "color": "#FF6B6B"
  },
  "date": "2025-01-16T12:30:00Z",
  "note": "麦当劳套餐",
  "paymentMethod": "wechat",
  "createdAt": "2025-01-16T12:30:00Z",
  "updatedAt": "2025-01-16T12:30:00Z"
}
```

---

## 7. 性能优化

### 7.1 数据库优化

- **索引**：为常用查询字段添加索引
- **分页**：列表数据分页加载
- **缓存**：使用Room的缓存机制
- **异步查询**：使用Flow进行响应式查询

### 7.2 UI优化

- **列表优化**：使用DiffUtil优化RecyclerView
- **图片加载**：使用Glide/Coil加载图标
- **懒加载**：图表数据懒加载
- **动画优化**：使用MotionLayout减少动画卡顿

### 7.3 内存优化

- **对象池**：复用常用对象
- **弱引用**：避免内存泄漏
- **内存监控**：使用LeakCanary检测泄漏

### 7.4 启动优化

- **懒加载**：延迟初始化非关键组件
- **线程优化**：使用后台线程初始化
- **资源优化**：减少资源文件大小

---

## 8. 安全设计

### 8.1 数据安全

- **加密存储**：敏感数据使用AES加密
- **密钥管理**：使用AndroidKeyStore存储密钥
- **备份加密**：备份文件使用密码保护

### 8.2 权限管理

- **最小权限**：只申请必要权限
- **权限说明**：清晰解释权限用途
- **运行时请求**：动态申请权限

### 8.3 代码安全

- **代码混淆**：使用ProGuard/R8
- **防篡改**：使用签名验证
- **日志脱敏**：敏感信息不记录日志

---

## 9. 测试策略

### 9.1 单元测试

- **覆盖率目标**：80%以上
- **测试框架**：JUnit 5 + MockK
- **测试内容**：
  * Use Cases
  * ViewModels
  * Repository
  * Utils

### 9.2 集成测试

- **测试框架**：AndroidX Test
- **测试内容**：
  * Database operations
  * DAO queries
  * Repository methods

### 9.3 UI测试

- **测试框架**：Espresso
- **测试内容**：
  * 关键用户流程
  * 页面跳转
  * 数据展示

### 9.4 性能测试

- **测试工具**：Android Profiler
- **测试内容**：
  * 启动时间
  * 页面渲染时间
  * 内存占用
  * CPU使用率

---

## 10. 部署策略

### 10.1 构建配置

**Build Types**：
- **debug**：开发调试
- **release**：正式发布

**Product Flavors**：
- **free**：免费版
- **pro**：付费版（未来）

### 10.2 版本管理

**版本号规则**：`主版本.次版本.修订版本`
- 主版本：重大功能变更
- 次版本：新增功能
- 修订版本：Bug修复

**1.0版本**：`1.0.0`

### 10.3 发布流程

1. **代码审查**：Pull Request Review
2. **测试验证**：通过所有测试
3. **构建APK**：签名打包
4. **内测发布**：TestFlight / 内部测试
5. **公测发布**：Play Store / 应用市场
6. **正式发布**：全量发布

---

## 11. 监控和日志

### 11.1 崩溃监控

- **工具**：Firebase Crashlytics
- **监控内容**：
  * 崩溃率
  * ANR率
  * 错误堆栈

### 11.2 性能监控

- **工具**：Firebase Performance
- **监控内容**：
  * 启动时间
  * 页面加载时间
  * 网络请求时间

### 11.3 用户行为分析

- **工具**：Firebase Analytics
- **追踪内容**：
  * 活跃用户数
  * 功能使用率
  * 用户留存率

### 11.4 日志管理

- **日志级别**：VERBOSE、DEBUG、INFO、WARN、ERROR
- **日志格式**：时间戳 + 级别 + 标签 + 消息
- **日志存储**：本地文件 + 远程上报（可选）

---

## 12. 开发规范

### 12.1 代码规范

- **Kotlin代码规范**：遵循Android Kotlin Style Guide
- **命名规范**：驼峰命名，语义清晰
- **注释规范**：公共API必须添加KDoc注释
- **代码格式化**：使用ktfmt统一格式

### 12.2 Git规范

- **分支策略**：Git Flow
- **提交信息**：Conventional Commits
  * feat: 新功能
  * fix: Bug修复
  * docs: 文档更新
  * style: 代码格式
  * refactor: 重构
  * test: 测试
  * chore: 构建/工具

- **分支命名**：
  * master：主分支
  * develop：开发分支
  * feature/*：功能分支
  * bugfix/*：修复分支
  * release/*：发布分支
  * hotfix/*：紧急修复

### 12.3 Code Review

- **Review时机**：Pull Request创建后
- **Review要点**：
  * 代码质量
  * 功能正确性
  * 性能影响
  * 安全问题
  * 测试覆盖

---

*文档版本：v1.0*
*创建日期：2025-01-16*
*最后更新：2025-01-16*
