"""
图普 BI API 客户端
封装与图普 BI API 的交互逻辑
"""
import re
import json
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
            response = await client.get(url, headers=headers)
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
            response = client.get(url, headers=headers)
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

    async def get_customer_info(self, uid: str, token: str) -> Dict[str, Any]:
        """
        获取客户信息

        Args:
            uid: 客户 UID（URL 路径参数）
            token: 认证 Token（请求头）

        Returns:
            客户信息

        Raises:
            httpx.HTTPError: HTTP 请求失败
        """
        url = f"{self.base_url}/v1/customer/{uid}"
        headers = {
            "token": token,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    def get_customer_info_sync(self, uid: str, token: str) -> Dict[str, Any]:
        """
        同步方式获取客户信息

        Args:
            uid: 客户 UID（URL 路径参数）
            token: 认证 Token（请求头）

        Returns:
            客户信息
        """
        url = f"{self.base_url}/v1/customer/{uid}"
        headers = {
            "token": token,
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_store_info(self, sid: str, uid: str, token: str) -> Dict[str, Any]:
        """
        获取门店信息

        Args:
            sid: 门店 SID（URL 路径参数）
            uid: 客户 UID（查询参数）
            token: 认证 Token（请求头）

        Returns:
            门店信息

        Raises:
            httpx.HTTPError: HTTP 请求失败
        """
        url = f"{self.base_url}/v1/store/{sid}"
        params = {"UID": uid}
        headers = {
            "token": token,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

    def get_store_info_sync(self, sid: str, uid: str, token: str) -> Dict[str, Any]:
        """
        同步方式获取门店信息

        Args:
            sid: 门店 SID（URL 路径参数）
            uid: 客户 UID（查询参数）
            token: 认证 Token（请求头）

        Returns:
            门店信息
        """
        url = f"{self.base_url}/v1/store/{sid}"
        params = {"UID": uid}
        headers = {
            "token": token,
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_device_full_info(
        self, device_id: str, token_id: str, secret: str, expires_in: int = 7200
    ) -> Dict[str, Any]:
        """
        获取设备完整信息（整合接口）

        流程：
        1. 获取摄像头配置（包含 UID 和 SID）
        2. 获取认证 Token
        3. 获取客户信息
        4. 获取门店信息

        Args:
            device_id: 设备标识符，支持 MAC 地址或序列号
            token_id: Token ID（用于获取认证 Token）
            secret: 认证密钥
            expires_in: Token 过期时间（秒），默认 7200

        Returns:
            整合后的完整信息，包含：
            - device_id: 硬件 ID
            - camera_config: 摄像头配置
            - customer_info: 客户信息
            - store_info: 门店信息

        Raises:
            httpx.HTTPError: HTTP 请求失败
        """
        # 1. 获取摄像头配置
        camera_config = await self.get_camera_config(device_id)

        # 从配置中提取 UID 和 SID
        # camera_config 的 data 字段是一个 JSON 字符串，需要解析
        uid = None
        sid = None

        data_field = camera_config.get("data")
        if data_field:
            try:
                config_data = json.loads(data_field) if isinstance(data_field, str) else data_field
                uid = config_data.get("UID")
                sid = config_data.get("SID")
            except (json.JSONDecodeError, TypeError):
                pass

        # 2. 获取认证 Token
        token_result = await self.get_auth_token(token_id, secret, expires_in)
        token = token_result.get("token")

        result = {
            "device_id": device_id,
            "camera_config": camera_config,
            "token_info": {
                "expiresIn": token_result.get("expiresIn", expires_in),
                "_note": "token 已用于获取客户和门店信息"
            }
        }

        # 3. 获取客户信息（如果有 UID）
        if uid:
            customer_info = await self.get_customer_info(uid, token)
            result["customer_info"] = customer_info
        else:
            result["customer_info"] = None
            result["_warning"] = "camera_config 中未找到 UID，跳过客户信息获取"

        # 4. 获取门店信息（如果有 SID 和 UID）
        if sid and uid:
            store_info = await self.get_store_info(sid, uid, token)
            result["store_info"] = store_info
        elif not sid:
            if "_warning" in result:
                result["_warning"] += "; 未找到 SID，跳过门店信息获取"
            else:
                result["_warning"] = "camera_config 中未找到 SID，跳过门店信息获取"

        return result

    def get_device_full_info_sync(
        self, device_id: str, token_id: str, secret: str, expires_in: int = 7200
    ) -> Dict[str, Any]:
        """
        同步方式获取设备完整信息（整合接口）

        流程：
        1. 获取摄像头配置（包含 UID 和 SID）
        2. 获取认证 Token
        3. 获取客户信息
        4. 获取门店信息

        Args:
            device_id: 设备标识符，支持 MAC 地址或序列号
            token_id: Token ID（用于获取认证 Token）
            secret: 认证密钥
            expires_in: Token 过期时间（秒），默认 7200

        Returns:
            整合后的完整信息，包含：
            - device_id: 硬件 ID
            - camera_config: 摄像头配置
            - customer_info: 客户信息
            - store_info: 门店信息
        """
        # 1. 获取摄像头配置
        camera_config = self.get_camera_config_sync(device_id)

        # 从配置中提取 UID 和 SID
        # camera_config 的 data 字段是一个 JSON 字符串，需要解析
        uid = None
        sid = None

        data_field = camera_config.get("data")
        if data_field:
            try:
                config_data = json.loads(data_field) if isinstance(data_field, str) else data_field
                uid = config_data.get("UID")
                sid = config_data.get("SID")
            except (json.JSONDecodeError, TypeError):
                pass

        # 2. 获取认证 Token
        token_result = self.get_auth_token_sync(token_id, secret, expires_in)
        token = token_result.get("token")

        result = {
            "device_id": device_id,
            "camera_config": camera_config,
            "token_info": {
                "expiresIn": token_result.get("expiresIn", expires_in),
                "_note": "token 已用于获取客户和门店信息"
            }
        }

        # 3. 获取客户信息（如果有 UID）
        if uid:
            customer_info = self.get_customer_info_sync(uid, token)
            result["customer_info"] = customer_info
        else:
            result["customer_info"] = None
            result["_warning"] = "camera_config 中未找到 UID，跳过客户信息获取"

        # 4. 获取门店信息（如果有 SID 和 UID）
        if sid and uid:
            store_info = self.get_store_info_sync(sid, uid, token)
            result["store_info"] = store_info
        elif not sid:
            if "_warning" in result:
                result["_warning"] += "; 未找到 SID，跳过门店信息获取"
            else:
                result["_warning"] = "camera_config 中未找到 SID，跳过门店信息获取"

        return result
