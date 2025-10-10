#!/usr/bin/env python3
"""
重试机制工具
用于处理API请求的重试逻辑
"""

import time
import random
import logging
from functools import wraps
from typing import Callable, Any, Optional, Type, Union

logger = logging.getLogger(__name__)


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 退避倍数
        exceptions: 需要重试的异常类型
        on_retry: 重试时的回调函数

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        # 计算延迟时间（指数退避 + 随机抖动）
                        base_delay = delay * (backoff ** attempt)
                        jitter = random.uniform(0.1, 0.5) * base_delay
                        total_delay = base_delay + jitter

                        logger.warning(
                            f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}. "
                            f"等待 {total_delay:.2f} 秒后重试..."
                        )

                        # 调用重试回调
                        if on_retry:
                            on_retry(e, attempt + 1)

                        time.sleep(total_delay)
                    else:
                        logger.error(
                            f"函数 {func.__name__} 在 {max_retries + 1} 次尝试后仍然失败"
                        )

            raise last_exception

        return wrapper
    return decorator


def rate_limiter(calls_per_second: float = 1.0):
    """
    速率限制装饰器

    Args:
        calls_per_second: 每秒允许的调用次数

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        last_called = [0.0]

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_time = time.time()
            elapsed = current_time - last_called[0]
            min_interval = 1.0 / calls_per_second

            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                logger.debug(f"速率限制: 等待 {sleep_time:.2f} 秒")
                time.sleep(sleep_time)

            last_called[0] = time.time()
            return func(*args, **kwargs)

        return wrapper
    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception
):
    """
    熔断器装饰器

    Args:
        failure_threshold: 失败次数阈值
        recovery_timeout: 恢复超时时间
        expected_exception: 预期的异常类型

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        state = {
            'failure_count': 0,
            'last_failure_time': None,
            'state': 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        }

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_time = time.time()

            # 检查熔断器状态
            if state['state'] == 'OPEN':
                if current_time - state['last_failure_time'] > recovery_timeout:
                    state['state'] = 'HALF_OPEN'
                    logger.info(f"熔断器 {func.__name__} 进入半开状态")
                else:
                    raise Exception(f"熔断器 {func.__name__} 处于开启状态")

            try:
                result = func(*args, **kwargs)

                # 成功执行，重置失败计数
                if state['state'] == 'HALF_OPEN':
                    state['state'] = 'CLOSED'
                    state['failure_count'] = 0
                    logger.info(f"熔断器 {func.__name__} 恢复到关闭状态")

                return result

            except expected_exception as e:
                state['failure_count'] += 1
                state['last_failure_time'] = current_time

                logger.warning(
                    f"函数 {func.__name__} 执行失败 ({state['failure_count']}/{failure_threshold}): {e}"
                )

                if state['failure_count'] >= failure_threshold:
                    state['state'] = 'OPEN'
                    logger.error(f"熔断器 {func.__name__} 进入开启状态")

                raise e

        return wrapper
    return decorator


class AdaptiveRetry:
    """自适应重试类"""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.success_history = []

    def calculate_delay(self, attempt: int) -> float:
        """
        计算延迟时间，基于历史成功率自适应调整

        Args:
            attempt: 当前尝试次数

        Returns:
            延迟时间（秒）
        """
        base_delay = min(
            self.initial_delay * (self.backoff_factor ** attempt),
            self.max_delay
        )

        # 基于历史成功率调整延迟
        if len(self.success_history) >= 5:
            recent_success_rate = sum(self.success_history[-5:]) / 5
            if recent_success_rate > 0.8:
                base_delay *= 0.5  # 成功率高，减少延迟
            elif recent_success_rate < 0.3:
                base_delay *= 2.0  # 成功率低，增加延迟

        return base_delay

    def record_success(self):
        """记录成功执行"""
        self.success_history.append(1)
        if len(self.success_history) > 20:
            self.success_history.pop(0)

    def record_failure(self):
        """记录失败执行"""
        self.success_history.append(0)
        if len(self.success_history) > 20:
            self.success_history.pop(0)

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行函数并根据需要进行重试

        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            函数执行结果
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result

            except Exception as e:
                last_exception = e
                self.record_failure()

                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    logger.warning(
                        f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}. "
                        f"等待 {delay:.2f} 秒后重试..."
                    )
                    time.sleep(delay)

        raise last_exception


if __name__ == "__main__":
    # 示例用法
    logging.basicConfig(level=logging.INFO)

    @retry_on_failure(max_retries=3, delay=1.0)
    def unreliable_function(success_rate: float = 0.3) -> str:
        """模拟一个不稳定的函数"""
        import random
        if random.random() < success_rate:
            return "成功!"
        else:
            raise ValueError("随机失败")

    @rate_limiter(calls_per_second=0.5)
    def rate_limited_function() -> str:
        """模拟一个有速率限制的函数"""
        return f"执行时间: {time.time()}"

    try:
        print("测试重试机制:")
        result = unreliable_function()
        print(f"结果: {result}")

    except Exception as e:
        print(f"最终失败: {e}")

    print("\n测试速率限制:")
    for i in range(3):
        result = rate_limited_function()
        print(result)