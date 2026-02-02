#!/usr/bin/env python3
"""
Email Template Renderer
统一风格的邮件模板渲染器

模板风格特点:
- 简洁现代的卡片式布局
- 渐变色头部，根据严重程度区分
- 清晰的信息层级和视觉引导
- 响应式设计，适配各种邮件客户端
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from jinja2 import Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


# ============================================================================
# 模板配置
# ============================================================================

TEMPLATES_DIR = Path(__file__).parent

# 严重程度对应的样式类
SEVERITY_STYLES = {
    'critical': {
        'header_class': 'critical',
        'status_class': 'critical',
        'icon': '🔴',
    },
    'warning': {
        'header_class': 'warning',
        'status_class': 'warning',
        'icon': '🟡',
    },
    'info': {
        'header_class': 'info',
        'status_class': 'success',
        'icon': '🔵',
    },
    'success': {
        'header_class': 'success',
        'status_class': 'success',
        'icon': '✅',
    },
}


# ============================================================================
# 模板渲染器
# ============================================================================

class EmailTemplateRenderer:
    """邮件模板渲染器"""

    def __init__(self, templates_dir: Path = None):
        """
        初始化渲染器

        Args:
            templates_dir: 模板目录路径，默认使用当前目录
        """
        if not JINJA2_AVAILABLE:
            raise ImportError("Jinja2 未安装，请运行: pip install jinja2")

        self.templates_dir = templates_dir or TEMPLATES_DIR
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
        )

    def _get_severity_style(self, severity: str) -> Dict[str, str]:
        """获取严重程度对应的样式"""
        return SEVERITY_STYLES.get(severity.lower(), SEVERITY_STYLES['info'])

    def render_status_report(
        self,
        title: str,
        subtitle: str,
        status_title: str,
        status_message: str,
        info_box_title: str,
        info_box_content: str,
        severity: str = "success",
        details_content: str = None,
        alert_list: List[Dict] = None,
        platform: str = "SDC",
        footer_message: str = "This is an automated message from Grafana Alert System.",
    ) -> str:
        """
        渲染状态报告邮件

        用于发送监控状态摘要，如"无告警"、"系统健康报告"等

        Args:
            title: 邮件标题
            subtitle: 副标题
            status_title: 状态框标题
            status_message: 状态消息
            info_box_title: 信息框标题
            info_box_content: 信息框内容（支持 HTML）
            severity: 严重程度 (critical/warning/info/success)
            details_content: 详细信息（可选，支持 HTML）
            alert_list: 告警列表，每个告警是包含以下字段的字典:
                - rule_name: 规则名称
                - device_id: 设备 ID
                - value: 当前值
                - threshold: 阈值
                - severity: 严重程度 (critical/warning/info)
                - timestamp: 时间戳
            platform: 平台名称
            footer_message: 页脚消息

        Returns:
            渲染后的 HTML 内容
        """
        template = self.env.get_template('email_status_report.html.j2')
        style = self._get_severity_style(severity)

        # 处理告警列表，添加渲染所需的字段
        processed_alerts = []
        for alert in (alert_list or []):
            alert_severity = alert.get('severity', 'warning')
            alert_style = self._get_severity_style(alert_severity)

            # 确定值颜色
            value_color = '#212529'
            if alert_severity == 'critical':
                value_color = '#dc3545'
            elif alert_severity == 'warning':
                value_color = '#ffc107'

            processed_alerts.append({
                'rule_name': alert.get('rule_name', 'N/A'),
                'device_id': alert.get('device_id', 'N/A'),
                'value': alert.get('value', 'N/A'),
                'threshold': alert.get('threshold', 'N/A'),
                'timestamp': alert.get('timestamp', 'N/A'),
                'severity_text': alert_severity.upper(),
                'severity_class': alert_style['header_class'],
                'value_color': value_color,
            })

        # 如果告警超过 20 条，只显示前 20 条
        alert_list_more = None
        if len(processed_alerts) > 20:
            alert_list_more = len(processed_alerts) - 20
            processed_alerts = processed_alerts[:20]

        return template.render(
            title=title,
            subtitle=subtitle,
            status_title=status_title,
            status_message=status_message,
            info_box_title=info_box_title,
            info_box_content=info_box_content,
            header_class=style['header_class'],
            status_class=style['status_class'],
            details_content=details_content,
            alert_list=processed_alerts,
            alert_list_more=alert_list_more,
            platform=platform,
            footer_message=footer_message,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )

    def render_metric_alert(
        self,
        rule_name: str,
        actual_value: Any,
        threshold_value: Any,
        severity: str = "warning",
        device_id: str = None,
        device_ip: str = None,
        device_location: str = None,
        metric_data: List[Dict] = None,
        grafana_chart_url: str = None,
        kibana_url: str = "#",
        grafana_dashboard_url: str = None,
        runbook_url: str = None,
        platform: str = "SDC",
    ) -> str:
        """
        渲染指标告警邮件

        用于发送指标类型告警，如 CPU、内存、磁盘使用率等

        Args:
            rule_name: 规则名称
            actual_value: 当前值
            threshold_value: 阈值
            severity: 严重程度
            device_id: 设备 ID
            device_ip: 设备 IP
            device_location: 设备位置
            metric_data: 指标数据列表
            grafana_chart_url: Grafana 图表 URL
            kibana_url: Kibana 链接
            grafana_dashboard_url: Grafana Dashboard 链接
            runbook_url: 处理手册链接
            platform: 平台名称

        Returns:
            渲染后的 HTML 内容
        """
        template = self.env.get_template('email_metric_alert.html.j2')
        style = self._get_severity_style(severity)

        # 确定标题
        title = f"{style['icon']} 指标告警"
        if severity == 'critical':
            title = f"{style['icon']} 严重告警"

        return template.render(
            title=title,
            rule_name=rule_name,
            actual_value=actual_value,
            threshold_value=threshold_value,
            severity=severity.upper(),
            severity_class=style['header_class'],
            header_class=style['header_class'],
            device_id=device_id,
            device_ip=device_ip,
            device_location=device_location,
            metric_data=metric_data or [],
            grafana_chart_url=grafana_chart_url,
            kibana_url=kibana_url,
            grafana_dashboard_url=grafana_dashboard_url,
            runbook_url=runbook_url,
            platform=platform,
            triggered_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )

    def render_error_alert(
        self,
        rule_name: str,
        hits: List[Dict],
        num_hits: int,
        severity: str = "critical",
        service_name: str = None,
        hostname: str = None,
        environment: str = "production",
        kibana_url: str = "#",
        grafana_url: str = None,
        runbook_url: str = None,
    ) -> str:
        """
        渲染错误告警邮件

        用于发送日志错误类型告警，如异常、错误日志等

        Args:
            rule_name: 规则名称
            hits: 匹配的日志记录列表
            num_hits: 匹配数量
            severity: 严重程度
            service_name: 服务名称
            hostname: 主机名
            environment: 环境名称
            kibana_url: Kibana 链接
            grafana_url: Grafana 链接
            runbook_url: 处理手册链接

        Returns:
            渲染后的 HTML 内容
        """
        template = self.env.get_template('email_error_alert.html.j2')
        style = self._get_severity_style(severity)

        return template.render(
            title=f"{style['icon']} 错误告警",
            rule_name=rule_name,
            hits=hits,
            num_hits=num_hits,
            severity=severity.upper(),
            severity_class=style['header_class'],
            header_class=style['header_class'],
            service_name=service_name,
            hostname=hostname,
            environment=environment,
            kibana_url=kibana_url,
            grafana_url=grafana_url,
            runbook_url=runbook_url,
            triggered_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )


# ============================================================================
# 快捷函数（不需要实例化）
# ============================================================================

_renderer: Optional[EmailTemplateRenderer] = None


def _get_renderer() -> EmailTemplateRenderer:
    """获取渲染器单例"""
    global _renderer
    if _renderer is None:
        _renderer = EmailTemplateRenderer()
    return _renderer


def render_status_report(*args, **kwargs) -> str:
    """快捷函数：渲染状态报告"""
    return _get_renderer().render_status_report(*args, **kwargs)


def render_metric_alert(*args, **kwargs) -> str:
    """快捷函数：渲染指标告警"""
    return _get_renderer().render_metric_alert(*args, **kwargs)


def render_error_alert(*args, **kwargs) -> str:
    """快捷函数：渲染错误告警"""
    return _get_renderer().render_error_alert(*args, **kwargs)


# 导出
__all__ = [
    'EmailTemplateRenderer',
    'render_status_report',
    'render_metric_alert',
    'render_error_alert',
]
