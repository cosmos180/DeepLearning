package collections

class Container {
    companion object {
        var list = mutableListOf(1, 2, 3, 4, 5)
        fun test() {
            for (i in 0 until getSize()) {
//                if (i == 3) {
                    print("remove---$i\n")
                    list.remove(i)
//                }
            }

            val shape = mutableListOf(
                arrayListOf(0.3223f,  0.2049f),
                arrayListOf(0.3379f,  0.7986f),
                arrayListOf(0.6328f,  0.816f),
                arrayListOf(0.3223f,  0.2049f)
            )

            var mutableZone = mutableListOf<ArrayList<Float>>()
            shape.mapIndexed { index, arrayList ->
                mutableZone.add(arrayList)
                if (index > 0 && index < shape.size-1) {
                    mutableZone.add(arrayList)
                }
            }


            val kInOutLine = mutableZone.flatMap {
                println(it)
                it.mapIndexed { index, any ->
                    if (index == 0) {
                        any * 1920
                    } else {
                        any * 1080
                    }
                }.toList()
            }

            println(kInOutLine)
        }

        fun getSize(): Int {
            print("---getSize")
            return list.size
        }
    }
}