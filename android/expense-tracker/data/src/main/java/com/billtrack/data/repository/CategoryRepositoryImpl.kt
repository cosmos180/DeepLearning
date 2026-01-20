package com.billtrack.data.repository

import com.billtrack.core.data.local.dao.CategoryDao
import com.billtrack.core.data.local.entity.CategoryEntity
import com.billtrack.core.domain.model.Category
import com.billtrack.core.domain.repository.CategoryRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

/**
 * 分类Repository实现
 */
class CategoryRepositoryImpl @Inject constructor(
    private val categoryDao: CategoryDao
) : CategoryRepository {

    override fun getAllCategories(): Flow<List<Category>> {
        return categoryDao.getAllCategories().map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    override suspend fun getCategoryById(id: String): Category? {
        return categoryDao.getCategoryById(id)?.toDomainModel()
    }

    override fun getRootCategories(): Flow<List<Category>> {
        return categoryDao.getRootCategories().map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    override fun getChildCategories(parentId: String): Flow<List<Category>> {
        return categoryDao.getChildCategories(parentId).map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    override fun getCustomCategories(): Flow<List<Category>> {
        return categoryDao.getCustomCategories().map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    override suspend fun insertCategory(category: Category): Result<Category> {
        return try {
            val entity = CategoryEntity.fromDomainModel(category)
            categoryDao.insertCategory(entity)
            Result.success(category)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateCategory(category: Category): Result<Category> {
        return try {
            val entity = CategoryEntity.fromDomainModel(category)
            categoryDao.updateCategory(entity)
            Result.success(category)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun deleteCategory(id: String): Result<Unit> {
        return try {
            // 检查是否有关联的消费记录
            val expenseCount = categoryDao.getExpenseCount(id)
            if (expenseCount > 0) {
                return Result.failure(
                    IllegalStateException("Cannot delete category with $expenseCount associated expenses")
                )
            }
            categoryDao.deleteCategoryById(id)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
