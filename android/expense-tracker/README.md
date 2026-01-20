# 账单通 (BillTrack)

一款专注于个人日常消费记录和分析的轻量级Android应用。

## 产品定位

**Slogan**: 记一笔,懂生活

账单通通过简单快速的记录方式和直观的数据可视化,帮助用户建立健康的消费习惯,实现理性消费。

## 核心特性

- **快速记账**: 3秒完成一笔消费记录
- **智能分类**: 预设8大分类,支持自定义
- **数据统计**: 直观的图表展示消费结构
- **隐私安全**: 数据本地存储,完全掌控个人财务信息

## 技术栈

### 核心技术
- **语言**: Kotlin 1.9.20
- **UI框架**: Jetpack Compose 1.5.4
- **架构模式**: MVVM + Clean Architecture
- **依赖注入**: Hilt 2.48
- **异步处理**: Coroutines + Flow
- **数据库**: Room Database 2.6.1

### 主要依赖
```
androidx.compose:compose-bom:2023.10.01
androidx.room:room-ktx:2.6.1
com.google.dagger:hilt-android:2.48
org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3
```

## 项目结构

```
BillTrack/
├── app/                    # 主应用模块
│   ├── src/main/java/com/billtrack/app/
│   │   ├── BillTrackApplication.kt
│   │   ├── MainActivity.kt
│   │   ├── di/             # 依赖注入配置
│   │   └── ui/theme/       # 主题配置
│   └── build.gradle.kts
│
├── core/                   # 核心模块
│   ├── domain/
│   │   ├── model/          # 领域模型
│   │   ├── repository/     # Repository接口
│   │   └── usecase/        # 用例(待实现)
│   ├── data/
│   │   ├── local/          # 本地数据
│   │   │   ├── dao/        # DAO接口
│   │   │   ├── entity/     # 数据库实体
│   │   │   └── converter/  # 类型转换器
│   │   └── repository/     # Repository实现(待实现)
│   ├── util/               # 工具类
│   └── common/             # 公共组件
│
├── data/                   # 数据模块
│   └── local/
│       ├── AppDatabase.kt  # 数据库配置
│       └── DatabaseInitializer.kt  # 数据库初始化
│
└── feature/                # 功能模块
    ├── home/               # 首页
    ├── expense/            # 消费记录
    ├── statistics/         # 统计分析
    ├── category/           # 分类管理
    ├── budget/             # 预算管理
    └── settings/           # 设置
```

## 架构设计

项目采用**Clean Architecture**架构模式,分为三层:

### 1. 表现层 (Presentation Layer)
- **职责**: UI展示、用户交互
- **组件**: Jetpack Compose UI + ViewModel
- **状态管理**: StateFlow + SharedFlow

### 2. 领域层 (Domain Layer)
- **职责**: 业务逻辑、用例编排
- **组件**: Use Case + Domain Model + Repository接口
- **原则**: 纯Kotlin代码,无Android依赖

### 3. 数据层 (Data Layer)
- **职责**: 数据持久化、缓存、数据转换
- **组件**: Repository实现 + DAO + Room Database
- **数据库**: SQLite (Room)

## 数据模型

### 核心实体
- **Expense** (消费记录): 金额、分类、日期、备注、支付方式
- **Category** (分类): 名称、图标、颜色、父子关系
- **Budget** (预算): 金额、月份、分类关联
- **UserSettings** (用户设置): 货币、主题、语言、提醒

### 预设分类
```
餐饮 (早餐、午餐、晚餐、零食)
交通 (公交地铁、打车)
购物 (服饰、日用品)
娱乐 (电影、游戏)
居住 (房租、水电燃气)
医疗 (门诊、药品)
教育 (书籍、课程)
其他
```

## 构建说明

### 环境要求
- Android Studio Hedgehog (2023.1.1) 或更高版本
- JDK 17
- Android SDK 34
- Gradle 8.2

### 构建步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd BillTrack
```

2. **打开项目**
```bash
# 使用Android Studio打开项目目录
open -a "Android Studio" .
```

3. **构建项目**
```bash
# Debug版本
./gradlew assembleDebug

# Release版本
./gradlew assembleRelease
```

4. **安装到设备**
```bash
# 连接Android设备或启动模拟器
./gradlew installDebug
```

### 运行测试
```bash
# 单元测试
./gradlew test

# UI测试
./gradlew connectedAndroidTest
```

## 开发指南

### 添加新功能

1. **创建领域模型** (core/domain/model)
```kotlin
data class YourFeature(val id: String, ...)
```

2. **创建Entity** (core/data/local/entity)
```kotlin
@Entity(tableName = "your_feature")
data class YourFeatureEntity(...)
```

3. **创建DAO** (core/data/local/dao)
```kotlin
@Dao
interface YourFeatureDao { ... }
```

4. **创建Repository** (core/domain/repository)
```kotlin
interface YourFeatureRepository { ... }
```

5. **创建Use Case** (core/domain/usecase)
```kotlin
class YourFeatureUseCase(...) { ... }
```

6. **创建UI** (feature/your_feature/presentation)
```kotlin
@Composable
fun YourFeatureScreen(...) { ... }
```

### 代码规范

- **命名**: 遵循Kotlin命名规范
- **注释**: 公开API必须添加KDoc注释
- **测试**: 核心功能单元测试覆盖率>80%
- **提交**: 使用Conventional Commits规范

## 版本规划

### v1.0.0 (MVP) - 当前版本
- ✅ 项目架构搭建
- ✅ 数据模型设计
- ✅ 数据库初始化
- ✅ Repository 实现 (Expense, Category, Budget, UserSettings)
- ✅ 核心 Use Cases (Add, Get, Delete, Update Expense, Statistics)
- ✅ 首页功能 (本月支出卡片、最近记录列表)
- ✅ 快速记账功能 (金额输入、分类选择、保存逻辑)
- ✅ 统计功能 (分类支出、每日趋势、月份切换)
- ✅ 导航系统 (页面路由、参数传递)
- 🚧 其他功能开发中
  - 消费详情页
  - 编辑消费记录
  - 设置页面
  - 预算管理
  - 消费搜索

### v1.1.0 (计划中)
- 数据导出(CSV/Excel)
- 数据备份恢复
- 搜索功能优化
- 图表展示优化

### v2.0.0 (远期规划)
- 跨平台支持 (Flutter)
- 云同步功能
- AI智能分类
- 多设备同步

## 贡献指南

欢迎贡献代码、报告Bug或提出新功能建议!

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

```
Copyright (c) 2025 BillTrack

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 邮箱: support@billtrack.app

---

**账单通 - 记一笔,懂生活**
