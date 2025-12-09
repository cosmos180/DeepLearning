import asyncio
import os
import sys
from pathlib import Path

from volcenginesdkarkruntime import AsyncArk

# API客户端配置
client = AsyncArk(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.getenv("ARK_API_KEY"),
)

# Prompt常量定义
VIDEO_ANALYSIS_PROMPT = """这个视频是大型超市自助收银台顾客自助买单的场景。
在顾客买单过程中，经常有一些商品没有被手动拿起对准扫码枪扫描，导致录入系统过程中出现了遗漏的情况，请你务必仔细检查，以JSON格式输出：
- 商品名称
- 商品数量
- 是否扫码

已经扫码的也需要列出来，用于后续和收银系统校验。
"""


async def process_video(video_path: str):
    """处理单个视频文件"""
    try:
        video_file = Path(video_path)
        if not video_file.exists():
            print(f"错误: 文件不存在: {video_path}")
            return None

        if not video_file.is_file():
            print(f"错误: 路径不是文件: {video_path}")
            return None

        print(f"\n{'=' * 60}")
        print(f"开始处理文件: {video_file.name}")
        print(f"{'=' * 60}")

        # upload video file
        print(f"正在上传视频文件: {video_path}")
        with open(video_path, "rb") as f:
            file = await client.files.create(
                file=f,
                purpose="user_data",
                preprocess_configs={
                    "video": {
                        "fps": 1.0,  # define the sampling fps of the video, default is 1.0
                    }
                },
            )
        print(f"✓ 文件上传成功: {file.id}")

        # Wait for the file to finish processing
        print(f"正在等待文件处理完成...")
        await client.files.wait_for_processing(file.id)
        print(f"✓ 文件处理完成: {file.id}")

        # 调用模型分析
        print(f"正在调用模型进行分析...")
        response = await client.responses.create(
            model="doubao-seed-1-6-251015",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_video",
                            "file_id": file.id,  # ref video file id
                        },
                        {
                            "type": "input_text",
                            "text": VIDEO_ANALYSIS_PROMPT,
                        },
                    ],
                },
            ],
        )

        print(f"\n✓ 分析完成:")
        print(f"{'-' * 60}")
        print(
            response.output_text if hasattr(response, "output_text") else str(response)
        )
        print(f"{'-' * 60}")

        return response

    except Exception as e:
        print(f"\n✗ 处理文件时出错 {video_path}: {str(e)}")
        return None


async def main():
    # 获取命令行参数
    if len(sys.argv) < 2:
        print("用法: python demo.py <视频文件1> <视频文件2> ...")
        print("\n示例:")
        print("  python demo.py video1.mp4")
        print("  python demo.py video1.mp4 video2.mp4 video3.mp4")
        print("  python demo.py /path/to/videos/*.mp4")
        sys.exit(1)

    video_paths = sys.argv[1:]
    print(f"准备处理 {len(video_paths)} 个视频文件...")

    # 处理所有视频文件
    results = []
    for video_path in video_paths:
        result = await process_video(video_path)
        results.append(result)

    # 统计结果
    successful = sum(1 for r in results if r is not None)
    print(f"\n{'=' * 60}")
    print(f"处理完成: 成功 {successful}/{len(video_paths)} 个文件")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
