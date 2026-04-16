import requests
from datetime import datetime
import os
import xml.etree.ElementTree as ET

# --- [정보 입력] ---
TELEGRAM_TOKEN = "8548489549:AAHkc7-PZrGHWPk-7EpyhK7CpiD4ZOu8bQ4"
CHAT_IDS = ["-1003807258780", "-1002443665222"] 

CMC_API_KEY = "c59e814980984b0c9fdd8c1429c70fcd"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
# ------------------

def fetch_rss_news(url, limit=5):
    """지정한 RSS URL에서 뉴스를 가져옵니다."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return ""
        root = ET.fromstring(res.content)
        news_text = ""
        for item in root.findall('.//item')[:limit]:
            title = item.find('title').text
            link = item.find('link').text
            news_text += f"Title: {title}\nLink: {link}\n\n"
        return news_text
    except:
        return ""

def get_ai_news_briefing():
    """두 곳의 외신 출처에서 뉴스를 수집하여 AI로 요약합니다."""
    if not OPENAI_API_KEY:
        return "AI 분석 엔진 동기화가 진행 중입니다. 잠시 후 다시 확인해 주세요."
    
    ct_news = fetch_rss_news("https://cointelegraph.com/rss", limit=5)
    cd_news = fetch_rss_news("https://www.coindesk.com/arc/outboundfeeds/rss/", limit=5)
    
    combined_news = f"[Source: CoinTelegraph]\n{ct_news}\n[Source: CoinDesk]\n{cd_news}"

    if not ct_news and not cd_news:
        return "현재 글로벌 외신망 동기화 지연으로 인해 데이터를 불러올 수 없습니다."

    prompt = (
        "당신은 가상자산 리서치 분석가입니다. 제공된 뉴스 목록을 바탕으로 가장 중요한 소식 6개를 선정하여 요약하십시오. "
        "반드시 CoinTelegraph에서 3개, CoinDesk에서 3개를 균형 있게 선정하십시오. "
        "결과는 한국어로 작성하며 제목은 굵게 처리하고 격식 있는 문체를 유지하십시오. "
        "이모티콘이나 감정적인 표현은 일절 배제하십시오. 각 뉴스 끝에 [원문] 링크를 포함하십시오.\n\n"
        f"{combined_news}"
    )
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code != 200:
            return "AI 분석 엔진 트래픽 과부하로 인해 요약 작업이 지연되었습니다."
            
        return response.json()['choices'][0]['message']['content']
    except:
        return "글로벌 뉴스망 동기화 지연으로 인해 요약 서비스가 일시 제한되었습니다."

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
        
        report += f"<b>[글로벌 크립토 인사이트 브리핑]</b>\n"
        report += get_ai_news_briefing()
        
        report += f"\n━━━━━━━━━━━━━━━━━━\n"
        report += f"<b>외신 인텔리전스 파이낸셜 인텔리전스 센터</b>"
        
        return report
    except:
        return "데이터 수집 서버 점검 중입니다. 잠시 후 다시 확인해 주세요."

def send_telegram(text):
    """지정된 모든 텔레그램 채널로 리포트를 발송합니다."""
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
