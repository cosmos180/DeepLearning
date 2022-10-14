/*
 * @Author: your name
 * @Date: 2021-01-14 12:30:10
 * @LastEditTime: 2021-01-18 14:23:03
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /conan/test_package/target/benchmark.h
 */

    enum class TimeUnit {
        milliseconds, microseconds
    };


    template<TimeUnit timeUnit = TimeUnit::milliseconds>
    class BenchmarkTimer {
    public:

        enum LogLevel {
            Debug,
            Info,
            Warn,
            Error
        };

        explicit BenchmarkTimer(std::string tag, LogLevel logLevel): begin{
                std::chrono::steady_clock::now()}, mTag{std::move(tag)}, mLogLevel{logLevel} {

        }

        explicit BenchmarkTimer(std::string tag) : BenchmarkTimer(tag, LogLevel::Error) {
        }

        explicit BenchmarkTimer() : BenchmarkTimer("Yaksha") {

        }


        ~BenchmarkTimer() {
            if (!isStop) {
                stop();
            }
        }


        void stop() {
            stopImpl(std::integral_constant<Yaksha::TimeUnit, timeUnit>{});
            isStop = true;
        }

    private:

        void stopImpl(std::integral_constant<Yaksha::TimeUnit, Yaksha::TimeUnit::milliseconds>) {
            std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
            log("[ %s ] cost time = %lld ms", mTag.c_str(),
                   std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count());
        }

        void stopImpl(std::integral_constant<Yaksha::TimeUnit, Yaksha::TimeUnit::microseconds>) {
            std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
            log("[ %s ] cost time = %lld us", mTag.c_str(),
                    std::chrono::duration_cast<std::chrono::microseconds>(end - begin).count());
        }

        void log(const char* fmt, const char* tag, long long int time) {
            TLogE(fmt, tag, time);
        }

    private:
        std::chrono::steady_clock::time_point begin;
        std::string mTag;
        LogLevel mLogLevel;
        bool isStop = false;
    };