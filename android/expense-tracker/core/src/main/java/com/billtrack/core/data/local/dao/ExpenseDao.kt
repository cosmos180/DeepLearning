package com.billtrack.core.data.local.dao

import androidx.room.*
import com.billtrack.core.data.local.entity.ExpenseEntity
import kotlinx.coroutines.flow.Flow
import java.math.BigDecimal
import java.time.LocalDateTime

/**
 * 消费记录DAO
 */
@Dao
interface ExpenseDao {
    // 基础CRUD
    @Query("SELECT * FROM expenses ORDER BY date DESC")
    fun getAllExpenses(): Flow<List<ExpenseEntity>>

    @Query("SELECT * FROM expenses WHERE id = :id")
    suspend fun getExpenseById(id: String): ExpenseEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertExpense(expense: ExpenseEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertExpenses(expenses: List<ExpenseEntity>)

    @Update
    suspend fun updateExpense(expense: ExpenseEntity)

    @Delete
    suspend fun deleteExpense(expense: ExpenseEntity)

    @Query("DELETE FROM expenses WHERE id = :id")
    suspend fun deleteExpenseById(id: String)

    @Query("DELETE FROM expenses WHERE id IN (:ids)")
    suspend fun deleteExpenses(ids: List<String>)

    @Query("DELETE FROM expenses")
    suspend fun deleteAllExpenses()

    // 查询方法
    @Query("SELECT * FROM expenses WHERE date >= :startDate AND date < :endDate ORDER BY date DESC")
    fun getExpensesByDateRange(startDate: LocalDateTime, endDate: LocalDateTime): Flow<List<ExpenseEntity>>

    @Query("SELECT * FROM expenses WHERE category_id = :categoryId ORDER BY date DESC")
    fun getExpensesByCategory(categoryId: String): Flow<List<ExpenseEntity>>

    @Query("""
        SELECT * FROM expenses
        WHERE note LIKE '%' || :keyword || '%'
        OR category_id IN (SELECT id FROM categories WHERE name LIKE '%' || :keyword || '%')
        ORDER BY date DESC
    """)
    fun searchExpenses(keyword: String): Flow<List<ExpenseEntity>>

    // 统计方法
    @Query("SELECT SUM(amount) FROM expenses WHERE date >= :startDate AND date < :endDate")
    suspend fun getTotalExpense(startDate: LocalDateTime, endDate: LocalDateTime): BigDecimal?

    @Query("""
        SELECT category_id, SUM(amount) as total, COUNT(*) as count
        FROM expenses
        WHERE date >= :startDate AND date < :endDate
        GROUP BY category_id
        ORDER BY total DESC
    """)
    suspend fun getExpenseByCategory(startDate: LocalDateTime, endDate: LocalDateTime): List<CategoryExpenseEntity>

    @Query("""
        SELECT date, SUM(amount) as total, COUNT(*) as count
        FROM expenses
        WHERE date >= :startDate AND date < :endDate
        GROUP BY date
        ORDER BY date ASC
    """)
    suspend fun getDailyTrend(startDate: LocalDateTime, endDate: LocalDateTime): List<DailyExpenseEntity>
}

/**
 * 分类支出统计实体
 */
data class CategoryExpenseEntity(
    @ColumnInfo(name = "category_id")
    val categoryId: String,
    val total: BigDecimal,
    val count: Int
)

/**
 * 每日支出统计实体
 */
data class DailyExpenseEntity(
    val date: LocalDateTime,
    val total: BigDecimal,
    val count: Int
)
