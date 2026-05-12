"""
📄 مولد تقارير PDF
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import matplotlib.pyplot as plt
import io
import os
from datetime import datetime

class ReportGenerator:

    def __init__(self):
        self.output_dir = 'static/reports'
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs('static/fonts', exist_ok=True)

        # تسجيل خط عربي (اختياري)
        try:
            pdfmetrics.registerFont(TTFont('Arabic', 'static/fonts/Amiri-Regular.ttf'))
        except:
            pass

    def create_chart(self, prices, symbol):
        """إنشاء رسم بياني"""
        plt.figure(figsize=(10, 6))
        plt.plot(prices.index, prices['Close'], label='السعر', color='blue', linewidth=2)

        # SMA
        sma20 = prices['Close'].rolling(window=20).mean()
        sma50 = prices['Close'].rolling(window=50).mean()
        plt.plot(prices.index, sma20, label='SMA 20', color='orange', alpha=0.7)
        plt.plot(prices.index, sma50, label='SMA 50', color='red', alpha=0.7)

        plt.title(f'{symbol} - Chart')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # حفظ الصورة
        chart_path = f'{self.output_dir}/{symbol}_chart.png'
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()

        return chart_path

    def generate_pdf(self, symbol, data, analysis):
        """توليد تقرير PDF كامل"""
        filename = f'{self.output_dir}/{symbol}_report_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'

        doc = SimpleDocTemplate(filename, pagesize=A4,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)

        story = []
        styles = getSampleStyleSheet()

        # عنوان
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        story.append(Paragraph(f"Technical Analysis Report", title_style))
        story.append(Paragraph(f"{data['name']} ({symbol})", title_style))
        story.append(Spacer(1, 20))

        # معلومات أساسية
        info_data = [
            ['Current Price', f"${data['current']}"],
            ['Change', f"{data['change']}%"],
            ['Day High', f"${data['high']}"],
            ['Day Low', f"${data['low']}"],
            ['Volume', f"{data['volume']:,}"],
            ['52W High', f"${data['high_52w']}"],
            ['52W Low', f"${data['low_52w']}"],
        ]

        info_table = Table(info_data, colWidths=[3*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))

        story.append(info_table)
        story.append(Spacer(1, 20))

        # المؤشرات الفنية
        story.append(Paragraph("Technical Indicators", styles['Heading2']))

        indicators = analysis['indicators']
        ind_data = [
            ['Indicator', 'Value', 'Signal'],
            ['RSI (14)', indicators['rsi'], 'Oversold' if indicators['rsi'] < 30 else 'Overbought' if indicators['rsi'] > 70 else 'Neutral'],
            ['SMA 20', indicators['sma_20'], ''],
            ['SMA 50', indicators['sma_50'], ''],
            ['SMA 200', indicators['sma_200'], ''],
            ['MACD', f"{indicators['macd']['macd']}", 'Bullish' if indicators['macd']['histogram'] > 0 else 'Bearish'],
            ['ATR', indicators['atr'], ''],
        ]

        ind_table = Table(ind_data, colWidths=[2*inch, 2*inch, 2*inch])
        ind_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))

        story.append(ind_table)
        story.append(Spacer(1, 20))

        # التوصية
        rec = analysis.get('recommendation', {})
        rec_color = colors.HexColor('#4caf50') if 'Buy' in str(rec.get('action', '')) else colors.HexColor('#f44336') if 'Sell' in str(rec.get('action', '')) else colors.HexColor('#9e9e9e')

        story.append(Paragraph("Recommendation", styles['Heading2']))
        story.append(Paragraph(f"<b>{rec.get('action', 'Neutral')}</b>", 
                              ParagraphStyle('Rec', parent=styles['Normal'], 
                                           textColor=rec_color, fontSize=18, alignment=TA_CENTER)))
        story.append(Spacer(1, 20))

        # إشارات
        story.append(Paragraph("Trading Signals", styles['Heading2']))
        for signal in analysis['signals']:
            story.append(Paragraph(f"• {signal}", styles['Normal']))

        # الرسم البياني
        chart_path = self.create_chart(data['prices'], symbol)
        story.append(Spacer(1, 30))
        story.append(Paragraph("Price Chart", styles['Heading2']))

        img = Image(chart_path, width=6*inch, height=3.6*inch)
        story.append(img)

        # تذييل
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                              ParagraphStyle('Footer', parent=styles['Normal'], 
                                           fontSize=8, textColor=colors.gray, alignment=TA_CENTER)))

        doc.build(story)

        return filename
