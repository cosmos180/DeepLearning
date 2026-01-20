# 项目目录结构设计

## 1. 项目结构概述

### 1.1 模块化架构

基于Clean Architecture和功能模块化,项目采用多模块结构:

```
BillTrack/
├── app/                    # 主应用模块
├── core/                   # 核心模块(公共依赖)
├── data/                  # 数据模块
├── feature/               # 功能模块集合
│   ├── home/             # 首页功能
│   ├── expense/           # 消费记录功能
│   ├── statistics/        # 统计分析功能
│   ├── category/          # 分类管理功能
│   ├── budget/            # 预算管理功能
│   └── settings/          # 设置功能
└── buildSrc/              # 构建配置
```

---

## 2. 详细目录结构

### 2.1 完整目录树

```
BillTrack/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/billtrack/app/
│   │   │   │   ├── BillTrackApplication.kt
│   │   │   │   └── di/
│   │   │   │       ├── AppModule.kt
│   │   │   │       └── NetworkModule.kt
│   │   │   ├── res/
│   │   │   │   ├── drawable/
│   │   │   │   ├── mipmap-hdpi/
│   │   │   │   ├── mipmap-mdpi/
│   │   │   │   ├── mipmap-xhdpi/
│   │   │   │   ├── mipmap-xxhdpi/
│   │   │   │   ├── mipmap-xxxhdpi/
│   │   │   │   ├── values/
│   │   │   │   │   ├── strings.xml
│   │   │   │   │   ├── colors.xml
│   │   │   │   │   └── themes.xml
│   │   │   │   └── xml/
│   │   │   │       └── backup_descriptor.xml
│   │   │   └── AndroidManifest.xml
│   │   └── test/
│   │       └── java/com/billtrack/app/
│   │           └── ExampleUnitTest.kt
│   │
│   └── build.gradle.kts
│
├── core/
│   ├── src/
│   │   └── main/java/com/billtrack/core/
│   │       ├── di/
│   │       │   ├── DispatcherModule.kt
│   │       │   └── DatabaseModule.kt
│   │       ├── domain/
│   │       │   ├── model/
│   │       │   │   ├── Expense.kt
│   │       │   │   ├── Category.kt
│   │       │   │   ├── Budget.kt
│   │       │   │   ├── UserSettings.kt
│   │       │   │   ├── Statistics.kt
│   │       │   │   └── Result.kt
│   │       │   ├── repository/
│   │       │   │   ├── ExpenseRepository.kt
│   │       │   │   ├── CategoryRepository.kt
│   │       │   │   ├── BudgetRepository.kt
│   │       │   │   └── UserSettingsRepository.kt
│   │       │   └── usecase/
│   │       │       ├── AddExpenseUseCase.kt
│   │       │       ├── GetExpensesUseCase.kt
│   │       │       ├── UpdateExpenseUseCase.kt
│   │       │       ├── DeleteExpenseUseCase.kt
│   │       │       ├── GetStatisticsUseCase.kt
│   │       │       ├── GetCategoriesUseCase.kt
│   │       │       ├── AddCategoryUseCase.kt
│   │       │       ├── SetBudgetUseCase.kt
│   │       │       └── GetUserSettingsUseCase.kt
│   │       ├── data/
│   │       │   ├── local/
│   │       │   │   ├── dao/
│   │       │   │   │   ├── ExpenseDao.kt
│   │       │   │   │   ├── CategoryDao.kt
│   │       │   │   │   ├── BudgetDao.kt
│   │       │   │   │   └── UserSettingsDao.kt
│   │       │   │   ├── entity/
│   │       │   │   │   ├── ExpenseEntity.kt
│   │       │   │   │   ├── CategoryEntity.kt
│   │       │   │   │   ├── BudgetEntity.kt
│   │       │   │   │   └── UserSettingsEntity.kt
│   │       │   │   └── converter/
│   │       │   │       ├── ExpenseConverter.kt
│   │       │   │       ├── CategoryConverter.kt
│   │       │   │       └── BudgetConverter.kt
│   │       │   ├── repository/
│   │       │   │   ├── ExpenseRepositoryImpl.kt
│   │       │   │   ├── CategoryRepositoryImpl.kt
│   │       │   │   ├── BudgetRepositoryImpl.kt
│   │       │   │   └── UserSettingsRepositoryImpl.kt
│   │       │   └── preferences/
│   │       │       └── UserPreferences.kt
│   │       ├── util/
│   │       │   ├── DateUtils.kt
│   │       │   ├── CurrencyUtils.kt
│   │       │   ├── ValidationUtils.kt
│   │       │   └── EncryptionUtils.kt
│   │       └── common/
│   │           ├── Result.kt
│   │           ├── UiEvent.kt
│   │           └── UiText.kt
│   └── build.gradle.kts
│
├── feature/
│   ├── home/
│   │   ├── src/
│   │   │   └── main/java/com/billtrack/feature/home/
│   │   │       ├── presentation/
│   │   │       │   ├── HomeScreen.kt
│   │   │       │   ├── HomeViewModel.kt
│   │   │       │   └── HomeUiState.kt
│   │   │       └── di/
│   │   │           └── HomeModule.kt
│   │   └── build.gradle.kts
│   │
│   ├── expense/
│   │   ├── src/
│   │   │   └── main/java/com/billtrack/feature/expense/
│   │   │       ├── presentation/
│   │   │       │   ├── ExpenseListScreen.kt
│   │   │       │   ├── ExpenseDetailScreen.kt
│   │   │       │   ├── AddExpenseDialog.kt
│   │   │       │   ├── ExpenseViewModel.kt
│   │   │       │   └── ExpenseUiState.kt
│   │   │       └── di/
│   │   │           └── ExpenseModule.kt
│   │   └── build.gradle.kts
│   │
│   ├── statistics/
│   │   ├── src/
│   │   │   └── main/java/com/billtrack/feature/statistics/
│   │   │       ├── presentation/
│   │   │       │   ├── StatisticsScreen.kt
│   │   │       │   ├── TrendChartView.kt
│   │   │       │   ├── CategoryPieChartView.kt
│   │   │       │   ├── StatisticsViewModel.kt
│   │   │       │   └── StatisticsUiState.kt
│   │   │       └── di/
│   │   │           └── StatisticsModule.kt
│   │   └── build.gradle.kts
│   │
│   ├── category/
│   │   ├── src/
│   │   │   └── main/java/com/billtrack/feature/category/
│   │   │       ├── presentation/
│   │   │       │   ├── CategoryListScreen.kt
│   │   │       │   ├── AddCategoryDialog.kt
│   │   │       │   ├── CategoryViewModel.kt
│   │   │       │   └── CategoryUiState.kt
│   │   │       └── di/
│   │   │           └── CategoryModule.kt
│   │   └── build.gradle.kts
│   │
│   ├── budget/
│   │   ├── src/
│   │   │   └── main/java/com/billtrack/feature/budget/
│   │   │       ├── presentation/
│   │   │       │   ├── BudgetScreen.kt
│   │   │       │   ├── BudgetSetupDialog.kt
│   │   │       │   ├── BudgetViewModel.kt
│   │   │       │   └── BudgetUiState.kt
│   │   │       └── di/
│   │   │           └── BudgetModule.kt
│   │   └── build.gradle.kts
│   │
│   └── settings/
│       ├── src/
│       │   └── main/java/com/billtrack/feature/settings/
│       │       ├── presentation/
│       │       │   ├── SettingsScreen.kt
│       │       │   ├── DataManagementScreen.kt
│       │       │   ├── SettingsViewModel.kt
│       │       │   └── SettingsUiState.kt
│       │       └── di/
│       │           └── SettingsModule.kt
│       └── build.gradle.kts
│
├── data/
│   ├── src/
│   │   └── main/java/com/billtrack/data/
│   │       ├── local/
│   │       │   ├── AppDatabase.kt
│   │       │   └── DatabaseInitializer.kt
│   │       └── remote/
│   │           ├── api/
│   │           │   ├── ApiService.kt
│   │           │   └── dto/
│   │           │       ├── ExpenseDto.kt
│   │           │       ├── CategoryDto.kt
│   │           │       └── StatisticsDto.kt
│   │           └── mapper/
│   │               ├── ExpenseMapper.kt
│   │               └── CategoryMapper.kt
│   └── build.gradle.kts
│
├── buildSrc/
│   ├── src/
│   │   └── main/java/com/billtrack/buildsrc/
│   │       ├── dependencies/
│   │       │   ├── Libraries.kt
│   │       │   └── Versions.kt
│   │       └── configuration/
│   │           └── Config.kt
│   └── build.gradle.kts
│
├── gradle/
│   ├── libs.versions.toml
│   └── wrapper/
│       └── gradle-wrapper.properties
│
├── .gitignore
├── .gitattributes
├── .editorconfig
├── LICENSE
├── README.md
├── build.gradle.kts (项目根目录)
└── settings.gradle.kts
```

---

## 3. 模块说明

### 3.1 app模块 (主应用)

**职责**: 应用入口、依赖注入配置

**关键文件**:
- `BillTrackApplication.kt`: Application类
- `di/AppModule.kt`: Hilt模块配置
- `di/NetworkModule.kt`: 网络模块(预留)

**依赖**:
- 依赖所有feature模块
- 依赖core模块

### 3.2 core模块 (核心)

**职责**: 领域层、数据层、公共组件

**关键包**:
- `domain/`: 领域模型、Repository接口、Use Case
- `data/`: 数据库实现、Repository实现
- `util/`: 工具类
- `common/`: 公共组件

**依赖**:
- 无其他模块依赖
- 被所有feature模块依赖

### 3.3 data模块 (数据层实现)

**职责**: 数据持久化实现

**关键包**:
- `local/`: 本地数据库
- `remote/`: 远程API(预留)

**依赖**:
- 依赖core模块

### 3.4 feature模块 (功能模块)

#### home模块

**职责**: 首页、统计概览

**关键文件**:
- `presentation/HomeScreen.kt`: 首页UI
- `presentation/HomeViewModel.kt`: 首页ViewModel

**依赖**:
- 依赖core模块

#### expense模块

**职责**: 消费记录管理

**关键文件**:
- `presentation/ExpenseListScreen.kt`: 记录列表
- `presentation/AddExpenseDialog.kt`: 添加记录对话框

#### statistics模块

**职责**: 统计分析、图表展示

**关键文件**:
- `presentation/StatisticsScreen.kt`: 统计页面
- `presentation/TrendChartView.kt`: 趋势图

#### category模块

**职责**: 分类管理

**关键文件**:
- `presentation/CategoryListScreen.kt`: 分类列表
- `presentation/AddCategoryDialog.kt`: 添加分类

#### budget模块

**职责**: 预算管理

**关键文件**:
- `presentation/BudgetScreen.kt`: 预算页面
- `presentation/BudgetSetupDialog.kt`: 预算设置

#### settings模块

**职责**: 设置、数据管理

**关键文件**:
- `presentation/SettingsScreen.kt`: 设置页面
- `presentation/DataManagementScreen.kt`: 数据管理

---

## 4. 命名规范

### 4.1 包命名

```
com.billtrack.{layer}.{feature}.{component}

示例:
- com.billtrack.feature.home.presentation
- com.billtrack.core.domain.model
- com.billtrack.core.data.local.dao
```

### 4.2 文件命名

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| Activity | XActivity | MainActivity.kt |
| Fragment | XFragment | HomeFragment.kt |
| Composable | XScreen / XDialog | HomeScreen.kt |
| ViewModel | XViewModel | HomeViewModel.kt |
| Use Case | XUseCase | AddExpenseUseCase.kt |
| Repository | XRepository | ExpenseRepository.kt |
| DAO | XDao | ExpenseDao.kt |
| Entity | XEntity | ExpenseEntity.kt |
| Model | X | Expense.kt |

### 4.3 变量命名

```kotlin
// UI状态
private val _uiState = MutableStateFlow<HomeUiState>(HomeUiState.Loading)
val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

// Use Case参数
class AddExpenseUseCase(
    private val expenseRepository: ExpenseRepository
)

// 函数参数
fun addExpense(
    amount: BigDecimal,
    categoryId: String,
    date: LocalDateTime
)

// 常量
private const val DEFAULT_PAGE_SIZE = 20
```

---

## 5. Gradle配置

### 5.1 根目录build.gradle.kts

```kotlin
plugins {
    id("com.android.application") version "8.1.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.0" apply false
    id("com.google.dagger.hilt.android") version "2.48" apply false
    id("com.google.devtools.ksp") version "1.9.0-1.0.0" apply false
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}
```

### 5.2 app/build.gradle.kts

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.devtools.ksp")
    id("com.google.dagger.hilt.android")
}

android {
    namespace = "com.billtrack.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.billtrack.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.4"
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    signingConfigs {
        create("release") {
            storeFile = file("keystore/billtrack-release.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = System.getenv("KEY_ALIAS")
            keyPassword = System.getenv("KEY_PASSWORD")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }

        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
        }
    }

    testOptions {
        unitTests {
            isIncludeAndroidResources = true
        }
    }
}

dependencies {
    implementation(project(":core"))
    implementation(project(":feature:home"))
    implementation(project(":feature:expense"))
    implementation(project(":feature:statistics"))
    implementation(project(":feature:category"))
    implementation(project(":feature:budget"))
    implementation(project(":feature:settings"))

    // Core dependencies
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.1")

    // Compose
    implementation(platform("androidx.compose:compose-bom:2023.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")

    // Hilt
    implementation("com.google.dagger:hilt-android:2.48")
    ksp("com.google.dagger:hilt-compiler:2.48")

    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.mockk:mockk:1.13.8")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.5.4")
}
```

### 5.3 core/build.gradle.kts

```kotlin
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("com.google.devtools.ksp")
    id("com.google.dagger.hilt.android")
}

android {
    namespace = "com.billtrack.core"
    compileSdk = 34

    defaultConfig {
        minSdk = 24
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildFeatures {
        buildConfig = true
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    // Kotlin
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")

    // Room
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")

    // Hilt
    implementation("com.google.dagger:hilt-android:2.48")
    ksp("com.google.dagger:hilt-compiler:2.48")

    // DataStore
    implementation("androidx.datastore:datastore-preferences:1.0.0")

    // Charts (MPAndroidChart for 1.0, consider Compose Charts later)
    implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")

    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.mockk:mockk:1.13.8")
}
```

---

## 6. 代码组织原则

### 6.1 文件组织

**单一职责**: 每个文件只包含一个主要类/组件

**示例**:
```
✅ 推荐:
- HomeScreen.kt (只包含HomeScreen Composable)
- HomeViewModel.kt (只包含HomeViewModel)
- AddExpenseUseCase.kt (只包含AddExpenseUseCase)

❌ 避免:
- HomeComponents.kt (包含多个组件)
- HomeViewModelAndUseCase.kt (混合职责)
```

### 6.2 包组织

**按功能分层**:
```
feature/home/
├── presentation/     # UI层
├── domain/          # 领域层(可选)
└── di/              # 依赖注入
```

**按技术分层**:
```
core/
├── domain/          # 领域层
├── data/            # 数据层
├── util/            # 工具类
└── common/          # 公共组件
```

### 6.3 依赖方向

```
┌─────────────────────┐
│   Feature Module    │
│   (依赖Core)         │
└──────────┬──────────┘
           │
           ↓
┌�─────────────────────┐
│   Core Module        │
│   (不依赖Feature)     │
└─────────────────────┘
```

---

## 7. 最佳实践

### 7.1 Compose组织

```kotlin
// 按功能拆分Compose函数
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Column {
        HomeHeader()
        when (val state = uiState) {
            is HomeUiState.Loading -> LoadingView()
            is HomeUiState.Success -> HomeContent(state.statistics)
            is HomeUiState.Error -> ErrorView(state.message)
        }
    }
}

@Composable
private fun HomeHeader() {
    // 顶部栏
}

@Composable
private fun HomeContent(statistics: Statistics) {
    // 内容区
}
```

### 7.2 ViewModel组织

```kotlin
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val getStatisticsUseCase: GetStatisticsUseCase
) : ViewModel() {

    // UI状态
    private val _uiState = MutableStateFlow<HomeUiState>(HomeUiState.Loading)
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    // 初始化
    init {
        loadStatistics()
    }

    // 公开方法
    fun refresh() {
        loadStatistics()
    }

    // 私有方法
    private fun loadStatistics() {
        viewModelScope.launch {
            // ...
        }
    }
}
```

### 7.3 Use Case组织

```kotlin
class GetStatisticsUseCase(
    private val expenseRepository: ExpenseRepository,
    private val budgetRepository: BudgetRepository
) {
    suspend operator fun invoke(
        startDate: LocalDateTime,
        endDate: LocalDateTime
    ): Statistics {
        // 1. 获取数据
        val expenses = expenseRepository.getExpensesByDateRange(startDate, endDate)
        val budget = budgetRepository.getBudget(startDate.toYearMonth())

        // 2. 计算统计
        val totalExpense = expenses.sumOf { it.amount }
        val categoryExpenses = calculateCategoryBreakdown(expenses, totalExpense)

        // 3. 返回结果
        return Statistics(
            totalExpense = totalExpense,
            expenseByCategory = categoryExpenses,
            dailyTrend = emptyList(),
            budgetUsage = null
        )
    }
}
```

---

## 8. 总结

### 8.1 架构优势

1. **模块化**: 功能独立,易于维护
2. **分层清晰**: 职责明确,易于测试
3. **依赖合理**: 避免循环依赖
4. **可扩展**: 易于添加新功能

### 8.2 开发效率

1. **新功能模块**: 只需创建新的feature模块
2. **代码复用**: Core模块提供公共能力
3. **团队协作**: 模块边界清晰,减少冲突

---

*文档版本: v1.0*
*创建日期: 2025-01-16*
*架构师: Claude (Software Architecture Agent)*
