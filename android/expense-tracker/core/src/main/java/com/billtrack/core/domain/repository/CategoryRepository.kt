package com.billtrack.core.domain.repository

import com.billtrack.core.domain.model.Category
import kotlinx.coroutines.flow.Flow

/**
 * 分类Repository接口
 */
interface CategoryRepository {
    /**
     * 获取所有分类
     */
    fun getAllCategories(): Flow<List<Category>>

    /**
     * 根据ID获取分类
     */
    suspend fun getCategoryById(id: String): Category?

    /**
     * 获取一级分类
     */
    fun getRootCategories(): Flow<List<Category>>

    /**
     * 获取子分类
     */
    fun getChildCategories(parentId: String): Flow<List<Category>>

    /**
     * 获取自定义分类
     */
    fun getCustomCategories(): Flow<List<Category>>

    /**
     * 插入分类
     */
    suspend fun insertCategory(category: Category): Result<Category>

    /**
     * 更新分类
     */
    suspend fun updateCategory(category: Category): Result<Category>

    /**
     * 删除分类
     */
    suspend fun deleteCategory(id: String): Result<Unit>
}
