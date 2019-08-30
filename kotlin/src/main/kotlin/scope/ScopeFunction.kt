package scope

class ScopeFunction {
    data class Person(var name: String, var age: UInt, var city: String) {
        fun moveTo(newCity: String) {
            city = newCity
        }

        fun incrementAge() {
            age += 1u
        }
    }

    companion object {
        fun let_test() {
            Person("Alice", 20u, "Amsterdam").let {
                println(it)
                it.moveTo("London")
                it.incrementAge()
                println(it)
            }
        }

        fun run_test() {
            val numbers = mutableListOf("one", "two", "three")
            val countEndsWithE = numbers.run {
                add("four")
                add("five")
                count { it.endsWith("e") }
            }
            println("There are $countEndsWithE elements that end with e.")
        }

        fun with_test() {
            val numbers = mutableListOf("one", "two", "three")
            val count = with(numbers) {
                val firstItem = first()
                val lastItem = last()
                println("First item: $firstItem, last item: $lastItem")
                size
            }

            print("count = $count")
        }


    }
}