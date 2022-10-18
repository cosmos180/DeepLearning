/*
 * @Author: houjinxin
 * @Date: 2022-10-17 16:33:47
 * @Last Modified by: houjinxin
 * @Last Modified time: 2022-10-17 17:42:30
 */
#ifndef AIR_PTHREAD_READER_WRITER_H
#define AIR_PTHREAD_READER_WRITER_H

#include <poll.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

#include "air_base.h"

#define ACCESS_ONCE(x) (*(volatile typeof(x) *)&(x))

pthread_mutex_t lock_a = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t lock_b = PTHREAD_MUTEX_INITIALIZER;

int x = 0;

void *lock_reader(void *arg) {
    // void *lock_reader(pthread_mutex_t *arg) {
    int i;
    int newx = -1;
    int oldx = -1;

    pthread_mutex_t *pmlp = (pthread_mutex_t *)arg;

    if (pthread_mutex_lock(pmlp) != 0) {
        perror("lock_reader: pthread_mutex_lock");
        exit(-1);
    }

    for (size_t i = 0; i < 100; i++) {
        newx = ACCESS_ONCE(x);

        if (newx != oldx) {
            printf("lock_reader(): x = %d\n", newx);
        }

        oldx = newx;

        poll(NULL, 0, 1);
    }

    if (pthread_mutex_unlock(pmlp) != 0) {
        perror("lock_reader: pthread_mutex_unlock");
        exit(-1);
    }

    printf("lock_reader: x = %d\n", ACCESS_ONCE(x));
    return NULL;
}

void *lock_writer(void *arg) {
    // void *lock_writer(pthread_mutex_t *arg) {
    int i;
    pthread_mutex_t *pmlp = (pthread_mutex_t *)arg;
    if (pthread_mutex_lock(pmlp) != 0) {
        perror("lock_writer: pthread_mutex_lock");
        exit(-1);
    }

    for (size_t i = 0; i < 3; i++) {
        ACCESS_ONCE(x)++;
        poll(NULL, 0, 5);
    }

    if (pthread_mutex_unlock(pmlp) != 0) {
        perror("lock_writer: pthread_mutex_unlock");
        exit(-1);
    }

    printf("lock_writer: x = %d\n", ACCESS_ONCE(x));

    return NULL;
}

class AIR_PTHREAD_READER_WRITER : public AIR_BASE {
  protected:
    void doTest() {
        printf("create two threads using same lock:\n");

        pthread_t tid1, tid2;

        // usleep(2 * 1000 * 1000);

        if (pthread_create(&tid1, NULL, lock_reader, &lock_a) != 0) {
            perror("pthread_create");
            exit(-1);
        }

        // if (pthread_create(&tid2, NULL, lock_writer, &lock_a) != 0) {
        //     perror("pthread_create");
        //     exit(-1);
        // }

        if (pthread_create(&tid2, NULL, lock_writer, &lock_b) != 0) {
            perror("pthread_create");
            exit(-1);
        }

        void *vp = NULL;

        if (pthread_join(tid1, &vp) != 0) {
            perror("pthread_join");
            exit(-1);
        }

        if (pthread_join(tid2, &vp) != 0) {
            perror("pthread_join");
            exit(-1);
        }
    }
};

#endif