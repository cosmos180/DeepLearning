"""
AI OCR识别模块

使用火山引擎视觉大模型识别收据图片，提取采购信息。
复用现有的视觉大模型demo代码。
"""

import asyncio
import io
import os
import sys
import re
import json
import logging
from pathlib import Path
from typing import Optional, Tuple
from datetime import date
from decimal import Decimal

logger = logging.getLogger(__name__)

try:
    from volcenginesdkarkruntime import AsyncArk
except ImportError:
    raise ImportError(
        "需要安装 volcenginesdkarkruntime: "
        "pip install volcenginesdkarkruntime"
    )

from . import PurchaseReceipt, PurchaseItem


# 复用demo.py中的FileWithProgress类
class FileWithProgress(io.IOBase):
    """带进度显示的文件包装类，继承自 io.IOBase"""

    def __init__(self, file_path: str):
        super().__init__()
        self.file = open(file_path, "rb")
        self.total_size = os.path.getsize(file_path)
        self.read_size = 0
        self.last_progress = -1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """关闭文件"""
        if hasattr(self, "file") and self.file:
            self.file.close()

    def readable(self) -> bool:
        """返回文件是否可读"""
        return True

    def read(self, size=-1):
        """读取文件数据并显示进度"""
        chunk = self.file.read(size)
        if chunk:
            self.read_size += len(chunk)
            self._display_progress()
        return chunk

    def _display_progress(self):
        """显示上传进度"""
        if self.total_size > 0:
            progress = int((self.read_size / self.total_size) * 100)
            if progress != self.last_progress:
                self.last_progress = progress
                bar_length = 40
                filled_length = int(bar_length * progress // 100)
                bar = "█" * filled_length + "-" * (bar_length - filled_length)
                size_mb = self.read_size / (1024 * 1024)
                total_mb = self.total_size / (1024 * 1024)

                sys.stdout.write(
                    f"\r  ↑ 上传中: [{bar}] {progress}% "
                    f"({size_mb:.1f}/{total_mb:.1f} MB)"
                )
                sys.stdout.flush()

                if progress == 100:
                    print()  # 完成时换行


# Prompt模板
RECEIPT_RECOGNITION_PROMPT = """你是一个专业的采购收据识别助手。请仔细分析这张收据图片，准确提取所有关键信息。

【重要提示】
1. 图片可能被旋转或倒置，请自动识别并正确解读所有内容
2. 以下字段必须100%准确：delivery_date（日期）、quantity（数量）、unit_price（单价）、amount（金额）
3. 金额可以通过 数量×单价 来验证，如果不一致请仔细核对

请提取以下信息并以JSON格式输出：

1. title: 主题标题（提取收据上的主题或商户名称，如"恒达图文数码快印"）

2. delivery_date: 交付日期（格式：YYYY-M-D，如2025-1-20）
   - 优先识别收据上的日期
   - 注意区分"开票日期"和"交付日期"
   - 如果是中文格式（2025年1月20日），请转换为YYYY-M-D

3. items: 商品清单数组，每个商品必须包含：
   - sequence: 序号（从1开始，按表格顺序）
   - name: 商品名称（完整名称，不要缩写）
   - spec: 规格型号（如果有，如"A4"、"8开"等）
   - unit: 单位（份、个、箱、本、套、张、支、包、kg等）
   - quantity: 数量（**务必准确**，纯数字）
   - unit_price: 单价（**务必准确**，纯数字，单位：元）
   - amount: 金额（**务必准确**，纯数字，单位：元）
   - remark: 备注（空字符串""如果没有）

4. confidence: 识别置信度（0-1之间，关键数据准确时给高置信度）

输出格式（只输出JSON，不要有其他文字）：
```json
{
  "title": "恒达图文数码快印",
  "delivery_date": "2025-1-20",
  "items": [
    {
      "sequence": 1,
      "name": "语文资料",
      "spec": "",
      "unit": "份",
      "quantity": 47,
      "unit_price": 6.0,
      "amount": 282.0,
      "remark": ""
    }
  ],
  "confidence": 0.95
}
```

【核对清单】
- 日期格式正确吗？YYYY-M-D格式
- 数量准确吗？与收据一致
- 单价准确吗？与收据一致
- 金额准确吗？验证：数量 × 单价 = 金额
- 单位正确吗？使用收据上的单位
"""


class AIRecognizer:
    """
    AI识别器

    使用火山引擎视觉大模型识别收据图片。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "doubao-seed-1-6-251015",
        timeout: int = 120,
    ):
        """
        初始化AI识别器

        Args:
            api_key: API密钥（默认从环境变量ARK_API_KEY读取）
            model: 模型名称
            timeout: 超时时间（秒）
        """
        self.api_key = api_key or os.getenv("ARK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API密钥未设置，请设置环境变量ARK_API_KEY或传入api_key参数"
            )

        self.model = model
        self.timeout = timeout
        self.client = AsyncArk(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=self.api_key,
        )

    async def recognize_receipt_async(
        self,
        image_path: str,
        title_hint: Optional[str] = None,
        date_hint: Optional[str] = None,
    ) -> Tuple[Optional[PurchaseReceipt], float]:
        """
        异步识别收据图片

        Args:
            image_path: 图片文件路径
            title_hint: 主题提示（可选）
            date_hint: 日期提示（可选）

        Returns:
            (收据数据, 置信度)
        """
        try:
            image_file = Path(image_path)
            if not image_file.exists():
                logger.error(f"文件不存在: {image_path}")
                return None, 0.0

            logger.info(f"开始识别收据: {image_file.name}")

            # 1. 上传图片
            logger.info("正在上传图片...")
            with FileWithProgress(image_path) as f:
                file = await self.client.files.create(  # type: ignore[arg-type]
                    file=f,
                    purpose="user_data",
                )
            logger.info(f"✓ 文件上传成功: {file.id}")

            # 2. 等待处理
            logger.info("正在等待文件处理完成...")
            await asyncio.wait_for(
                self.client.files.wait_for_processing(file.id),
                timeout=self.timeout,
            )
            logger.info(f"✓ 文件处理完成")

            # 3. 构建Prompt
            prompt = RECEIPT_RECOGNITION_PROMPT
            if title_hint:
                prompt += f"\n\n提示：主题可能包含 '{title_hint}'"
            if date_hint:
                prompt += f"\n\n提示：日期是 {date_hint}"

            # 4. 调用模型
            logger.info("正在调用模型识别...")
            response = await self.client.responses.create(  # type: ignore[arg-type]
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "file_id": file.id,
                            },
                            {
                                "type": "input_text",
                                "text": prompt,
                            },
                        ],
                    },
                ],
            )

            # 5. 解析响应
            logger.info("正在解析识别结果...")
            receipt, confidence = self._parse_response(response, image_path)

            logger.info(
                f"✓ 识别完成: 置信度={confidence:.2f}, "
                f"商品数={len(receipt.items)}, "
                f"总金额={receipt.total_amount:.2f}"
            )

            return receipt, confidence

        except asyncio.TimeoutError:
            logger.error(f"识别超时: {image_path}")
            return None, 0.0
        except Exception as e:
            logger.exception(f"识别失败: {image_path}")
            return None, 0.0

    def recognize_receipt(
        self,
        image_path: str,
        title_hint: Optional[str] = None,
        date_hint: Optional[str] = None,
    ) -> Tuple[Optional[PurchaseReceipt], float]:
        """
        同步识别收据图片（包装异步方法）

        Args:
            image_path: 图片文件路径
            title_hint: 主题提示（可选）
            date_hint: 日期提示（可选）

        Returns:
            (收据数据, 置信度)
        """
        return asyncio.run(
            self.recognize_receipt_async(image_path, title_hint, date_hint)
        )

    def _parse_response(
        self, response, source_file: str
    ) -> Tuple[PurchaseReceipt, float]:
        """
        解析模型响应

        Args:
            response: 模型响应 (Response 对象)
            source_file: 源文件路径

        Returns:
            (收据数据, 置信度)
        """
        # 从 Response 对象中提取文本内容
        response_text = ""

        # 先打印完整的响应结构用于调试
        logger.info(f"响应类型: {type(response)}")
        logger.info(f"响应属性: {dir(response)}")

        # 遍历 output 数组提取文本
        if hasattr(response, "output") and response.output:
            logger.info(f"输出数组长度: {len(response.output)}")
            for i, item in enumerate(response.output):
                logger.info(f"Output[{i}] 类型: {type(item)}, 属性: {dir(item)}")

                # 检查是否有 content 属性
                if hasattr(item, "content"):
                    logger.info(f"Output[{i}].content: {item.content}")
                    for content_item in item.content:
                        if hasattr(content_item, "text"):
                            response_text += content_item.text
                            logger.info(f"找到文本: {content_item.text[:100]}...")

                # 检查是否有 summary 属性 (推理步骤)
                if hasattr(item, "summary"):
                    logger.info(f"Output[{i}] 有 summary，跳过推理步骤")

                # 检查是否有 type 属性
                if hasattr(item, "type"):
                    logger.info(f"Output[{i}].type: {item.type}")

        # 如果没有提取到内容，使用原始方式
        if not response_text:
            logger.warning("未能从 output 中提取内容，使用 str(response)")
            response_text = str(response)

        logger.info(f"完整响应文本: {response_text}")

        # 查找完整的 JSON 对象（包含 items 数组）
        # 使用更精确的正则表达式匹配
        json_pattern = r'\{\s*"title".*?"items".*?\[\s*\{.*?\}\s*\].*?\}'
        json_match = re.search(json_pattern, response_text, re.DOTALL)

        if not json_match:
            # 尝试更宽松的匹配
            json_match = re.search(r'\{[\s\S]*?"title"[\s\S]*?\}', response_text)

        if not json_match:
            logger.error(f"无法从响应中提取完整JSON")
            logger.error(f"响应内容: {response_text}")
            raise ValueError("响应中未找到完整JSON数据，请检查 Prompt 格式要求")

        json_str = json_match.group()
        logger.info(f"提取的JSON: {json_str}")

        # 尝试解析JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"JSON内容: {json_str}")

            # 尝试清理和修复常见问题
            cleaned = json_str
            # 移除尾部逗号
            cleaned = re.sub(r',\s*}', '}', cleaned)
            cleaned = re.sub(r',\s*]', ']', cleaned)

            try:
                data = json.loads(cleaned)
            except json.JSONDecodeError as e2:
                logger.error(f"清理后仍然无法解析: {e2}")
                raise ValueError(f"JSON解析失败: {e}")

        # 解析标题
        title = data.get("title", "未命名采购")

        # 解析日期（处理 null 或缺失的情况）
        delivery_date_str = data.get("delivery_date")
        if not delivery_date_str:
            # 如果 AI 没有识别出日期，使用今天
            logger.warning("AI 未识别出日期，使用当前日期")
            delivery_date = date.today()
        else:
            delivery_date = self._parse_date(delivery_date_str)

        # 解析商品列表
        items_data = data.get("items", [])
        items = []
        for item_data in items_data:
            item = PurchaseItem(
                sequence=item_data.get("sequence", len(items) + 1),
                name=item_data.get("name", ""),
                spec=item_data.get("spec"),
                unit=item_data.get("unit", "个"),
                quantity=Decimal(str(item_data.get("quantity", 1))),
                unit_price=Decimal(str(item_data.get("unit_price", 0))),
                amount=Decimal(str(item_data.get("amount", 0))),
                remark=item_data.get("remark"),
            )
            items.append(item)

        # 解析置信度
        confidence = data.get("confidence", 0.8)

        # 创建收据
        receipt = PurchaseReceipt(
            title=title,
            delivery_date=delivery_date,
            items=items,
            recognition_method="ai",
            confidence=confidence,
            source_file=source_file,
        )

        return receipt, confidence

    def _parse_date(self, date_str: str) -> date:
        """
        解析日期字符串

        支持格式：
        - YYYY-M-D (如 2025-1-20)
        - YYYY-MM-DD (如 2025-01-20)
        - M-D (如 1-20，默认当前年份)

        Args:
            date_str: 日期字符串

        Returns:
            日期对象
        """
        # 尝试 YYYY-M-D 或 YYYY-MM-DD
        match = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", date_str)
        if match:
            year, month, day = match.groups()
            return date(int(year), int(month), int(day))

        # 尝试 M-D，默认当前年份
        match = re.match(r"(\d{1,2})-(\d{1,2})", date_str)
        if match:
            month, day = match.groups()
            today = date.today()
            return date(today.year, int(month), int(day))

        # 默认返回今天
        return date.today()


# 便捷函数
def recognize_receipt(
    image_path: str,
    api_key: Optional[str] = None,
    title_hint: Optional[str] = None,
    date_hint: Optional[str] = None,
) -> Tuple[Optional[PurchaseReceipt], float]:
    """
    识别收据图片（便捷函数）

    Args:
        image_path: 图片文件路径
        api_key: API密钥（默认从环境变量读取）
        title_hint: 主题提示
        date_hint: 日期提示

    Returns:
        (收据数据, 置信度)
    """
    recognizer = AIRecognizer(api_key=api_key)
    return recognizer.recognize_receipt(image_path, title_hint, date_hint)


async def recognize_receipt_async(
    image_path: str,
    api_key: Optional[str] = None,
    title_hint: Optional[str] = None,
    date_hint: Optional[str] = None,
) -> Tuple[Optional[PurchaseReceipt], float]:
    """
    异步识别收据图片（便捷函数）

    Args:
        image_path: 图片文件路径
        api_key: API密钥（默认从环境变量读取）
        title_hint: 主题提示
        date_hint: 日期提示

    Returns:
        (收据数据, 置信度)
    """
    recognizer = AIRecognizer(api_key=api_key)
    return await recognizer.recognize_receipt_async(image_path, title_hint, date_hint)
