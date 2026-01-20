package com.billtrack.core.domain.usecase.category

import com.billtrack.core.domain.model.Category
import com.billtrack.core.domain.repository.CategoryRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

/**
 * 获取分类用例
 */
class GetCategoriesUseCase @Inject constructor(
    private val categoryRepository: CategoryRepository
) {
    /**
     * 获取所有分类
     */
    fun getAllCategories(): Flow<List<Category>> {
        return categoryRepository.getAllCategories()
    }

    /**
     * 根据ID获取分类
     */
    suspend fun getCategoryById(id: String): Category? {
        return categoryRepository.getCategoryById(id)
    }

    /**
     * 获取一级分类
     */
    fun getRootCategories(): Flow<List<Category>> {
        return categoryRepository.getRootCategories()
    }

    /**
     * 获取子分类
     */
    fun getChildCategories(parentId: String): Flow<List<Category>> {
        return categoryRepository.getChildCategories(parentId)
    }

    /**
     * 获取自定义分类
     */
    fun getCustomCategories(): Flow<List<Category>> {
        return categoryRepository.getCustomCategories()
    }
}
