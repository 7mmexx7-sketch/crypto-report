import requests
from datetime import datetime
import os

# --- [정보 입력] ---
TELEGRAM_TOKEN = "8548489549:AAHkc7-PZrGHWPk-7EpyhK7CpiD4ZOu8bQ4"
CHAT_IDS = ["-1003807258780", "-1002443665222"] 

CMC_API_KEY = "c59e814980984b0c9fdd8c1429c70fcd"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
# ------------------

def get_ai_news_briefing():
    """해외 뉴스를 가져와 AI(GPT-4o-mini)로 요약합니다."""
    if not OPENAI_API_KEY:
        return "AI 분석 엔진 동기화가 진행 중입니다. 잠시 후 다시 확인해 주세요."
    
    try:
        news_url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
        news_res = requests.get(news_url)
        
        if news_res.status_code != 200:
            return "글로벌 외신 데이터망 접속이 지연되고 있습니다. 신속히 복구하겠습니다."
            
        news_data = news_res.json()
        news_list = news_data.get('Data', [])

        if not isinstance(news_list, list):
            return "현재 외신 서버의 트래픽 급증으로 요약 데이터 제공이 일시 지연되고 있습니다."

        raw_news = ""
        for post in news_list[:10]:
            title = post.get('title', '')
            url = post.get('url', '')
            if title and url:
                raw_news += f"Title: {title}\nLink: {url}\n\n"

        if not raw_news.strip():
            return "현재 시장에 주목할 만한 특이 동향 외신이 없습니다."

        prompt = f"당신은 가상자산 전문가입니다. 아래 뉴스를 한국어로 핵심만 7개 요약하세요. 제목은 굵게 처리하고 격식 있는 문체로 작성하세요. 각 뉴스 끝에 [원문] 링크를 포함하세요.\n\n{raw_news}"
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        
        if response.status_code != 200:
            return "AI 분석 엔진 트래픽 과부하로 인해 요약 작업이 지연되었습니다."
            
        return response.json()['choices'][0]['message']['content']
        
    except Exception:
        return "글로벌 뉴스망 동기화 지연으로 인해 요약 서비스가 일시 제한되었습니다. 빠르고 정확한 정보를 위해 신속히 정상화하겠습니다."

def get_crypto_report():
    """모든 데이터를 취합하여 최종 리포트를 작성합니다."""
    try:
        cmc_url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        cmc_res = requests.get(cmc_url, headers={"X-CMC_PRO_API_KEY": CMC_API_KEY}).json()
        btc_dom = cmc_res['data']['btc_dominance']
        total_mcap = cmc_res['data']['quote']['USD']['total_market_cap']

        upbit_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC").json()
        upbit_price = float(upbit_res[0]['trade_price'])
        
        fng_res = requests.get("https://api.alternative.me/fng/").json()
        fng_value = fng_res['data'][0]['value']
        fng_status = fng_res['data'][0]['value_classification']

        today = datetime.now().strftime('%Y-%m-%d %H:%M')
        report =  f"■ <b>MY COIN DAILY REPORT</b>\n"
        report += f"발행일시: {today}\n"
        report += f"━━━━━━━━━━━━━━━━━━\n\n"
        
        report += f"<b>[비트코인 실시간 시세]</b>\n"
        report += f"KRW: <b>{upbit_price:,.0f}원</b>\n\n"
        
        report += f"<b>[시장 주요 지표]</b>\n"
        report += f"공포탐욕지수: {fng_value} ({fng_status})\n"
        report += f"BTC 점유율: {btc_dom:.1f}%\n"
        report += f"글로벌 시총: ${total_mcap/1e12:.2f}T\n\n"
        
        report += f"<b>[AI 가상자산 뉴스 요약]</b>\n"
        report += get_ai_news_briefing()
        
        report += f"\n━━━━━━━━━━━━━━━━━━\n"
        report += f"<b>마이코인 리포트 데이터 센터</b>"
        
        return report
    except Exception:
        return "시황 데이터 수집 서버 점검 중입니다. 잠시 후 다시 확인해 주세요."

def send_telegram(text):
    """지정된 모든 텔레그램 채널로 메시지를 발송합니다."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        params = {
            "chat_id": chat_id, 
            "text": text, 
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        requests.get(url, params=params)

if __name__ == "__main__":
    final_msg = get_crypto_report()
    send_telegram(final_msg)
