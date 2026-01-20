#!/usr/bin/env python3
"""
File Alerter for ElastAlert
将告警内容写入文件，模拟邮件告警功能
"""

import datetime
import json
import os
from typing import Dict, Any, List

# 告警输出目录
ALERT_OUTPUT_DIR = "/home/bughero/Documents/github/DeepLearning/python/mcp/grafana/monitoring/alerts"


class FileAlerter:
    """将告警写入文件"""

    def __init__(self, rule: Dict[str, Any], args=None):
        self.rule = rule
        # 确保输出目录存在
        os.makedirs(ALERT_OUTPUT_DIR, exist_ok=True)

    def alert(self, matches: List[Dict[str, Any]]):
        """处理告警并写入文件"""
        if not matches:
            return

        # 生成告警文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        rule_name = self.rule.get('name', 'unknown').replace(' ', '_').replace('/', '_')
        filename = f"{ALERT_OUTPUT_DIR}/alert_{rule_name}_{timestamp}.json"

        # 准备告警数据
        alert_data = {
            "rule_name": self.rule.get('name'),
            "rule_type": self.rule.get('type'),
            "alert_time": datetime.datetime.now().isoformat(),
            "match_count": len(matches),
            "matches": matches[:10],  # 只保留前10条匹配
            "rule_config": {
                "index": self.rule.get('index'),
                "num_events": self.rule.get('num_events'),
                "timeframe": self.rule.get('timeframe'),
            }
        }

        # 写入 JSON 文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(alert_data, f, ensure_ascii=False, indent=2)

        # 同时写入可读的文本格式
        txt_filename = filename.replace('.json', '.txt')
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(self._format_text_alert(alert_data))

        print(f"✅ 告警已写入: {filename}")
        print(f"   匹配数量: {len(matches)}")

    def _format_text_alert(self, alert_data: Dict[str, Any]) -> str:
        """格式化告警为可读文本"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"🚨 告警通知: {alert_data['rule_name']}")
        lines.append("=" * 60)
        lines.append(f"时间: {alert_data['alert_time']}")
        lines.append(f"规则类型: {alert_data['rule_type']}")
        lines.append(f"匹配数量: {alert_data['match_count']}")
        lines.append("")
        lines.append("规则配置:")
        for key, value in alert_data['rule_config'].items():
            lines.append(f"  {key}: {value}")
        lines.append("")
        lines.append("匹配数据（前10条）:")
        lines.append("-" * 60)

        for i, match in enumerate(alert_data.get('matches', [])[:10], 1):
            lines.append(f"\n[{i}] 匹配记录:")
            if '_source' in match:
                source = match['_source']
                if '@timestamp' in source:
                    lines.append(f"  时间: {source['@timestamp']}")
                if 'sInfo' in source:
                    lines.append(f"  应用: {source['sInfo'].get('app', 'N/A')}")
                    lines.append(f"  环境: {source['sInfo'].get('env', 'N/A')}")
                    lines.append(f"  主机: {source['sInfo'].get('hostname', 'N/A')}")
                if 'contents' in source:
                    lines.append(f"  级别: {source['contents'].get('level', 'N/A')}")
                    msg = source['contents'].get('message', 'N/A')
                    if len(msg) > 200:
                        msg = msg[:200] + "..."
                    lines.append(f"  消息: {msg}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def get_info(self):
        """返回告警器信息"""
        return {
            "type": "file",
            "output_dir": ALERT_OUTPUT_DIR
        }


def alert_file(rule: Dict[str, Any], args=None):
    """文件告警器入口函数"""
    return FileAlerter(rule, args)
