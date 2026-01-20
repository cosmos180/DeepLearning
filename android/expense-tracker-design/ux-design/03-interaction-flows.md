# 页面交互流程设计

## 1. 交互流程概述

本文档使用Mermaid序列图和流程图，详细描述账单通核心页面的交互流程，结合心理学原理设计每个交互节点。

---

## 2. 快速记账交互流程

### 2.1 完整记账序列图

```mermaid
sequenceDiagram
    participant U as 用户
    participant H as 首页
    participant FAB as 悬浮按钮
    participant D as 记账弹窗
    participant K as 数字键盘
    participant C as 分类选择器
    participant V as 验证器
    participant DB as 数据库
    participant T as Toast提示

    U->>FAB: 点击"+"按钮
    Note over U,FAB: 触发: 视觉+触觉反馈<br/>心理学: 即时响应建立信心

    FAB->>D: 弹出对话框(200ms动画)
    Note over D: 背景: 模糊化<br/>心理学: 创建"专注模式"

    D->>D: 金额输入框自动聚焦
    D->>K: 弹出数字键盘
    Note over D,K: 心理学: 减少操作步骤

    U->>K: 输入"2850"
    K->>D: 实时格式化显示
    Note over D: 显示: ¥28.50<br/>心理学: 格式化降低认知负荷

    U->>D: 点击分类区域
    D->>C: 显示常用分类列表
    Note over C: 默认: 常用分类置顶<br/>心理学: 基于频率的智能排序

    U->>C: 选择"餐饮-午餐"
    C->>D: 高亮选中分类
    Note over D: 心理学: 视觉确认<br/>颜色: 主题色高亮

    U->>D: 确认日期(默认今天)
    U->>D: 输入备注"麦当劳"(可选)

    U->>D: 点击"保存"按钮
    D->>V: 验证输入数据

    alt 验证失败
        V->>D: 返回错误
        D->>U: 显示错误提示<br/>震动反馈
        Note over D: 心理学: 温和而非责备<br/>颜色: 红色边框抖动
    else 验证成功
        V->>DB: 保存记录
        DB->>D: 保存成功(<200ms)

        D->>D: 关闭弹窗(200ms动画)
        D->>T: 显示Toast"已保存"
        T->>U: 触觉震动(100ms)
        Note over T: 心理学: 奖赏机制<br/>强化记录行为

        D->>H: 刷新统计数据
        H->>H: 更新动画(300ms)
        Note over H: 心理学: 即时因果关联<br/>看到数据变化产生满足感
    end
```

### 2.2 记账流程状态机

```mermaid
stateDiagram-v2
    [*] --> Idle: 用户在首页

    Idle --> Opening: 点击FAB
    Opening --> InputAmount: 弹窗打开完成

    InputAmount --> InputAmount: 输入数字
    InputAmount --> SelectCategory: 点击分类区域

    SelectCategory --> SelectCategory: 浏览分类
    SelectCategory --> InputNote: 选择分类完成

    InputNote --> InputNote: 输入备注(可选)
    InputNote --> Validating: 点击保存

    Validating --> ValidationError: 验证失败
    Validating --> Saving: 验证成功

    ValidationError --> InputAmount: 显示错误<br/>保持输入
    Saving --> Success: 保存完成

    Success --> Closed: 关闭弹窗
    Closed --> Idle: 返回首页<br/>显示Toast

    note right of InputAmount
        心理学提示:
        - 默认值减少决策
        - 格式化降低认知
    end note

    note right of Success
        心理学提示:
        - 即时反馈强化行为
        - 数据更新满足掌控感
    end note
```

### 2.3 快速记账心理学设计要点

#### 触发机制设计
- **视觉触发**：右下角悬浮按钮，主题色（绿色），吸引注意
- **空间触发**：始终可见，无需记忆位置
- **行为触发**：支持摇一摇（可选），增加趣味性

#### 输入优化设计
- **智能格式化**：自动添加小数点，千分位分隔
- **默认值策略**：
  - 日期：默认今天
  - 分类：常用分类置顶
  - 支付方式：记住上次选择
- **键盘优化**：直接弹出数字键盘，减少切换

#### 反馈机制设计
- **视觉反馈**：按钮按下缩放，选中高亮
- **触觉反馈**：保存成功轻微震动
- **信息反馈**：Toast提示 + 数据更新动画

---

## 3. 统计页面交互流程

### 3.1 统计浏览序列图

```mermaid
sequenceDiagram
    participant U as 用户
    participant S as 统计页
    participant T as 时间选择器
    participant CH as 趋势图表
    participant PH as 饼图
    participant DB as 数据库

    U->>S: 进入统计页
    S->>DB: 请求本月数据
    DB->>S: 返回统计数据
    Note over S: 加载时间<1秒

    S->>U: 显示本月支出概览
    S->>CH: 渲染趋势图
    S->>PH: 渲染饼图
    Note over U: 心理学: 可视化降低理解难度

    U->>T: 点击时间选择器
    T->>U: 显示月份列表
    Note over T: 心理学: 提供选择而非输入

    U->>T: 选择"上月"
    T->>DB: 请求上月数据
    DB->>S: 返回数据

    S->>S: 切换动画(300ms)
    Note over S: 旧数据淡出<br/>新数据淡入<br/>心理学: 平滑过渡减少突兀

    S->>U: 显示上月统计
    S->>CH: 更新图表
    S->>PH: 更新饼图

    U->>CH: 点击图表数据点
    CH->>U: 显示详情卡片
    Note over U: 金额: ¥1,234.00<br/>日期: 01-15<br/>心理学: 点击探索满足好奇心

    U->>PH: 点击饼图"餐饮"区块
    PH->>U: 高亮该区块
    PH->>S: 钻取到二级分类
    Note over S: 显示餐饮子分类占比<br/>心理学: 渐进披露避免信息过载

    U->>S: 点击分类列表项
    S->>U: 跳转到分类详情页
    Note over U: 心理学: 钻取模式符合探索习惯
```

### 3.2 图表交互状态机

```mermaid
stateDiagram-v2
    [*] --> Overview: 进入统计页

    Overview --> Overview: 查看概览
    Overview --> TimeSelect: 点击时间选择器

    TimeSelect --> TimeSelect: 选择月份
    TimeSelect --> Overview: 确认选择

    Overview --> TrendView: 滚动到趋势图
    TrendView --> PointDetail: 点击数据点

    PointDetail --> TrendView: 关闭详情
    PointDetail --> PointDetail: 切换数据点

    TrendView --> PieView: 滚动到饼图
    PieView --> SliceDetail: 点击饼图区块

    SliceDetail --> DrillDown: 点击查看详情
    DrillDown --> CategoryDetail: 进入分类详情页

    PieView --> ListView: 切换到列表视图
    ListView --> ItemDetail: 点击列表项
    ItemDetail --> CategoryDetail: 进入详情页

    CategoryDetail --> [*]: 返回统计页

    note right of TrendView
        交互设计:
        - 缩放: 双指捏合
        - 平移: 单指拖动
        - 长按: 高亮数据点
    end note

    note right of PieView
        心理学设计:
        - 旋转动画吸引注意
        - 点击区块符合直觉
        - 高亮提供确认反馈
    end note
```

### 3.3 统计页面心理学设计要点

#### 可视化设计原则
- **颜色编码**：每个分类使用固定颜色，建立颜色-分类关联
- **视觉层级**：大数字突出关键指标，小图表展示细节
- **交互反馈**：悬停/点击高亮，提供即时确认

#### 信息层级设计
- **一级信息**：本月总支出（大字体、居中）
- **二级信息**：趋势图、饼图（辅助理解）
- **三级信息**：分类列表（详细数据）

#### 探索式交互设计
- **点击探索**：所有图表元素可点击
- **渐进披露**：从概览到详情，逐步深入
- **自由导航**：支持在图表间自由切换

---

## 4. 记录管理交互流程

### 4.1 记录列表浏览序列图

```mermaid
sequenceDiagram
    participant U as 用户
    participant L as 列表页
    participant Search as 搜索框
    participant List as 记录列表
    participant Item as 列表项
    participant Detail as 详情页
    participant DB as 数据库

    U->>L: 进入记录页
    L->>DB: 请求记录列表
    DB->>L: 返回数据(分页)

    L->>List: 渲染列表
    List->>U: 显示按日期分组<br/>的记录
    Note over U: 心理学: 分组降低认知负荷

    U->>List: 下拉刷新
    List->>DB: 请求最新数据
    DB->>List: 返回更新
    List->>List: 刷新动画
    Note over List: 心理学: 刷新动画提供<br/>操作确认反馈

    U->>List: 上拉加载更多
    List->>DB: 请求下一页
    DB->>List: 返回数据
    List->>U: 追加到列表

    U->>Search: 点击搜索框
    Search->>U: 显示搜索页
    Note over U: 心理学: 全屏模式<br/>减少干扰

    U->>Search: 输入"麦当劳"
    Search->>DB: 实时搜索
    DB->>Search: 返回匹配结果
    Search->>U: 显示结果列表<br/>高亮关键词
    Note over U: 心理学: 高亮提供<br/>视觉确认

    U->>Item: 点击列表项
    Item->>Detail: 打开详情页
    Detail->>U: 显示完整信息
    Note over U: 心理学: 详情页提供<br/>信息安全感
```

### 4.2 记录操作序列图

```mermaid
sequenceDiagram
    participant U as 用户
    participant Item as 列表项
    participant Menu as 操作菜单
    participant Edit as 编辑模式
    participant Confirm as 确认对话框
    participant DB as 数据库

    U->>Item: 长按列表项
    Item->>Item: 震动反馈
    Item->>Menu: 显示操作菜单
    Note over Menu: 选项: 编辑 / 删除<br/>心理学: 即时反馈确认长按

    alt 选择编辑
        U->>Menu: 点击"编辑"
        Menu->>Edit: 进入编辑模式
        Note over Edit: 复用记账弹窗<br/>预填充数据

        U->>Edit: 修改金额/分类/备注
        U->>Edit: 点击"保存"

        Edit->>DB: 更新记录
        DB->>Edit: 更新成功

        Edit->>U: 显示Toast"已修改"
        Edit->>Item: 更新列表项
        Note over U: 心理学: 即时更新<br/>提供掌控感
    else 选择删除
        U->>Menu: 点击"删除"
        Menu->>Confirm: 显示确认对话框
        Note over Confirm: 心理学: 二次确认<br/>防止误操作<br/>降低焦虑

        alt 确认删除
            U->>Confirm: 点击"删除"
            Confirm->>DB: 删除记录
            DB->>Confirm: 删除成功

            Confirm->>Item: 列表项消失动画
            Note over Item: 心理学: 消失动画<br/>提供视觉确认
            Confirm->>U: 显示Toast"已删除"
        else 取消删除
            U->>Confirm: 点击"取消"
            Confirm->>Item: 返回列表
        end
    end
```

### 4.3 记录管理心理学设计要点

#### 列表设计原则
- **分组显示**：按日期分组（今天、昨天、更早）
- **视觉层次**：图标 + 分类名 + 金额，信息清晰
- **快速扫描**：金额右对齐，便于比较

#### 操作效率设计
- **长按菜单**：减少操作步骤
- **左滑删除**：快捷操作（需确认）
- **批量操作**：长按进入选择模式

#### 错误预防设计
- **删除确认**：防止误删
- **编辑预填充**：减少重复输入
- **自动保存**：避免意外丢失

---

## 5. 设置页面交互流程

### 5.1 设置浏览与修改序列图

```mermaid
sequenceDiagram
    participant U as 用户
    participant S as 设置页
    participant Section as 设置分组
    participant Item as 设置项
    participant Modal as 设置弹窗
    participant DB as 数据库

    U->>S: 进入设置页
    S->>U: 显示分组列表<br/>分组: 基本/预算/数据/关于
    Note over U: 心理学: 分组降低信息密度

    U->>Section: 点击"基本设置"
    Section->>U: 展开设置项
    Note over U: 货币 / 小数位 / 主题 / 语言

    U->>Item: 点击"货币"
    Item->>Modal: 显示货币选择器
    Note over Modal: 选项: CNY / USD / EUR ...<br/>心理学: 选择而非输入

    U->>Modal: 选择"USD"
    Modal->>Modal: 高亮选中项
    Note over Modal: 心理学: 视觉确认

    U->>Modal: 点击"确认"
    Modal->>DB: 保存设置
    Modal->>Item: 更新显示<br/>货币: USD

    U->>Item: 点击"主题"
    Item->>Modal: 显示主题选择器
    Note over Modal: 选项: 浅色 / 深色 / 跟随系统

    U->>Modal: 选择"深色"
    Modal->>S: 切换到深色模式
    Note over S: 心理学: 即时预览<br/>降低决策焦虑

    U->>Modal: 点击"确认"
    Modal->>DB: 保存设置
    Modal->>S: 应用深色主题
```

### 5.2 预算设置序列图

```mermaid
sequenceDiagram
    participant U as 用户
    participant B as 预算页
    participant Total as 总预算
    participant Progress as 进度条
    participant Alert as 提醒设置
    participant DB as 数据库

    U->>B: 进入预算管理
    B->>DB: 请求预算数据
    DB->>B: 返回预算信息

    B->>U: 显示预算卡片
    Note over U: 总预算: ¥5000<br/>已用: ¥3245 (65%)<br/>进度条: 黄色警告

    U->>Total: 点击"总预算"
    Total->>Total: 显示输入框
    Note over Total: 当前值: ¥5000<br/>心理学: 显示当前值<br/>作为参考锚点

    U->>Total: 修改为"6000"
    Total->>Total: 实时验证
    Note over Total: 验证: 数字<br/>范围: 100-999999

    U->>Total: 点击"保存"
    Total->>DB: 更新预算
    Total->>Progress: 更新进度条
    Note over Progress: 使用率: 54%<br/>颜色: 绿色(健康)

    U->>Alert: 点击"提醒设置"
    Alert->>U: 显示提醒选项
    Note over U: - 80%时警告<br/>- 100%时超支<br/>心理学: 预设阈值<br/>减少决策

    U->>Alert: 开启提醒
    Alert->>DB: 保存设置
    Alert->>U: 显示Toast"提醒已开启"
```

### 5.3 数据管理序列图

```mermaid
sequenceDiagram
    participant U as 用户
    participant D as 数据管理页
    participant Export as 导出功能
    participant Backup as 备份功能
    participant Restore as 恢复功能
    participant Confirm as 确认对话框
    participant DB as 数据库

    U->>D: 进入数据管理
    D->>U: 显示操作选项<br/>导出 / 备份 / 恢复 / 清除

    alt 导出数据
        U->>Export: 点击"导出数据"
        Export->>Export: 显示格式选择
        Note over Export: CSV / Excel<br/>心理学: 提供选择

        U->>Export: 选择"Excel"
        Export->>DB: 请求导出数据
        DB->>Export: 返回数据
        Export->>U: 生成文件<br/>显示分享菜单
        Note over U: 心理学: 提供即时反馈<br/>文件生成成功
    end

    alt 备份数据
        U->>Backup: 点击"备份数据"
        Backup->>DB: 生成备份文件
        DB->>Backup: 返回JSON文件
        Backup->>U: 显示保存位置<br/>Toast: "备份已创建"
        Note over U: 心理学: 明确告知备份位置<br/>降低焦虑
    end

    alt 恢复数据
        U->>Restore: 点击"恢复数据"
        Restore->>Restore: 显示文件选择器

        U->>Restore: 选择备份文件
        Restore->>Confirm: 显示警告对话框
        Note over Confirm: 心理学: 强调后果<br/>降低误操作风险<br/>警告: 将覆盖当前数据

        alt 确认恢复
            U->>Confirm: 点击"恢复"
            Confirm->>DB: 恢复数据
            DB->>Confirm: 恢复成功
            Confirm->>U: 显示Toast"恢复成功"<br/>重启应用
            Note over U: 心理学: 重启提供<br/>明确的状态转换
        else 取消恢复
            U->>Confirm: 点击"取消"
            Confirm->>Restore: 返回数据管理
        end
    end
```

### 5.4 设置页面心理学设计要点

#### 分组设计原则
- **逻辑分组**：基本 / 预算 / 数据 / 关于
- **视觉分隔**：使用分隔线或卡片区分
- **渐进披露**：点击展开详细选项

#### 选择器设计
- **提供选项**：而非自由输入，减少决策负担
- **显示当前值**：作为参考锚点
- **即时预览**：主题切换立即预览效果

#### 安全操作设计
- **明确警告**：破坏性操作前强调后果
- **二次确认**：防止误操作
- **可逆性**：尽可能提供撤销选项

---

## 6. 交互流程总结

### 6.1 通用交互模式

| 交互类型 | 标准流程 | 心理学原理 |
|---------|---------|-----------|
| 打开页面 | 淡入/滑入动画 | 建立空间层级 |
| 返回页面 | 反向滑出动画 | 一致性预期 |
| 保存数据 | 验证 → 保存 → 反馈 | 即时强化 |
| 删除数据 | 确认 → 删除 → 动画 | 降低焦虑 |
| 加载数据 | 骨架屏 → 内容填充 | 减少等待焦虑 |

### 6.2 性能与感知性能

| 操作 | 目标时间 | 感知优化策略 |
|------|---------|-------------|
| 页面切换 | < 300ms | 并行加载数据 |
| 数据保存 | < 200ms | 乐观UI更新 |
| 列表加载 | < 500ms | 分页 + 虚拟滚动 |
| 图表渲染 | < 1s | 渐进式渲染 |

---

*文档版本：v1.0*
*创建日期：2025-01-16*
*最后更新：2025-01-16*
*设计师：Claude (UX Designer Agent)*
