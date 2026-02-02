#!/usr/bin/env python3
"""
Alert Email Reporter Tool
告警邮件报告工具 - 为每个 platform 生成告警 panel 截图并发送邮件
"""

import asyncio
import base64
import json
import os
import smtplib
from dataclasses import dataclass, field
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import nest_asyncio

# 允许嵌套事件循环
nest_asyncio.apply()


# ============================================================================
# 配置文件路径
# ============================================================================

# 收件人配置文件路径
RECIPIENTS_CONFIG_FILE = Path(__file__).parent.parent / "monitoring" / "config" / "recipients.json"


# ============================================================================
# 配置
# ============================================================================

@dataclass
class GrafanaConfig:
    """Grafana 配置"""
    url: str = "https://g.dev.tuputech.com"
    api_key: str = ""
    dashboard_uid: str = "urJcwIvHz"
    dashboard_slug: str = "ye-wu-yi-chang-jian-kong"
    org_id: int = 1


@dataclass
class EmailConfig:
    """邮件配置"""
    smtp_host: str = "smtp.exmail.qq.com"
    smtp_port: int = 465
    sender_email: str = ""
    sender_password: str = ""
    sender_name: str = "[Grafana-Alert-System]"
    # 支持多个收件人
    recipients: List[str] = field(default_factory=list)


@dataclass
class AlertReportConfig:
    """告警报告配置"""
    time_range: str = "today"  # 截图时间范围，默认为"今天"
    image_width: int = 1200  # 截图宽度
    image_height: int = 600  # 截图高度
    platforms: List[str] = field(default_factory=lambda: ["sdc", "tpboxv3", "tpboxv2", "android_armv7", "1800A", "rv1109", "tpboxv1"])
    email_subject: str = "🚨 Grafana 告警报告 - Platform: {platform} (含截图)"


# 默认告警规则与 Panel 的映射关系
DEFAULT_ALERT_PANELS = {
    "IPC 数据积压告警-JSON缓存": {"panel_id": 5, "title": "数据积压【json】"},
    "IPC 数据积压告警-JPEG缓存": {"panel_id": 6, "title": "数据积压【jpeg】"},
    "IPC 模型调用失败-reid": {"panel_id": 11, "title": "模型调用失败【reid】"},
    "IPC 模型调用失败-attr": {"panel_id": 12, "title": "模型调用失败【attr】"},
    "IPC 数据上传失败-uploadTrack": {"panel_id": 13, "title": "数据上传失败【uploadTrack】"},
    "IPC 磁盘使用率警告": {"panel_id": 23, "title": "磁盘使用率"},
    "IPC 磁盘使用率告警": {"panel_id": 23, "title": "磁盘使用率"},
    "IPC 磁盘使用率严重告警": {"panel_id": 23, "title": "磁盘使用率"},
    "IPC 摄像头离线告警": {"panel_id": 21, "title": "摄像头离线"},
}


# ============================================================================
# 收件人管理
# ============================================================================

class RecipientsManager:
    """收件人管理器"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        初始化收件人管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file or RECIPIENTS_CONFIG_FILE
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_recipients(self) -> List[str]:
        """
        从配置文件加载收件人列表
        
        Returns:
            收件人邮箱列表
        """
        if not self.config_file.exists():
            # 创建默认配置
            default_recipients = os.getenv("RECIPIENTS_TO", "").split(",") if os.getenv("RECIPIENTS_TO") else []
            self.save_recipients(default_recipients)
            return default_recipients
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("recipients", [])
        except Exception as e:
            print(f"⚠️ 加载收件人配置失败: {e}")
            return []
    
    def save_recipients(self, recipients: List[str]) -> bool:
        """
        保存收件人列表到配置文件
        
        Args:
            recipients: 收件人邮箱列表
        
        Returns:
            是否保存成功
        """
        try:
            data = {
                "recipients": recipients,
                "updated_at": datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存收件人配置失败: {e}")
            return False
    
    def add_recipient(self, email: str) -> bool:
        """
        添加收件人
        
        Args:
            email: 邮箱地址
        
        Returns:
            是否添加成功
        """
        recipients = self.load_recipients()
        if email not in recipients:
            recipients.append(email)
            return self.save_recipients(recipients)
        return True
    
    def remove_recipient(self, email: str) -> bool:
        """
        移除收件人
        
        Args:
            email: 邮箱地址
        
        Returns:
            是否移除成功
        """
        recipients = self.load_recipients()
        if email in recipients:
            recipients.remove(email)
            return self.save_recipients(recipients)
        return False
    
    def list_recipients(self) -> List[str]:
        """
        列出所有收件人
        
        Returns:
            收件人邮箱列表
        """
        return self.load_recipients()


# ============================================================================
# Alert Email Reporter
# ============================================================================

class AlertEmailReporter:
    """告警邮件报告器"""
    
    def __init__(
        self,
        grafana_config: Optional[GrafanaConfig] = None,
        email_config: Optional[EmailConfig] = None,
        report_config: Optional[AlertReportConfig] = None,
        alert_panels: Optional[Dict[str, Dict]] = None,
    ):
        """
        初始化告警邮件报告器
        
        Args:
            grafana_config: Grafana 配置
            email_config: 邮件配置
            report_config: 报告配置
            alert_panels: 告警规则与 Panel 的映射关系
        """
        self.grafana = grafana_config or GrafanaConfig(
            url=os.getenv("GRAFANA_URL", "https://g.dev.tuputech.com"),
            api_key=os.getenv("GRAFANA_API_KEY", ""),
        )
        
        # 初始化收件人管理器
        self.recipients_manager = RecipientsManager()
        
        # 邮件配置
        if email_config:
            # 如果传入的 email_config 的收件人为空，从配置文件加载
            if not email_config.recipients:
                recipients = self.recipients_manager.load_recipients()
                if not recipients:
                    # 尝试从环境变量获取
                    recipients_str = os.getenv("RECIPIENTS_TO", "")
                    recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]
                # 更新 email_config 的收件人
                email_config.recipients = recipients
            self.email = email_config
        else:
            # 从配置文件或环境变量加载收件人
            recipients = self.recipients_manager.load_recipients()
            if not recipients:
                # 尝试从环境变量获取
                recipients_str = os.getenv("RECIPIENTS_TO", "")
                recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]

            self.email = EmailConfig(
                sender_email=os.getenv("SENDER_EMAIL", ""),
                sender_password=os.getenv("SENDER_PASSWORD", ""),
                recipients=recipients,
            )
        
        self.report = report_config or AlertReportConfig()
        self.alert_panels = alert_panels or DEFAULT_ALERT_PANELS
        
        # 去重 panel（多个规则可能对应同一个 panel）
        self.unique_panels = {}
        for rule_name, panel_info in self.alert_panels.items():
            panel_id = panel_info["panel_id"]
            if panel_id not in self.unique_panels:
                self.unique_panels[panel_id] = panel_info
    
    def _format_time_range(self, time_range: str) -> str:
        """
        格式化时间范围显示
        
        Args:
            time_range: 原始时间范围
        
        Returns:
            格式化后的时间范围
        """
        if time_range == "today":
            return "今天 (00:00:00 ~ 现在)"
        return f"最近 {time_range}"
    
    async def download_panel_render(
        self,
        panel_id: int,
        platform: str,
    ) -> Dict[str, Any]:
        """
        下载 Panel 的渲染图片
        
        Args:
            panel_id: Panel ID
            platform: 平台名称
        
        Returns:
            包含图片数据、URL 和状态的字典
        """
        dashboard_uid = self.grafana.dashboard_uid
        slug = self.grafana.dashboard_slug
        
        # 解析时间范围
        time_from = "now/d" if self.report.time_range == "today" else f"now-{self.report.time_range}"
        
        # 生成渲染 URL
        render_url = (
            f"{self.grafana.url}/render/d-solo/{dashboard_uid}/{slug}"
            f"?panelId={panel_id}"
            f"&from={time_from}"
            f"&to=now"
            f"&width={self.report.image_width}"
            f"&height={self.report.image_height}"
            f"&timezone=Asia%2FShanghai"
            f"&var-platform={platform}"
        )
        
        # 设置请求头
        headers = {}
        if self.grafana.api_key:
            headers["Authorization"] = f"Bearer {self.grafana.api_key}"
        
        try:
            async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
                response = await client.get(render_url)
                
                content_type = response.headers.get("content-type", "")
                
                if "text/html" in content_type or response.status_code != 200:
                    return {
                        "success": False,
                        "status": "render_unavailable",
                        "fallback_url": render_url
                    }
                
                response.raise_for_status()
                
                return {
                    "success": True,
                    "status": "success",
                    "image_data": response.content,
                    "fallback_url": render_url
                }
        
        except Exception as e:
            return {
                "success": False,
                "status": f"error: {str(e)}",
                "fallback_url": render_url
            }
    
    async def _download_all_panels(self, platform: str) -> Dict[int, Dict]:
        """下载指定平台的所有 Panel 截图"""
        panels_data = {}
        
        for panel_id, panel_info in self.unique_panels.items():
            title = panel_info["title"]
            print(f"  正在下载 Panel {panel_id}: {title}...")
            
            result = await self.download_panel_render(panel_id, platform)
            
            if result["success"]:
                # 转换为 base64
                image_base64 = base64.b64encode(result["image_data"]).decode('utf-8')
                panels_data[panel_id] = {
                    "image_base64": image_base64,
                    "render_url": result["fallback_url"]
                }
                print(f"    ✅ 截图下载成功 ({len(result['image_data'])} bytes)")
            else:
                panels_data[panel_id] = {
                    "fallback_url": result["fallback_url"],
                    "error": result["status"]
                }
                print(f"    ⚠️ 截图不可用: {result['status']}")
        
        return panels_data
    
    def _build_email_html(self, platform: str, panels_data: Dict[int, Dict]) -> str:
        """构建邮件 HTML 内容"""
        panels_html = ""
        time_range_display = self._format_time_range(self.report.time_range)
        
        for panel_id, panel_info in self.unique_panels.items():
            title = panel_info["title"]
            panel_data = panels_data.get(panel_id)
            
            if panel_data and panel_data.get("image_base64"):
                # 有截图
                panels_html += f"""
                <div style="margin-bottom: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #e0e0e0;">
                    <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px;">
                        📊 {title}
                    </div>
                    <div style="text-align: center;">
                        <img src="data:image/png;base64,{panel_data['image_base64']}" 
                             alt="{title}" 
                             style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    </div>
                    <div style="margin-top: 10px; font-size: 12px; color: #666;">
                        时间范围: {time_range_display} | Platform: {platform}
                    </div>
                </div>
                """
            else:
                # 没有截图，显示备用链接
                fallback_url = panel_data.get("fallback_url", "") if panel_data else ""
                error_msg = panel_data.get("error", "未知错误") if panel_data else "数据不可用"
                
                panels_html += f"""
                <div style="margin-bottom: 30px; padding: 20px; background-color: #fff3cd; border-radius: 8px; border: 1px solid #ffc107;">
                    <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px;">
                        📊 {title}
                    </div>
                    <div style="color: #856404; margin-bottom: 15px;">
                        ⚠️ 截图不可用 ({error_msg})
                    </div>
                    <a href="{fallback_url}" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px;">
                        🔗 在 Grafana 中查看
                    </a>
                </div>
                """
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Microsoft YaHei', 'PingFang SC', Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; font-weight: bold; }}
        .header p {{ margin: 10px 0 0; opacity: 0.95; font-size: 16px; }}
        .content {{ padding: 30px; }}
        .info-box {{ background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .info-box p {{ margin: 8px 0; color: #495057; }}
        .footer {{ background-color: #f8f9fa; padding: 25px; text-align: center; color: #6c757d; font-size: 14px; border-top: 1px solid #dee2e6; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 Grafana 告警监控报告</h1>
            <p style="font-size: 20px; margin-top: 15px;">Platform: <strong>{platform}</strong></p>
        </div>
        <div class="content">
            <div class="info-box">
                <p><strong>📅 报告时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>📊 监控 Dashboard:</strong> 【业务异常监控】</p>
                <p><strong>🔍 监控 Panel 数量:</strong> {len(self.unique_panels)}</p>
                <p><strong>⏱️ 数据时间范围:</strong> {time_range_display}</p>
            </div>
            
            <h2 style="color: #333; border-bottom: 3px solid #667eea; padding-bottom: 15px; margin-top: 30px;">📋 告警 Panel 截图</h2>
            
            {panels_html}
            
            <div class="info-box" style="margin-top: 30px;">
                <p style="font-weight: bold; margin-bottom: 10px;">💡 说明:</p>
                <ul style="margin: 10px 0; padding-left: 20px; color: #495057;">
                    <li>以上截图显示了该 platform 下各告警指标的实时状态</li>
                    <li>截图时间范围: {time_range_display}</li>
                    <li>建议定期查看以监控系统健康状态</li>
                </ul>
            </div>
        </div>
        <div class="footer">
            <p>此邮件由 Grafana 告警系统自动生成</p>
            <p>Dashboard: <a href="{self.grafana.url}/d/{self.grafana.dashboard_uid}/{self.grafana.dashboard_slug}">【业务异常监控】</a></p>
        </div>
    </div>
</body>
</html>
        """
    
    async def _send_email(self, platform: str, panels_data: Dict[int, Dict]) -> Dict[str, Any]:
        """
        发送邮件给所有收件人
        
        Returns:
            发送结果（包含成功和失败的收件人列表）
        """
        html_content = self._build_email_html(platform, panels_data)
        subject = self.report.email_subject.format(platform=platform)
        
        results = {
            "success": [],
            "failed": []
        }
        
        for recipient in self.email.recipients:
            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = formataddr([self.email.sender_name, self.email.sender_email])
                msg['To'] = recipient
                
                msg.attach(MIMEText(html_content, 'html', 'utf-8'))
                
                with smtplib.SMTP_SSL(self.email.smtp_host, self.email.smtp_port) as server:
                    server.login(self.email.sender_email, self.email.sender_password)
                    server.send_message(msg)
                
                results["success"].append(recipient)
            except Exception as e:
                results["failed"].append({"email": recipient, "error": str(e)})
        
        # 打印结果
        if results["success"]:
            print(f"✅ 邮件发送成功: {platform} -> {', '.join(results['success'])}")
        if results["failed"]:
            failed_list = [f"{f['email']}({f['error']})" for f in results['failed']]
            print(f"❌ 邮件发送失败: {platform} -> {', '.join(failed_list)}")
        
        return results
    
    async def send_for_platform(self, platform: str) -> Dict[str, Any]:
        """
        为指定 platform 发送告警邮件
        
        Args:
            platform: 平台名称
        
        Returns:
            发送结果
        """
        print(f"\n{'='*70}")
        print(f"处理 Platform: {platform}")
        print(f"{'='*70}")
        
        panels_data = await self._download_all_panels(platform)
        email_results = await self._send_email(platform, panels_data)
        
        return {
            "platform": platform,
            "success": len(email_results["success"]) > 0,
            "recipients_success": email_results["success"],
            "recipients_failed": email_results["failed"],
            "panels_count": len(panels_data),
            "screenshots_count": sum(1 for p in panels_data.values() if "image_base64" in p)
        }
    
    async def send_all_platforms(self) -> List[Dict[str, Any]]:
        """
        为所有配置的 platform 发送告警邮件
        
        Returns:
            发送结果列表
        """
        print("=" * 70)
        print("开始为每个 platform 生成告警报告邮件（带截图）")
        print("=" * 70)
        print(f"收件人: {', '.join(self.email.recipients) if self.email.recipients else '(无)'}")
        print(f"时间范围: {self._format_time_range(self.report.time_range)}")
        print("=" * 70)
        
        results = []
        for platform in self.report.platforms:
            result = await self.send_for_platform(platform)
            results.append(result)
        
        print("\n" + "=" * 70)
        print("所有平台告警报告邮件发送完成！")
        print("=" * 70)
        
        return results


# ============================================================================
# 辅助函数
# ============================================================================

def _run_async(coro):
    """运行异步代码"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# ============================================================================
# Agent Tool Functions
# ============================================================================

def send_alert_report_email(
    platforms: str = None,
    time_range: str = "today",
    recipients: str = None,
) -> str:
    """
    发送告警报告邮件
    
    Args:
        platforms: 平台列表，逗号分隔（如 "sdc,tpboxv3"），默认发送所有平台
        time_range: 时间范围（如 "today", "6h", "24h", "7d"），默认为 "today"（今天）
        recipients: 收件人邮箱列表，逗号分隔（覆盖配置文件）
    
    Returns:
        发送结果摘要
    
    示例:
        send_alert_report_email()
        send_alert_report_email(platforms="sdc,tpboxv3")
        send_alert_report_email(time_range="today")
        send_alert_report_email(recipients="user1@example.com,user2@example.com")
    """
    # 解析平台列表
    platform_list = None
    if platforms:
        platform_list = [p.strip() for p in platforms.split(',')]
    
    # 创建配置
    grafana_config = GrafanaConfig(
        url=os.getenv("GRAFANA_URL", "https://g.dev.tuputech.com"),
        api_key=os.getenv("GRAFANA_API_KEY", ""),
    )
    
    # 解析收件人列表
    recipient_list = None
    if recipients:
        recipient_list = [r.strip() for r in recipients.split(',')]
    
    email_config = EmailConfig(
        sender_email=os.getenv("SENDER_EMAIL", ""),
        sender_password=os.getenv("SENDER_PASSWORD", ""),
        recipients=recipient_list if recipient_list else [],  # 空列表会让 Reporter 从配置文件加载
    )
    
    report_config = AlertReportConfig(
        time_range=time_range,
        platforms=platform_list or ["sdc", "tpboxv3", "tpboxv2", "android_armv7", "1800A", "rv1109", "tpboxv1"],
    )
    
    # 创建报告器并发送
    reporter = AlertEmailReporter(
        grafana_config=grafana_config,
        email_config=email_config,
        report_config=report_config,
    )
    
    results = _run_async(reporter.send_all_platforms())
    
    # 格式化结果
    lines = [
        f"📧 告警报告邮件发送结果",
        f"{'='*60}",
        f"  总计: {len(results)} 个平台",
        f"  成功: {sum(1 for r in results if r['success'])} 个",
        f"  失败: {sum(1 for r in results if not r['success'])} 个",
        f"{'='*60}",
    ]
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        recipients_info = ""
        if result["recipients_success"]:
            recipients_info = f" -> {', '.join(result['recipients_success'])}"
        
        lines.append(
            f"{status} {result['platform']}: "
            f"{result['screenshots_count']}/{result['panels_count']} 张截图{recipients_info}"
        )
    
    return "\n".join(lines)


def manage_recipients(action: str = "list", email: str = None) -> str:
    """
    管理收件人列表
    
    Args:
        action: 操作类型 ("list", "add", "remove")
        email: 邮箱地址（用于 add 和 remove 操作）
    
    Returns:
        操作结果
    
    示例:
        manage_recipients("list")
        manage_recipients("add", "user@example.com")
        manage_recipients("remove", "user@example.com")
    """
    manager = RecipientsManager()
    
    if action == "list":
        recipients = manager.list_recipients()
        
        if not recipients:
            return "📋 收件人列表为空\n\n💡 使用 manage_recipients('add', 'email@example.com') 添加收件人"
        
        lines = [
            f"📋 收件人列表 ({len(recipients)} 个)",
            f"{'='*60}",
        ]
        for i, recipient in enumerate(recipients, 1):
            lines.append(f"  {i}. {recipient}")
        
        return "\n".join(lines)
    
    elif action == "add":
        if not email:
            return "❌ 请提供邮箱地址"
        
        if manager.add_recipient(email):
            return f"✅ 已添加收件人: {email}"
        else:
            return f"⚠️ 收件人已存在或添加失败: {email}"
    
    elif action == "remove":
        if not email:
            return "❌ 请提供邮箱地址"
        
        if manager.remove_recipient(email):
            return f"✅ 已移除收件人: {email}"
        else:
            return f"❌ 收件人不存在或移除失败: {email}"
    
    else:
        return f"❌ 未知操作: {action}\n支持的操作: list, add, remove"


# ============================================================================
# 命令行入口
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Grafana 告警报告邮件发送工具")
    parser.add_argument("--platforms", type=str, help="平台列表，逗号分隔")
    parser.add_argument("--time-range", type=str, default="today", help="时间范围（默认: today）")
    parser.add_argument("--recipients", type=str, help="收件人邮箱列表，逗号分隔")
    
    # 收件人管理子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # list 命令
    subparsers.add_parser("list", help="列出所有收件人")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加收件人")
    add_parser.add_argument("email", help="邮箱地址")
    
    # remove 命令
    remove_parser = subparsers.add_parser("remove", help="移除收件人")
    remove_parser.add_argument("email", help="邮箱地址")
    
    args = parser.parse_args()
    
    if args.command:
        # 收件人管理命令
        if args.command == "list":
            result = manage_recipients("list")
        elif args.command == "add":
            result = manage_recipients("add", args.email)
        elif args.command == "remove":
            result = manage_recipients("remove", args.email)
        print(result)
    else:
        # 发送邮件命令
        result = send_alert_report_email(
            platforms=args.platforms,
            time_range=args.time_range,
            recipients=args.recipients,
        )
        print(result)
