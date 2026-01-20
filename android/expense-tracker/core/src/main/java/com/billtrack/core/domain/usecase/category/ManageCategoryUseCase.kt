package com.billtrack.core.domain.usecase.category

import com.billtrack.core.domain.model.Category
import com.billtrack.core.domain.repository.CategoryRepository
import javax.inject.Inject

/**
 * 管理分类用例
 */
class ManageCategoryUseCase @Inject constructor(
    private val categoryRepository: CategoryRepository
) {
    /**
     * 添加分类
     */
    suspend fun addCategory(category: Category): Result<Category> {
        return categoryRepository.insertCategory(category)
    }

    /**
     * 创建自定义分类
     */
    suspend fun createCustomCategory(
        name: String,
        parentId: String? = null,
        icon: String,
        color: String,
        sortOrder: Int = 0
    ): Result<Category> {
        if (name.isBlank()) {
            return Result.failure(IllegalArgumentException("Category name cannot be blank"))
        }
        if (icon.isBlank()) {
            return Result.failure(IllegalArgumentException("Category icon cannot be blank"))
        }
        if (color.isBlank()) {
            return Result.failure(IllegalArgumentException("Category color cannot be blank"))
        }

        val category = Category.createCustom(
            name = name,
            parentId = parentId,
            icon = icon,
            color = color,
            sortOrder = sortOrder
        )

        return categoryRepository.insertCategory(category)
    }

    /**
     * 更新分类
     */
    suspend fun updateCategory(category: Category): Result<Category> {
        return categoryRepository.updateCategory(category)
    }

    /**
     * 删除分类
     */
    suspend fun deleteCategory(id: String): Result<Unit> {
        if (id.isBlank()) {
            return Result.failure(IllegalArgumentException("Category ID cannot be blank"))
        }
        return categoryRepository.deleteCategory(id)
    }
}
