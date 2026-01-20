# 技术选型文档

## 1. 技术选型概述

### 1.1 选型标准

基于产品需求、团队技能和项目约束,技术选型遵循以下标准:

| 优先级 | 标准 | 说明 |
|--------|------|------|
| P0 | 快速开发 | 2个月内完成MVP |
| P0 | 性能优异 | 记账<3秒,启动<2秒 |
| P0 | 稳定可靠 | 生产级质量 |
| P1 | 易维护 | 代码清晰、模块化 |
| P1 | 成本控制 | 开源优先、免费工具 |
| P2 | 跨平台 | 预留扩展能力 |

### 1.2 选型决策矩阵

```
维度权重分配:
├── 开发效率 (40%)    - 快速迭代、低学习成本
├── 性能表现 (30%)    - 响应速度、流畅度
├── 生态成熟度 (20%)  - 社区支持、文档完善
└── 成本控制 (10%)    - 工具免费、云服务成本
```

---

## 2. 前端技术栈

### 2.1 开发语言: Kotlin

**选择理由**:

| 维度 | 评分 | 说明 |
|------|------|------|
| 开发效率 | ⭐⭐⭐⭐⭐ | 简洁语法、类型推断、空安全 |
| 性能表现 | ⭐⭐⭐⭐⭐ | 编译为字节码,与Java性能相当 |
| 生态成熟度 | ⭐⭐⭐⭐⭐ | Google官方支持、JetBrains维护 |
| 学习成本 | ⭐⭐⭐⭐ | 对Java开发者友好 |
| 社区支持 | ⭐⭐⭐⭐⭐ | Android开发首选语言 |

**核心优势**:
1. **空安全**: 编译时检查空指针,减少90%运行时崩溃
2. **协程**: 原生协程支持,简化异步编程
3. **扩展函数**: 增强现有类功能,提高代码复用
4. **数据类**: 自动生成equals/hashCode/toString
5. **互操作性**: 与Java 100%互操作

**替代方案对比**:

| 语言 | 优势 | 劣势 | 决策 |
|------|------|------|------|
| Kotlin | 现代、安全、高效 | 相对新 | ✅ 选择 |
| Java | 熟悉、稳定 | 冗长、空指针风险 | ❌ |
| Dart (Flutter) | 跨平台 | 生态小、包大 | ❌ MVP阶段 |
| JavaScript (RN) | 跨平台、热更新 | 性能、依赖JS桥接 | ❌ |

### 2.2 UI框架: Jetpack Compose

**选择理由**:

| 维度 | 评分 | 说明 |
|------|------|------|
| 开发效率 | ⭐⭐⭐⭐⭐ | 声明式UI,代码量减少50% |
| 性能表现 | ⭐⭐⭐⭐⭐ | 跳过XML,直接渲染,60fps稳定 |
| 生态成熟度 | ⭐⭐⭐⭐ | Google官方推荐,1.5.x版本稳定 |
| 学习成本 | ⭐⭐⭐ | 新范式,需要学习曲线 |
| 工具支持 | ⭐⭐⭐⭐⭐ | Android Studio完整支持 |

**核心优势**:
1. **声明式UI**: `@Composable` 函数式UI,状态驱动
2. **预览功能**: 实时预览UI,无需编译运行
3. **强类型**: 编译时检查布局错误
4. **动画简化**: API简洁,易于实现复杂动画
5. **Material 3**: 原生支持Material Design 3

**代码示例对比**:

**传统XML方式**:
```xml
<!-- activity_home.xml -->
<LinearLayout>
    <TextView android:id="@+id/title" />
    <RecyclerView android:id="@+id/list" />
</LinearLayout>

// HomeActivity.kt
val title = findViewById<TextView>(R.id.title)
title.text = "本月支出"
```

**Compose方式**:
```kotlin
@Composable
fun HomeScreen() {
    Column {
        Text("本月支出")
        ExpenseList()
    }
}
```

**替代方案对比**:

| UI框架 | 优势 | 劣势 | 决策 |
|--------|------|------|------|
| Compose | 现代、高效、类型安全 | 相对新 | ✅ 选择 |
| XML | 熟悉、稳定 | 冗长、维护成本高 | ❌ |
| Flutter | 跨平台 | Dart生态、包体积 | ❌ |

### 2.3 架构模式: MVVM + Clean Architecture

**选择理由**:

| 维度 | 评分 | 说明 |
|------|------|------|
| 可测试性 | ⭐⭐⭐⭐⭐ | 层间解耦,易于单元测试 |
| 可维护性 | ⭐⭐⭐⭐⭐ | 职责清晰,易于修改 |
| 可扩展性 | ⭐⭐⭐⭐ | 预留扩展接口 |
| 学习成本 | ⭐⭐⭐ | 需要理解分层概念 |

**架构层次**:

```
┌─────────────────────────────────────────┐
│  Presentation Layer (表现层)            │
│  - Jetpack Compose UI                   │
│  - ViewModel (StateFlow)                │
│  - 用户交互处理                          │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Domain Layer (领域层)                   │
│  - Use Case (业务逻辑)                   │
│  - Domain Model (领域模型)               │
│  - Repository Interface                 │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Data Layer (数据层)                     │
│  - Repository Implementation             │
│  - Room DAO                              │
│  - Local Storage                         │
└─────────────────────────────────────────┘
```

**替代方案对比**:

| 架构 | 优势 | 劣势 | 决策 |
|------|------|------|------|
| MVVM + Clean | 测试性好、分层清晰 | 代码量略多 | ✅ 选择 |
| MVC | 简单 | Controller臃肿 | ❌ |
| MVP | 视图独立 | 接口冗多 | ❌ |
| MVI | 单向数据流 | 学习曲线陡 | ❌ |

---

## 3. 数据层技术栈

### 3.1 本地数据库: Room Database

**选择理由**:

| 维度 | 评分 | 说明 |
|------|------|------|
| 性能表现 | ⭐⭐⭐⭐⭐ | SQLite封装,查询高效 |
| 开发效率 | ⭐⭐⭐⭐⭐ | 编译时SQL验证,类型安全 |
| 生态成熟度 | ⭐⭐⭐⭐⭐ | Google官方ORM |
| 功能完整性 | ⭐⭐⭐⭐⭐ | 迁移、Flow、缓存全支持 |

**核心特性**:
1. **编译时验证**: SQL语法检查,类型安全
2. **Flow支持**: 响应式查询,自动更新UI
3. **数据库迁移**: 版本管理,自动化迁移
4. **类型转换**: TypeConverter支持复杂类型
5. **索引优化**: 自动创建索引,提升查询性能

**数据库设计**:

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

**替代方案对比**:

| 数据库 | 优势 | 劣势 | 决策 |
|--------|------|------|------|
| Room | 官方、类型安全、Flow支持 | 略重 | ✅ 选择 |
| Realm | 快速、跨平台 | 非官方、体积大 | ❌ |
| ObjectBox | 超快、API简洁 | 生态小 | ❌ |
| SharedPreferences | 简单 | 只支持键值对 | ❌ |
| DataStore | 现代化 | 不支持关系型数据 | ❌ |

### 3.2 数据格式: JSON / CSV / Excel

**选择理由**:

| 格式 | 用途 | 优势 | 库 |
|------|------|------|-----|
| **JSON** | 备份文件 | 结构化、易解析 | kotlinx.serialization |
| **CSV** | 导出数据 | 通用、Excel兼容 | Apache Commons CSV |
| **Excel** | 导出报表 | 格式化、可视化 | Apache POI |

**实现方案**:

```kotlin
// JSON序列化
@Serializable
data class ExpenseData(
    val expenses: List<Expense>,
    val categories: List<Category>,
    val backupTime: Long
)

// CSV导出
class CsvExporter {
    fun exportExpenses(expenses: List<Expense>): File {
        val csv = CSVPrinter( FileWriter("expenses.csv"), CSVFormat.DEFAULT)
        expenses.forEach { expense ->
            csv.printRecord(
                expense.id,
                expense.amount,
                expense.categoryName,
                expense.date
            )
        }
        return csv.file
    }
}

// Excel导出
class ExcelExporter {
    fun exportToExcel(expenses: List<Expense>): File {
        val workbook = XSSFWorkbook()
        val sheet = workbook.createSheet("消费记录")
        expenses.forEachIndexed { index, expense ->
            val row = sheet.createRow(index)
            row.createCell(0).setCellValue(expense.amount.toString())
            row.createCell(1).setCellValue(expense.categoryName)
        }
        return File("expenses.xlsx")
    }
}
```

---

## 4. 异步处理技术

### 4.1 协程: Kotlin Coroutines

**选择理由**:

| 维度 | 评分 | 说明 |
|------|------|------|
| 开发效率 | ⭐⭐⭐⭐⭐ | 同步代码写异步逻辑 |
| 性能表现 | ⭐⭐⭐⭐⭐ | 轻量级线程,内存占用低 |
| 生态成熟度 | ⭐⭐⭐⭐⭐ | 官方推荐,广泛使用 |
| 错误处理 | ⭐⭐⭐⭐⭐ | try-catch机制清晰 |

**使用场景**:

```kotlin
// 1. 数据库操作(挂起函数)
@Dao
interface ExpenseDao {
    @Query("SELECT * FROM expenses")
    suspend fun getAllExpenses(): List<Expense>
}

// 2. 业务逻辑(协程作用域)
class ExpenseViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadExpenses() {
        viewModelScope.launch {
            try {
                val expenses = expenseRepository.getAllExpenses()
                _uiState.value = UiState.Success(expenses)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
            }
        }
    }
}

// 3. 响应式流(Flow)
fun observeExpenses(): Flow<List<Expense>> {
    return expenseDao.getAllExpensesFlow()
        .catch { e -> emit(emptyList()) }
}
```

**替代方案对比**:

| 异步方案 | 优势 | 劣势 | 决策 |
|----------|------|------|------|
| Coroutines | 简洁、高效、官方 | 需要学习 | ✅ 选择 |
| RxJava | 强大、成熟 | 陡峭学习曲线 | ❌ |
| LiveData | 生命周期感知 | 功能有限 | 仅UI层 |
| Callback | 简单 | 回调地狱 | ❌ |

### 4.2 响应式流: Flow

**选择理由**:

| 维度 | 评分 | 说明 |
|------|------|------|
| 开发效率 | ⭐⭐⭐⭐⭐ | 操作符丰富,链式调用 |
| 性能表现 | ⭐⭐⭐⭐⭐ | 冷流,按需订阅 |
| 集成性 | ⭐⭐⭐⭐⭐ | Room原生支持 |

**数据流设计**:

```kotlin
// Repository层返回Flow
class ExpenseRepository(
    private val expenseDao: ExpenseDao
) {
    fun getAllExpenses(): Flow<List<Expense>> {
        return expenseDao.getAllExpenses()
            .map { entities -> entities.map { it.toDomainModel() } }
            .catch { e -> emit(emptyList()) }
    }
}

// ViewModel层转换为StateFlow
class HomeViewModel(
    private val expenseRepository: ExpenseRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<HomeUiState>(HomeUiState.Loading)
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        expenseRepository.getAllExpenses()
            .onEach { expenses ->
                _uiState.value = HomeUiState.Success(expenses)
            }
            .launchIn(viewModelScope)
    }
}

// UI层收集StateFlow
@Composable
fun HomeScreen(viewModel: HomeViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    when (val state = uiState) {
        is HomeUiState.Success -> ExpenseList(state.expenses)
        is HomeUiState.Loading -> LoadingView()
        is HomeUiState.Error -> ErrorView(state.message)
    }
}
```

---

## 5. 依赖注入: Hilt

**选择理由**:

| 维度 | 评分 | 说明 |
|------|------|------|
| 开发效率 | ⭐⭐⭐⭐⭐ | 编译时生成代码,无需反射 |
| 性能表现 | ⭐⭐⭐⭐⭐ | 无运行时开销 |
| 生态成熟度 | ⭐⭐⭐⭐⭐ | Google官方推荐 |
| Android集成 | ⭐⭐⭐⭐⭐ | ViewModel、WorkManager集成 |

**使用示例**:

```kotlin
// 1. Application
@HiltAndroidApp
class BillTrackApplication : Application()

// 2. Module
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "billtrack_db"
        ).build()
    }

    @Provides
    fun provideExpenseDao(database: AppDatabase): ExpenseDao {
        return database.expenseDao()
    }
}

// 3. 注入ViewModel
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val getExpensesUseCase: GetExpensesUseCase
) : ViewModel()

// 4. 注入Composable
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel()
) {
    // ...
}
```

**替代方案对比**:

| DI框架 | 优势 | 劣势 | 决策 |
|--------|------|------|------|
| Hilt | 官方、编译时、ViewModel支持 | 需要注解 | ✅ 选择 |
| Dagger 2 | 强大、稳定 | 配置繁琐 | Hilt基于Dagger |
| Koin | 简单、无注解 | 运行时、性能差 | ❌ |

---

## 6. 图表库: MPAndroidChart / Compose Charts

**选择理由**:

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能完整性 | ⭐⭐⭐⭐⭐ | 折线、饼图、柱状图全覆盖 |
| 性能表现 | ⭐⭐⭐⭐ | 大数据集流畅 |
| 定制性 | ⭐⭐⭐⭐ | 高度可定制 |

**使用方案**:

**阶段1: MPAndroidChart (稳定)**

```kotlin
// 依赖
implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")

// 使用
class ChartAdapter {
    fun createLineChart(data: List<DailyExpense>): LineChart {
        val entries = data.map { Entry(it.day.toFloat(), it.amount.toFloat()) }
        val dataSet = LineDataSet(entries, "每日支出").apply {
            color = Color.parseColor("#4CAF50")
            setCircleColor(Color.parseColor("#4CAF50"))
        }
        val lineData = LineData(dataSet)
        chart.data = lineData
        chart.invalidate()
        return chart
    }
}
```

**阶段2: Compose Charts (迁移中,2025年)**

```kotlin
// 依赖(当Compose Charts稳定后)
implementation("com.github.bytebeats:compose-charts:0.1.0")

// 使用
@Composable
fun ExpenseLineChart(data: List<DailyExpense>) {
    LineChart(
        data = data.map { it.amount.toFloat() },
        modifier = Modifier.fillMaxWidth()
    )
}
```

**替代方案对比**:

| 图表库 | 优势 | 劣势 | 决策 |
|--------|------|------|------|
| MPAndroidChart | 成熟、稳定、功能全 | 非Compose原生 | ✅ 选择(1.0版本) |
| Compose Charts | Compose原生 | 不够成熟 | 考虑(1.2版本) |
| AnyChart | 功能强大 | 商业收费 | ❌ |
| Vico | 现代、Compose友好 | 生态小 | 观望 |

---

## 7. 测试技术栈

### 7.1 单元测试: JUnit 5 + MockK

**选择理由**:

| 工具 | 用途 | 优势 |
|------|------|------|
| **JUnit 5** | 测试框架 | 现代化、参数化测试 |
| **MockK** | Mock框架 | Kotlin原生,语法简洁 |
| **Truth** | 断言库 | Google推荐,可读性强 |

**测试示例**:

```kotlin
class AddExpenseUseCaseTest {
    private lateinit var useCase: AddExpenseUseCase
    private lateinit var mockRepo: ExpenseRepository
    private lateinit var mockCategoryRepo: CategoryRepository

    @Before
    fun setup() {
        mockRepo = mockk()
        mockCategoryRepo = mockk()
        useCase = AddExpenseUseCase(mockRepo, mockCategoryRepo)
    }

    @Test
    fun `should add expense successfully`() = runTest {
        // Given
        val expense = Expense(amount = BigDecimal("28.50"), categoryId = "cat1")
        coEvery { mockCategoryRepo.getCategoryById("cat1") } returns Category(id = "cat1")
        coEvery { mockRepo.insertExpense(any()) } just Runs

        // When
        val result = useCase(expense.amount, expense.categoryId, LocalDateTime.now())

        // Then
        assertTrue(result.isSuccess)
        coVerify { mockRepo.insertExpense(any()) }
    }
}
```

### 7.2 UI测试: Compose Testing

**选择理由**:

| 工具 | 用途 | 优势 |
|------|------|------|
| **Compose Testing** | UI测试 | Jetpack集成,语义化 |
| **Robolectric** | 本地单元测试 | 无需模拟器 |

**测试示例**:

```kotlin
class AddExpenseUiTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun `should show error when amount is empty`() {
        // Given
        composeTestRule.setContent {
            AddExpenseScreen()
        }

        // When
        composeTestRule.onNodeWithText("保存").performClick()

        // Then
        composeTestRule.onNodeWithText("请输入金额").assertIsDisplayed()
    }
}
```

---

## 8. 工具链

### 8.1 构建工具: Gradle (Kotlin DSL)

**选择理由**:
- 官方支持,类型安全
- IDEA完美集成
- 插件生态丰富

**配置示例**:

```kotlin
// build.gradle.kts (Module)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("kotlin-parcelize")
}

android {
    compileSdk = 34

    defaultConfig {
        applicationId = "com.billtrack.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }

    buildFeatures {
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.4"
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    // Core
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")

    // Compose
    implementation(platform("androidx.compose:compose-bom:2023.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")

    // Hilt
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")

    // Room
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")

    // Charts
    implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")

    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.mockk:mockk:1.13.8")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.5.4")
}
```

### 8.2 CI/CD: GitHub Actions

**选择理由**:
- 免费用于公开项目
- YAML配置简单
- 与GitHub深度集成

**工作流示例**:

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

      - name: Run unit tests
        run: ./gradlew test

      - name: Run instrumented tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 29
          script: ./gradlew connectedCheck

      - name: Build APK
        run: ./gradlew assembleDebug
```

---

## 9. 第三方库依赖清单

### 9.1 核心依赖

| 库名 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| androidx.core:core-ktx | 1.12.0 | Android核心KTX | Apache 2.0 |
| androidx.compose.ui | 1.5.4 | Compose UI框架 | Apache 2.0 |
| androidx.compose.material3 | 1.1.2 | Material Design 3 | Apache 2.0 |
| androidx.lifecycle | 2.7.0 | 生命周期管理 | Apache 2.0 |
| androidx.room:room-ktx | 2.6.1 | 本地数据库 | Apache 2.0 |
| com.google.dagger:hilt-android | 2.48 | 依赖注入 | Apache 2.0 |
| org.jetbrains.kotlinx:kotlinx-coroutines-android | 1.7.3 | 协程支持 | Apache 2.0 |
| com.github.PhilJay:MPAndroidChart | v3.1.0 | 图表库 | GPL-3.0 |

### 9.2 测试依赖

| 库名 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| junit:junit | 4.13.2 | 单元测试框架 | EPL |
| io.mockk:mockk | 1.13.8 | Mock框架 | Apache 2.0 |
| androidx.compose.ui:ui-test-junit4 | 1.5.4 | Compose UI测试 | Apache 2.0 |

### 9.3 可选依赖(功能扩展)

| 库名 | 版本 | 用途 | 计划版本 |
|------|------|------|---------|
| androidx.security:security-crypto | 1.1.0-alpha06 | 数据加密 | 1.1版本 |
| org.apache.poi:poi-ooxml | 5.2.3 | Excel导出 | 1.1版本 |
| com.google.code.gson:gson | 2.10.1 | JSON序列化 | 备份功能 |

---

## 10. 技术选型总结

### 10.1 技术栈全景图

```
┌─────────────────────────────────────────────────────────┐
│                     技术栈全景图                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  前端层                                         │  │
│  │  ├─ Kotlin 1.9.x (语言)                        │  │
│  │  ├─ Jetpack Compose 1.5.x (UI框架)             │  │
│  │  ├─ Material Design 3 (设计系统)               │  │
│  │  └─ Coroutines + Flow (异步处理)               │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  架构层                                         │  │
│  │  ├─ MVVM + Clean Architecture                 │  │
│  │  ├─ Hilt (依赖注入)                            │  │
│  │  └─ StateFlow (状态管理)                       │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  数据层                                         │  │
│  │  ├─ Room Database 2.6.x (本地数据库)           │  │
│  │  ├─ SQLite (存储引擎)                          │  │
│  │  ├─ Flow (响应式流)                            │  │
│  │  └─ SharedPreferences/DataStore (KV存储)        │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  第三方库                                       │  │
│  │  ├─ MPAndroidChart (图表)                      │  │
│  │  ├─ Apache POI (Excel导出)                     │  │
│  │  └─ kotlinx.serialization (JSON)               │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  测试工具                                       │  │
│  │  ├─ JUnit 5 (单元测试)                         │  │
│  │  ├─ MockK (Mock框架)                           │  │
│  │  └─ Compose Testing (UI测试)                   │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  开发工具                                       │  │
│  │  ├─ Android Studio (IDE)                      │  │
│  │  ├─ Gradle 8.x (构建工具)                      │  │
│  │  ├─ Git (版本控制)                             │  │
│  │  └─ GitHub Actions (CI/CD)                     │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 10.2 技术选型决策记录

| 决策点 | 选择 | 理由 | 替代方案 |
|--------|------|------|---------|
| 开发语言 | Kotlin | 现代、安全、官方支持 | Java, Dart |
| UI框架 | Compose | 声明式、高效、类型安全 | XML, Flutter |
| 架构模式 | MVVM + Clean | 测试性好、分层清晰 | MVC, MVP |
| 数据库 | Room | 官方ORM、Flow支持 | Realm, ObjectBox |
| 异步处理 | Coroutines | 简洁、高效、官方 | RxJava, Callback |
| 依赖注入 | Hilt | 官方、编译时、ViewModel支持 | Koin, Dagger2 |
| 图表库 | MPAndroidChart | 成熟稳定 | Compose Charts |
| 测试框架 | JUnit + MockK | Kotlin原生、语法简洁 | JUnit + Mockito |

### 10.3 技术风险与应对

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| Compose不稳定 | UI bug | 中 | 使用稳定版本(1.5.x),预留回退方案 |
| Room性能问题 | 查询慢 | 低 | 索引优化,分页加载,测试验证 |
| 第三方库更新 | 兼容性问题 | 低 | 锁定版本号,渐进升级 |
| Kotlin版本更新 | 语法变化 | 低 | 渐进迁移,保持Kotlin编译器版本 |

---

*文档版本: v1.0*
*创建日期: 2025-01-16*
*架构师: Claude (Software Architecture Agent)*
