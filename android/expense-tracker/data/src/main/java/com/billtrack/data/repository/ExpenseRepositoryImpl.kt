package com.billtrack.data.repository

import com.billtrack.core.data.local.dao.ExpenseDao
import com.billtrack.core.data.local.entity.ExpenseEntity
import com.billtrack.core.domain.model.Expense
import com.billtrack.core.domain.repository.CategoryExpenseStat
import com.billtrack.core.domain.repository.DailyExpenseStat
import com.billtrack.core.domain.repository.ExpenseRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.math.BigDecimal
import java.time.LocalDateTime
import javax.inject.Inject

/**
 * 消费记录Repository实现
 */
class ExpenseRepositoryImpl @Inject constructor(
    private val expenseDao: ExpenseDao
) : ExpenseRepository {

    override fun getAllExpenses(): Flow<List<Expense>> {
        return expenseDao.getAllExpenses().map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    override suspend fun getExpenseById(id: String): Expense? {
        return expenseDao.getExpenseById(id)?.toDomainModel()
    }

    override fun getExpensesByDateRange(
        startDate: LocalDateTime,
        endDate: LocalDateTime
    ): Flow<List<Expense>> {
        return expenseDao.getExpensesByDateRange(startDate, endDate).map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    override fun getExpensesByCategory(categoryId: String): Flow<List<Expense>> {
        return expenseDao.getExpensesByCategory(categoryId).map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    override fun searchExpenses(keyword: String): Flow<List<Expense>> {
        return expenseDao.searchExpenses(keyword).map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    override suspend fun insertExpense(expense: Expense): Result<Expense> {
        return try {
            val entity = ExpenseEntity.fromDomainModel(expense)
            expenseDao.insertExpense(entity)
            Result.success(expense)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateExpense(expense: Expense): Result<Expense> {
        return try {
            val entity = ExpenseEntity.fromDomainModel(expense)
            expenseDao.updateExpense(entity)
            Result.success(expense)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun deleteExpense(id: String): Result<Unit> {
        return try {
            expenseDao.deleteExpenseById(id)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun deleteExpenses(ids: List<String>): Result<Unit> {
        return try {
            expenseDao.deleteExpenses(ids)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getTotalExpense(
        startDate: LocalDateTime,
        endDate: LocalDateTime
    ): BigDecimal? {
        return expenseDao.getTotalExpense(startDate, endDate)
    }

    override suspend fun getExpenseByCategory(
        startDate: LocalDateTime,
        endDate: LocalDateTime
    ): List<CategoryExpenseStat> {
        val entityStats = expenseDao.getExpenseByCategory(startDate, endDate)
        return entityStats.map { stat ->
            CategoryExpenseStat(
                categoryId = stat.categoryId,
                total = stat.total,
                count = stat.count
            )
        }
    }

    override suspend fun getDailyTrend(
        startDate: LocalDateTime,
        endDate: LocalDateTime
    ): List<DailyExpenseStat> {
        val entityStats = expenseDao.getDailyTrend(startDate, endDate)
        return entityStats.map { stat ->
            DailyExpenseStat(
                date = stat.date,
                total = stat.total,
                count = stat.count
            )
        }
    }
}
