import collections.Container
import coroutines.DeepLearningCoroutine


class main {
    companion object {

        fun getFloatThreshold(): Float {
            return 0.8f
        }

        @JvmStatic
        fun main(args: Array<String>) {
//            DeepLearningCoroutine.basic()

//            DeepLearningCoroutine.block()

//            DeepLearningCoroutine.sum_v_1()
//            DeepLearningCoroutine.sum_v_2()

//            DeepLearningCoroutine.lazy()

//            DeepLearningCoroutine.repeat()

//            DeepLearningCoroutine.scope()

//            ScopeFunction.let_test()

//            ScopeFunction.run_test()

//            ScopeFunction.with_test()

//            Benchmark.threadSum()

//            Benchmark.coroutinesSum()


//            DeepLearningChannel.basic()

//            DeepLearningChannel.closeAndIteration()

//            DeepLearningChannel.channelProducers()

//            DeepLearningChannel.pipeline()

//            TimestampPrinter.strToTimestamp()

//            DeepLearningRX.basic()

//            DeepLearningRX.fromFuture()

//            DeepLearningRX.fromIterable()

//            DeepLearningRX.defer()
//
//            DeepLearningRX.timer()

//            DeepLearningRX.interval()

//            DeepLearningRX.empty_never_error()

//            DeepLearningRX.map()

//            print("Hello world")
//            for (i in 0 until 10) {
////                print(i)
//                print(min(2, 2))
//            }


//            val animals = listOf(1, 2, 3, 4, 5, 6)
//            val ret = animals.reduce { acc, i ->
////                print("Result = ${acc.toInt()}, i = $i\n")
//                acc + i
//            }
//
//            print(ret)

//            FileUtility.getFilePathExcludeType()

//            val t1 = tan(48.0 /180 * Math.PI/2)
//            val t2 = tan(48.0/180 * Math.PI/2)
//            val ratio = (t1 * 960 / (t2 * 480)).toFloat()

//            if (getFloatThreshold() >= 0.65f) {
//                print("getFloatThreshold() > 0.65f")
//            } else {
//                print("getFloatThreshold() < 0.65f")
//            }


//            val map = HashMap<String, String>()
//            map["1"] = "test1"
//            map["2"] = "test2"
//            map["3"] = "test3"
//            map["4"] = "test4"
//
//            //完整遍历Map
//            for ((key, value) in map) {
//                System.out.printf("key: %s value:%s\r\n", key, value)
//            }
//
//            //删除元素
//            val it = map.entries.iterator()
//            while (it.hasNext()) {
//                val entry = it.next()
//                val key = entry.key
//                val k = Integer.parseInt(key)
//                if (k % 2 == 1) {
//                    System.out.printf("delete key:%s value:%s\r\n", key, entry.value)
//                    it.remove()
//                }
//            }
//
//            //完整遍历Map
//            for ((key, value) in map) {
//                System.out.printf("key: %s value:%s\r\n", key, value)
//            }

//            val timeA = "2020-09-08 18:30~2020-09-08 19:30"
//            val timeB = "09-08 18:30~09-08 19:30"
//            val timeC = "0:0~0:0"
////            val timeC = ""
//
//            val regexA= "^20\\d{2}-\\d{1,2}-\\d{1,2} \\d{1,2}:\\d{1,2}~20\\d{2}-\\d{1,2}-\\d{1,2} \\d{1,2}:\\d{1,2}"
//            val regexB= "^\\d{1,2}-\\d{1,2} \\d{1,2}:\\d{1,2}~\\d{1,2}-\\d{1,2} \\d{1,2}:\\d{1,2}"
//            val regexC= "^\\d{1,2}:\\d{1,2}~\\d{1,2}:\\d{1,2}"
//
//            print("${timeA.matches(Regex(regexA))}\n")
//            print("${timeA.matches(Regex(regexB))}\n")
//            print("${timeA.matches(Regex(regexC))}\n")
//
//            print("--------------------\n")
//
//            print("${timeB.matches(Regex(regexA))}\n")
//            print("${timeB.matches(Regex(regexB))}\n")
//            print("${timeB.matches(Regex(regexC))}\n")
//
//            print("--------------------\n")
//
//            print("${timeC.matches(Regex(regexA))}\n")
//            print("${timeC.matches(Regex(regexB))}\n")
//            print("${timeC.matches(Regex(regexC))}\n")
//
//            print("--------------------\n")
//
//            if (timeA.matches(Regex(regexA))) {
//                val beginTag = timeA.split("~")[0]
//                val endTag = timeA.split("~")[1]
//                val beginDate = SimpleDateFormat("yyyy-MM-dd HH:mm").parse(beginTag)
//                val endDate = SimpleDateFormat("yyyy-MM-dd HH:mm").parse(endTag)
//
//                print("${beginDate.time/1000}\n")
//                print("${endDate.time/1000}\n")
//            }
//
//            if (timeB.matches(Regex(regexB))) {
//                val beginTag = timeB.split("~")[0]
//                val endTag = timeB.split("~")[1]
//                val beginDate = SimpleDateFormat("MM-dd HH:mm").parse(beginTag)
//                val endDate = SimpleDateFormat("MM-dd HH:mm").parse(endTag)
//
//                val calendar = Calendar.getInstance()
////                calendar.time
//                print("${calendar.get(Calendar.YEAR)}\n")
//                val year = calendar.get(Calendar.YEAR)
//                val month = calendar.get(Calendar.MONTH)
//
//                calendar.time = beginDate
//                calendar.set(Calendar.YEAR, year)
//
//                print("${calendar.time.time/1000}\n")
//
//                calendar.time = endDate
//                calendar.set(Calendar.YEAR, year)
//                print("${calendar.time.time/1000}\n")
//
//            }
//
//            if (timeC.matches(Regex(regexC))) {
//                val beginTag = timeC.split("~")[0]
//                val endTag = timeC.split("~")[1]
//                val beginDate = SimpleDateFormat("HH:mm").parse(beginTag)
//                val endDate = SimpleDateFormat("HH:mm").parse(endTag)
//
//                val calendar = Calendar.getInstance()
//                print("${calendar.get(Calendar.YEAR)}\n")
//                val year = calendar.get(Calendar.YEAR)
//                val month = calendar.get(Calendar.MONTH)
//                val day = calendar.get(Calendar.DAY_OF_MONTH)
//
//                calendar.time = beginDate
//                calendar.set(Calendar.YEAR, year)
//                calendar.set(Calendar.MONTH, month)
//                calendar.set(Calendar.DAY_OF_MONTH, month)
//
//                print("${calendar.time}-${month}-${day}\n")
//
//                print("${calendar.time.time/1000}\n")
//
//                calendar.time = endDate
//                calendar.set(Calendar.YEAR, 2020)
//                calendar.set(Calendar.MONTH,8)
//                calendar.set(Calendar.DAY_OF_MONTH, 8)
//                print("${calendar.time.time/1000}\n")
//            }
//            Container.test()
                DeepLearningCoroutine.diffFunc()
        }
    }
}