import requests
from datetime import datetime
import os

# --- [정보 입력] ---
TELEGRAM_TOKEN = "8548489549:AAHkc7-PZrGHWPk-7EpyhK7CpiD4ZOu8bQ4"
CHAT_IDS = ["-1003807258780", "-1002443665222"] 
CMC_API_KEY = "c59e814980984b0c9fdd8c1429c70fcd"

# ⭐ 절대 여기에 sk- 키를 직접 적지 마세요! 금고에서 자동으로 가져옵니다.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
# ------------------

def get_ai_news_briefing():
    if not OPENAI_API_KEY:
        return "⚠️ OpenAI API 키가 설정되지 않았습니다."
    try:
        news_url = "https://cryptopanic.com/api/v1/posts/?auth_token=PUBLIC&filter=hot"
        news_data = requests.get(news_url).json()
        raw_news = ""
        for post in news_data['results'][:12]:
            raw_news += f"Title: {post['title']}\nLink: {post['url']}\n\n"

        prompt = f"가상자산 전문가로서 아래 뉴스를 한국어로 핵심만 7개 요약하세요. 제목 굵게, 이모지 포함, [원문] 링크 필수.\n\n{raw_news}"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5}
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"뉴스 요약 중 오류 발생: {e}"

def get_crypto_report():
    try:
        # 시황 데이터 수집
        cmc_url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        cmc_res = requests.get(cmc_url, headers={"X-CMC_PRO_API_KEY": CMC_API_KEY}).json()
        btc_dom, total_mcap = cmc_res['data']['btc_dominance'], cmc_res['data']['quote']['USD']['total_market_cap']
        upbit_price = float(requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC").json()[0]['trade_price'])
        fng_res = requests.get("https://api.alternative.me/fng/").json()
        fng_val, fng_status = fng_res['data'][0]['value'], fng_res['data'][0]['value_classification']

        # 리포트 조립
        today = datetime.now().strftime('%Y-%m-%d %H:%M')
        report =  f"■ <b>MY COIN DAILY REPORT</b>\n발행일시: {today}\n━━━━━━━━━━━━━━━━━━\n\n"
        report += f"<b>[비트코인 실시간 시세]</b>\nKRW: <b>{upbit_price:,.0f}원</b>\n\n"
        report += f"<b>[시장 주요 지표]</b>\n공포탐욕지수: {fng_val} ({fng_status})\nBTC 점유율: {btc_dom:.1f}%\n\n"
        report += f"🚀 <b>AI 가상자산 뉴스 요약</b>\n{get_ai_news_briefing()}\n"
        report += f"\n━━━━━━━━━━━━━━━━━━\n<b>마이코인 리포트 데이터 센터</b>"
        return report
    except Exception as e:
        return f"데이터 오류: {e}"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        requests.get(url, params={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True})

final_msg = get_crypto_report()
send_telegram(final_msg)
