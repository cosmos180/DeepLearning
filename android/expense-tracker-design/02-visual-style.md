# 视觉风格定义 (Visual Style)

> **设计风格**: 现代极简主义 + 柔和玻璃态 (Modern Minimalist + Soft Glassmorphism)
> **核心特征**: 清晰、高效、温暖、可信

---

## 1. 设计风格选择

### 1.1 风格定位: 新拟物主义 2.0 (Neumorphism 2.0)

**为什么选择这种风格？**

**✅ 优势**:
- **触感真实**: 按钮和卡片具有物理按键的触觉暗示
- **层级清晰**: 通过光影建立明确的信息层级
- **现代感强**: 符合年轻用户的审美偏好
- **适配性好**: 在浅色和深色模式下都表现出色

**⚠️ 改进点**:
- 传统新拟物主义对比度不足 → **增加色彩对比度**
- 阴影过于柔和 → **强化边框和分割线**
- 可访问性差 → **结合扁平化设计提高可读性**

**最终风格融合**:
```
60% 扁平化设计 - 清晰、高效、可访问
30% 新拟物主义 - 柔和阴影、物理触感
10% 玻璃态设计 - 半透明、层次感
```

---

### 1.2 核心设计原则

#### 原则 1: 克制 (Constraint)
**"少即是多"**
- 每个屏幕最多 3 种主要颜色
- 避免过度装饰和装饰性元素
- 留白占画面的 40% 以上
- 每个元素必须有明确功能

#### 原则 2: 一致性 (Consistency)
**"可预测即可控"**
- 相同功能使用相同的视觉语言
- 间距、圆角、阴影形成系统化规范
- 动画时长和缓动函数统一
- 交互反馈模式一致

#### 原则 3: 层级 (Hierarchy)
**"引导视线，而非强迫"**
- 使用大小、颜色、位置建立视觉层级
- 关键信息通过对比度和位置突出
- 次要信息使用较浅的颜色和较小的字体
- 渐进式披露复杂信息

#### 原则 4: 反馈 (Feedback)
**"每个操作都有回应"**
- 按钮点击有视觉反馈
- 加载状态有进度指示
- 错误和成功有明确提示
- 手势操作有视觉引导

---

## 2. 阴影系统 (Shadow System)

### 2.1 阴影层级

```css
/* 级别 1: 轻微提升 - 按钮、标签 */
--shadow-sm:
  0 1px 2px 0 rgba(0, 0, 0, 0.05),
  0 1px 3px 0 rgba(0, 0, 0, 0.1);

/* 级别 2: 中等提升 - 卡片、弹窗 */
--shadow-md:
  0 4px 6px -1px rgba(0, 0, 0, 0.1),
  0 2px 4px -1px rgba(0, 0, 0, 0.06),
  0 0 0 1px rgba(0, 0, 0, 0.05);

/* 级别 3: 明显提升 - 模态框、悬浮元素 */
--shadow-lg:
  0 10px 15px -3px rgba(0, 0, 0, 0.1),
  0 4px 6px -2px rgba(0, 0, 0, 0.05),
  0 0 0 1px rgba(0, 0, 0, 0.05);

/* 级别 4: 强烈提升 - 抽屉、全屏覆盖 */
--shadow-xl:
  0 20px 25px -5px rgba(0, 0, 0, 0.1),
  0 10px 10px -5px rgba(0, 0, 0, 0.04),
  0 0 0 1px rgba(0, 0, 0, 0.05);

/* 内阴影 - 输入框、搜索框 */
--shadow-inner:
  inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
```

### 2.2 阴影使用原则

- **浅色模式**: 使用黑色半透明阴影 (rgba(0, 0, 0, x))
- **深色模式**: 使用白色半透明阴影 (rgba(255, 255, 255, x))
- **距离感**: 阴影越扩散、越远，元素离用户越近
- **角度**: 统一使用 45 度角（右下光源）

---

## 3. 圆角系统 (Border Radius)

```css
--radius-xs: 4px;   /* 小元素：标签、徽章 */
--radius-sm: 6px;   /* 按钮、输入框 */
--radius-md: 8px;   /* 卡片、列表项 */
--radius-lg: 12px;  /* 大卡片、模态框 */
--radius-xl: 16px;  /* 底部抽屉、图片 */
--radius-2xl: 24px; /* 特殊卡片、顶部图片 */
--radius-full: 9999px; /* 圆形元素：头像、图标按钮 */
```

**心理学应用**:
- **小圆角 (4-6px)**: 传达精确、高效、专业
- **中圆角 (8-12px)**: 平衡友好与专业
- **大圆角 (16-24px)**: 传达温暖、柔和、安全
- **完全圆形**: 强调聚焦、完整性

**使用场景**:
- 记账按钮: `--radius-lg` (12px) - 突出但不过分
- 卡片: `--radius-md` (8px) - 专业感
- 头像: `--radius-full` - 人性化
- 标签: `--radius-xs` (4px) - 精确感

---

## 4. 图标系统 (Icon System)

### 4.1 图标风格

**选择**: 线性图标 (Outline Icons) + 填充变体 (Filled Variants)

**理由**:
- **轻量感**: 线条图标视觉重量轻，适合极简风格
- **清晰度**: 在小尺寸下依然清晰可辨
- **一致性**: 易于保持风格统一
- **灵活性**: 支持双色填充和动画

**设计规范**:
```css
/* 网格系统 */
icon-grid: 24x24px;
stroke-width: 2px;
stroke-linecap: round;
stroke-linejoin: round;

/* 尺寸变体 */
--icon-xs: 16px;
--icon-sm: 20px;
--icon-md: 24px; /* 标准尺寸 */
--icon-lg: 32px;
--icon-xl: 48px;
```

### 4.2 核心图标库

**记账相关**:
- `plus-circle` - 快速记账
- `receipt` - 账单列表
- `calendar` - 定期记账
- `repeat` - 循环账单

**分类图标** (使用色彩区分):
- `utensils` - 餐饮 (橙色)
- `car` - 交通 (蓝色)
- `shopping-bag` - 购物 (粉色)
- `home` - 居住 (绿色)
- `book` - 教育 (靛蓝)
- `heart-pulse` - 医疗 (红色)
- `game-controller` - 娱乐 (黄色)
- `users` - 社交 (紫色)
- `trending-up` - 投资 (深绿)

**统计相关**:
- `chart-bar` - 柱状图
- `chart-line` - 趋势图
- `chart-pie` - 饼图
- `arrow-up-right` - 增长
- `arrow-down-right` - 下降

**预算相关**:
- `wallet` - 预算总览
- `alert-triangle` - 预算预警
- `target` - 预算目标
- `piggy-bank` - 储蓄目标

**操作相关**:
- `search` - 搜索
- `filter` - 筛选
- `settings` - 设置
- `bell` - 通知
- `user` - 账户
- `lock` - 隐私/安全
- `cloud-upload` - 备份
- `download` - 导出

### 4.3 图标使用原则

**✅ 推荐做法**:
- 图标 + 文字标签（提高可访问性）
- 24px 标准尺寸，保持视觉平衡
- 使用色彩传达状态（成功、警告、错误）
- 支持深色模式自适应

**❌ 避免做法**:
- 仅使用图标无文字（认知负荷高）
- 过度装饰性图标（降低功能性）
- 混合多种图标风格（破坏一致性）
- 过小的图标尺寸（< 16px）

---

## 5. 插画风格 (Illustration Style)

### 5.1 空状态插画

**场景**: 无数据、首次使用、搜索无结果

**风格**: 扁平化 + 柔和色彩

**示例场景**:
1. **首次使用**: 温馨的家庭记账场景
2. **无账单**: 空白的记账本 + 铅笔
3. **预算健康**: 存钱罐 + 金币
4. **预算预警**: 温和的提示牌（非惊吓式）

**色彩原则**:
- 使用品牌色系的浅色变体
- 避免纯黑，使用深灰 (#111827)
- 保持简洁，不过度绘制细节

### 5.2 功能引导插画

**场景**: 功能介绍、新手引导

**风格**: 线性图标 + 色彩点缀

**设计原则**:
- 每个步骤一个核心视觉元素
- 使用数字标记步骤顺序
- 色彩渐进引入（避免信息过载）

---

## 6. 字体系统 (Typography)

### 6.1 字体选择

**中文**: 思源黑体 (Noto Sans SC) / 苹方 (PingFang SC)
**英文**: Inter / SF Pro Display / Roboto
**数字**: SF Mono / Roboto Mono (等宽字体，对齐优化)

**回退栈**:
```css
font-family:
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  "PingFang SC",
  "Hiragino Sans GB",
  "Microsoft YaHei",
  "Helvetica Neue",
  Helvetica,
  Arial,
  sans-serif;
```

### 6.2 字体大小系统

```css
/* 标题系统 */
--text-xs: 0.75rem;    /* 12px - 辅助文本 */
--text-sm: 0.875rem;   /* 14px - 次要文本 */
--text-base: 1rem;     /* 16px - 正文 */
--text-lg: 1.125rem;   /* 18px - 强调文本 */
--text-xl: 1.25rem;    /* 20px - 小标题 */
--text-2xl: 1.5rem;    /* 24px - 中标题 */
--text-3xl: 1.875rem;  /* 30px - 大标题 */
--text-4xl: 2.25rem;   /* 36px - 特大标题 */

/* 数字系统（财务数据） */
--number-sm: 1.5rem;   /* 24px - 小金额 */
--number-md: 2rem;     /* 32px - 标准金额 */
--number-lg: 2.5rem;   /* 40px - 大金额 */
--number-xl: 3rem;     /* 48px - 特大金额 */
```

### 6.3 字重系统

```css
--font-light: 300;     /* 轻盈 - 装饰性文本 */
--font-normal: 400;    /* 正常 - 正文 */
--font-medium: 500;    /* 中等 - 强调文本 */
--font-semibold: 600;  /* 半粗 - 小标题 */
--font-bold: 700;      /* 粗体 - 大标题 */
```

**使用原则**:
- **财务数字**: 使用 `font-medium` (500) 或 `font-semibold` (600)
- **按钮文字**: 使用 `font-medium` (500)
- **标题**: 使用 `font-semibold` (600) 或 `font-bold` (700)
- **正文**: 使用 `font-normal` (400)

### 6.4 行高与字间距

```css
/* 行高系统 */
--leading-tight: 1.25;   /* 标题 - 紧凑 */
--leading-normal: 1.5;   /* 正文 - 标准 */
--leading-relaxed: 1.75; /* 长文本 - 宽松 */

/* 字间距 */
--tracking-tight: -0.025em;  /* 紧凑 - 大标题 */
--tracking-normal: 0;        /* 正常 - 正文 */
--tracking-wide: 0.025em;    /* 宽松 - 强调文本 */
```

---

## 7. 间距系统 (Spacing System)

### 7.1 8点网格系统

基于 8px 的倍数建立统一的间距系统：

```css
--spacing-0: 0;
--spacing-1: 0.25rem;  /* 4px */
--spacing-2: 0.5rem;   /* 8px */
--spacing-3: 0.75rem;  /* 12px */
--spacing-4: 1rem;     /* 16px */
--spacing-5: 1.25rem;  /* 20px */
--spacing-6: 1.5rem;   /* 24px */
--spacing-8: 2rem;     /* 32px */
--spacing-10: 2.5rem;  /* 40px */
--spacing-12: 3rem;    /* 48px */
--spacing-16: 4rem;    /* 64px */
--spacing-20: 5rem;    /* 80px */
--spacing-24: 6rem;    /* 96px */
```

### 7.2 组件内间距

```css
/* 按钮 */
--button-padding-x: 1rem;   /* 16px */
--button-padding-y: 0.75rem; /* 12px */

/* 输入框 */
--input-padding-x: 1rem;    /* 16px */
--input-padding-y: 0.75rem;  /* 12px */

/* 卡片 */
--card-padding: 1.5rem; /* 24px */

/* 列表项 */
--list-item-padding: 1rem; /* 16px */
```

---

## 8. 动效原则 (Animation Principles)

### 8.1 动效价值观

- **功能性优先**: 动效必须有明确目的，非装饰性
- **性能友好**: 避免影响页面性能和电池寿命
- **可访问性**: 尊重用户的动画偏好设置

### 8.2 缓动函数 (Easing Functions)

```css
/* 标准缓动 */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

/* 入场缓动 */
--ease-out: cubic-bezier(0, 0, 0.2, 1);

/* 出场缓动 */
--ease-in: cubic-bezier(0.4, 0, 1, 1);

/* 弹性缓动 */
--ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### 8.3 动画时长

```css
--duration-fast: 150ms;    /* 微交互：按钮点击 */
--duration-base: 200ms;    /* 标准过渡：悬停、聚焦 */
--duration-slow: 300ms;    /* 页面切换：模态框 */
--duration-slower: 500ms;  /* 复杂动画：图表 */
```

---

## 9. 渐变与纹理 (Gradients & Textures)

### 9.1 渐变系统

```css
/* 主色渐变 - 用于强调 */
--gradient-primary: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);

/* 成功渐变 */
--gradient-success: linear-gradient(135deg, #34D399 0%, #10B981 100%);

/* 背景渐变 - 微妙 */
--gradient-bg: linear-gradient(180deg, #F9FAFB 0%, #F3F4F6 100%);

/* 卡片高光 - 玻璃态 */
--gradient-glass: linear-gradient(
  135deg,
  rgba(255, 255, 255, 0.1) 0%,
  rgba(255, 255, 255, 0.05) 100%
);
```

### 9.2 玻璃态效果

```css
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* 深色模式 */
.glass-card-dark {
  background: rgba(17, 24, 39, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

**使用场景**:
- 悬浮工具栏
- 模态框背景
- 底部导航栏
- 卡片叠加效果

---

## 10. 图片处理 (Image Handling)

### 10.1 图片风格

**分类图标**: 使用扁平化插画风格
**用户头像**: 支持圆形裁剪 + 渐变边框
**截图/票据**: 自动边缘检测 + 阴影增强

### 10.2 图片占位符

```css
/* 渐变占位符 */
.placeholder-gradient {
  background: linear-gradient(
    90deg,
    #F3F4F6 0%,
    #E5E7EB 50%,
    #F3F4F6 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

## 11. 设计系统总结

### 11.1 核心设计标记

| 元素 | 规范 |
|------|------|
| 主色 | #2563EB (深海蓝) |
| 成功色 | #10B981 (翡翠绿) |
| 警告色 | #F59E0B (琥珀橙) |
| 危险色 | #EF4444 (珊瑚红) |
| 主字体 | Inter / 思源黑体 |
| 字号基准 | 16px |
| 行高基准 | 1.5 |
| 圆角基准 | 8px |
| 间距基准 | 8px 网格 |
| 阴影基准 | 多层柔和阴影 |

### 11.2 视觉风格关键词

- **清晰**: 高对比度、明确层级
- **高效**: 快速识别、简单操作
- **温暖**: 柔和圆角、友好配色
- **可信**: 专业细节、一致性
- **现代**: 当前设计趋势、简洁

---

**版本**: v1.0
**最后更新**: 2026-01-15
**状态**: 待评审
