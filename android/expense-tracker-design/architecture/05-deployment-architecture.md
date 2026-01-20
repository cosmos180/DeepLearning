# 部署架构设计

## 1. 部署架构概述

### 1.1 部署策略

**1.0版本部署策略**: 本地优先架构,无需服务器部署

```
┌─────────────────────────────────────────────────────────┐
│                 1.0版本部署架构                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Google Play Store                               │  │
│  │  (应用分发)                                        │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓ APK                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │  用户设备 (Android)                               │  │
│  │  ├─ App (本地存储)                                │  │
│  │  ├─ Room Database (SQLite)                       │  │
│  │  └─ Firebase (监控)                               │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Firebase Services (监控与分析)                  │  │
│  │  ├─ Crashlytics (崩溃监控)                        │  │
│  │  ├─ Analytics (用户行为分析)                     │  │
│  │  └─ Performance (性能监控)                        │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**2.0版本部署架构(预留)**: 云同步支持

```
┌─────────────────────────────────────────────────────────┐
│                 2.0版本部署架构 (规划)                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Client Apps                                      │  │
│  │  ├─ Android App                                   │  │
│  │  ├─ iOS App                                       │  │
│  │  └─ Web App (PWA)                                 │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓ HTTPS                             │
│  ┌─────────────────────────────────────────────────┐  │
│  │  CDN (静态资源)                                   │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Load Balancer                                   │  │
│  └─────────────────────────────────────────────────┘  │
│                      ↓                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  API Server (Node.js/Python)                     │  │
│  │  ├─ REST API                                      │  │
│  │  └─ WebSocket (实时同步)                          │  │
│  └─────────────────────────────────────────────────┘  │
│          ↓              ↓              ↓                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ PostgreSQL  │ │    Redis     │ │    S3        │  │
│  │  (主数据库)  │ │   (缓存)      │ │  (文件存储)   │  │
│  └──────────────┘ └──────────────┘ └──────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 1.0版本部署架构

### 2.1 应用分发

#### Google Play Store发布

**发布流程**:

```
1. 准备应用素材
   ├─ 应用图标 (512x512 PNG)
   ├─ 功能截图 (至少2张,手机/平板)
   ├─ 应用描述 (简短+完整)
   ├─ 隐私政策 (URL)
   └─ 内容分级 (问卷)

2. 签名APK
   ├─ 生成签名密钥 (.jks)
   └─ 使用Gradle构建Release APK

3. 上传到Google Play Console
   ├─ 创建应用
   ├─ 填写商店信息
   ├─ 上传APK (AAB格式)
   └─ 提交审核

4. 审核与发布
   ├─ 人工审核 (约3-7天)
   ├─ 审核通过后自动发布
   └─ 可选择分阶段发布
```

**关键配置**:

```kotlin
// build.gradle.kts (Module)
android {
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
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

#### 国内应用市场

**目标市场**:
- 华为应用市场
- 小米应用商店
- OPPO软件商店
- vivo应用商店
- 应用宝

**分发策略**:
1. 优先Google Play (国际版)
2. 同步发布国内市场 (需单独审核)
3. 官网提供APK下载

### 2.2 监控与分析

#### Firebase集成

**项目配置**:

```kotlin
// build.gradle.kts (Project)
buildscript {
    dependencies {
        classpath("com.google.gms:google-services:4.4.0")
    }
}

// build.gradle.kts (Module)
plugins {
    id("com.google.gms.google-services")
}

dependencies {
    implementation(platform("com.google.firebase:firebase-bom:32.7.0"))
    implementation("com.google.firebase:firebase-analytics")
    implementation("com.google.firebase:firebase-crashlytics")
    implementation("com.google.firebase:firebase-performance")
}
```

**监控配置**:

```kotlin
// Application.kt
@HiltAndroidApp
class BillTrackApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Firebase初始化
        FirebaseApp.initializeApp(this)

        // Crashlytics
        FirebaseCrashlytics.getInstance().setCrashlyticsCollectionEnabled(true)

        // Performance
        FirebasePerformance.getInstance().setPerformanceCollectionEnabled(true)

        // Analytics
        FirebaseAnalytics.getInstance(this).setDefaultEventParameters(
            bundleOf("app_version" to BuildConfig.VERSION_NAME)
        )
    }
}
```

**事件追踪**:

```kotlin
// 用户行为追踪
object AnalyticsEvents {
    fun logExpenseAdded(amount: BigDecimal, category: String) {
        firebaseAnalytics.logEvent("expense_added") {
            param("amount", amount.toDouble())
            param("category", category)
        }
    }

    fun logBudgetSet(amount: BigDecimal) {
        firebaseAnalytics.logEvent("budget_set") {
            param("amount", amount.toDouble())
        }
    }

    fun logViewStatistics() {
        firebaseAnalytics.logEvent("view_statistics")
    }
}
```

---

## 3. 2.0版本部署架构 (规划)

### 3.1 后端服务部署

#### 技术栈选择

| 服务 | 技术选型 | 说明 |
|------|---------|------|
| API服务器 | Node.js + Express / Python + FastAPI | RESTful API |
| 数据库 | PostgreSQL 14+ | 主数据库 |
| 缓存 | Redis 6+ | 会话、缓存 |
| 文件存储 | AWS S3 / 阿里云OSS | 备份文件、图片 |
| CDN | Cloudflare / CloudFront | 静态资源分发 |

#### 服务器架构

```
┌───────────────────────────────────────────────────────┐
│                    CDN Layer                         │
│              (Cloudflare / CloudFront)                │
└───────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────┐
│                 Load Balancer                         │
│                  (nginx / ALB)                         │
└───────────────────────────────────────────────────────┘
            ↓                           ↓
┌─────────────────────┐   ┌─────────────────────┐
│  API Server 1        │   │  API Server 2        │
│  (Node.js/Python)     │   │  (Node.js/Python)     │
│  - REST API           │   │  - REST API           │
│  - WebSocket         │   │  - WebSocket         │
└─────────────────────┘   └─────────────────────┘
            ↓                           ↓
┌───────────────────────────────────────────────────────┐
│                  Data Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ PostgreSQL   │  │    Redis     │  │    S3     │ │
│  │  (Primary)   │  │   (Cache)    │  │  (Files)  │ │
│  │  ┌─────────┐ │  │              │  │           │ │
│  │  │Standby  │ │  │              │  │           │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└───────────────────────────────────────────────────────┘
```

### 3.2 数据库架构

#### PostgreSQL主从架构

```sql
-- 主库配置
postgresql.conf:
  - listen_addresses = '*'
  - max_connections = 100
  - shared_buffers = 256MB
  - wal_level = replica

-- 从库配置
recovery.conf:
  - standby_mode = on
  - primary_conninfo = 'host=primary port=5432 user=replica'
```

#### 数据库分片策略 (远期)

```
┌─────────────────────────────────────────────────────┐
│                  应用层                              │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│                分片路由                              │
│         (按user_id进行哈希分片)                      │
└─────────────────────────────────────────────────────┘
        ↓           ↓           ↓           ↓
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Shard 1  │ │ Shard 2  │ │ Shard 3  │ │ Shard 4  │
│ 用户0-25%│ │用户25-50%│ │用户50-75%│ │用户75-100%│
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### 3.3 缓存策略

#### Redis缓存架构

```kotlin
// 缓存策略
class CacheStrategy {
    // 用户数据缓存 (TTL: 1小时)
    suspend fun getUser(userId: String): User? {
        return redis.get("user:$userId")
            ?: database.getUser(userId).also {
                redis.setex("user:$userId", 3600, it)
            }
    }

    // 统计数据缓存 (TTL: 5分钟)
    suspend fun getStatistics(userId: String, month: String): Statistics? {
        val key = "stats:$userId:$month"
        return redis.get(key)
            ?: database.calculateStatistics(userId, month).also {
                redis.setex(key, 300, it)
            }
    }

    // 热点数据预热
    suspend fun warmupCache() {
        // 预加载常用分类
        redis.set("categories:popular", categoryService.getPopularCategories())
    }
}
```

---

## 4. CI/CD流程

### 4.1 持续集成

#### GitHub Actions工作流

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

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

      - name: Grant execute permission
        run: chmod +x gradlew

      - name: Run unit tests
        run: ./gradlew test testDebugUnitTest

      - name: Run instrumented tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 29
          script: ./gradlew connectedCheck

      - name: Upload test reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: app/build/reports/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Grant execute permission
        run: chmod +x gradlew

      - name: Build Release APK
        run: ./gradlew assembleRelease

      - name: Sign APK
        run: |
          echo "${{ secrets.KEYSTORE_PASSWORD }}" | keystore-pass -v build/app/release/app-release.apk
          jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA256 -keystore keystore/billtrack-release.jks -storepass "${{ secrets.KEYSTORE_PASSWORD }}" -keypass "${{ secrets.KEY_PASSWORD }}" build/app/release/app-release.apk "${{ secrets.KEY_ALIAS }}"

      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: app-release
          path: build/app/release/app-release.apk
```

### 4.2 持续部署

#### 自动发布到Google Play

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy-play:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Release AAB
        run: ./gradlew bundleRelease

      - name: Deploy to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
          packageName: com.billtrack.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
          status: completed
```

---

## 5. 监控与告警

### 5.1 应用监控

#### Firebase Crashlytics

```kotlin
// Application.kt
class BillTrackApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Crashlytics配置
        FirebaseCrashlytics.getInstance().apply {
            setCrashlyticsCollectionEnabled(!BuildConfig.DEBUG)
            setUserId(getUserId())
            setCustomKey("app_version", BuildConfig.VERSION_NAME)
            setCustomKey("device_model", Build.MODEL)
        }
    }

    private fun getUserId(): String {
        // 获取或生成用户ID
        val prefs = getSharedPreferences("user_prefs", MODE_PRIVATE)
        return prefs.getString("user_id", UUID.randomUUID().toString()).also {
            prefs.edit().putString("user_id", it).apply()
        }
    }
}
```

#### 自定义错误上报

```kotlin
// 错误处理工具
object ErrorHandler {
    fun handleError(exception: Throwable, userVisible: Boolean = false) {
        // 记录到Crashlytics
        FirebaseCrashlytics.getInstance().recordException(exception)

        // 记录到日志
        Log.e("BillTrack", "Error occurred", exception)

        // 用户可见的错误
        if (userVisible) {
            // 显示友好的错误提示
            showErrorToUser(exception)
        }
    }

    private fun showErrorToUser(exception: Throwable) {
        when (exception) {
            is ValidationException -> showToast(exception.message ?: "输入验证失败")
            is NotFoundException -> showToast("资源不存在")
            is NetworkException -> showToast("网络连接失败,请检查网络设置")
            else -> showToast("操作失败,请重试")
        }
    }
}
```

### 5.2 性能监控

#### Firebase Performance

```kotlin
// 性能追踪
class PerformanceTracker {

    fun trackExpenseSave() {
        val trace = FirebasePerformance.getInstance().newTrace("expense_save")
        trace.start()
        // ... 保存操作 ...
        trace.stop()
    }

    fun trackStatisticsLoad() {
        val trace = FirebasePerformance.getInstance().newTrace("statistics_load")
        trace.start()
        // ... 加载统计 ...
        trace.stop()
    }
}
```

### 5.3 用户分析

#### Google Analytics事件

```kotlin
// 用户行为分析
object AnalyticsManager {

    private val firebaseAnalytics = Firebase.analytics

    fun logExpenseAdded(
        amount: BigDecimal,
        category: String,
        paymentMethod: String?
    ) {
        firebaseAnalytics.logEvent(FirebaseAnalytics.Event.ADD_TO_CART) {
            param(FirebaseAnalytics.Param.VALUE, amount.toDouble())
            param(FirebaseAnalytics.Param.ITEM_CATEGORY, category)
            param("payment_method", paymentMethod ?: "unknown")
        }
    }

    fun logCategoryViewed(categoryName: String) {
        firebaseAnalytics.logEvent("view_category") {
            param("category_name", categoryName)
        }
    }

    fun logBudgetAlert(threshold: Float) {
        firebaseAnalytics.logEvent("budget_alert") {
            param("threshold", threshold.toDouble())
        }
    }
}
```

---

## 6. 版本管理

### 6.1 版本号规则

**语义化版本**:
```
主版本.次版本.修订版本 (Major.Minor.Patch)

示例: 1.0.0
- 主版本: 1 (重大功能变更)
- 次版本: 0 (新增功能)
- 修订版本: 0 (Bug修复)
```

**版本策略**:

| 版本类型 | 发布频率 | 更新内容 | 强制更新 |
|---------|---------|---------|---------|
| Major | 数月/年 | 架构重构、重大功能 | 是 |
| Minor | 1-2月 | 新功能、优化 | 否 |
| Patch | 1-2周 | Bug修复 | 否 |

### 6.2 应用升级

#### 应用内更新检查

```kotlin
// 版本更新检查
class UpdateManager @Inject constructor(
    private val apiService: ApiService,
    private val preferenceManager: PreferenceManager
) {
    suspend fun checkUpdate(): UpdateInfo? {
        val currentVersion = BuildConfig.VERSION_CODE
        val latestVersion = apiService.getLatestVersion()

        return if (latestVersion.versionCode > currentVersion) {
            latestVersion
        } else {
            null
        }
    }

    data class UpdateInfo(
        val versionCode: Int,
        val versionName: String,
        val changelog: String,
        val forceUpdate: Boolean,
        val downloadUrl: String
    )
}
```

---

## 7. 数据备份与恢复

### 7.1 本地备份

```kotlin
// 备份管理器
class BackupManager @Inject constructor(
    private val database: AppDatabase,
    private val context: Context
) {
    suspend fun createBackup(): Result<File> {
        return try {
            // 1. 导出所有数据
            val data = exportAllData()

            // 2. 加密数据
            val encryptedData = EncryptionUtil.encrypt(data, getUserPassword())

            // 3. 保存到文件
            val fileName = "billtrack_backup_${getTimestamp()}.json.enc"
            val file = File(context.getExternalFilesDir(null), fileName)
            file.writeText(encryptedData)

            Result.success(file)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private suspend fun exportAllData(): String {
        // 导出所有数据为JSON
        val expenses = database.expenseDao().getAllExpensesSync()
        val categories = database.categoryDao().getAllCategoriesSync()
        val budgets = database.budgetDao().getAllBudgetsSync()
        val settings = database.userSettingsDao().getSettings()

        return Json.encodeToString(
            BackupData(expenses, categories, budgets, settings)
        )
    }

    @Serializable
    data class BackupData(
        val expenses: List<ExpenseEntity>,
        val categories: List<CategoryEntity>,
        val budgets: List<BudgetEntity>,
        val settings: UserSettingsEntity
    )
}
```

### 7.2 云备份 (2.0版本)

```kotlin
// 云备份管理器
class CloudBackupManager @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun backupToCloud(): Result<Unit> {
        return try {
            val backupFile = createLocalBackup()
            val encryptedFile = encryptBackupFile(backupFile)

            apiService.uploadBackup(encryptedFile)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun restoreFromCloud(): Result<Unit> {
        return try {
            val encryptedData = apiService.downloadBackup()
            val decryptedData = decryptBackupData(encryptedData)

            restoreData(decryptedData)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

---

## 8. 部署清单

### 8.1 上线前检查清单

**功能测试**:
- [ ] 所有P0、P1功能正常
- [ ] 记账流程完整测试
- [ ] 统计图表渲染正确
- [ ] 数据导出功能正常
- [ ] 备份恢复功能正常

**性能测试**:
- [ ] 应用启动时间 < 2秒
- [ ] 记账操作 < 3秒
- [ ] 统计页面加载 < 1秒
- [ ] 内存占用 < 100MB
- [ ] APK体积 < 20MB

**兼容性测试**:
- [ ] Android 7.0-14测试通过
- [ ] 不同分辨率适配正常
- [ ] 不同厂商设备兼容

**安全检查**:
- [ ] 代码混淆 (ProGuard/R8)
- [ ] 签名配置正确
- [ ] 敏感数据加密
- [ ] 权限申请最小化

**文档准备**:
- [ ] 应用图标和截图
- [ ] 应用描述
- [ ] 隐私政策
- [ ] 更新日志

---

## 9. 灾难恢复

### 9.1 数据恢复

**场景1: 用户换机**

```
1. 用户在新设备安装应用
2. 登录账号
3. 选择"从云端恢复"
4. 应用下载备份数据
5. 恢复到本地数据库
6. 提示恢复成功
```

**场景2: 应用数据损坏**

```
1. 用户打开应用检测到数据损坏
2. 提示"数据损坏,是否从备份恢复?"
3. 用户选择"恢复"
4. 从最近备份恢复数据
5. 提示恢复成功
```

### 9.2 回滚策略

**版本回滚**:
```
如果新版本出现严重问题:

1. 立即下架问题版本
2. 从备份恢复上一版本
3. 发布紧急修复版本
4. 重新上线
```

---

*文档版本: v1.0*
*创建日期: 2025-01-16*
*架构师: Claude (Software Architecture Agent)*
