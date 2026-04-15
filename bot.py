import requests
from datetime import datetime
import os

# --- [정보 입력] ---
TELEGRAM_TOKEN = "8548489549:AAHkc7-PZrGHWPk-7EpyhK7CpiD4ZOu8bQ4"

# 방금 찾으신 새 방 번호가 완벽하게 적용되었습니다!
CHAT_IDS = [
    "-1003807258780", 
    "-1002443665222"  
] 

CMC_API_KEY = "c59e814980984b0c9fdd8c1429c70fcd"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ------------------

def get_ai_news_briefing():
    """해외 핫 이슈를 가져와 AI가 한국어로 요약합니다."""
    if not OPENAI_API_KEY:
        return "⚠️ OpenAI API 키가 설정되지 않아 뉴스를 가져올 수 없습니다."
    
    try:
        news_url = "https://cryptopanic.com/api/v1/posts/?auth_token=PUBLIC&filter=hot"
        news_data = requests.get(news_url).json()
        raw_news = ""
        for post in news_data['results'][:12]:
            raw_news += f"Title: {post['title']}\nLink: {post['url']}\n\n"

        prompt = f"당신은 가상자산 전문가입니다. 아래 뉴스를 한국어로 핵심만 5~7개 요약하세요. 제목은 굵게 처리하고 이모지를 사용하세요. 각 뉴스 끝에 [원문] 링크를 포함하세요.\n\n{raw_news}"
        
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"뉴스 요약 중 오류 발생: {e}"

def get_crypto_report():
    try:
        # 데이터 수집 (시총, 도미넌스, 가격, 김프, 공탐지수)
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

        # 리포트 구성
        today = datetime.now().strftime('%Y-%m-%d %H:%M')
        report =  f"■ <b>MY COIN DAILY REPORT</b>\n"
        report += f"발행일시: {today}\n"
        report += f"━━━━━━━━━━━━━━━━━━\n\n"
        
        report += f"<b>[비트코인 실시간 시세]</b>\n"
        report += f"KRW: <b>{upbit_price:,.0f}원</b>\n"
        report += f"KIMP: <b>{kimp:.2f}%</b>\n\n"
        
        report += f"<b>[시장 주요 지표]</b>\n"
        report += f"공포탐욕지수: {fng_value} ({fng_kor})\n"
        report += f"BTC 점유율: {btc_dom:.1f}%\n"
        report += f"글로벌 시총: ${total_mcap/1e12:.2f}T\n\n"
        
        report += f"🚀 <b>AI 가상자산 뉴스 요약</b>\n"
        report += get_ai_news_briefing()
        
        report += f"\n━━━━━━━━━━━━━━━━━━\n"
        report += f"<b>마이코인 리포트 데이터 센터</b>"
        
        return report
    except Exception as e:
        return f"데이터 로드 오류: {e}"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # 두 개의 방에 순서대로 꼼꼼하게 배달합니다.
    for chat_id in CHAT_IDS:
        params = {
            "chat_id": chat_id, 
            "text": text, 
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        requests.get(url, params=params)

# 최종 실행
final_msg = get_crypto_report()
send_telegram(final_msg)
