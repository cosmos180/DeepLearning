package rx

import io.reactivex.Observable
import io.reactivex.ObservableSource
import io.reactivex.Observer
import io.reactivex.disposables.Disposable
import java.util.concurrent.Callable
import java.util.concurrent.FutureTask
import java.util.concurrent.TimeUnit

class DeepLearningRX {
    companion object {
        fun basic() {
//            Observable.create(ObservableOnSubscribe<String> {
//                it.onNext("Hello\n")
//                it.onNext("World\n")
//                it.onComplete()
//            }).subscribe(object: Observer<String> {
//                override fun onComplete() {
//                    print("onComplete\n")
//                }
//
//                override fun onSubscribe(d: Disposable) {
//                    print("onSubscribe\n")
//                }
//
//                override fun onNext(t: String) {
//                    print(t)
//                }
//
//                override fun onError(e: Throwable) {
//                    print(e.message)
//                }
//            })

            val signal = Observable.fromCallable(object: Callable<String> {
                override fun call(): String {
                    return "Tuputech\n"
                }
            })

            signal.subscribe(object: Observer<String> {
                override fun onComplete() {
                    print("onComplete\n")
                }

                override fun onSubscribe(d: Disposable) {
                    print("onSubscribe\n")
                }

                override fun onNext(t: String) {
                    print(t)
                }

                override fun onError(e: Throwable) {
                    print(e.message)
                }
            })

            signal.subscribe {
                print(it)
            }

            signal.subscribe {
                print(it)
            }
        }

        fun fromFuture() {
            val futureTask = FutureTask<String>(Callable<String> {
                print("CallableDemo is Running\n")
                return@Callable "FromFuture\n"
            })

            Observable.fromFuture(futureTask)
                .doOnSubscribe {
                    print("doOnSubscribe is Running\n")
                    futureTask.run()
                }
                .subscribe {
                    print(it)
                }
        }

        fun fromIterable() {
            val list = ArrayList<Int>()
            list.add(1)
            list.add(2)
            list.add(3)
            list.add(4)
            Observable.fromIterable(list)
                .subscribe {
                    print(it)
                }
        }

        fun defer() {
            var i = 100

            val signal = Observable.defer(Callable<ObservableSource<Int>> {
                return@Callable Observable.just(i)
            })

            i = 200

            val observer = object : Observer<Int> {
                override fun onComplete() {
                    print("onComplete\n")
                }

                override fun onSubscribe(d: Disposable) {

                }

                override fun onNext(t: Int) {
                    print("$t\n")
                }

                override fun onError(e: Throwable) {

                }
            }

            signal.subscribe(observer)

            i = 300

            signal.subscribe(observer)
        }

        fun timer() {
            Observable.timer(500, TimeUnit.MILLISECONDS)
                .subscribe {
                    print(it)
                }
            Thread.sleep(1000)
        }

        fun interval() {
//            Observable.interval(4, TimeUnit.SECONDS)
//            Observable.intervalRange(10, 3, 0, 4, TimeUnit.SECONDS)
            Observable.rangeLong(100, 100)
                .subscribe(object : Observer<Long> {
                    override fun onComplete() {

                    }

                    override fun onSubscribe(d: Disposable) {

                    }

                    override fun onNext(t: Long) {
                        print("$t\n")
                    }

                    override fun onError(e: Throwable) {

                    }

                })

//            Thread.sleep(20*1000)
        }

        fun empty_never_error() {
//            Observable.empty<Int>()
//            Observable.never<Int>()
            Observable.error<Int>(Throwable("Hello World"))
                .subscribe(object : Observer<Int> {
                    override fun onComplete() {
                        print("onComplete\n")
                    }

                    override fun onSubscribe(d: Disposable) {
                        print("onSubscribe\n")
                    }

                    override fun onNext(t: Int) {
                        print("onNext\n")
                    }

                    override fun onError(e: Throwable) {
                        print("onError: ${e.message}\n")
                    }
                })
        }

        data class Plan(val time: String, val content: String, val actionList: ArrayList<String>?)
        data class Person(val name: String, val planList: ArrayList<Plan>)

        fun map() {
            Observable.just(1, 2,3)
                .map {
                    return@map "I am $it\n"
                }
                .subscribe {
                    print(it)
                }
        }

        fun flatmap() {
            val personList = arrayListOf(
                (
                    Person("zhang", arrayListOf
                        (
                            Plan("a", "a_1_2_3", arrayListOf("1","2","3")),
                            Plan("b", "b_1_2_3", arrayListOf("4","5","6")),
                            Plan("c", "c_1_2_3", arrayListOf("7","8","9"))
                        )
                    )
                ),
                (
                    Person("Li", arrayListOf
                        (
                            Plan("e", "e_1_2_3", arrayListOf("10","11","12")),
                            Plan("f", "f_1_2_3", arrayListOf("13","14","15")),
                            Plan("g", "g_1_2_3", arrayListOf("16","17","18"))
                        )
                    )
                )
            )

        }
    }
}
