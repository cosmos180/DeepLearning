/*
 * @Author: houjinxin
 * @Date: 2021-06-29 19:36:31
 * @Last Modified by: houjinxin
 * @Last Modified time: 2022-10-14 17:39:28
 */
#ifndef TPTHREADSAFEQUEUE_H
#define TPTHREADSAFEQUEUE_H

#define USE_PTHREAD

#ifdef USE_PTHREAD
#include <pthread.h>
#include <sstream>
#include <thread>
#else
#include <condition_variable>
#include <mutex>
#endif

#include <queue>

#define MUTEX_OWNER(m) (m >> 16) & 0xffff
#define MUTEX_COUNTER(m) (m >> 2) & 0xfff

namespace TupuIPC {
    template <typename T>
    class TPThreadSafeQueue {
      private:
#ifdef USE_PTHREAD
        mutable pthread_mutex_t mut;
        mutable pthread_cond_t data_cond;
#else
        mutable std::recursive_mutex mut;
        mutable std::condition_variable_any data_cond;
#endif

        mutable bool forceExit = false;
        using queue_type = std::queue<T>;
        queue_type data_queue;

      private:
        void init() {
#ifdef USE_PTHREAD
            pthread_mutexattr_t attr;
            pthread_mutexattr_init(&attr);
            pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_ERRORCHECK);
            pthread_mutex_init(&mut, &attr);
            pthread_mutexattr_destroy(&attr);

            pthread_cond_init(&data_cond, NULL);
#endif
        }

      public:
        using value_type = typename queue_type::value_type;
        using container_type = typename queue_type::container_type;

        TPThreadSafeQueue() { init(); };

        /*
         * 使用迭代器为参数的构造函数,适用所有容器对象
         */
        template <typename _InputIterator>
        TPThreadSafeQueue(_InputIterator first, _InputIterator last) {
            init();
            for (auto itor = first; itor != last; ++itor) {
                data_queue.push(*itor);
            }
        }

        explicit TPThreadSafeQueue(const container_type &c) : data_queue(c) { init(); }

        /*
         * 使用初始化列表为参数的构造函数
         */
        TPThreadSafeQueue(std::initializer_list<value_type> list)
            : TPThreadSafeQueue(list.begin(), list.end()) {
            init();
        }

        /*
         * 将元素加入队列
         */
        void push(const value_type &new_value) {
#ifdef USE_PTHREAD
            pthread_mutex_lock(&mut);

            // const auto &data = mut.__private[0];
            // auto owner = MUTEX_OWNER(data);
            // auto counter = MUTEX_COUNTER(data);
            // std::stringstream ss;
            // ss << std::this_thread::get_id();
            // uint64_t id = std::stoull(ss.str());
            // printf("this_id %d, current mux owner %d, counter %d\n", owner, counter);

            data_queue.push(new_value);

            pthread_mutex_unlock(&mut);
            pthread_cond_broadcast(&data_cond);
#else
            std::lock_guard<std::recursive_mutex> lk(mut);
            data_queue.push(new_value);
            data_cond.notify_all();
#endif
        }

        void push(value_type &&new_value) {
#ifdef USE_PTHREAD
            pthread_mutex_lock(&mut);

            // const auto &data = mut.__private[0];
            // printf("current mux ower %d, counter %d\n", MUTEX_OWNER(data), MUTEX_COUNTER(data));

            data_queue.push(std::move(new_value));

            pthread_mutex_unlock(&mut);
            pthread_cond_broadcast(&data_cond);
#else
            std::lock_guard<std::recursive_mutex> lk(mut);
            data_queue.push(std::move(new_value));
            data_cond.notify_all();
#endif
        }

        template <class... _Args>
        void emplace(_Args &&...__args) {
#ifdef USE_PTHREAD
            pthread_mutex_lock(&mut);

            data_queue.emplace(std::forward<_Args>(__args)...);

            pthread_mutex_unlock(&mut);
            pthread_cond_broadcast(&data_cond);
#else
            std::lock_guard<std::recursive_mutex> lk(mut);
            data_queue.emplace(std::forward<_Args>(__args)...);
            data_cond.notify_all();
#endif
        }

        /*
         * 从队列中弹出一个元素,如果队列为空就阻塞
         */
        value_type wait_and_pop() {
#ifdef USE_PTHREAD
            pthread_mutex_lock(&mut);
            while (this->data_queue.empty() && !forceExit) {
                pthread_cond_wait(&data_cond, &mut);
            }
            if (!forceExit) {
                auto value = std::move(data_queue.front());
                data_queue.pop();
                pthread_mutex_unlock(&mut);
                return value;
            } else {
                return {};
            }
#else
            std::unique_lock<std::recursive_mutex> lk(mut);
            data_cond.wait(lk, [this] { return (!this->data_queue.empty() || forceExit); });
            if (forceExit) {
                forceExit = false;
                return {};
            }
            auto value = std::move(data_queue.front());
            data_queue.pop();
            return value;
#endif
        }

        /*
         * 从队列中弹出一个元素,如果队列为空返回false
         */
        bool try_pop(value_type &value) {
#ifdef USE_PTHREAD
            bool ret = false;
            pthread_mutex_lock(&mut);
            do {
                if (data_queue.empty()) {
                    break;
                }

                value = std::move(data_queue.front());
                data_queue.pop();
                ret = true;
            } while (0);

            pthread_mutex_unlock(&mut);

            return ret;
#else
            std::lock_guard<std::recursive_mutex> lk(mut);
            if (data_queue.empty())
                return false;
            value = std::move(data_queue.front());
            data_queue.pop();
            return true;
#endif
        }

        /*
         * 返回队列是否为空
         */
        auto empty() const -> decltype(data_queue.empty()) {
#ifdef USE_PTHREAD
            bool ret = true;
            pthread_mutex_lock(&mut);

            ret = data_queue.empty();

            pthread_mutex_unlock(&mut);

            return ret;
#else
            std::lock_guard<std::recursive_mutex> lk(mut);
            return data_queue.empty();
#endif
        }

        /*
         * 返回队列中元素数个
         */
        auto size() const -> decltype(data_queue.size()) {
#ifdef USE_PTHREAD
            decltype(data_queue.size()) ret;
            pthread_mutex_lock(&mut);

            ret = data_queue.size();

            pthread_mutex_unlock(&mut);

            return ret;
#else
            std::lock_guard<std::recursive_mutex> lk(mut);
            return data_queue.size();
#endif
        }

        void endupWait() {
#ifdef USE_PTHREAD
            pthread_mutex_lock(&mut);

            forceExit = true;

            pthread_mutex_unlock(&mut);
            pthread_cond_broadcast(&data_cond);
#else
            std::lock_guard<std::recursive_mutex> lk(mut);
            forceExit = true;
            data_cond.notify_all();
#endif
        }
    };
    /* TPThreadSafeQueue */
} // namespace TupuIPC

#endif // TPTHREADSAFEQUEUE_H
