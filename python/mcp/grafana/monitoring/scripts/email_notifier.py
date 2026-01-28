#!/usr/bin/env python3
"""
Email Notification Module
支持通过 SMTP 发送告警邮件
"""

import os
import re
import smtplib
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Any, List, Optional

import yaml
from dotenv import load_dotenv


# ============================================================================
# 环境变量处理
# ============================================================================

# 尝试加载 .env 文件（如果存在）
_env_loaded = False
_possible_env_paths = [
    Path.cwd() / '.env',
    Path(__file__).parent.parent / '.env',
    Path(__file__).parent.parent.parent / '.env',
]
for env_path in _possible_env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        _env_loaded = True
        break


def _resolve_env_vars(value: Any) -> Any:
    """递归解析配置中的环境变量

    支持格式:
    - ${VAR}          - 必须的环境变量
    - ${VAR:-default} - 带默认值的环境变量
    """
    if isinstance(value, str):
        # 匹配 ${VAR} 或 ${VAR:-default}
        pattern = r'\$\{([^}:]+)(:-([^}]*))?\}'

        def replace_env_var(match):
            var_name = match.group(1)
            default_value = match.group(3) if match.group(3) is not None else None
            env_value = os.getenv(var_name)
            if env_value is None:
                if default_value is not None:
                    return default_value
                # 如果没有默认值且环境变量不存在，保持原样
                return match.group(0)
            return env_value

        return re.sub(pattern, replace_env_var, value)
    elif isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        # 处理列表，特别处理逗号分隔的字符串
        if len(value) == 1 and isinstance(value[0], str):
            # 检查是否是逗号分隔的字符串
            items = [item.strip() for item in value[0].split(',') if item.strip()]
            if len(items) > 1:
                return items
        return [_resolve_env_vars(item) for item in value]
    return value


def _normalize_recipients(value: Any) -> List[str]:
    """将收件人值标准化为字符串列表"""
    if isinstance(value, str):
        # 逗号分隔的字符串
        return [item.strip() for item in value.split(',') if item.strip()]
    elif isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, str):
                result.append(item)
        return result
    return []


def _parse_bool(value: Any) -> bool:
    """解析布尔值（支持字符串 "true"/"false"）"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    return bool(value)


# ============================================================================
# 配置
# ============================================================================

@dataclass
class SMTPConfig:
    """SMTP 配置"""
    host: str
    port: int
    use_tls: bool


@dataclass
class SenderConfig:
    """发件人配置"""
    email: str
    password: str
    name: str


@dataclass
class RecipientsConfig:
    """收件人配置"""
    to: List[str]
    cc: List[str]
    bcc: Optional[List[str]] = None

    def __post_init__(self):
        if self.bcc is None:
            self.bcc = []

    def get_all(self) -> List[str]:
        """获取所有收件人"""
        return self.to + self.cc + (self.bcc or [])


@dataclass
class EmailConfig:
    """邮件配置"""
    smtp: SMTPConfig
    sender: SenderConfig
    recipients: RecipientsConfig
    severity_routes: dict
    subject_template: str

    @classmethod
    def from_yaml(cls, config_path: str = "monitoring/config/email.yaml") -> 'EmailConfig':
        """从 YAML 文件加载配置

        支持环境变量替换:
        - ${VAR}          - 必须的环境变量
        - ${VAR:-default} - 带默认值的环境变量

        也支持 .env 文件（自动检测加载）
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 解析配置中的环境变量
        config = _resolve_env_vars(config)

        # 标准化收件人配置（支持字符串或列表）
        recipients_cfg = config.get('recipients', {})
        recipients = RecipientsConfig(
            to=_normalize_recipients(recipients_cfg.get('to', [])),
            cc=_normalize_recipients(recipients_cfg.get('cc', [])),
            bcc=_normalize_recipients(recipients_cfg.get('bcc', [])),
        )

        return cls(
            smtp=SMTPConfig(
                host=config['smtp']['host'],
                port=config['smtp']['port'],
                use_tls=_parse_bool(config['smtp'].get('use_tls', True)),
            ),
            sender=SenderConfig(
                email=config['sender']['email'],
                password=config['sender']['password'],
                name=config['sender'].get('name', 'Alert System'),
            ),
            recipients=recipients,
            severity_routes=config.get('severity_routes', {}),
            subject_template=config.get('templates', {}).get(
                'subject_template', '[{severity}] {rule_name} - {device_id}'
            ),
        )

    def get_recipients_for_severity(self, severity: str) -> RecipientsConfig:
        """根据告警级别获取收件人"""
        if severity in self.severity_routes:
            route = self.severity_routes[severity]
            return RecipientsConfig(
                to=_normalize_recipients(route.get('to', [])),
                cc=_normalize_recipients(route.get('cc', [])),
                bcc=_normalize_recipients(route.get('bcc', [])),
            )
        return self.recipients


# ============================================================================
# 邮件发送器
# ============================================================================

class EmailNotifier:
    """邮件通知器"""

    def __init__(self, config: EmailConfig):
        self.config = config

    def _create_message(
        self,
        subject: str,
        body: str,
        recipients: RecipientsConfig,
        html: bool = False,
    ) -> MIMEMultipart:
        """创建邮件消息"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        # From 头部直接使用邮箱地址，避免格式问题
        msg['From'] = self.config.sender.email
        msg['To'] = ', '.join(recipients.to)
        if recipients.cc:
            msg['Cc'] = ', '.join(recipients.cc)

        # 添加正文
        if html:
            msg.attach(MIMEText(body, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

        return msg

    def _get_smtp_connection(self) -> smtplib.SMTP:
        """获取 SMTP 连接

        端口说明:
        - 465: SMTP_SSL (直接 SSL 连接)
        - 587: SMTP + STARTTLS (先连接后升级 TLS)
        """
        timeout = 10  # 10秒超时

        if self.config.smtp.use_tls:
            # STARTTLS (端口 587)
            server = smtplib.SMTP(self.config.smtp.host, self.config.smtp.port, timeout=timeout)
            server.starttls()
        else:
            # SSL (端口 465)
            server = smtplib.SMTP_SSL(self.config.smtp.host, self.config.smtp.port, timeout=timeout)

        server.login(self.config.sender.email, self.config.sender.password)
        return server

    def send(
        self,
        subject: str,
        body: str,
        severity: str = "warning",
        html: bool = False,
    ) -> bool:
        """发送邮件"""
        # 根据告警级别获取收件人
        recipients = self.config.get_recipients_for_severity(severity)

        # 创建邮件
        msg = self._create_message(subject, body, recipients, html)

        # 获取所有收件人
        all_recipients = recipients.get_all()

        if not all_recipients:
            print("⚠️ No recipients configured, skipping email send")
            return False

        try:
            # 发送邮件
            with self._get_smtp_connection() as server:
                # 使用 sendmail 而不是 send_message，确保 envelope sender 正确
                # from_addr 必须与认证用户一致
                server.sendmail(
                    from_addr=self.config.sender.email,
                    to_addrs=all_recipients,
                    msg=msg.as_string()
                )
                print(f"✅ Email sent to {len(all_recipients)} recipients")
                return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

    def send_alert(
        self,
        rule_name: str,
        device_id: str,
        field: str,
        value: float,
        threshold: float,
        severity: str,
        timestamp: str,
    ) -> bool:
        """发送告警邮件"""
        # 格式化主题
        subject = self.config.subject_template.format(
            severity=severity.upper(),
            rule_name=rule_name,
            device_id=device_id,
        )

        # 格式化正文 (HTML) - 表格形式
        icon = "🔴" if severity == "critical" else "🟡" if severity == "warning" else "🔵"
        border_color = '#dc3545' if severity == 'critical' else '#ffc107' if severity == 'warning' else '#17a2b8'

        body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .alert-table {{
            border-collapse: collapse;
            width: 100%;
            max-width: 600px;
            margin: 20px 0;
        }}
        .alert-table th, .alert-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .alert-table th {{
            background-color: {border_color};
            color: white;
            font-weight: bold;
        }}
        .alert-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .header {{
            color: {border_color};
        }}
        .footer {{
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <h2 class="header">{icon} Alert Triggered</h2>

    <table class="alert-table">
        <tr>
            <th width="30%">Field</th>
            <th>Value</th>
        </tr>
        <tr>
            <td><strong>Rule</strong></td>
            <td>{rule_name}</td>
        </tr>
        <tr>
            <td><strong>Device ID</strong></td>
            <td>{device_id}</td>
        </tr>
        <tr>
            <td><strong>Field</strong></td>
            <td>{field}</td>
        </tr>
        <tr>
            <td><strong>Current Value</strong></td>
            <td>{value}</td>
        </tr>
        <tr>
            <td><strong>Threshold</strong></td>
            <td>{threshold}</td>
        </tr>
        <tr>
            <td><strong>Severity</strong></td>
            <td>{severity.upper()}</td>
        </tr>
        <tr>
            <td><strong>Time</strong></td>
            <td>{timestamp}</td>
        </tr>
    </table>

    <p class="footer">
        This is an automated message from Grafana Alert System.
    </p>
</body>
</html>
"""

        return self.send(subject, body, severity, html=True)

    def send_alert_summary(self, alerts: list, severity: str = "summary") -> bool:
        """发送告警摘要邮件"""
        if not alerts:
            return False

        # 统计
        total = len(alerts)
        critical = sum(1 for a in alerts if a.get('severity') == 'critical')
        warning = sum(1 for a in alerts if a.get('severity') == 'warning')

        subject = f"[{severity.upper()}] Alert Summary - {total} alerts ({critical} critical, {warning} warning)"

        # 构建 HTML 正文
        rows = ""
        for alert in alerts:
            icon = "🔴" if alert['severity'] == 'critical' else "🟡"
            rows += f"""
        <tr>
            <td>{icon}</td>
            <td>{alert.get('rule_name', 'N/A')}</td>
            <td>{alert.get('device_id', 'N/A')}</td>
            <td>{alert.get('value', 'N/A')}</td>
            <td>{alert.get('threshold', 'N/A')}</td>
            <td>{alert.get('timestamp', 'N/A')}</td>
        </tr>"""

        body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .summary {{ background-color: #f8f9fa; padding: 15px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h2>📊 Alert Summary</h2>

    <div class="summary">
        <p><strong>Total Alerts:</strong> {total}</p>
        <p><strong>Critical:</strong> {critical}</p>
        <p><strong>Warning:</strong> {warning}</p>
    </div>

    <h3>Alert Details</h3>
    <table>
        <thead>
            <tr>
                <th>Severity</th>
                <th>Rule</th>
                <th>Device</th>
                <th>Value</th>
                <th>Threshold</th>
                <th>Time</th>
            </tr>
        </thead>
        <tbody>
{rows}
        </tbody>
    </table>

    <hr>
    <p style="color: #666; font-size: 0.9em;">
        This is an automated message from Grafana Alert System.
    </p>
</body>
</html>
"""

        return self.send(subject, body, severity, html=True)


# ============================================================================
# 测试
# ============================================================================

def test_email():
    """测试邮件发送"""
    # 加载配置
    try:
        config = EmailConfig.from_yaml()
    except Exception as e:
        print(f"❌ Failed to load email config: {e}")
        print("\n配置方式（任选其一）:")
        print("\n方式一: 使用 .env 文件（推荐）")
        print("  cp .env.example .env")
        print("  # 编辑 .env 文件填入真实配置")
        print("\n方式二: 直接修改 email.yaml")
        print("  cp monitoring/config/email.yaml.example monitoring/config/email.yaml")
        print("  # 编辑 email.yaml 文件填入真实配置")
        print("\n方式三: 使用环境变量")
        print("  export SMTP_HOST='smtp.exmail.qq.com'")
        print("  export SMTP_PORT='465'")
        print("  export SENDER_EMAIL='your@company.com'")
        print("  export SENDER_PASSWORD='your-password'")
        return False

    notifier = EmailNotifier(config)

    # 发送测试邮件
    print("📧 Sending test email...")
    success = notifier.send(
        subject="[TEST] Grafana Alert System - Test Email",
        body="<h1>Test Email</h1><p>This is a test email from Grafana Alert System.</p>",
        severity="warning",
        html=True,
    )

    if success:
        print("✅ Test email sent successfully!")
    else:
        print("\n❌ Failed to send email. Check your SMTP configuration.")

    return success


if __name__ == "__main__":
    test_email()
