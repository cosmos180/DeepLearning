# BillTrack 开发文档

## 项目概述

账单通是一个基于Kotlin和Jetpack Compose开发的个人消费记录Android应用。项目采用Clean Architecture架构模式,遵循MVVM设计理念。

## 架构说明

### 分层架构

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (Compose UI + ViewModel + StateFlow)   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           Domain Layer                  │
│  (Use Case + Domain Model + Repository) │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│            Data Layer                   │
│   (Repository Impl + DAO + Room DB)     │
└─────────────────────────────────────────┘
```

### 模块职责

#### app模块
- 应用入口
- 依赖注入配置
- 主题配置

#### core模块
- **domain**: 领域模型、Repository接口、Use Case
- **data**: 数据库实体、DAO、Repository实现
- **util**: 工具类(日期、货币、验证)
- **common**: 公共组件(UI事件、UI文本)

#### data模块
- AppDatabase配置
- 数据库初始化
- 预设数据

#### feature模块
- **home**: 首页、统计概览
- **expense**: 消费记录管理
- **statistics**: 统计分析、图表
- **category**: 分类管理
- **budget**: 预算管理
- **settings**: 设置

## 数据库设计

### 表结构

#### expenses表
```sql
CREATE TABLE expenses (
    id TEXT PRIMARY KEY,
    amount TEXT NOT NULL,
    category_id TEXT NOT NULL,
    date INTEGER NOT NULL,
    note TEXT,
    payment_method TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

#### categories表
```sql
CREATE TABLE categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    parent_id TEXT,
    icon TEXT NOT NULL,
    color TEXT NOT NULL,
    is_custom INTEGER DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
);
```

#### budgets表
```sql
CREATE TABLE budgets (
    id TEXT PRIMARY KEY,
    category_id TEXT,
    amount TEXT NOT NULL,
    month TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

#### user_settings表
```sql
CREATE TABLE user_settings (
    id TEXT PRIMARY KEY,
    currency TEXT DEFAULT 'CNY',
    decimal_places INTEGER DEFAULT 2,
    month_start_day INTEGER DEFAULT 1,
    theme TEXT DEFAULT 'light',
    language TEXT DEFAULT 'zh-CN',
    reminder_enabled INTEGER DEFAULT 1,
    reminder_time TEXT DEFAULT '21:00'
);
```

## 开发流程

### 1. 添加新的数据模型

1. 在`core/domain/model/`创建领域模型
2. 在`core/data/local/entity/`创建Entity
3. 在`core/data/local/entity/`中添加转换方法
4. 在`AppDatabase`中添加Entity
5. 创建DAO接口
6. 运行数据库迁移(如需要)

### 2. 添加新的功能

1. 创建feature模块
2. 定义Use Case
3. 实现Repository
4. 创建ViewModel
5. 实现Compose UI
6. 添加导航配置

### 3. 调试技巧

#### 查看数据库
```bash
adb shell
run-as com.billtrack.app
cd databases
sqlite3 billtrack_db.db
.tables
```

#### 查看日志
```bash
adb logcat | grep BillTrack
```

## 性能优化

### 数据库优化
- 使用索引加速查询
- 使用Flow进行响应式查询
- 分页加载大量数据

### UI优化
- 使用Compose的稳定性注解
- 使用key优化LazyColumn
- 细粒度组件拆分

### 内存优化
- 使用弱引用避免内存泄漏
- 及时清理Flow订阅
- 使用对象池复用对象

## 测试策略

### 单元测试
- Use Case测试
- Repository测试
- ViewModel测试
- 工具类测试

### UI测试
- Compose UI测试
- 导航测试
- 用户流程测试

### 集成测试
- 数据库操作测试
- Repository集成测试

## 常见问题

### Q: 如何添加新的分类?
A: 在`DatabaseInitializer.getPresetCategories()`中添加。

### Q: 如何修改主题颜色?
A: 在`app/ui/theme/Theme.kt`中修改颜色定义。

### Q: 如何添加新的语言?
A: 创建新的`values-xx/strings.xml`文件。

### Q: 数据库如何迁移?
A: 增加数据库版本号,添加Migration对象。

## 相关资源

- [Jetpack Compose文档](https://developer.android.com/jetpack/compose)
- [Room数据库文档](https://developer.android.com/training/data-storage/room)
- [Hilt依赖注入](https://developer.android.com/training/dependency-injection/hilt-android)
- [Kotlin Coroutines](https://developer.android.com/kotlin/coroutines)
