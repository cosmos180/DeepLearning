#!/usr/bin/env python3
"""
A股数据获取脚本
支持从公开API获取A股行情、财务、板块等数据
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional


class AStockDataFetcher:
    """A股数据获取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_stock_info(self, symbol: str) -> Dict:
        """
        获取个股基本信息

        Args:
            symbol: 股票代码（如 600519）

        Returns:
            包含股票信息的字典
        """
        # 这里使用公开API接口
        # 实际使用时可能需要根据具体API调整
        try:
            # 东方财富API示例
            url = f"http://push2.eastmoney.com/api/qt/stock/get"
            params = {
                'secid': self._format_secid(symbol),
                'fields': 'f57,f58,f162,f163,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f60'
            }
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_stock_info(data, symbol)
        except Exception as e:
            return {'error': str(e)}

        # 返回模拟数据作为fallback
        return self._get_mock_stock_info(symbol)

    def get_market_overview(self) -> Dict:
        """获取市场概览"""
        try:
            # 获取主要指数
            indices = ['000001', '399001', '399006', '000688']
            index_names = {
                '000001': '上证指数',
                '399001': '深证成指',
                '399006': '创业板指',
                '000688': '科创50'
            }
            result = {'indices': [], 'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

            for idx in indices:
                url = f"http://push2.eastmoney.com/api/qt/stock/get"
                params = {'secid': f'1.{idx}' if idx.startswith('00') else f'0.{idx}'}
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    result['indices'].append({
                        'name': index_names.get(idx, idx),
                        'code': idx,
                        'price': data.get('data', {}).get('f43', 0) / 100,
                        'change': data.get('data', {}).get('169', 0) / 100,
                        'change_pct': data.get('data', {}).get('170', 0) / 100
                    })

            return result
        except Exception as e:
            return {'error': str(e), 'indices': self._get_mock_indices()}

    def get_sector_performance(self, sector_type: str = 'sw') -> List[Dict]:
        """
        获取板块表现

        Args:
            sector_type: 板块类型 (sw=申万, concept=概念)

        Returns:
            板块表现列表
        """
        try:
            # 申万行业API
            url = "http://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1,
                'pz': 50,
                'po': 1,
                'np': 1,
                'fltt': 2,
                'invt': 2,
                'fid': 'f62',
                'fs': 'm:90+t:2',  # 申万行业
                'fields': 'f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13'
            }
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_sector_data(data)
        except Exception as e:
            return [{'error': str(e)}]

        return self._get_mock_sectors()

    def search_stock(self, keyword: str) -> List[Dict]:
        """股票搜索"""
        try:
            url = "http://search.eastmoney.com/api/suggest/get"
            params = {
                'input': keyword,
                'type': '14',
                'token': 'D43BF722C8B820CE54461279EEC55AD8'
            }
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_search_result(data)
        except:
            pass
        return []

    def _format_secid(self, symbol: str) -> str:
        """格式化证券ID"""
        if symbol.startswith('6'):
            return f'1.{symbol}'  # 上海
        elif symbol.startswith(('0', '3')):
            return f'0.{symbol}'  # 深圳
        elif symbol.startswith('8') or symbol.startswith('4'):
            return f'0.{symbol}'  # 北交所
        return f'1.{symbol}'

    def _parse_stock_info(self, data: dict, symbol: str) -> dict:
        """解析股票信息"""
        info = data.get('data', {})
        return {
            'symbol': symbol,
            'name': info.get('f58', ''),
            'price': info.get('f43', 0) / 100 if info.get('f43') else 0,
            'change': info.get('f169', 0) / 100 if info.get('f169') else 0,
            'change_pct': info.get('f170', 0) / 100 if info.get('f170') else 0,
            'open': info.get('f46', 0) / 100 if info.get('f46') else 0,
            'high': info.get('f44', 0) / 100 if info.get('f44') else 0,
            'low': info.get('f45', 0) / 100 if info.get('f45') else 0,
            'volume': info.get('f47', 0) if info.get('f47') else 0,
            'amount': info.get('f48', 0) / 10000 if info.get('f48') else 0,
            'market_cap': info.get('f116', 0) / 100000000 if info.get('f116') else 0,
            'pe_ttm': info.get('f162', 0) / 100 if info.get('f162') else 0,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _parse_sector_data(self, data: dict) -> list:
        """解析板块数据"""
        sectors = []
        for item in data.get('data', {}).get('diff', []):
            sectors.append({
                'name': item.get('f14', ''),
                'code': item.get('f12', ''),
                'change_pct': item.get('f3', 0) / 100 if item.get('f3') else 0,
                'amount': item.get('f6', 0) / 100000000 if item.get('f6') else 0,
                'up_count': item.get('f104', 0),
                'down_count': item.get('f105', 0),
                'leader': item.get('f136', '')
            })
        return sectors

    def _parse_search_result(self, data: dict) -> list:
        """解析搜索结果"""
        results = []
        for item in data.get('quotationCodeTable', {}).get('table', []):
            results.append({
                'code': item.get('code', ''),
                'name': item.get('name', ''),
                'market': item.get('market', {})
            })
        return results

    # Mock数据方法（用于演示和fallback）
    def _get_mock_stock_info(self, symbol: str) -> dict:
        """模拟股票数据"""
        mock_data = {
            '600519': {'name': '贵州茅台', 'price': 1680.50, 'change': 15.30, 'change_pct': 0.92},
            '000858': {'name': '五粮液', 'price': 145.20, 'change': -2.30, 'change_pct': -1.56},
            '300750': {'name': '宁德时代', 'price': 185.60, 'change': 5.40, 'change_pct': 3.00},
        }
        data = mock_data.get(symbol, {'name': '未知股票', 'price': 10.00, 'change': 0, 'change_pct': 0})
        return {
            'symbol': symbol,
            'name': data['name'],
            'price': data['price'],
            'change': data['change'],
            'change_pct': data['change_pct'],
            'open': data['price'] - data['change'] / 2,
            'high': data['price'] + abs(data['change']),
            'low': data['price'] - abs(data['change']),
            'volume': 1000000,
            'amount': 150000000,
            'market_cap': 200000000000,
            'pe_ttm': 25.5,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_mock_indices(self) -> list:
        """模拟指数数据"""
        return [
            {'name': '上证指数', 'code': '000001', 'price': 3050.25, 'change': 15.30, 'change_pct': 0.50},
            {'name': '深证成指', 'code': '399001', 'price': 9850.60, 'change': -30.20, 'change_pct': -0.31},
            {'name': '创业板指', 'code': '399006', 'price': 1920.45, 'change': 20.10, 'change_pct': 1.06},
            {'name': '科创50', 'code': '000688', 'price': 780.30, 'change': 8.50, 'change_pct': 1.10}
        ]

    def _get_mock_sectors(self) -> list:
        """模拟板块数据"""
        return [
            {'name': '半导体', 'change_pct': 3.25, 'amount': 280.5, 'up_count': 45, 'down_count': 8},
            {'name': '新能源汽车', 'change_pct': 2.80, 'amount': 350.2, 'up_count': 38, 'down_count': 12},
            {'name': '白酒', 'change_pct': -1.20, 'amount': 180.3, 'up_count': 5, 'down_count': 25},
            {'name': '银行', 'change_pct': 0.50, 'amount': 120.8, 'up_count': 15, 'down_count': 18}
        ]


def main():
    """测试函数"""
    fetcher = AStockDataFetcher()

    # 测试获取股票信息
    print("=== 获取股票信息 ===")
    info = fetcher.get_stock_info('600519')
    print(json.dumps(info, ensure_ascii=False, indent=2))

    # 测试获取市场概览
    print("\n=== 获取市场概览 ===")
    overview = fetcher.get_market_overview()
    print(json.dumps(overview, ensure_ascii=False, indent=2))

    # 测试获取板块表现
    print("\n=== 获取板块表现 ===")
    sectors = fetcher.get_sector_performance()
    print(json.dumps(sectors, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
