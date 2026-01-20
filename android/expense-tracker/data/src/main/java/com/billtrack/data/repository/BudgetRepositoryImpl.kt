package com.billtrack.data.repository

import com.billtrack.core.data.local.dao.BudgetDao
import com.billtrack.core.data.local.entity.BudgetEntity
import com.billtrack.core.domain.model.Budget
import com.billtrack.core.domain.repository.BudgetRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.math.BigDecimal
import java.time.YearMonth
import java.util.UUID
import javax.inject.Inject

/**
 * 预算Repository实现
 */
class BudgetRepositoryImpl @Inject constructor(
    private val budgetDao: BudgetDao
) : BudgetRepository {

    override fun getBudgetsByMonth(month: YearMonth): Flow<List<Budget>> {
        return budgetDao.getBudgetsByMonth(month.toString()).map { entities ->
            entities.map { it.toDomainModel() }
        }
    }

    override suspend fun getTotalBudget(month: YearMonth): Budget? {
        return budgetDao.getTotalBudget(month.toString())?.toDomainModel()
    }

    override suspend fun getCategoryBudget(month: YearMonth, categoryId: String): Budget? {
        return budgetDao.getCategoryBudget(month.toString(), categoryId)?.toDomainModel()
    }

    override suspend fun setTotalBudget(amount: BigDecimal, month: YearMonth): Result<Budget> {
        return try {
            val existing = budgetDao.getTotalBudget(month.toString())
            val budget = if (existing != null) {
                existing.copy(amount = amount)
            } else {
                BudgetEntity(
                    id = UUID.randomUUID().toString(),
                    categoryId = null,
                    amount = amount,
                    month = month.toString(),
                    createdAt = java.time.LocalDateTime.now(),
                    updatedAt = java.time.LocalDateTime.now()
                )
            }
            budgetDao.insertBudget(budget)
            Result.success(budget.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun setCategoryBudget(
        categoryId: String,
        amount: BigDecimal,
        month: YearMonth
    ): Result<Budget> {
        return try {
            val existing = budgetDao.getCategoryBudget(month.toString(), categoryId)
            val budget = if (existing != null) {
                existing.copy(amount = amount)
            } else {
                BudgetEntity(
                    id = UUID.randomUUID().toString(),
                    categoryId = categoryId,
                    amount = amount,
                    month = month.toString(),
                    createdAt = java.time.LocalDateTime.now(),
                    updatedAt = java.time.LocalDateTime.now()
                )
            }
            budgetDao.insertBudget(budget)
            Result.success(budget.toDomainModel())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun updateBudget(budget: Budget): Result<Budget> {
        return try {
            val entity = BudgetEntity.fromDomainModel(budget)
            budgetDao.updateBudget(entity)
            Result.success(budget)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun deleteBudget(id: String): Result<Unit> {
        return try {
            budgetDao.deleteBudgetById(id)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
