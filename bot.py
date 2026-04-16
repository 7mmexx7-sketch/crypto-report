import requests
from datetime import datetime
import os

# --- [정보 입력] ---
# 1. 텔레그램 봇 설정
TELEGRAM_TOKEN = "8548489549:AAHkc7-PZrGHWPk-7EpyhK7CpiD4ZOu8bQ4"
# 2. 리포트를 보낼 방 번호 목록 (기존 방 & 새 방)
CHAT_IDS = ["-1003807258780", "-1002443665222"] 

# 3. API 키 설정 (깃허브 Secrets와 이름을 통일했습니다)
CMC_API_KEY = "c59e814980984b0c9fdd8c1429c70fcd"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
# ------------------

def get_ai_news_briefing():
    """해외 핫 이슈를 가져와 AI가 한국어로 요약합니다."""
    if not OPENAI_API_KEY:
        return "⚠️ OpenAI API 키가 설정되지 않았습니다. 깃허브 Secrets를 확인해주세요."
    
    try:
        # 뉴스 데이터 가져오기 (CryptoPanic API)
        news_url = "https://cryptopanic.com/api/v1/posts/?auth_token=PUBLIC&filter=hot"
        news_data = requests.get(news_url).json()
        raw_news = ""
        for post in news_data['results'][:10]: # 최신 뉴스 10개 추출
            raw_news += f"Title: {post['title']}\nLink: {post['url']}\n\n"

        # AI에게 요약 요청
        prompt = f"당신은 가상자산 전문가입니다. 아래 뉴스를 한국어로 핵심만 7개 요약하세요. 제목은 굵게 처리하고 이모지를 사용하세요. 각 뉴스 끝에 [원문] 링크를 포함하세요.\n\n{raw_news}"
        
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
    """시황 데이터를 수집하여 리포트를 작성합니다."""
    try:
        # 1. 글로벌 메트릭 (시총, 도미넌스)
        cmc_url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        cmc_res = requests.get(cmc_url, headers={"X-CMC_PRO_API_KEY": CMC_API_KEY}).json()
        btc_dom = cmc_res['data']['btc_dominance']
        total_mcap = cmc_res['data']['quote']['USD']['total_market_cap']

        # 2. 업비트 비트코인 가격
        upbit_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC").json()
        upbit_price = float(upbit_res[0]['trade_price'])
        
        # 3. 공포탐욕지수
        fng_res = requests.get("https://api.alternative.me/fng/").json()
        fng_value = fng_res['data'][0]['value']
        fng_status = fng_res['data'][0]['value_classification']

        # 리포트 양식 조립
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
        
        report += f"🚀 <b>AI 가상자산 뉴스 요약</b>\n"
        report += get_ai_news_briefing()
        
        report += f"\n━━━━━━━━━━━━━━━━━━\n"
        report += f"<b>마이코인 리포트 데이터 센터</b>"
        
        return report
    except Exception as e:
        return f"데이터 로드 오류: {e}"

def send_telegram(text):
    """지정된 모든 채널에 리포트를 발송합니다."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        params = {
            "chat_id": chat_id, 
            "text": text, 
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        requests.get(url, params=params)

# 실행부
if __name__ == "__main__":
    final_msg = get_crypto_report()
    send_telegram(final_msg)
