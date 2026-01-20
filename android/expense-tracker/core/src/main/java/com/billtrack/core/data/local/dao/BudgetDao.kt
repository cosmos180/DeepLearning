package com.billtrack.core.data.local.dao

import androidx.room.*
import com.billtrack.core.data.local.entity.BudgetEntity
import kotlinx.coroutines.flow.Flow

/**
 * 预算DAO
 */
@Dao
interface BudgetDao {
    @Query("SELECT * FROM budgets WHERE month = :month ORDER BY category_id IS NULL, category_id")
    fun getBudgetsByMonth(month: String): Flow<List<BudgetEntity>>

    @Query("SELECT * FROM budgets WHERE month = :month AND category_id IS NULL LIMIT 1")
    suspend fun getTotalBudget(month: String): BudgetEntity?

    @Query("SELECT * FROM budgets WHERE month = :month AND category_id = :categoryId LIMIT 1")
    suspend fun getCategoryBudget(month: String, categoryId: String): BudgetEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBudget(budget: BudgetEntity)

    @Update
    suspend fun updateBudget(budget: BudgetEntity)

    @Delete
    suspend fun deleteBudget(budget: BudgetEntity)

    @Query("DELETE FROM budgets WHERE id = :id")
    suspend fun deleteBudgetById(id: String)
}
