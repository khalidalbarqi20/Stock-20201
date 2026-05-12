// متغيرات عامة
let currentMarket = 'all';

// عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    loadMarketOverview();
    
    // البحث بالإنتر
    document.getElementById('symbolInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchStock();
    });
});

// تبديل السوق
function switchMarket(market) {
    currentMarket = market;
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    loadMarketOverview();
}

// البحث عن سهم
async function searchStock() {
    const symbol = document.getElementById('symbolInput').value.trim();
    if (!symbol) {
        alert('أدخل رمز السهم');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`/api/analyze/${symbol}`);
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            showLoading(false);
            return;
        }
        
        displayResult(data);
    } catch (error) {
        console.error('Error:', error);
        alert('حدث خطأ في الاتصال');
    }
    
    showLoading(false);
}

// عرض النتائج
function displayResult(data) {
    const resultDiv = document.getElementById('result');
    const analysis = data.analysis || {};
    const indicators = analysis.indicators || {};
    const recommendation = data.recommendation || {};
    
    const changeClass = data.change >= 0 ? 'positive' : 'negative';
    const changeSign = data.change >= 0 ? '+' : '';
    
    let recClass = 'rec-neutral';
    if (recommendation.action?.includes('شراء')) recClass = 'rec-buy';
    if (recommendation.action?.includes('بيع')) recClass = 'rec-sell';
    
    resultDiv.innerHTML = `
        <div class="stock-header">
            <div class="stock-name">
                ${data.name || data.symbol}
                <small style="display:block; color:#666; font-size:0.9rem">${data.symbol}</small>
            </div>
            <div class="stock-price">
                <div class="current-price">$${data.current}</div>
                <div class="price-change ${changeClass}">${changeSign}${data.change}%</div>
            </div>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <label>الافتتاح</label>
                <value>${data.open}</value>
            </div>
            <div class="info-card">
                <label>أعلى</label>
                <value>${data.high}</value>
            </div>
            <div class="info-card">
                <label>أدنى</label>
                <value>${data.low}</value>
            </div>
            <div class="info-card">
                <label>الحجم</label>
                <value>${(data.volume / 1000000).toFixed(2)}M</value>
            </div>
            <div class="info-card">
                <label>أعلى 52 أسبوع</label>
                <value>${data.high_52w}</value>
            </div>
            <div class="info-card">
                <label>أدنى 52 أسبوع</label>
                <value>${data.low_52w}</value>
            </div>
        </div>
        
        <h3 style="margin:20px 0; color:var(--primary)">المؤشرات الفنية</h3>
        <div class="indicators-grid">
            <div class="indicator-card">
                <h3>RSI (14)</h3>
                <div class="indicator-value">${indicators.rsi || '-'}</div>
            </div>
            <div class="indicator-card">
                <h3>MACD</h3>
                <div class="indicator-value">${indicators.macd?.macd || '-'}</div>
            </div>
            <div class="indicator-card">
                <h3>SMA 50</h3>
                <div class="indicator-value">${indicators.sma_50 || '-'}</div>
            </div>
            <div class="indicator-card">
                <h3>ATR</h3>
                <div class="indicator-value">${indicators.atr || '-'}</div>
            </div>
        </div>
        
        <div class="recommendation ${recClass}">
            التوصية: ${recommendation.action || 'محايد'}
        </div>
        
        ${analysis.signals?.length ? `
            <h3 style="margin:20px 0; color:var(--primary)">إشارات التداول</h3>
            <ul class="signals-list">
                ${analysis.signals.map(s => `<li>${s}</li>`).join('')}
            </ul>
        ` : ''}
        
        <div class="action-buttons">
            <button class="btn btn-success" onclick="downloadReport('${data.symbol}')">
                📄 تحميل تقرير PDF
            </button>
            <button class="btn btn-primary" onclick="addToWatchlist('${data.symbol}')">
                ⭐ إضافة للمفضلة
            </button>
        </div>
    `;
    
    resultDiv.classList.remove('hidden');
}

// تحميل تقرير PDF
function downloadReport(symbol) {
    window.open(`/api/report/${symbol}`, '_blank');
}

// إضافة للمفضلة
function addToWatchlist(symbol) {
    let watchlist = JSON.parse(localStorage.getItem('watchlist') || '[]');
    if (!watchlist.includes(symbol)) {
        watchlist.push(symbol);
        localStorage.setItem('watchlist', JSON.stringify(watchlist));
        alert('تمت الإضافة للمفضلة');
    } else {
        alert('السهم موجود في المفضلة');
    }
}

// تحميل نظرة عامة
async function loadMarketOverview() {
    try {
        const response = await fetch('/api/market-overview');
        const data = await response.json();
        
        const grid = document.getElementById('marketsGrid');
        grid.innerHTML = '';
        
        // السوق السعودي
        if (data.saudi && (currentMarket === 'all' || currentMarket === 'saudi')) {
            const saudiSection = createMarketSection('🇸🇦 السوق السعودي', data.saudi);
            grid.appendChild(saudiSection);
        }
        
        // السوق الأمريكي
        if (data.us && (currentMarket === 'all' || currentMarket === 'us')) {
            const usSection = createMarketSection('🇺🇸 السوق الأمريكي', data.us);
            grid.appendChild(usSection);
        }
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

// إنشاء قسم السوق
function createMarketSection(title, stocks) {
    const section = document.createElement('div');
    section.className = 'market-section';
    
    const changeClass = (change) => change >= 0 ? 'positive' : 'negative';
    const changeSign = (change) => change >= 0 ? '+' : '';
    
    section.innerHTML = `
        <h3>${title}</h3>
        ${stocks.map(stock => `
            <div class="stock-item" onclick="loadStock('${stock.symbol}')">
                <div>
                    <strong>${stock.symbol}</strong>
                    <small style="display:block; color:#666">${stock.name || ''}</small>
                </div>
                <div style="text-align:left">
                    <div style="font-weight:700">$${stock.price}</div>
                    <div class="${changeClass(stock.change)}">${changeSign(stock.change)}${stock.change}%</div>
                </div>
            </div>
        `).join('')}
    `;
    
    return section;
}

// تحميل سهم محدد
function loadStock(symbol) {
    document.getElementById('symbolInput').value = symbol.replace('.SR', '');
    searchStock();
}

// إظهار/إخفاء التحميل
function showLoading(show) {
    document.getElementById('loading').classList.toggle('hidden', !show);
    if (show) document.getElementById('result').classList.add('hidden');
}
