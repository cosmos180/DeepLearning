/*
 * @Author: houjinxin
 * @Date: 2021-06-29 19:36:31
 * @Last Modified by: houjinxin
 * @Last Modified time: 2022-10-14 12:23:15
 */
#ifndef TPTHREADSAFEQUEUE_H
#define TPTHREADSAFEQUEUE_H

#if USE_PTHREAD
#include <pthread.h>
#else
#include <condition_variable>
#include <mutex>
#endif

#include <queue>

namespace jason {
    template <typename T>
    class TPThreadSafeQueue {
      private:
#if USE_PTHREAD
        pthread_mutex_t mut;
        pthread_cond_t data_cond;
#else
        mutable std::recursive_mutex mut;
        mutable std::condition_variable_any data_cond;
#endif

        mutable bool forceExit = false;
        using queue_type = std::queue<T>;
        queue_type data_queue;

      private:
        void init() {
#if USE_PTHREAD
            pthread_mutex_init(&mut, nullptr);
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
#if USE_PTHREAD
            pthread_mutex_lock(&mut);

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
#if USE_PTHREAD
            pthread_mutex_lock(&mut);

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
#if USE_PTHREAD
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
#if USE_PTHREAD
            value_type value;
            pthread_mutex_lock(&mut);
            do {
                while (this->data_queue.empty() && !forceExit) {
                    pthread_cond_wait(&data_cond, &mut);
                }

                if (!forceExit) {
                    value = std::move(data_queue.front());
                    data_queue.pop();
                }
            } while (0);

            pthread_mutex_unlock(&mut);

            return value;
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
#if USE_PTHREAD
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
#if USE_PTHREAD
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
#if USE_PTHREAD
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
#if USE_PTHREAD
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
} // namespace jason

#endif // TPTHREADSAFEQUEUE_H
