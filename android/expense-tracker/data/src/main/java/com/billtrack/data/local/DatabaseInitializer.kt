package com.billtrack.data.local

import com.billtrack.core.data.local.dao.CategoryDao
import com.billtrack.core.data.local.entity.CategoryEntity
import kotlinx.coroutines.flow.first
import java.time.LocalDateTime
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 数据库初始化器
 * 用于创建预设分类数据
 */
@Singleton
class DatabaseInitializer @Inject constructor(
    private val database: AppDatabase,
    private val categoryDao: CategoryDao
) {
    suspend fun initialize() {
        // 检查是否已初始化
        val categories = categoryDao.getAllCategories().first()
        if (categories.isNotEmpty()) return

        // 插入预设分类
        val presetCategories = getPresetCategories()
        categoryDao.insertCategories(presetCategories)
    }

    private fun getPresetCategories(): List<CategoryEntity> {
        val now = LocalDateTime.now()
        return listOf(
            // 餐饮
            CategoryEntity("cat_1", "餐饮", null, "restaurant", "#FF6B6B", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_1_1", "早餐", "cat_1", "breakfast", "#FF8E8E", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_1_2", "午餐", "cat_1", "lunch", "#FF8E8E", isCustom = false, sortOrder = 2, now),
            CategoryEntity("cat_1_3", "晚餐", "cat_1", "dinner", "#FF8E8E", isCustom = false, sortOrder = 3, now),
            CategoryEntity("cat_1_4", "零食", "cat_1", "snack", "#FF8E8E", isCustom = false, sortOrder = 4, now),

            // 交通
            CategoryEntity("cat_2", "交通", null, "transport", "#4ECDC4", isCustom = false, sortOrder = 2, now),
            CategoryEntity("cat_2_1", "公交地铁", "cat_2", "subway", "#7EDDD5", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_2_2", "打车", "cat_2", "taxi", "#7EDDD5", isCustom = false, sortOrder = 2, now),

            // 购物
            CategoryEntity("cat_3", "购物", null, "shopping", "#95E1D3", isCustom = false, sortOrder = 3, now),
            CategoryEntity("cat_3_1", "服饰", "cat_3", "clothing", "#B8E8DE", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_3_2", "日用品", "cat_3", "daily", "#B8E8DE", isCustom = false, sortOrder = 2, now),

            // 娱乐
            CategoryEntity("cat_4", "娱乐", null, "entertainment", "#F38181", isCustom = false, sortOrder = 4, now),
            CategoryEntity("cat_4_1", "电影", "cat_4", "movie", "#F5A3A3", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_4_2", "游戏", "cat_4", "game", "#F5A3A3", isCustom = false, sortOrder = 2, now),

            // 居住
            CategoryEntity("cat_5", "居住", null, "home", "#AA96DA", isCustom = false, sortOrder = 5, now),
            CategoryEntity("cat_5_1", "房租", "cat_5", "rent", "#C5B7E6", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_5_2", "水电燃气", "cat_5", "utility", "#C5B7E6", isCustom = false, sortOrder = 2, now),

            // 医疗
            CategoryEntity("cat_6", "医疗", null, "medical", "#FCBAD3", isCustom = false, sortOrder = 6, now),
            CategoryEntity("cat_6_1", "门诊", "cat_6", "clinic", "#FDCDE0", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_6_2", "药品", "cat_6", "medicine", "#FDCDE0", isCustom = false, sortOrder = 2, now),

            // 教育
            CategoryEntity("cat_7", "教育", null, "education", "#FFFFD2", isCustom = false, sortOrder = 7, now),
            CategoryEntity("cat_7_1", "书籍", "cat_7", "book", "#FFFFE5", isCustom = false, sortOrder = 1, now),
            CategoryEntity("cat_7_2", "课程", "cat_7", "course", "#FFFFE5", isCustom = false, sortOrder = 2, now),

            // 其他
            CategoryEntity("cat_8", "其他", null, "other", "#A8D8EA", isCustom = false, sortOrder = 8, now)
        )
    }
}
