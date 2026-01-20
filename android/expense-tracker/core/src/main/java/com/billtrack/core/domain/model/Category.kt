package com.billtrack.core.domain.model

import java.time.LocalDateTime

/**
 * 分类领域模型
 *
 * @property id 唯一标识
 * @property name 分类名称
 * @property parentId 父分类ID (null表示一级分类)
 * @property parent 父分类(关联查询时填充)
 * @property children 子分类列表(关联查询时填充)
 * @property icon 图标名称
 * @property color 颜色值 (HEX)
 * @property isCustom 是否自定义分类
 * @property sortOrder 排序序号
 * @property createdAt 创建时间
 */
data class Category(
    val id: String,
    val name: String,
    val parentId: String? = null,
    val parent: Category? = null,
    val children: List<Category>? = null,
    val icon: String,
    val color: String,
    val isCustom: Boolean = false,
    val sortOrder: Int = 0,
    val createdAt: LocalDateTime
) {
    val isRootCategory: Boolean
        get() = parentId == null

    val fullName: String
        get() = if (parent != null) "${parent.name} - $name" else name

    companion object {
        fun createPreset(
            id: String,
            name: String,
            parentId: String? = null,
            icon: String,
            color: String,
            sortOrder: Int
        ): Category {
            return Category(
                id = id,
                name = name,
                parentId = parentId,
                icon = icon,
                color = color,
                isCustom = false,
                sortOrder = sortOrder,
                createdAt = LocalDateTime.now()
            )
        }

        fun createCustom(
            name: String,
            parentId: String? = null,
            icon: String,
            color: String,
            sortOrder: Int
        ): Category {
            return Category(
                id = java.util.UUID.randomUUID().toString(),
                name = name,
                parentId = parentId,
                icon = icon,
                color = color,
                isCustom = true,
                sortOrder = sortOrder,
                createdAt = LocalDateTime.now()
            )
        }
    }
}
