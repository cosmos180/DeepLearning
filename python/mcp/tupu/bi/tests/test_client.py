"""
TupuBiClient 真实 API 集成测试

测试需要配置以下环境变量：
- TUPI_BI_API_BASE: API 基础地址（可选，默认为 https://api.bi.tuputech.com）
- TUPI_BI_AUTH_SECRET: 认证密钥（必填）
- TUPI_BI_TEST_TOKEN_ID: 测试用 Token ID（必填）
- TUPI_BI_TEST_DEVICE_MAC: 测试用设备 MAC 地址（必填）
- TUPI_BI_TEST_DEVICE_SERIAL: 测试用设备序列号（必填）

运行测试：
export TUPI_BI_AUTH_SECRET="your-secret"
export TUPI_BI_TEST_TOKEN_ID="your-token-id"
export TUPI_BI_TEST_DEVICE_MAC="aa:bb:cc:dd:ee:ff"
export TUPI_BI_TEST_DEVICE_SERIAL="your-serial-number"
pytest tests/ -v
"""
import os
import pytest

import httpx

from tupu_bi.client import TupuBiClient


# 从环境变量获取测试配置
API_BASE = os.getenv("TUPI_BI_API_BASE", "https://api.bi.tuputech.com")
AUTH_SECRET = os.getenv("TUPI_BI_AUTH_SECRET")
TEST_TOKEN_ID = os.getenv("TUPI_BI_TEST_TOKEN_ID")
TEST_DEVICE_MAC = os.getenv("TUPI_BI_TEST_DEVICE_MAC")
TEST_DEVICE_SERIAL = os.getenv("TUPI_BI_TEST_DEVICE_SERIAL")


def skip_if_no_env():
    """如果缺少环境变量则跳过测试"""
    missing = []
    if not AUTH_SECRET:
        missing.append("TUPI_BI_AUTH_SECRET")
    if not TEST_TOKEN_ID:
        missing.append("TUPI_BI_TEST_TOKEN_ID")
    if not TEST_DEVICE_MAC:
        missing.append("TUPI_BI_TEST_DEVICE_MAC")
    if not TEST_DEVICE_SERIAL:
        missing.append("TUPI_BI_TEST_DEVICE_SERIAL")

    if missing:
        return f"缺少环境变量: {', '.join(missing)}"
    return None


class TestTupuBiClientMACPattern:
    """测试 MAC 地址模式匹配"""

    def test_valid_mac_address(self):
        """测试有效的 MAC 地址格式"""
        client = TupuBiClient()
        # 小写 MAC 地址
        assert client.MAC_PATTERN.match("aa:bb:cc:dd:ee:ff")
        # 大写 MAC 地址
        assert client.MAC_PATTERN.match("AA:BB:CC:DD:EE:FF")
        # 混合大小写
        assert client.MAC_PATTERN.match("Aa:Bb:Cc:Dd:Ee:Ff")

    def test_invalid_mac_address(self):
        """测试无效的 MAC 地址格式"""
        client = TupuBiClient()
        # 缺少分隔符
        assert not client.MAC_PATTERN.match("aabbccddeeff")
        # 分隔符错误
        assert not client.MAC_PATTERN.match("aa-bb-cc-dd-ee-ff")
        # 格式不完整
        assert not client.MAC_PATTERN.match("aa:bb:cc:dd:ee")
        # 非十六进制字符
        assert not client.MAC_PATTERN.match("gg:hh:ii:jj:kk:ll")

    def test_serial_number_patterns(self):
        """测试序列号格式（不应匹配 MAC 模式）"""
        client = TupuBiClient()
        # 典型序列号
        assert not client.MAC_PATTERN.match("6AB2F0C3E97DD45610FE4C45EA1E71B1")
        assert not client.MAC_PATTERN.match("12345678")


class TestBuildUserAgent:
    """测试 User-Agent 构建逻辑"""

    def test_mac_address_user_agent(self):
        """测试 MAC 地址构建的 User-Agent"""
        client = TupuBiClient()
        mac = "a8:3f:a1:30:16:fb"
        expected = "tupu-smart-endpoint:1.0/box_a8:3f:a1:30:16:fb"
        assert client._build_user_agent(mac) == expected

    def test_serial_number_user_agent(self):
        """测试序列号构建的 User-Agent"""
        client = TupuBiClient()
        serial = "6AB2F0C3E97DD45610FE4C45EA1E71B1"
        expected = "tupu-smart-endpoint:1.0/boxsn_6AB2F0C3E97DD45610FE4C45EA1E71B1"
        assert client._build_user_agent(serial) == expected


@pytest.mark.integration
class TestGetCameraConfig:
    """测试 get_camera_config 真实 API 调用"""

    @pytest.mark.asyncio
    async def test_get_camera_config_with_mac(self):
        """测试使用 MAC 地址获取摄像头配置（异步）"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        client = TupuBiClient(base_url=API_BASE)
        result = await client.get_camera_config(TEST_DEVICE_MAC)

        # 验证返回数据结构
        assert isinstance(result, dict)
        print(f"\n摄像头配置响应: {result}")

    @pytest.mark.asyncio
    async def test_get_camera_config_with_serial(self):
        """测试使用序列号获取摄像头配置（异步）"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        client = TupuBiClient(base_url=API_BASE)
        result = await client.get_camera_config(TEST_DEVICE_SERIAL)

        # 验证返回数据结构
        assert isinstance(result, dict)
        print(f"\n摄像头配置响应: {result}")

    @pytest.mark.asyncio
    async def test_get_camera_config_invalid_device(self):
        """测试无效设备标识符的错误处理"""
        client = TupuBiClient(base_url=API_BASE)

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_camera_config("invalid:device:id")

    def test_get_camera_config_sync(self):
        """测试同步方式获取摄像头配置"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        client = TupuBiClient(base_url=API_BASE)
        result = client.get_camera_config_sync(TEST_DEVICE_MAC)

        # 验证返回数据结构
        assert isinstance(result, dict)
        print(f"\n摄像头配置响应: {result}")


@pytest.mark.integration
class TestGetAuthToken:
    """测试 get_auth_token 真实 API 调用"""

    @pytest.mark.asyncio
    async def test_get_auth_token_success(self):
        """测试成功获取认证 Token"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        client = TupuBiClient(base_url=API_BASE)
        result = await client.get_auth_token(
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET,
            expires_in=3600
        )

        # 验证返回数据
        assert isinstance(result, dict)
        assert "token" in result
        print(f"\nToken 响应: {result}")

    @pytest.mark.asyncio
    async def test_get_auth_token_default_expires(self):
        """测试使用默认过期时间"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        client = TupuBiClient(base_url=API_BASE)
        result = await client.get_auth_token(
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )

        # 验证返回数据
        assert isinstance(result, dict)
        assert "token" in result
        print(f"\nToken 响应: {result}")

    @pytest.mark.asyncio
    async def test_get_auth_token_invalid_credentials(self):
        """测试无效认证信息的错误处理"""
        client = TupuBiClient(base_url=API_BASE)

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_auth_token(
                token_id="invalid-token-id",
                secret="invalid-secret"
            )

    def test_get_auth_token_sync(self):
        """测试同步方式获取认证 Token"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        client = TupuBiClient(base_url=API_BASE)
        result = client.get_auth_token_sync(
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )

        # 验证返回数据
        assert isinstance(result, dict)
        assert "token" in result
        print(f"\nToken 响应: {result}")


@pytest.mark.integration
class TestGetCustomerInfo:
    """测试 get_customer_info 真实 API 调用"""

    @pytest.mark.asyncio
    async def test_get_customer_info_success(self):
        """测试成功获取客户信息"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        # 先获取 token
        client = TupuBiClient(base_url=API_BASE)
        token_result = await client.get_auth_token(
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )
        token = token_result.get("token")

        # 使用 token 获取客户信息
        test_uid = os.getenv("TUPI_BI_TEST_CUSTOMER_UID", "682ffb703953c231e8cc46a7")

        result = await client.get_customer_info(test_uid, token)

        # 验证返回数据
        assert isinstance(result, dict)
        print(f"\n客户信息响应: {result}")

    @pytest.mark.asyncio
    async def test_get_customer_info_invalid_uid(self):
        """测试无效 UID 的错误处理"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        # 先获取 token
        client = TupuBiClient(base_url=API_BASE)
        token_result = await client.get_auth_token(
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )
        token = token_result.get("token")

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_customer_info("invalid-uid", token)

    @pytest.mark.asyncio
    async def test_get_customer_info_invalid_token(self):
        """测试无效 Token 的错误处理"""
        client = TupuBiClient(base_url=API_BASE)

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_customer_info("682ffb703953c231e8cc46a7", "invalid-token")

    def test_get_customer_info_sync(self):
        """测试同步方式获取客户信息"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        # 先获取 token
        client = TupuBiClient(base_url=API_BASE)
        token_result = client.get_auth_token_sync(
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )
        token = token_result.get("token")

        test_uid = os.getenv("TUPI_BI_TEST_CUSTOMER_UID", "682ffb703953c231e8cc46a7")

        result = client.get_customer_info_sync(test_uid, token)

        # 验证返回数据
        assert isinstance(result, dict)
        print(f"\n客户信息响应: {result}")


@pytest.mark.integration
class TestGetStoreInfo:
    """测试 get_store_info 真实 API 调用"""

    @pytest.mark.asyncio
    async def test_get_store_info_success(self):
        """测试成功获取门店信息"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        # 先获取 token
        client = TupuBiClient(base_url=API_BASE)
        token_result = await client.get_auth_token(
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )
        token = token_result.get("token")

        # 使用 token 获取门店信息
        test_uid = os.getenv("TUPI_BI_TEST_CUSTOMER_UID", "682ffb703953c231e8cc46a7")
        test_sid = os.getenv("TUPI_BI_TEST_STORE_SID", "682ffbae23e8639b53ec6aad")

        result = await client.get_store_info(test_sid, test_uid, token)

        # 验证返回数据
        assert isinstance(result, dict)
        print(f"\n门店信息响应: {result}")

    @pytest.mark.asyncio
    async def test_get_store_info_invalid_sid(self):
        """测试无效 SID 的错误处理"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        # 先获取 token
        client = TupuBiClient(base_url=API_BASE)
        token_result = await client.get_auth_token(
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )
        token = token_result.get("token")

        test_uid = os.getenv("TUPI_BI_TEST_CUSTOMER_UID", "682ffb703953c231e8cc46a7")

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_store_info("invalid-sid", test_uid, token)

    @pytest.mark.asyncio
    async def test_get_store_info_invalid_token(self):
        """测试无效 Token 的错误处理"""
        client = TupuBiClient(base_url=API_BASE)

        with pytest.raises(httpx.HTTPStatusError):
            await client.get_store_info("682ffbae23e8639b53ec6aad", "682ffb703953c231e8cc46a7", "invalid-token")

    def test_get_store_info_sync(self):
        """测试同步方式获取门店信息"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        # 先获取 token
        client = TupuBiClient(base_url=API_BASE)
        token_result = client.get_auth_token_sync(
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )
        token = token_result.get("token")

        test_uid = os.getenv("TUPI_BI_TEST_CUSTOMER_UID", "682ffb703953c231e8cc46a7")
        test_sid = os.getenv("TUPI_BI_TEST_STORE_SID", "682ffbae23e8639b53ec6aad")

        result = client.get_store_info_sync(test_sid, test_uid, token)

        # 验证返回数据
        assert isinstance(result, dict)
        print(f"\n门店信息响应: {result}")


@pytest.mark.integration
class TestGetDeviceFullInfo:
    """测试 get_device_full_info 真实 API 调用（整合接口）"""

    @pytest.mark.asyncio
    async def test_get_device_full_info_success(self):
        """测试成功获取设备完整信息（整合接口）"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        client = TupuBiClient(base_url=API_BASE)

        # 使用 MAC 地址或序列号
        test_device_id = TEST_DEVICE_MAC  # 或 TEST_DEVICE_SERIAL

        result = await client.get_device_full_info(
            device_id=test_device_id,
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )

        # 验证返回数据结构
        assert isinstance(result, dict)
        assert "device_id" in result
        assert "camera_config" in result
        assert "customer_info" in result
        assert "store_info" in result
        assert "token_info" in result

        # 验证设备 ID 匹配
        assert result["device_id"] == test_device_id

        print(f"\n设备完整信息响应:")
        print(f"  设备 ID: {result.get('device_id')}")
        print(f"  客户名称: {result.get('customer_info', {}).get('name')}")
        print(f"  门店名称: {result.get('store_info', {}).get('name')}")
        print(f"  警告信息: {result.get('_warning', '无')}")

    @pytest.mark.asyncio
    async def test_get_device_full_info_missing_device_id(self):
        """测试缺少 device_id 参数时的错误处理"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        client = TupuBiClient(base_url=API_BASE)

        with pytest.raises(httpx.HTTPStatusError):
            # 无效 device_id 会触发 HTTP 错误
            await client.get_device_full_info(
                device_id="",  # 空字符串
                token_id=TEST_TOKEN_ID,
                secret=AUTH_SECRET
            )

    def test_get_device_full_info_sync(self):
        """测试同步方式获取设备完整信息（整合接口）"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        client = TupuBiClient(base_url=API_BASE)

        test_device_id = TEST_DEVICE_MAC
        test_device_id = TEST_DEVICE_SERIAL

        result = client.get_device_full_info_sync(
            device_id=test_device_id,
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )

        # 验证返回数据结构
        assert isinstance(result, dict)
        assert "device_id" in result
        assert "camera_config" in result
        assert "customer_info" in result
        assert "store_info" in result

        print(f"\n同步获取设备完整信息:")
        print(f"  设备 ID: {result.get('device_id')}")
        print(f"  客户名称: {result.get('customer_info', {}).get('name')}")
        print(f"  门店名称: {result.get('store_info', {}).get('name')}")
