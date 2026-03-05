package file

import java.io.File

class FileUtility {
    companion object {
        fun getFilePathExcludeType() {
            val file = File("/sdcard/bac/xyz.jpg")
            println(file.absolutePath)
            println(file.canonicalPath)
            println(file.absoluteFile)
            println(file.nameWithoutExtension)
            println(file.name)
            println(file.parentFile)
            println(file.parent)
            println(file.extension)
            println(System.currentTimeMillis())
        }
    }
}