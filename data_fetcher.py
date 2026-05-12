"""
📡 جلب بيانات الأسهم من مصادر متعددة
"""

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta

class StockDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_stock_data(self, symbol, market='us'):
        """
        جلب بيانات السهم

        Args:
            symbol: رمز السهم (2222 للسعودي, AAPL للأمريكي)
            market: 'saudi' أو 'us'
        """
        try:
            if market == 'saudi':
                # السوق السعودي - إضافة .SR
                if not symbol.endswith('.SR'):
                    yahoo_symbol = f"{symbol}.SR"
                else:
                    yahoo_symbol = symbol
            else:
                yahoo_symbol = symbol.upper()

            # جلب البيانات من Yahoo Finance
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info

            # بيانات الأسعار (6 أشهر)
            hist = ticker.history(period="6mo", interval="1d")

            if hist.empty:
                return None

            # آخر سعر
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change = ((current - prev) / prev) * 100

            # أعلى وأدنى (52 أسبوع)
            high_52w = hist['High'].max()
            low_52w = hist['Low'].min()

            # حجم التداول
            volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].mean()

            return {
                'symbol': yahoo_symbol,
                'name': info.get('longName', symbol),
                'market': market,
                'current': round(current, 2),
                'change': round(change, 2),
                'open': round(hist['Open'].iloc[-1], 2),
                'high': round(hist['High'].iloc[-1], 2),
                'low': round(hist['Low'].iloc[-1], 2),
                'previous_close': round(prev, 2),
                'volume': int(volume),
                'avg_volume': int(avg_volume),
                'high_52w': round(high_52w, 2),
                'low_52w': round(low_52w, 2),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'prices': hist,  # DataFrame كامل للتحليل
                'currency': info.get('currency', 'USD'),
                'sector': info.get('sector', 'Unknown'),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"خطأ في جلب {symbol}: {e}")
            return None

    def get_multiple_stocks(self, symbols, market='us'):
        """جلب عدة أسهم"""
        results = []
        for symbol in symbols:
            data = self.get_stock_data(symbol, market)
            if data:
                results.append(data)
        return results
