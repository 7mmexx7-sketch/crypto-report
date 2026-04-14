import requests
from datetime import datetime

# --- [정보 입력] ---
TELEGRAM_TOKEN = "8548489549:AAHkc7-PZrGHWPk-7EpyhK7CpiD4ZOu8bQ4"
CHAT_ID = "-1003807258780"
CMC_API_KEY = "c59e814980984b0c9fdd8c1429c70fcd"
# ------------------

def get_crypto_report():
    try:
        # 1. 데이터 수집
        cmc_url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        cmc_res = requests.get(cmc_url, headers={"X-CMC_PRO_API_KEY": CMC_API_KEY}).json()
        btc_dom = cmc_res['data']['btc_dominance']
        total_mcap = cmc_res['data']['quote']['USD']['total_market_cap']

        upbit_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC").json()
        upbit_price = float(upbit_res[0]['trade_price'])
        
        binance_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()
        binance_usd = float(binance_res.get('price', 0))
        exch_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
        usd_krw = exch_res['rates']['KRW']
        binance_krw = binance_usd * usd_krw
        kimp = ((upbit_price - binance_krw) / binance_krw) * 100 if binance_krw > 0 else 0

        fng_res = requests.get("https://api.alternative.me/fng/").json()
        fng_value = fng_res['data'][0]['value']
        fng_status = fng_res['data'][0]['value_classification']
        
        status_dict = {"Fear": "공포", "Extreme Fear": "극단적 공포", "Neutral": "중립", "Greed": "탐욕", "Extreme Greed": "극단적 탐욕"}
        fng_kor = status_dict.get(fng_status, fng_status)

        # 2. [디자인 변경] 주요 제목 진하게 강조
        today = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        report =  f"■ **SELLER UNION DAILY REPORT**\n"
        report += f"발행일시: {today}\n"
        report += f"━━━━━━━━━━━━━━━━━━\n\n"
        
        # 핵심: ** 기호로 감싸면 텔레그램에서 진하게 나옵니다.
        report += f"**[비트코인 실시간 시세]**\n"
        report += f"현재가: **{upbit_price:,.0f}원**\n"
        report += f"프리미엄: **{kimp:.2f}%**\n\n"
        
        report += f"**[시장 주요 지표]**\n"
        report += f"공포탐욕지수: {fng_value} ({fng_kor})\n"
        report += f"BTC 점유율: {btc_dom:.1f}%\n"
        report += f"글로벌 시총: ${total_mcap/1e12:.2f}T\n\n"
        
        report += f"━━━━━━━━━━━━━━━━━━\n"
        report += f"**셀러유니온(Seller Union) 데이터 센터**\n"
        report += f"본 리포트는 실시간 데이터를 기반으로 작성되었습니다."
        
        return report
    except Exception as e:
        return f"데이터 로드 오류: {e}"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # parse_mode를 Markdown으로 설정해야 ** 기호가 작동합니다.
    params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.get(url, params=params)

# 실행 및 전송
final_msg = get_crypto_report()
send_telegram(final_msg)
