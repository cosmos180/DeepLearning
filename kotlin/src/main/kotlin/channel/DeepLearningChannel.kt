package channel

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.cancelChildren
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.ReceiveChannel
import kotlinx.coroutines.channels.consumeEachIndexed
import kotlinx.coroutines.channels.produce
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

class DeepLearningChannel {
    companion object {
        fun basic() {
            runBlocking {
                //sampleStart
                val channel = Channel<Int>()
                launch {
                    // this might be heavy CPU-consuming computation or async logic, we'll just send five squares
                    for (x in 1..5) channel.send(x * x)
                }
                // here we print five received integers:
                repeat(3) { println(channel.receive()) }
                println("Done!")
                //sampleEnd
            }
        }

        fun closeAndIteration() {
            runBlocking {
                val channel = Channel<Int>()
                launch {
                    for (i in 1..5) channel.send(i)
                    channel.close()
                }
                for (y in channel) print(y)
            }
        }

        fun CoroutineScope.produceSquares(): ReceiveChannel<Int> = produce {
            for (x in 1..5) send(x * x)
        }

        fun channelProducers() {
            runBlocking {
                val squares = produceSquares()
                squares.consumeEachIndexed {
                    print("${it.index} - ${it.value}")
                    print("\n")
                }
            }
        }

        fun CoroutineScope.numbersFrom(start: Int) = produce<Int> {
            var x = start
            while (true) send(x++) // infinite stream of integers from start
        }

        fun CoroutineScope.filter(numbers: ReceiveChannel<Int>, prime: Int) = produce<Int> {
            for (x in numbers) if (x % prime != 0) send(x)
        }

        fun pipeline() {
            runBlocking {
                var cur = numbersFrom(2)
//                for (i in 1..10) {
                    val prime = cur.receive()
                    println(prime)
//                    cur = filter(cur, prime)
//                }
//                coroutineContext.cancelChildren() // cancel all children to let main finish
            }
        }
    }
}