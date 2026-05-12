"""
📊 التحليل الفني المتقدم
"""

import pandas as pd
import numpy as np
from datetime import datetime

class TechnicalAnalyzer:

    def calculate_sma(self, prices, period):
        """المتوسط المتحرك البسيط"""
        return prices['Close'].rolling(window=period).mean().iloc[-1]

    def calculate_ema(self, prices, period):
        """المتوسط المتحرك الأسي"""
        return prices['Close'].ewm(span=period, adjust=False).mean().iloc[-1]

    def calculate_rsi(self, prices, period=14):
        """مؤشر القوة النسبية"""
        delta = prices['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi.iloc[-1], 2)

    def calculate_macd(self, prices):
        """مؤشر MACD"""
        exp1 = prices['Close'].ewm(span=12, adjust=False).mean()
        exp2 = prices['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal

        return {
            'macd': round(macd.iloc[-1], 4),
            'signal': round(signal.iloc[-1], 4),
            'histogram': round(histogram.iloc[-1], 4)
        }

    def calculate_bollinger(self, prices, period=20):
        """نطاقات بولينجر"""
        sma = prices['Close'].rolling(window=period).mean()
        std = prices['Close'].rolling(window=period).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)

        return {
            'upper': round(upper.iloc[-1], 2),
            'middle': round(sma.iloc[-1], 2),
            'lower': round(lower.iloc[-1], 2),
            'bandwidth': round((upper.iloc[-1] - lower.iloc[-1]) / sma.iloc[-1] * 100, 2)
        }

    def calculate_atr(self, prices, period=14):
        """متوسط المدى الحقيقي"""
        high_low = prices['High'] - prices['Low']
        high_close = np.abs(prices['High'] - prices['Close'].shift())
        low_close = np.abs(prices['Low'] - prices['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(period).mean()
        return round(atr.iloc[-1], 2)

    def calculate_stochastic(self, prices, period=14):
        """مؤشر ستوكاستيك"""
        low_min = prices['Low'].rolling(window=period).min()
        high_max = prices['High'].rolling(window=period).max()
        k = 100 * ((prices['Close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=3).mean()

        return {
            'k': round(k.iloc[-1], 2),
            'd': round(d.iloc[-1], 2)
        }

    def calculate_all(self, prices):
        """حساب جميع المؤشرات"""
        return {
            'sma_20': round(self.calculate_sma(prices, 20), 2),
            'sma_50': round(self.calculate_sma(prices, 50), 2),
            'sma_200': round(self.calculate_sma(prices, 200), 2),
            'ema_12': round(self.calculate_ema(prices, 12), 2),
            'ema_26': round(self.calculate_ema(prices, 26), 2),
            'rsi': self.calculate_rsi(prices),
            'macd': self.calculate_macd(prices),
            'bollinger': self.calculate_bollinger(prices),
            'atr': self.calculate_atr(prices),
            'stochastic': self.calculate_stochastic(prices)
        }

    def full_analysis(self, prices):
        """تحليل شامل"""
        indicators = self.calculate_all(prices)

        # تحديد الاتجاه
        current = prices['Close'].iloc[-1]
        sma20 = indicators['sma_20']
        sma50 = indicators['sma_50']
        sma200 = indicators['sma_200']

        trend = 'neutral'
        if current > sma20 > sma50 > sma200:
            trend = 'strong_bullish'
        elif current > sma50 > sma200:
            trend = 'bullish'
        elif current < sma20 < sma50 < sma200:
            trend = 'strong_bearish'
        elif current < sma50 < sma200:
            trend = 'bearish'

        # مستويات الدعم والمقاومة
        recent = prices.tail(20)
        support = round(recent['Low'].min(), 2)
        resistance = round(recent['High'].max(), 2)

        # إشارات
        signals = []

        # RSI
        rsi = indicators['rsi']
        if rsi < 30:
            signals.append('RSI: منطقة تشبع بيعي (إشارة شراء)')
        elif rsi > 70:
            signals.append('RSI: منطقة تشبع شرائي (إشارة بيع)')

        # MACD
        macd = indicators['macd']
        if macd['histogram'] > 0 and macd['macd'] > macd['signal']:
            signals.append('MACD: إشارة صعودية')
        elif macd['histogram'] < 0 and macd['macd'] < macd['signal']:
            signals.append('MACD: إشارة هبوطية')

        # بولينجر
        bb = indicators['bollinger']
        if current <= bb['lower']:
            signals.append('بولينجر: السعر عند الحد السفلي (ربما ارتداد)')
        elif current >= bb['upper']:
            signals.append('بولينجر: السعر عند الحد العلوي (ربما تصحيح)')

        return {
            'indicators': indicators,
            'trend': trend,
            'support': support,
            'resistance': resistance,
            'signals': signals,
            'current_price': round(current, 2)
        }

    def get_recommendation(self, analysis):
        """توصية تداول"""
        trend = analysis['trend']
        signals = analysis['signals']
        rsi = analysis['indicators']['rsi']

        score = 0

        if 'bullish' in trend:
            score += 2
        if 'bearish' in trend:
            score -= 2

        for signal in signals:
            if 'شراء' in signal or 'صعودية' in signal:
                score += 1
            if 'بيع' in signal or 'هبوطية' in signal:
                score -= 1

        if score >= 3:
            return {'action': 'شراء قوي', 'score': score, 'color': 'green'}
        elif score >= 1:
            return {'action': 'شراء', 'score': score, 'color': 'lightgreen'}
        elif score <= -3:
            return {'action': 'بيع قوي', 'score': score, 'color': 'red'}
        elif score <= -1:
            return {'action': 'بيع', 'score': score, 'color': 'orange'}
        else:
            return {'action': 'محايد', 'score': score, 'color': 'gray'}
