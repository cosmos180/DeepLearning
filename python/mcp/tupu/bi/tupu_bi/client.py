"""
图普 BI API 客户端
封装与图普 BI API 的交互逻辑
"""
import re
from typing import Dict, Any
import httpx


class TupuBiClient:
    """图普 BI API 客户端"""

    # MAC 地址格式：xx:xx:xx:xx:xx:xx（6组十六进制，用冒号分隔）
    MAC_PATTERN = re.compile(r'^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}$')

    def __init__(self, base_url: str = "https://api.bi.tuputech.com"):
        self.base_url = base_url.rstrip("/")

    def _build_user_agent(self, device_id: str) -> str:
        """
        根据设备标识符类型构建正确的 User-Agent

        Args:
            device_id: 设备标识符，可能是 MAC 地址或序列号

        Returns:
            User-Agent 字符串，格式为 tupu-smart-endpoint:1.0/{type}_{id}
        """
        # 判断是否为 MAC 地址格式
        if self.MAC_PATTERN.match(device_id):
            return f"tupu-smart-endpoint:1.0/box_{device_id}"
        else:
            # 序列号格式
            return f"tupu-smart-endpoint:1.0/boxsn_{device_id}"

    async def get_camera_config(self, device_id: str) -> Dict[str, Any]:
        """
        获取摄像头基本参数配置

        Args:
            device_id: 设备标识符，支持 MAC 地址或序列号

        Returns:
            摄像头配置信息

        Raises:
            httpx.HTTPError: HTTP 请求失败
        """
        url = f"{self.base_url}/v1/inner/camera/config/json"
        headers = {
            "user-agent": self._build_user_agent(device_id),
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, json={})
            response.raise_for_status()
            return response.json()

    def get_camera_config_sync(self, device_id: str) -> Dict[str, Any]:
        """
        同步方式获取摄像头基本参数配置

        Args:
            device_id: 设备标识符，支持 MAC 地址或序列号

        Returns:
            摄像头配置信息
        """
        url = f"{self.base_url}/v1/inner/camera/config/json"
        headers = {
            "user-agent": self._build_user_agent(device_id),
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers, json={})
            response.raise_for_status()
            return response.json()

    async def get_auth_token(
        self, token_id: str, secret: str, expires_in: int = 7200
    ) -> Dict[str, Any]:
        """
        获取认证 Token

        Args:
            token_id: Token ID（URL 路径参数）
            secret: 认证密钥（敏感信息，不记录日志）
            expires_in: 过期时间（秒），默认 7200

        Returns:
            Token 信息

        Raises:
            httpx.HTTPError: HTTP 请求失败

        Security Note:
            secret 参数仅在请求中使用，不会被记录到日志
        """
        url = f"{self.base_url}/v1/auth/token/{token_id}"
        headers = {"Content-Type": "application/json"}

        payload = {"secret": secret, "expiresIn": expires_in}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    def get_auth_token_sync(
        self, token_id: str, secret: str, expires_in: int = 7200
    ) -> Dict[str, Any]:
        """
        同步方式获取认证 Token

        Args:
            token_id: Token ID（URL 路径参数）
            secret: 认证密钥（敏感信息，不记录日志）
            expires_in: 过期时间（秒），默认 7200

        Returns:
            Token 信息
        """
        url = f"{self.base_url}/v1/auth/token/{token_id}"
        headers = {"Content-Type": "application/json"}

        payload = {"secret": secret, "expiresIn": expires_in}

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
