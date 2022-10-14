package benchmark

import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import java.util.concurrent.atomic.AtomicLong
import kotlin.concurrent.thread

class Benchmark {
    companion object {
        fun threadSum() {
            val c = AtomicLong()

            for (i in 1..1_000_000L)
                thread(start = true) {
                    c.addAndGet(i)
                }

            println(c.get())
        }

        fun coroutinesSum() {
            val c = AtomicLong()

            for (i in 1..1_000_000L)
                GlobalScope.launch {
                    c.addAndGet(i)
                }

            println(c.get())
        }


    }
}