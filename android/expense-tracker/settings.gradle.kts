pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { url = uri("https://jitpack.io") }
    }
}

rootProject.name = "BillTrack"
include(":app")
include(":core")
include(":data")
// 注意：feature 模块暂时禁用，UI 代码在 app 模块中实现
// include(":feature:home")
// include(":feature:expense")
// include(":feature:statistics")
// include(":feature:category")
// include(":feature:budget")
// include(":feature:settings")
