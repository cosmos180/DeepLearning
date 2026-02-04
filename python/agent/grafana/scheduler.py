#!/usr/bin/env python3
"""
Grafana 告警定时任务调度器

支持以下调度方式:
- 每天固定时间执行 (默认 09:00)
- 按间隔执行 (每 N 小时/分钟)
- 启动时立即执行

环境变量:
    ALERT_SCHEDULE_TIME: 每天执行时间 (默认: 09:00)
    ALERT_INTERVAL_HOURS: 每隔 N 小时执行 (覆盖 ALERT_SCHEDULE_TIME)
    RUN_ON_START: 启动时立即执行 (默认: false)
    TIME_RANGE: 告警时间范围 (默认: today)
"""
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

import schedule

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.alert_email_reporter import send_alert_report_email

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def get_env_int(name: str, default: int = None) -> int:
    """获取环境变量并转换为整数"""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(f"环境变量 {name} 值无效: {value}，使用默认值 {default}")
        return default


def send_scheduled_alert():
    """
    发送定时告警邮件

    从环境变量读取配置:
        TIME_RANGE: 时间范围 (today, 1h, 6h, 24h, 7d)
        ALERT_PLATFORMS: 指定平台，逗号分隔
    """
    time_range = os.getenv("TIME_RANGE", "today")
    platforms = os.getenv("ALERT_PLATFORMS", "")

    logger.info("=" * 70)
    logger.info(f"开始执行定时任务: 发送告警邮件")
    logger.info(f"时间范围: {time_range}")
    if platforms:
        logger.info(f"指定平台: {platforms}")
    logger.info("=" * 70)

    try:
        result = send_alert_report_email(
            platforms=platforms if platforms else None,
            time_range=time_range
        )
        logger.info("任务完成")
        logger.info(result)
    except Exception as e:
        logger.error(f"任务失败: {e}", exc_info=True)


def setup_schedule():
    """
    配置定时任务

    优先级:
    1. ALERT_INTERVAL_HOURS - 按小时间隔执行
    2. ALERT_SCHEDULE_TIME - 每天固定时间执行
    """
    interval_hours = get_env_int("ALERT_INTERVAL_HOURS")
    schedule_time = os.getenv("ALERT_SCHEDULE_TIME", "09:00")

    if interval_hours and interval_hours > 0:
        # 按间隔执行
        logger.info(f"调度模式: 每 {interval_hours} 小时执行一次")
        schedule.every(interval_hours).hours.do(send_scheduled_alert)
    else:
        # 每天固定时间执行
        logger.info(f"调度模式: 每天 {schedule_time} 执行")
        schedule.every().day.at(schedule_time).do(send_scheduled_alert)


def main():
    """主函数"""
    # 读取配置
    run_on_start = os.getenv("RUN_ON_START", "false").lower() in ("true", "1", "yes", "on")
    loop_interval = get_env_int("SCHEDULER_LOOP_INTERVAL", 60)

    logger.info("=" * 70)
    logger.info("Grafana 告警定时调度器已启动")
    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"检查间隔: {loop_interval} 秒")
    logger.info("=" * 70)

    # 设置定时任务
    setup_schedule()

    # 可选：启动时立即执行一次
    if run_on_start:
        logger.info("RUN_ON_START=true，启动时立即执行一次...")
        send_scheduled_alert()
        logger.info("初始任务执行完成，进入定时调度循环")
    else:
        logger.info("等待定时任务触发...")

    # 主循环
    try:
        while True:
            schedule.run_pending()
            time.sleep(loop_interval)
    except KeyboardInterrupt:
        logger.info("\n收到中断信号，调度器已停止")
        sys.exit(0)


if __name__ == "__main__":
    main()
