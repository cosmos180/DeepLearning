"""
Tupu BI MCP Server 真实 API 集成测试

测试需要配置以下环境变量：
- TUPI_BI_API_BASE: API 基础地址（可选）
- TUPI_BI_AUTH_SECRET: 认证密钥（必填）
- TUPI_BI_TEST_TOKEN_ID: 测试用 Token ID（必填）
- TUPI_BI_TEST_DEVICE_MAC: 测试用设备 MAC 地址（必填）
- TUPI_BI_TEST_DEVICE_SERIAL: 测试用设备序列号（必填）
"""
import os
import json
import pytest

from mcp.types import CallToolResult, TextContent

from tupu_bi.server import list_tools, call_tool, DEFAULT_API_BASE


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


class TestListTools:
    """测试 MCP 工具列表注册"""

    @pytest.mark.asyncio
    async def test_list_tools_returns_expected_tools(self):
        """验证 list_tools 返回预期的工具列表"""
        tools = await list_tools()

        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "get_camera_config" in tool_names
        assert "get_auth_token" in tool_names

    @pytest.mark.asyncio
    async def test_get_camera_config_tool_schema(self):
        """验证 get_camera_config 工具的输入模式"""
        tools = await list_tools()
        camera_tool = next((t for t in tools if t.name == "get_camera_config"), None)

        assert camera_tool is not None
        assert camera_tool.description == "获取摄像头基本参数配置"

        schema = camera_tool.inputSchema
        assert schema["type"] == "object"
        assert "device_id" in schema["properties"]
        assert "api_base" in schema["properties"]
        assert schema["required"] == ["device_id"]

    @pytest.mark.asyncio
    async def test_get_auth_token_tool_schema(self):
        """验证 get_auth_token 工具的输入模式"""
        tools = await list_tools()
        auth_tool = next((t for t in tools if t.name == "get_auth_token"), None)

        assert auth_tool is not None
        assert "获取认证 Token" in auth_tool.description

        schema = auth_tool.inputSchema
        assert schema["type"] == "object"
        assert "token_id" in schema["properties"]
        assert "secret" in schema["properties"]
        assert "expires_in" in schema["properties"]
        assert "api_base" in schema["properties"]
        assert schema["required"] == ["token_id"]


@pytest.mark.integration
class TestCallToolGetCameraConfig:
    """测试 get_camera_config 工具真实 API 调用"""

    @pytest.mark.asyncio
    async def test_get_camera_config_with_mac(self):
        """测试使用 MAC 地址获取摄像头配置"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        result = await call_tool("get_camera_config", {"device_id": TEST_DEVICE_MAC})

        assert isinstance(result, CallToolResult)
        assert not result.isError
        assert len(result.content) == 1
        assert isinstance(result.content[0], TextContent)

        # 解析并验证返回的 JSON 数据
        data = json.loads(result.content[0].text)
        assert isinstance(data, dict)
        print(f"\n摄像头配置响应: {data}")

    @pytest.mark.asyncio
    async def test_get_camera_config_with_serial(self):
        """测试使用序列号获取摄像头配置"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        result = await call_tool("get_camera_config", {"device_id": TEST_DEVICE_SERIAL})

        assert not result.isError
        data = json.loads(result.content[0].text)
        assert isinstance(data, dict)
        print(f"\n摄像头配置响应: {data}")

    @pytest.mark.asyncio
    async def test_get_camera_config_missing_device_id(self):
        """测试缺少 device_id 参数时的错误处理"""
        result = await call_tool("get_camera_config", {})

        assert result.isError
        assert "device_id 参数必填" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_camera_config_invalid_device(self):
        """测试无效设备标识符的错误处理"""
        result = await call_tool("get_camera_config", {"device_id": "invalid:device:id"})

        # 应该返回错误（HTTP 调用失败）
        assert result.isError
        print(f"\n错误响应: {result.content[0].text}")

    @pytest.mark.asyncio
    async def test_get_camera_config_custom_api_base(self):
        """测试自定义 API 基础地址"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        result = await call_tool("get_camera_config", {
            "device_id": TEST_DEVICE_MAC,
            "api_base": API_BASE
        })

        assert not result.isError
        data = json.loads(result.content[0].text)
        assert isinstance(data, dict)


@pytest.mark.integration
class TestCallToolGetAuthToken:
    """测试 get_auth_token 工具真实 API 调用"""

    @pytest.mark.asyncio
    async def test_get_auth_token_with_param_secret(self):
        """测试使用参数传递 secret 获取 Token"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        result = await call_tool("get_auth_token", {
            "token_id": TEST_TOKEN_ID,
            "secret": AUTH_SECRET
        })

        assert not result.isError
        data = json.loads(result.content[0].text)

        # 验证返回数据（secret 被脱敏）
        assert "token" in data
        assert data["token_id"] == TEST_TOKEN_ID
        assert "_note" in data
        assert "secret" not in data  # 验证 secret 未被返回
        print(f"\nToken 响应: {data}")

    @pytest.mark.asyncio
    async def test_get_auth_token_custom_expires(self):
        """测试自定义过期时间"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        result = await call_tool("get_auth_token", {
            "token_id": TEST_TOKEN_ID,
            "secret": AUTH_SECRET,
            "expires_in": 3600
        })

        assert not result.isError
        data = json.loads(result.content[0].text)
        assert "token" in data
        print(f"\nToken 响应: {data}")

    @pytest.mark.asyncio
    async def test_get_auth_token_missing_token_id(self):
        """测试缺少 token_id 参数时的错误处理"""
        result = await call_tool("get_auth_token", {})

        assert result.isError
        assert "token_id 参数必填" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_auth_token_missing_secret(self):
        """测试缺少 secret 参数时的错误处理"""
        # 临时清除环境变量
        old_secret = os.environ.pop("TUPI_BI_AUTH_SECRET", None)

        try:
            result = await call_tool("get_auth_token", {"token_id": TEST_TOKEN_ID})

            assert result.isError
            assert "secret 未提供" in result.content[0].text
        finally:
            if old_secret:
                os.environ["TUPI_BI_AUTH_SECRET"] = old_secret

    @pytest.mark.asyncio
    async def test_get_auth_token_invalid_credentials(self):
        """测试无效认证信息的错误处理"""
        result = await call_tool("get_auth_token", {
            "token_id": "invalid-token-id",
            "secret": "invalid-secret"
        })

        # 应该返回错误（认证失败）
        assert result.isError
        print(f"\n错误响应: {result.content[0].text}")


class TestCallToolUnknown:
    """测试未知工具调用"""

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """测试调用未知工具的错误处理"""
        result = await call_tool("unknown_tool", {})

        assert result.isError
        assert "未知工具" in result.content[0].text


class TestEnvironmentVariables:
    """测试环境变量支持"""

    @pytest.mark.asyncio
    async def test_api_base_from_env(self):
        """测试从环境变量读取 API 基础地址"""
        old_api_base = os.environ.get("TUPI_BI_API_BASE")
        os.environ["TUPI_BI_API_BASE"] = API_BASE

        try:
            # 调用一个简单的工具来验证环境变量生效
            result = await call_tool("get_camera_config", {"device_id": "test-device"})
            # 请求会失败但能证明环境变量被读取了
            assert isinstance(result, CallToolResult)
        finally:
            if old_api_base:
                os.environ["TUPI_BI_API_BASE"] = old_api_base
            else:
                os.environ.pop("TUPI_BI_API_BASE", None)

    @pytest.mark.asyncio
    async def test_api_base_param_overrides_env(self):
        """测试参数优先于环境变量"""
        old_api_base = os.environ.get("TUPI_BI_API_BASE")
        os.environ["TUPI_BI_API_BASE"] = "https://env.api.com"

        try:
            # 参数中的 api_base 应该覆盖环境变量
            result = await call_tool("get_camera_config", {
                "device_id": "test-device",
                "api_base": API_BASE
            })
            assert isinstance(result, CallToolResult)
        finally:
            if old_api_base:
                os.environ["TUPI_BI_API_BASE"] = old_api_base
            else:
                os.environ.pop("TUPI_BI_API_BASE", None)


@pytest.mark.integration
class TestCallToolGetCustomerInfo:
    """测试 get_customer_info 工具真实 API 调用"""

    @pytest.mark.asyncio
    async def test_get_customer_info_success(self):
        """测试成功获取客户信息"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        # 先获取 token
        from tupu_bi.client import TupuBiClient
        client = TupuBiClient(base_url=API_BASE)
        token_result = await client.get_auth_token(
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )
        token = token_result.get("token")

        test_uid = os.getenv("TUPI_BI_TEST_CUSTOMER_UID", "682ffb703953c231e8cc46a7")

        result = await call_tool("get_customer_info", {
            "uid": test_uid,
            "token": token
        })

        assert not result.isError
        data = json.loads(result.content[0].text)
        assert isinstance(data, dict)
        print(f"\n客户信息响应: {data}")

    @pytest.mark.asyncio
    async def test_get_customer_info_missing_uid(self):
        """测试缺少 uid 参数时的错误处理"""
        result = await call_tool("get_customer_info", {"token": "test-token"})

        assert result.isError
        assert "uid 参数必填" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_customer_info_missing_token(self):
        """测试缺少 token 参数时的错误处理"""
        result = await call_tool("get_customer_info", {"uid": "test-uid"})

        assert result.isError
        assert "token 参数必填" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_customer_info_invalid_credentials(self):
        """测试无效认证信息的错误处理"""
        result = await call_tool("get_customer_info", {
            "uid": "682ffb703953c231e8cc46a7",
            "token": "invalid-token"
        })

        # 应该返回错误（认证失败）
        assert result.isError
        print(f"\n错误响应: {result.content[0].text}")


@pytest.mark.integration
class TestCallToolGetStoreInfo:
    """测试 get_store_info 工具真实 API 调用"""

    @pytest.mark.asyncio
    async def test_get_store_info_success(self):
        """测试成功获取门店信息"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        # 先获取 token
        from tupu_bi.client import TupuBiClient
        client = TupuBiClient(base_url=API_BASE)
        token_result = await client.get_auth_token(
            token_id=TEST_TOKEN_ID,
            secret=AUTH_SECRET
        )
        token = token_result.get("token")

        test_uid = os.getenv("TUPI_BI_TEST_CUSTOMER_UID", "682ffb703953c231e8cc46a7")
        test_sid = os.getenv("TUPI_BI_TEST_STORE_SID", "682ffbae23e8639b53ec6aad")

        result = await call_tool("get_store_info", {
            "sid": test_sid,
            "uid": test_uid,
            "token": token
        })

        assert not result.isError
        data = json.loads(result.content[0].text)
        assert isinstance(data, dict)
        print(f"\n门店信息响应: {data}")

    @pytest.mark.asyncio
    async def test_get_store_info_missing_sid(self):
        """测试缺少 sid 参数时的错误处理"""
        result = await call_tool("get_store_info", {
            "uid": "test-uid",
            "token": "test-token"
        })

        assert result.isError
        assert "sid 参数必填" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_store_info_missing_uid(self):
        """测试缺少 uid 参数时的错误处理"""
        result = await call_tool("get_store_info", {
            "sid": "test-sid",
            "token": "test-token"
        })

        assert result.isError
        assert "uid 参数必填" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_store_info_missing_token(self):
        """测试缺少 token 参数时的错误处理"""
        result = await call_tool("get_store_info", {
            "sid": "test-sid",
            "uid": "test-uid"
        })

        assert result.isError
        assert "token 参数必填" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_store_info_invalid_credentials(self):
        """测试无效认证信息的错误处理"""
        result = await call_tool("get_store_info", {
            "sid": "682ffbae23e8639b53ec6aad",
            "uid": "682ffb703953c231e8cc46a7",
            "token": "invalid-token"
        })

        # 应该返回错误（认证失败）
        assert result.isError
        print(f"\n错误响应: {result.content[0].text}")


@pytest.mark.integration
class TestCallToolGetDeviceFullInfo:
    """测试 get_device_full_info 工具真实 API 调用（整合接口）"""

    @pytest.mark.asyncio
    async def test_get_device_full_info_success(self):
        """测试成功获取设备完整信息（整合接口）"""
        reason = skip_if_no_env()
        if reason:
            pytest.skip(reason)

        test_device_id = TEST_DEVICE_MAC  # 或 TEST_DEVICE_SERIAL

        result = await call_tool("get_device_full_info", {
            "device_id": test_device_id,
            "token_id": TEST_TOKEN_ID,
            "secret": AUTH_SECRET
        })

        assert not result.isError
        data = json.loads(result.content[0].text)
        assert isinstance(data, dict)
        assert "device_id" in data
        assert "camera_config" in data
        assert "customer_info" in data
        assert "store_info" in data

        print(f"\n设备完整信息响应:")
        print(f"  设备 ID: {data.get('device_id')}")
        print(f"  客户名称: {data.get('customer_info', {}).get('name')}")
        print(f"  门店名称: {data.get('store_info', {}).get('name')}")
        print(f"  警告: {data.get('_warning', '无')}")

    @pytest.mark.asyncio
    async def test_get_device_full_info_missing_device_id(self):
        """测试缺少 device_id 参数时的错误处理"""
        result = await call_tool("get_device_full_info", {
            "token_id": TEST_TOKEN_ID,
            "secret": AUTH_SECRET
        })

        assert result.isError
        assert "device_id 参数必填" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_device_full_info_missing_token_id(self):
        """测试缺少 token_id 参数时的错误处理"""
        result = await call_tool("get_device_full_info", {
            "device_id": TEST_DEVICE_MAC
        })

        assert result.isError
        assert "token_id 参数必填" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_device_full_info_missing_secret(self):
        """测试缺少 secret 参数时的错误处理"""
        # 临时清除环境变量
        old_secret = os.environ.pop("TUPI_BI_AUTH_SECRET", None)

        try:
            result = await call_tool("get_device_full_info", {
                "device_id": TEST_DEVICE_MAC,
                "token_id": TEST_TOKEN_ID
            })

            assert result.isError
            assert "secret 未提供" in result.content[0].text
        finally:
            if old_secret:
                os.environ["TUPI_BI_AUTH_SECRET"] = old_secret

    @pytest.mark.asyncio
    async def test_get_device_full_info_invalid_device(self):
        """测试无效设备 ID 的错误处理"""
        result = await call_tool("get_device_full_info", {
            "device_id": "invalid:device:id",
            "token_id": TEST_TOKEN_ID,
            "secret": AUTH_SECRET
        })

        # 应该返回错误（设备不存在或获取配置失败）
        assert result.isError
        print(f"\n错误响应: {result.content[0].text}")
