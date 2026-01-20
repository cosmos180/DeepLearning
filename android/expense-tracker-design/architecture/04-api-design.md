# API接口设计 (预留)

## 1. API设计概述

### 1.1 设计原则

**注意**: 1.0版本为本地优先架构,无需后端API。本文档为未来云同步功能预留设计。

**RESTful API设计原则**:
- 资源导向: URL表示资源,HTTP方法表示操作
- 统一接口: 使用标准HTTP方法和状态码
- 无状态: 每个请求包含完整信息
- 版本控制: URL中包含版本号 `/v1/`

**JSON API规范**:
- 请求/响应使用JSON格式
- 统一响应结构
- 错误信息清晰友好

---

## 2. API基础信息

### 2.1 基础URL

```
开发环境: https://dev-api.billtrack.com/v1
测试环境: https://staging-api.billtrack.com/v1
生产环境: https://api.billtrack.com/v1
```

### 2.2 认证方式

```http
Authorization: Bearer <access_token>

Token格式:
{
  "user_id": "uuid",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### 2.3 统一响应格式

**成功响应**:
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功",
  "timestamp": "2025-01-16T12:30:00Z"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "金额必须大于0",
    "details": { ... }
  },
  "timestamp": "2025-01-16T12:30:00Z"
}
```

---

## 3. 用户认证API

### 3.1 注册

```http
POST /v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "nickname": "昵称"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "access_token": "jwt_token",
    "refresh_token": "refresh_token"
  }
}
```

### 3.2 登录

```http
POST /v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "access_token": "jwt_token",
    "refresh_token": "refresh_token"
  }
}
```

### 3.3 刷新Token

```http
POST /v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "refresh_token"
}
```

---

## 4. 消费记录API

### 4.1 获取记录列表

```http
GET /v1/expenses?page=1&limit=20&start_date=2025-01-01&end_date=2025-01-31
Authorization: Bearer <access_token>
```

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码,默认1 |
| limit | int | 否 | 每页数量,默认20 |
| start_date | string | 否 | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | 结束日期 (YYYY-MM-DD) |
| category_id | string | 否 | 分类ID筛选 |
| keyword | string | 否 | 搜索关键词 |

**响应**:
```json
{
  "success": true,
  "data": {
    "expenses": [
      {
        "id": "uuid",
        "amount": 28.50,
        "category": {
          "id": "cat_1",
          "name": "餐饮",
          "icon": "restaurant",
          "color": "#FF6B6B"
        },
        "date": "2025-01-16T12:30:00Z",
        "note": "麦当劳套餐",
        "payment_method": "wechat",
        "created_at": "2025-01-16T12:30:00Z",
        "updated_at": "2025-01-16T12:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

### 4.2 创建记录

```http
POST /v1/expenses
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount": 28.50,
  "category_id": "cat_1",
  "date": "2025-01-16T12:30:00Z",
  "note": "麦当劳套餐",
  "payment_method": "wechat"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "amount": 28.50,
    "category_id": "cat_1",
    "date": "2025-01-16T12:30:00Z",
    "note": "麦当劳套餐",
    "payment_method": "wechat",
    "created_at": "2025-01-16T12:30:00Z",
    "updated_at": "2025-01-16T12:30:00Z"
  }
}
```

### 4.3 获取记录详情

```http
GET /v1/expenses/:id
Authorization: Bearer <access_token>
```

### 4.4 更新记录

```http
PUT /v1/expenses/:id
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount": 30.00,
  "category_id": "cat_1",
  "note": "肯德基套餐"
}
```

### 4.5 删除记录

```http
DELETE /v1/expenses/:id
Authorization: Bearer <access_token>
```

### 4.6 批量删除

```http
DELETE /v1/expenses
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "ids": ["uuid1", "uuid2", "uuid3"]
}
```

---

## 5. 统计分析API

### 5.1 获取统计数据

```http
GET /v1/expenses/statistics?start_date=2025-01-01&end_date=2025-01-31
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "total_expense": 3245.80,
    "expense_by_category": [
      {
        "category": {
          "id": "cat_1",
          "name": "餐饮",
          "icon": "restaurant",
          "color": "#FF6B6B"
        },
        "amount": 1200.00,
        "percentage": 37.0,
        "count": 45
      }
    ],
    "daily_trend": [
      {
        "date": "2025-01-01",
        "amount": 128.50,
        "count": 5
      }
    ],
    "budget_usage": {
      "budget": 5000.00,
      "used": 3245.80,
      "remaining": 1754.20,
      "percentage": 65.0,
      "status": "ATTENTION"
    }
  }
}
```

---

## 6. 分类管理API

### 6.1 获取分类列表

```http
GET /v1/categories
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": "cat_1",
        "name": "餐饮",
        "parent_id": null,
        "icon": "restaurant",
        "color": "#FF6B6B",
        "is_custom": false,
        "sort_order": 1,
        "children": [
          {
            "id": "cat_1_1",
            "name": "早餐",
            "parent_id": "cat_1",
            "icon": "breakfast",
            "color": "#FF8E8E"
          }
        ]
      }
    ]
  }
}
```

### 6.2 创建自定义分类

```http
POST /v1/categories
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "咖啡",
  "parent_id": null,
  "icon": "coffee",
  "color": "#8B4513"
}
```

### 6.3 更新分类

```http
PUT /v1/categories/:id
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "咖啡店",
  "color": "#A0522D"
}
```

### 6.4 删除分类

```http
DELETE /v1/categories/:id
Authorization: Bearer <access_token>
```

---

## 7. 预算管理API

### 7.1 获取预算列表

```http
GET /v1/budgets?month=2025-01
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "budgets": [
      {
        "id": "budget_1",
        "category_id": null,
        "amount": 5000.00,
        "month": "2025-01",
        "used": 3245.80,
        "remaining": 1754.20,
        "percentage": 65.0
      }
    ]
  }
}
```

### 7.2 设置预算

```http
POST /v1/budgets
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "category_id": null,
  "amount": 5000.00,
  "month": "2025-01"
}
```

### 7.3 更新预算

```http
PUT /v1/budgets/:id
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount": 6000.00
}
```

---

## 8. 数据同步API

### 8.1 拉取数据

```http
GET /v1/sync/pull?last_sync=1642329600
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "expenses": [
      { "id": "uuid", "amount": 28.50, ... }
    ],
    "categories": [
      { "id": "cat_1", "name": "餐饮", ... }
    ],
    "budgets": [
      { "id": "budget_1", "amount": 5000.00, ... }
    ],
    "last_sync": 1642416000
  }
}
```

### 8.2 推送数据

```http
POST /v1/sync/push
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "expenses": [
    { "id": "uuid", "amount": 28.50, ... }
  ],
  "categories": [
    { "id": "cat_9", "name": "咖啡", ... }
  ]
}
```

---

## 9. 用户设置API

### 9.1 获取设置

```http
GET /v1/settings
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "currency": "CNY",
    "decimal_places": 2,
    "month_start_day": 1,
    "theme": "light",
    "language": "zh-CN",
    "reminder_enabled": true,
    "reminder_time": "21:00"
  }
}
```

### 9.2 更新设置

```http
PUT /v1/settings
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "theme": "dark",
  "reminder_time": "22:00"
}
```

---

## 10. 错误码定义

### 10.1 HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 500 | 服务器错误 |

### 10.2 业务错误码

| 错误码 | 说明 |
|--------|------|
| VALIDATION_ERROR | 参数验证失败 |
| NOT_FOUND | 资源不存在 |
| DUPLICATE | 资源重复 |
| UNAUTHORIZED | 未授权 |
| FORBIDDEN | 禁止访问 |
| RATE_LIMIT_EXCEEDED | 超出速率限制 |

---

## 11. 数据同步策略

### 11.1 同步机制

**增量同步**:
- 客户端记录last_sync时间戳
- 每次同步只拉取/推送变更数据
- 使用乐观锁处理冲突

**冲突解决**:
- 服务器时间戳优先
- 客户端需要合并变更

### 11.2 同步流程

```
1. 客户端推送本地变更
   POST /v1/sync/push { expenses: [...], categories: [...] }

2. 服务器处理变更,返回最新数据
   { expenses: [...], categories: [...], last_sync: 1642416000 }

3. 客户端合并服务器数据
   - 新数据: 直接插入
   - 已有数据: 比较时间戳,保留最新

4. 更新本地last_sync时间
```

---

## 12. 安全设计

### 12.1 认证安全

**密码加密**:
- 前端: 不传输明文密码,使用bcrypt加密
- 后端: bcrypt哈希存储,加盐

**Token安全**:
- Access Token有效期: 1小时
- Refresh Token有效期: 30天
- HTTPS传输

### 12.2 数据加密

**敏感数据加密**:
- 备份文件使用AES加密
- 传输使用TLS 1.3

---

## 13. 速率限制

### 13.1 限制规则

| 接口类型 | 限制 | 窗口 |
|---------|------|------|
| 认证接口 | 5次/分钟 | IP |
| 查询接口 | 100次/分钟 | 用户 |
| 写入接口 | 20次/分钟 | 用户 |
| 同步接口 | 10次/分钟 | 用户 |

### 13.2 响应

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1642329600

{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求过于频繁,请稍后再试"
  }
}
```

---

*文档版本: v1.0*
*创建日期: 2025-01-16*
*架构师: Claude (Software Architecture Agent)*
