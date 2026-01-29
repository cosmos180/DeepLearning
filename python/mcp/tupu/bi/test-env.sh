#!/bin/bash
# Tupu BI 测试环境变量
# 使用方式: source test-env.sh

export TUPI_BI_API_BASE="https://api.bi.tuputech.com"
export TUPI_BI_AUTH_SECRET="your-secret-here"
export TUPI_BI_TEST_TOKEN_ID="your-token-id-here"
export TUPI_BI_TEST_DEVICE_MAC="aa:bb:cc:dd:ee:ff"
export TUPI_BI_TEST_DEVICE_SERIAL="your-serial-number-here"

echo "测试环境变量已加载"
