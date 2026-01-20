# 账单通 (BillTrack) 架构设计文档索引

## 文档导航

本目录包含"账单通"产品的完整技术架构设计文档,为开发团队提供清晰的实现指导。

---

## 架构文档列表

### 核心文档

1. **[架构设计概述](./00-architecture-overview.md)** ⭐ 必读
   - 架构设计原则
   - 技术栈选型理由
   - 系统架构总览
   - 安全、性能、扩展性设计

2. **[技术选型文档](./01-technology-stack.md)**
   - 开发语言: Kotlin
   - UI框架: Jetpack Compose
   - 架构模式: MVVM + Clean Architecture
   - 数据库: Room Database
   - 第三方库依赖清单

3. **[系统架构设计](./02-system-architecture.md)**
   - 分层架构设计
   - 核心模块设计
   - 数据流设计
   - 状态管理设计
   - 性能优化策略

4. **[数据模型设计](./03-data-model.md)**
   - 领域模型定义
   - 数据库实体设计
   - DAO接口定义
   - 数据转换逻辑
   - 预设数据初始化

5. **[API接口设计](./04-api-design.md)** (预留,2.0版本)
   - RESTful API规范
   - 用户认证API
   - 消费记录API
   - 统计分析API
   - 数据同步API

6. **[部署架构设计](./05-deployment-architecture.md)**
   - 1.0版本部署架构
   - 应用分发策略
   - CI/CD流程
   - 监控与告警
   - 版本管理策略

---

## 快速开始指南

### 对于新加入团队的成员

**建议阅读顺序**:

1. **第一步**: 阅读 [架构设计概述](./00-architecture-overview.md)
   - 了解整体架构思路
   - 理解技术选型理由
   - 把握质量属性目标

2. **第二步**: 阅读 [技术选型文档](./01-technology-stack.md)
   - 熟悉技术栈
   - 了解第三方库
   - 配置开发环境

3. **第三步**: 阅读 [数据模型设计](./03-data-model.md)
   - 理解核心数据结构
   - 学习数据库设计
   - 了解数据流转

4. **第四步**: 阅读 [系统架构设计](./02-system-architecture.md)
   - 理解分层架构
   - 学习模块划分
   - 掌握代码组织

### 对于Android开发工程师

**重点关注**:
- [技术选型文档](./01-technology-stack.md) - Kotlin + Compose使用指南
- [系统架构设计](./02-system-architecture.md) - MVVM + Clean Architecture实现
- [数据模型设计](./03-data-model.md) - Room Database使用指南

### 对于后端工程师(2.0版本)

**重点关注**:
- [API接口设计](./04-api-design.md) - RESTful API规范
- [部署架构设计](./05-deployment-architecture.md) - 云服务部署

### 对于DevOps工程师

**重点关注**:
- [部署架构设计](./05-deployment-architecture.md) - CI/CD流程
- [技术选型文档](./01-technology-stack.md) - 工具链配置

---

## 架构设计决策记录

### 关键决策

| 决策点 | 选择 | 理由 | 文档链接 |
|--------|------|------|---------|
| 开发语言 | Kotlin | 现代、安全、官方支持 | [技术选型](./01-technology-stack.md#2-前端技术栈) |
| UI框架 | Jetpack Compose | 声明式UI、高效 | [技术选型](./01-technology-stack.md#2-2-ui框架-jetpack-compose) |
| 架构模式 | MVVM + Clean | 测试性好、分层清晰 | [系统架构](./02-system-architecture.md#2-分层架构设计) |
| 数据库 | Room | 官方ORM、Flow支持 | [技术选型](./01-technology-stack.md#3-1-本地数据库-room-database) |
| 异步处理 | Coroutines + Flow | 简洁、高效 | [技术选型](./01-technology-stack.md#4-异步处理技术) |
| 依赖注入 | Hilt | 官方、编译时 | [技术选型](./01-technology-stack.md#6-依赖注入-hilt) |

---

## 架构图索引

### 系统架构图

- [整体架构图](./00-architecture-overview.md#3-系统架构设计)
- [分层架构图](./02-system-architecture.md#2-分层架构设计)
- [数据流图](./02-system-architecture.md#4-数据流设计)
- [模块架构图](./02-system-architecture.md#3-核心模块设计)

### 数据模型图

- [ER关系图](./03-data-model.md#4-1-room-database)
- [数据库表结构](./03-data-model.md#4-2-table-schemas)

---

## 开发资源

### 代码仓库

**主仓库**: (待创建)

**目录结构**: 参见[技术选型文档](./01-technology-stack.md#9-目录结构设计)

### 技术文档

- [Kotlin官方文档](https://kotlinlang.org/docs/)
- [Jetpack Compose文档](https://developer.android.com/jetpack/compose)
- [Room Database文档](https://developer.android.com/training/data-storage/room)
- [Hilt文档](https://dagger.dev/hilt/)
- [Material Design 3](https://m3.material.io/)

---

## 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0 | 2025-01-16 | 初始版本,完成1.0MVP架构设计 | Claude |

---

## 联系方式

**架构师**: Claude (Software Architecture Agent)
**创建日期**: 2025-01-16
**文档版本**: v1.0

---

## 附录

### A. 术语表

| 术语 | 说明 |
|------|------|
| **MVP** | Minimum Viable Product (最小可行产品) |
| **MVVM** | Model-View-ViewModel架构模式 |
| **Clean Architecture** | 清洁架构,关注点分离 |
| **Room Database** | Android官方ORM框架 |
| **Flow** | Kotlin响应式数据流 |
| **StateFlow** | 状态容器,用于UI状态管理 |
| **Hilt** | Android依赖注入框架 |
| **Compose** | Jetpack声明式UI框架 |
| **Use Case** | 用例,封装单一业务逻辑 |
| **Repository** | 仓库,数据抽象层 |

### B. 参考资料

1. [Android Developers Guide](https://developer.android.com/guide)
2. [Kotlin Language Specification](https://kotlinlang.org/spec/)
3. [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
4. [Google Material Design](https://material.io/design)
5. [RESTful API Design Best Practices](https://restfulapi.net/)

---

*本文档持续更新中,如有疑问请联系架构师*
