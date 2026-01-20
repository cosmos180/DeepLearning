#!/usr/bin/env python3
"""
ElastAlert 规则验证脚本
Validate ElastAlert rules YAML syntax and structure
"""

import os
import sys
import argparse
import yaml
from pathlib import Path


# 必需的规则字段
REQUIRED_FIELDS = ['name', 'type', 'index', 'alert']

# 支持的规则类型
VALID_RULE_TYPES = [
    'any', 'blacklist', 'change', 'frequency', 'flatline',
    'spike', 'whitelist', 'cardinality', 'metric_aggregation',
    'percentage_match', 'period_frequency', 'term_aggregation'
]

# 支持的告警类型
VALID_ALERT_TYPES = [
    'email', 'jira', 'opsgenie', 'stomp', 'ms_teams',
    'slack', 'telegram', 'sns', 'mattermost', 'pagerduty',
    'exotel', 'twilio', 'victorops', 'gitter', 'discord',
    'alerta', 'chatwork', 'telegram', 'dingtalk', 'linework',
    'pushover', 'google_chat', 'github', 'servicenow', 'debug'
]


def validate_rule_file(file_path):
    """验证单个规则文件"""
    errors = []
    warnings = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            rule_config = yaml.safe_load(f)

        # 检查必需字段
        for field in REQUIRED_FIELDS:
            if field not in rule_config:
                errors.append(f"Missing required field: {field}")

        # 检查规则类型
        if 'type' in rule_config:
            if rule_config['type'] not in VALID_RULE_TYPES:
                errors.append(f"Invalid rule type: {rule_config['type']}. Valid types: {VALID_RULE_TYPES}")

        # 检查告警类型
        if 'alert' in rule_config:
            for alert_type in rule_config['alert']:
                if alert_type not in VALID_ALERT_TYPES:
                    warnings.append(f"Unknown alert type: {alert_type}")

        # 检查 email 配置
        if 'alert' in rule_config and 'email' in rule_config:
            if 'email' not in rule_config['alert'] and 'email' not in rule_config:
                warnings.append(f"'email' alert is configured but no email addresses specified")

        # 检查查询条件
        if 'filter' not in rule_config and 'query_key' not in rule_config:
            warnings.append(f"Rule has no filter or query_key - may match all documents")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    except yaml.YAMLError as e:
        return {
            'valid': False,
            'errors': [f"YAML syntax error: {str(e)}"],
            'warnings': []
        }
    except Exception as e:
        return {
            'valid': False,
            'errors': [f"Error reading file: {str(e)}"],
            'warnings': []
        }


def validate_rules_directory(rules_dir):
    """验证规则目录中的所有 YAML 文件"""
    results = []
    rules_path = Path(rules_dir)

    if not rules_path.exists():
        print(f"Error: Rules directory not found: {rules_dir}")
        return False

    # 查找所有 YAML 文件
    yaml_files = list(rules_path.rglob('*.yaml')) + list(rules_path.rglob('*.yml'))

    if not yaml_files:
        print(f"Warning: No YAML files found in {rules_dir}")
        return True

    print(f"Found {len(yaml_files)} rule files to validate\n")

    total_valid = 0
    total_errors = 0

    for yaml_file in yaml_files:
        result = validate_rule_file(yaml_file)
        results.append((yaml_file, result))

        relative_path = yaml_file.relative_to(rules_dir)
        status = "✓ VALID" if result['valid'] else "✗ INVALID"

        print(f"{status}: {relative_path}")

        if result['errors']:
            for error in result['errors']:
                print(f"  ERROR: {error}")
            total_errors += 1

        if result['warnings']:
            for warning in result['warnings']:
                print(f"  WARNING: {warning}")

        print()

        if result['valid']:
            total_valid += 1

    # 打印摘要
    print("=" * 50)
    print(f"Validation Summary:")
    print(f"  Total files: {len(yaml_files)}")
    print(f"  Valid: {total_valid}")
    print(f"  Invalid: {len(yaml_files) - total_valid}")

    return total_errors == 0


def main():
    parser = argparse.ArgumentParser(description='Validate ElastAlert rules')
    parser.add_argument(
        '--rules-dir',
        default='/home/bughero/Documents/github/DeepLearning/python/mcp/grafana/monitoring/elastalert_rules',
        help='Path to ElastAlert rules directory'
    )
    parser.add_argument(
        '--file',
        help='Validate a single rule file'
    )

    args = parser.parse_args()

    if args.file:
        # 验证单个文件
        result = validate_rule_file(args.file)
        print(f"Validating: {args.file}")
        print(f"Status: {'✓ VALID' if result['valid'] else '✗ INVALID'}")

        if result['errors']:
            print("\nErrors:")
            for error in result['errors']:
                print(f"  - {error}")

        if result['warnings']:
            print("\nWarnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")

        sys.exit(0 if result['valid'] else 1)
    else:
        # 验证整个目录
        success = validate_rules_directory(args.rules_dir)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
