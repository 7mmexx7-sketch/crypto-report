import requests
from datetime import datetime

# --- [정보 입력] ---
TELEGRAM_TOKEN = "8548489549:AAHkc7-PZrGHWPk-7EpyhK7CpiD4ZOu8bQ4"
CHAT_ID = "-1003807258780"
CMC_API_KEY = "c59e814980984b0c9fdd8c1429c70fcd"
# ------------------

def get_crypto_report():
    try:
        # 1. 코인마켓캡 (시총, 도미넌스)
        cmc_url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        cmc_res = requests.get(cmc_url, headers={"X-CMC_PRO_API_KEY": CMC_API_KEY}).json()
        btc_dom = cmc_res['data']['btc_dominance']
        total_mcap = cmc_res['data']['quote']['USD']['total_market_cap']

        # 2. 업비트 비트코인 가격
        upbit_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC").json()
        upbit_price = float(upbit_res[0]['trade_price'])
        
        # 3. 바이낸스 비트코인 가격 (USDT) - 에러 방지 처리
        binance_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()
        binance_usd = float(binance_res.get('price', 0)) # price가 없으면 0으로 가져옴
        
        # 4. 실시간 환율 (김프 계산용)
        exch_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
        usd_krw = exch_res['rates']['KRW']
        
        # 5. 김치 프리미엄 계산
        binance_krw = binance_usd * usd_krw
        kimp = ((upbit_price - binance_krw) / binance_krw) * 100 if binance_krw > 0 else 0

        # 리포트 조립
        today = datetime.now().strftime('%Y-%m-%d %H:%M')
        report =  f"오전 온체인 데이터 리포트 ({today})\n"
        report += f"------------------------------------\n\n"
        report += f"비트코인 가격: {upbit_price:,.0f} 원\n"
        report += f"김치 프리미엄: {kimp:.2f} %\n\n"
        report += f"비트코인 도미넌스: {btc_dom:.1f} %\n"
        report += f"글로벌 시가총액: ${total_mcap/1e12:.2f} T\n\n"
        report += f"------------------------------------\n"
        report += f"셀러 유니온(Seller Union) 데이터 센터"
        
        return report
    except Exception as e:
        return f"데이터 수집 중 오류 발생: {e}"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text}
    requests.get(url, params=params)

# 최종 실행
final_msg = get_crypto_report()
send_telegram(final_msg)
print("✅ 리포트 전송 시도 완료!")
