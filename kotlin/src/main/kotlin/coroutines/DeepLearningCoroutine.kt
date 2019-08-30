package coroutines

import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

class DeepLearningCoroutine {
    companion object {
        fun basic() {
            GlobalScope.launch { // launch a new coroutine in background and continue
                delay(1000L) // non-blocking delay for 1 second (default time unit is ms)
                println("World!") // print after delay
            }
            println("Hello,") // main thread continues while coroutine is delayed
            Thread.sleep(2000L) // block main thread for 2 seconds to keep JVM alive
        }

        fun block() {
            GlobalScope.launch { // launch a new coroutine in background and continue
                delay(1000L)
                println("World!")
            }
            println("Hello,") // main thread continues here immediately
            runBlocking {     // but this expression blocks the main thread
                delay(2000L)  // ... while we delay for 2 seconds to keep JVM alive
            }
        }

        fun main() = runBlocking<Unit> { // start main coroutine
            GlobalScope.launch { // launch a new coroutine in background and continue
                delay(1000L)
                println("World!")
            }
            println("Hello,") // main coroutine continues here immediately
            delay(2000L)      // delaying for 2 seconds to keep JVM alive
        }

        suspend fun doSomethingUsefulOne(): Int {
            delay(1000L) // pretend we are doing something useful here
            return 13
        }

        suspend fun doSomethingUsefulTwo(): Int {
            delay(1000L) // pretend we are doing something useful here, too
            return 29
        }

        fun sum_v_1() = runBlocking {
            val time = measureTimeMillis {
                val one = doSomethingUsefulOne()
                val two = doSomethingUsefulTwo()
                println("The answer is ${one + two}")
            }
            println("Completed in $time ms")
        }

        fun sum_v_2() = runBlocking {
            val time = measureTimeMillis {
                val one = async { doSomethingUsefulOne() }
                val two = async { doSomethingUsefulTwo() }
                println("The answer is ${one.await() + two.await()}")
            }
            println("Completed in $time ms")
        }

        fun lazy() = runBlocking {
            val time = measureTimeMillis {
                val one = async(start = CoroutineStart.LAZY) { doSomethingUsefulOne() }
                val two = async(start = CoroutineStart.LAZY) { doSomethingUsefulTwo() }
                // some computation
//                one.start() // start the first one
//                two.start() // start the second one
                println("The answer is ${one.await() + two.await()}")
            }
            println("Completed in $time ms")
        }

        fun repeat() = runBlocking {
            repeat(100_000) { // launch a lot of coroutines
                launch {
                    delay(1000L)
                    print(".")
                }
            }

//            delay(1300L)
        }

        fun scope() = runBlocking { // this: CoroutineScope
            launch {
                delay(200L)
                println("Task from runBlocking")
            }

            coroutineScope { // Creates a coroutine scope
                launch {
                    delay(500L)
                    println("Task from nested launch")
                }

                delay(100L)
                println("Task from coroutine scope") // This line will be printed before the nested launch
            }

            println("Coroutine scope is over") // This line is not printed until the nested launch completes
        }
    }
}