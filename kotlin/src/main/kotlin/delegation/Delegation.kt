package delegation

interface Base {
    fun print()
}

class BaseImpl(val x: Int) : Base {
    override fun print() { print(x) }
}

class Derived(private val y: Base = BaseImpl(20)) : Base by y

fun main() {
//    val b = BaseImpl(10)
    Derived().print()
}