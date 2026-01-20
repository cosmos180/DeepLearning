package com.billtrack.core.data.local.dao

import androidx.room.*
import com.billtrack.core.data.local.entity.CategoryEntity
import kotlinx.coroutines.flow.Flow

/**
 * 分类DAO
 */
@Dao
interface CategoryDao {
    @Query("SELECT * FROM categories ORDER BY sort_order ASC")
    fun getAllCategories(): Flow<List<CategoryEntity>>

    @Query("SELECT * FROM categories WHERE id = :id")
    suspend fun getCategoryById(id: String): CategoryEntity?

    @Query("SELECT * FROM categories WHERE parent_id IS NULL ORDER BY sort_order ASC")
    fun getRootCategories(): Flow<List<CategoryEntity>>

    @Query("SELECT * FROM categories WHERE parent_id = :parentId ORDER BY sort_order ASC")
    fun getChildCategories(parentId: String): Flow<List<CategoryEntity>>

    @Query("SELECT * FROM categories WHERE is_custom = 1 ORDER BY sort_order ASC")
    fun getCustomCategories(): Flow<List<CategoryEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCategory(category: CategoryEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCategories(categories: List<CategoryEntity>)

    @Update
    suspend fun updateCategory(category: CategoryEntity)

    @Delete
    suspend fun deleteCategory(category: CategoryEntity)

    @Query("DELETE FROM categories WHERE id = :id")
    suspend fun deleteCategoryById(id: String)

    @Query("SELECT COUNT(*) FROM expenses WHERE category_id = :categoryId")
    suspend fun getExpenseCount(categoryId: String): Int
}
