# 组件设计建议 (Component Library)

> **设计原则**: 一致性、可复用性、可访问性、可维护性
> **目标**: 构建统一的视觉语言和交互模式

---

## 1. 按钮组件 (Buttons)

### 1.1 主要按钮 (Primary Button)

**用途**: 主要操作、提交表单

**视觉规范**:
```css
.primary-button {
  background-color: var(--primary-600);
  color: #FFFFFF;
  font-size: 16px;
  font-weight: 500;
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
  transition: all 150ms ease-out;
}

.primary-button:hover {
  background-color: var(--primary-500);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

.primary-button:active {
  transform: translateY(0) scale(0.95);
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
}

.primary-button:disabled {
  background-color: var(--gray-300);
  color: var(--gray-500);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
```

**尺寸变体**:
- 小 (Small): 32px 高度，padding 8px 16px
- 中 (Medium): 40px 高度，padding 12px 24px（默认）
- 大 (Large): 48px 高度，padding 16px 32px

**使用场景**:
- 记账按钮（最大尺寸）
- 保存按钮
- 确认操作

**心理学应用**:
- 高视觉权重（吸引注意）
- 阴影增强（立体感）
- 悬停提升（可点击暗示）

---

### 1.2 次要按钮 (Secondary Button)

**用途**: 次要操作、取消、返回

**视觉规范**:
```css
.secondary-button {
  background-color: transparent;
  color: var(--primary-600);
  font-size: 16px;
  font-weight: 500;
  padding: 12px 24px;
  border-radius: 12px;
  border: 2px solid var(--primary-600);
  transition: all 150ms ease-out;
}

.secondary-button:hover {
  background-color: var(--primary-50);
  border-color: var(--primary-500);
}

.secondary-button:active {
  transform: scale(0.95);
}
```

**使用场景**:
- 取消按钮
- 返回按钮
- 编辑按钮

---

### 1.3 文字按钮 (Text Button)

**用途**: 轻量级操作、链接式操作

**视觉规范**:
```css
.text-button {
  background-color: transparent;
  color: var(--primary-600);
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  transition: background-color 150ms ease-out;
}

.text-button:hover {
  background-color: var(--primary-50);
}

.text-button:active {
  background-color: var(--primary-100);
}
```

**使用场景**:
- 查看详情
- 跳过引导
- 取消选择

---

### 1.4 图标按钮 (Icon Button)

**用途**: 工具栏、快速操作

**视觉规范**:
```css
.icon-button {
  background-color: transparent;
  color: var(--gray-600);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 150ms ease-out;
}

.icon-button:hover {
  background-color: var(--gray-100);
}

.icon-button:active {
  background-color: var(--gray-200);
  transform: scale(0.95);
}

.icon-button.active {
  background-color: var(--primary-100);
  color: var(--primary-600);
}
```

**使用场景**:
- 设置按钮
- 搜索按钮
- 收藏按钮
- 分享按钮

---

### 1.5 浮动操作按钮 (FAB)

**用途**: 主要操作、快速创建

**视觉规范**:
```css
.fab {
  background-color: var(--primary-600);
  color: #FFFFFF;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  border: none;
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  position: fixed;
  bottom: 24px;
  right: 24px;
  transition: all 200ms ease-out;
}

.fab:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.5);
}

.fab:active {
  transform: scale(0.95);
}

.fab.extended {
  width: auto;
  padding: 0 20px;
  gap: 8px;
}
```

**使用场景**:
- 快速记账（主要功能）
- 新建账户
- 添加预算

---

### 1.6 按钮组 (Button Group)

**用途**: 相关操作组合

**视觉规范**:
```css
.button-group {
  display: flex;
  gap: 8px;
}

.button-group.vertical {
  flex-direction: column;
}

.button-group .button:first-child {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.button-group .button:not(:first-child):not(:last-child) {
  border-radius: 0;
}

.button-group .button:last-child {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}
```

**使用场景**:
- 编辑 / 删除
- 保存 / 取消
- 导入 / 导出

---

## 2. 卡片组件 (Cards)

### 2.1 基础卡片 (Base Card)

**视觉规范**:
```css
.card {
  background-color: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--gray-100);
  transition: all 200ms ease-out;
}

.card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card.clickable {
  cursor: pointer;
}

.card.clickable:active {
  transform: translateY(0) scale(0.98);
}
```

**卡片结构**:
```
┌─────────────────────────────┐
│  [头部 - 可选]              │
│  ─────────────────────────  │
│  [内容区域]                 │
│  [内容区域]                 │
│  [内容区域]                 │
│  ─────────────────────────  │
│  [底部 - 可选]              │
└─────────────────────────────┘
```

---

### 2.2 账单卡片 (Transaction Card)

**视觉规范**:
```css
.transaction-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background-color: #FFFFFF;
  border-radius: 12px;
  border-bottom: 1px solid var(--gray-100);
  transition: background-color 150ms ease-out;
}

.transaction-card:hover {
  background-color: var(--gray-50);
}

.transaction-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: var(--primary-50);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.transaction-content {
  flex: 1;
}

.transaction-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--gray-900);
  margin-bottom: 4px;
}

.transaction-subtitle {
  font-size: 14px;
  color: var(--gray-500);
}

.transaction-amount {
  font-size: 18px;
  font-weight: 600;
  color: var(--danger-500);
}

.transaction-amount.income {
  color: var(--success-500);
}
```

**卡片布局**:
```
┌─────────────────────────────┐
│  [图标]  麦当劳      -¥35.00│
│          午餐 - 餐饮美食      │
└─────────────────────────────┘
```

**交互状态**:
- 左滑删除
- 右滑操作
- 点击查看详情

---

### 2.3 预算卡片 (Budget Card)

**视觉规范**:
```css
.budget-card {
  background-color: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.budget-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.budget-category {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

.budget-amount {
  font-size: 14px;
  color: var(--gray-500);
}

.budget-progress {
  height: 8px;
  background-color: var(--gray-200);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.budget-progress-bar {
  height: 100%;
  background-color: var(--success-500);
  border-radius: 4px;
  transition: width 300ms ease-out;
}

.budget-progress-bar.warning {
  background-color: var(--warning-500);
}

.budget-progress-bar.over {
  background-color: var(--danger-500);
}

.budget-status {
  font-size: 12px;
  color: var(--gray-500);
}

.budget-status.warning {
  color: var(--warning-600);
}

.budget-status.over {
  color: var(--danger-600);
}
```

**卡片布局**:
```
┌─────────────────────────────┐
│  🍔 餐饮美食         ¥820/1000│
│  ━━━━━━━━━━━━━━━ 82%        │
│  ⚠️ 即将超支                │
└─────────────────────────────┘
```

---

### 2.4 统计卡片 (Stats Card)

**视觉规范**:
```css
.stats-card {
  background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
  color: #FFFFFF;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.3);
}

.stats-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.stats-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stats-change {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stats-change.positive {
  color: var(--success-300);
}

.stats-change.negative {
  color: var(--danger-300);
}
```

**卡片布局**:
```
┌─────────────────────────────┐
│  本月支出                   │
│  ¥3,240.50                 │
│  ↗️ 环比 +12.3%             │
└─────────────────────────────┘
```

---

## 3. 表单组件 (Form Components)

### 3.1 输入框 (Input)

**视觉规范**:
```css
.input {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  color: var(--gray-900);
  background-color: #FFFFFF;
  border: 2px solid var(--gray-300);
  border-radius: 8px;
  transition: all 150ms ease-out;
}

.input::placeholder {
  color: var(--gray-400);
}

.input:hover {
  border-color: var(--gray-400);
}

.input:focus {
  outline: none;
  border-color: var(--primary-600);
  box-shadow: 0 0 0 3px var(--primary-100);
}

.input.error {
  border-color: var(--danger-500);
}

.input.error:focus {
  box-shadow: 0 0 0 3px var(--danger-100);
}

.input.success {
  border-color: var(--success-500);
}

.input:disabled {
  background-color: var(--gray-100);
  color: var(--gray-500);
  cursor: not-allowed;
}
```

**状态示例**:
```
正常: ┌─────────────────────┐
      │ 请输入金额...        │
      └─────────────────────┘

聚焦: ┌─────────────────────┐  ← 蓝色边框 + 阴影
      │ 请输入金额...        │
      └─────────────────────┘

错误: ┌─────────────────────┐  ← 红色边框
      │ abc              ✗  │
      └─────────────────────┘
      请输入有效的金额

成功: ┌─────────────────────┐  ← 绿色边框
      │ ¥100.00         ✓  │
      └─────────────────────┘
```

---

### 3.2 金额输入框 (Amount Input)

**特殊设计**:
- 超大字号（32px）
- 货币符号前缀
- 数字键盘
- 实时格式化

**视觉规范**:
```css
.amount-input {
  font-size: 32px;
  font-weight: 600;
  text-align: center;
  padding: 20px;
  border: none;
  border-bottom: 2px solid var(--gray-300);
  border-radius: 0;
}

.amount-input:focus {
  border-bottom-color: var(--primary-600);
  box-shadow: none;
}
```

**布局**:
```
┌─────────────────────────────┐
│                             │
│         ¥ 0.00              │  ← 超大字号
│         ━━━━━━━             │  ← 底部边框
│                             │
└─────────────────────────────┘
```

---

### 3.3 选择器 (Select)

**视觉规范**:
```css
.select {
  position: relative;
  width: 100%;
}

.select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #FFFFFF;
  border: 2px solid var(--gray-300);
  border-radius: 8px;
  cursor: pointer;
  transition: all 150ms ease-out;
}

.select-trigger:hover {
  border-color: var(--gray-400);
}

.select-trigger.open {
  border-color: var(--primary-600);
  box-shadow: 0 0 0 3px var(--primary-100);
}

.select-options {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: #FFFFFF;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-top: 4px;
  z-index: 100;
  opacity: 0;
  transform: translateY(-8px);
  pointer-events: none;
  transition: all 150ms ease-out;
}

.select-options.open {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.select-option {
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 100ms ease-out;
}

.select-option:hover {
  background-color: var(--gray-100);
}

.select-option.selected {
  background-color: var(--primary-50);
  color: var(--primary-600);
}
```

**布局**:
```
关闭状态:
┌─────────────────────────────┐
│  餐饮美食               ▼   │
└─────────────────────────────┘

打开状态:
┌─────────────────────────────┐
│  餐饮美食               ▲   │
├─────────────────────────────┤
│  🍔 餐饮美食                 │
│  🚇 交通出行                 │
│  🛒 购物消费                 │
│  🏠 居住生活                 │
└─────────────────────────────┘
```

---

### 3.4 开关 (Switch)

**视觉规范**:
```css
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 28px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--gray-300);
  border-radius: 14px;
  transition: background-color 200ms ease-out;
}

.switch-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 4px;
  bottom: 4px;
  background-color: #FFFFFF;
  border-radius: 50%;
  transition: transform 200ms ease-out;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.switch input:checked + .switch-slider {
  background-color: var(--primary-600);
}

.switch input:checked + .switch-slider:before {
  transform: translateX(20px);
}
```

**状态**:
```
关闭: ┌──────┐
      │ ●────│
      └──────┘

开启: ┌──────┐
      │ ────●│  ← 蓝色背景
      └──────┘
```

---

## 4. 导航组件 (Navigation)

### 4.1 底部导航栏 (Bottom Navigation)

**视觉规范**:
```css
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background-color: #FFFFFF;
  border-top: 1px solid var(--gray-200);
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border: none;
  background: none;
  cursor: pointer;
  transition: all 150ms ease-out;
}

.bottom-nav-item.active {
  color: var(--primary-600);
}

.bottom-nav-item:not(.active) {
  color: var(--gray-500);
}

.bottom-nav-item:active {
  transform: scale(0.95);
}

.bottom-nav-icon {
  width: 24px;
  height: 24px;
}

.bottom-nav-label {
  font-size: 12px;
  font-weight: 500;
}

.bottom-nav-fab {
  width: 48px;
  height: 48px;
  background-color: var(--primary-600);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
  margin-bottom: 16px;
  transition: all 200ms ease-out;
}

.bottom-nav-fab:active {
  transform: scale(0.95);
}
```

**布局**:
```
┌─────────────────────────────┐
│  [🏠] [📊] [ + ] [💰] [👤]  │
│   主页  统计  记账  预算  我的│
└─────────────────────────────┘
```

---

### 4.2 标签栏 (Tab Bar)

**视觉规范**:
```css
.tab-bar {
  display: flex;
  gap: 8px;
  padding: 8px 16px;
  background-color: var(--gray-100);
  border-radius: 12px;
}

.tab-item {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 150ms ease-out;
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-600);
}

.tab-item.active {
  background-color: #FFFFFF;
  color: var(--primary-600);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.tab-item:hover:not(.active) {
  background-color: rgba(255, 255, 255, 0.5);
}
```

**布局**:
```
┌─────────────────────────────┐
│  [ 支出 ]  [ 收入 ]  [ 全部 ]│
│   (激活)                     │
└─────────────────────────────┘
```

---

## 5. 反馈组件 (Feedback)

### 5.1 Toast 通知

**视觉规范**:
```css
.toast {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--gray-900);
  color: #FFFFFF;
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0;
  pointer-events: none;
  transition: all 200ms ease-out;
  z-index: 1000;
}

.toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.toast.success {
  background-color: var(--success-600);
}

.toast.error {
  background-color: var(--danger-600);
}

.toast.warning {
  background-color: var(--warning-600);
}
```

**布局**:
```
┌──────────────────────┐
│  ✓ 记账成功          │
└──────────────────────┘
```

---

### 5.2 进度条 (Progress Bar)

**线性进度条**:
```css
.progress-bar {
  width: 100%;
  height: 8px;
  background-color: var(--gray-200);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background-color: var(--primary-600);
  border-radius: 4px;
  transition: width 300ms ease-out;
}

.progress-bar-fill.indeterminate {
  animation: indeterminate 1.5s infinite;
}

@keyframes indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
```

**环形进度条**:
```css
.progress-ring {
  transform: rotate(-90deg);
}

.progress-ring-circle {
  stroke-dasharray: 283;
  stroke-dashoffset: 283;
  transition: stroke-dashoffset 300ms ease-out;
}
```

---

## 6. 图表组件 (Charts)

### 6.1 设计原则

- **清晰性**: 数据点清晰可辨
- **对比度**: 使用色彩区分数据
- **交互性**: 悬停显示详细数据
- **动画性**: 数据变化有过渡动画

---

### 6.2 折线图 (Line Chart)

**用途**: 消费趋势、收入变化

**视觉规范**:
```css
.line-chart {
  width: 100%;
  height: 200px;
  position: relative;
}

.line-chart-line {
  fill: none;
  stroke: var(--primary-600);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.line-chart-dot {
  fill: #FFFFFF;
  stroke: var(--primary-600);
  stroke-width: 3;
  r: 6;
  transition: r 150ms ease-out;
}

.line-chart-dot:hover {
  r: 8;
  cursor: pointer;
}

.line-chart-grid {
  stroke: var(--gray-200);
  stroke-width: 1;
}

.line-chart-label {
  font-size: 12px;
  fill: var(--gray-500);
}
```

---

### 6.3 柱状图 (Bar Chart)

**用途**: 分类对比、月度对比

**视觉规范**:
```css
.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  height: 200px;
  padding: 16px 0;
}

.bar-chart-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.bar-chart-bar {
  width: 100%;
  background-color: var(--primary-600);
  border-radius: 4px 4px 0 0;
  transition: all 150ms ease-out;
  cursor: pointer;
}

.bar-chart-bar:hover {
  opacity: 0.8;
  transform: scaleY(1.02);
}

.bar-chart-label {
  font-size: 12px;
  color: var(--gray-600);
  text-align: center;
}
```

---

### 6.4 环形图 (Donut Chart)

**用途**: 分类占比

**视觉规范**:
```css
.donut-chart {
  position: relative;
  width: 200px;
  height: 200px;
}

.donut-chart-segment {
  fill: none;
  stroke-width: 32;
  transition: all 150ms ease-out;
  cursor: pointer;
}

.donut-chart-segment:hover {
  stroke-width: 36;
}

.donut-chart-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.donut-chart-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--gray-900);
}

.donut-chart-label {
  font-size: 14px;
  color: var(--gray-600);
}
```

---

## 7. 列表组件 (Lists)

### 7.1 基础列表

**视觉规范**:
```css
.list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list-item {
  padding: 16px;
  border-bottom: 1px solid var(--gray-100);
  transition: background-color 150ms ease-out;
  cursor: pointer;
}

.list-item:hover {
  background-color: var(--gray-50);
}

.list-item:last-child {
  border-bottom: none;
}

.list-item-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--gray-900);
  margin-bottom: 4px;
}

.list-item-subtitle {
  font-size: 14px;
  color: var(--gray-500);
}
```

---

### 7.2 分组列表

**视觉规范**:
```css
.list-group {
  margin-bottom: 24px;
}

.list-group-header {
  padding: 12px 16px;
  background-color: var(--gray-100);
  font-size: 14px;
  font-weight: 600;
  color: var(--gray-700);
  position: sticky;
  top: 0;
  z-index: 10;
}
```

**布局**:
```
┌─────────────────────────────┐
│  今天                       │  ← 分组标题
├─────────────────────────────┤
│  🍔 麦当劳      -¥35.00     │
│  🚇 地铁充值      -¥100.00   │
├─────────────────────────────┤
│  昨天                       │
├─────────────────────────────┤
│  🍜 真功夫       -¥28.00     │
└─────────────────────────────┘
```

---

## 8. 组件使用总结

| 组件类型 | 主要用途 | 尺寸变体 | 状态数量 |
|---------|---------|---------|---------|
| 按钮 | 操作触发 | 3 (S/M/L) | 5 (正常/悬停/按下/禁用/加载) |
| 卡片 | 内容容器 | 3 (基础/账单/统计) | 3 (正常/悬停/点击) |
| 输入框 | 数据输入 | 3 (标准/大/小) | 4 (正常/聚焦/错误/禁用) |
| 导航 | 页面切换 | 2 (底部/顶部) | 2 (正常/激活) |
| 反馈 | 状态提示 | 3 (Toast/Alert/Modal) | 4 (成功/错误/警告/信息) |
| 图表 | 数据可视化 | 4 (折线/柱状/饼图/环形) | 3 (正常/悬停/加载) |

---

**版本**: v1.0
**最后更新**: 2026-01-15
**状态**: 待评审
