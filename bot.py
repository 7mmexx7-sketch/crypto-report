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
        return "⚠️ OpenAI API 키가 설정되지 않았습니다. 깃허브 Secrets를 확인해주세요."
    
    try:
        # 1. 가입이 필요 없는 무료 뉴스 API로 변경 (CryptoCompare)
        news_url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
        news_res = requests.get(news_url)
        
        if news_res.status_code != 200:
            return f"⚠️ 뉴스 사이트 접속 지연 (서버 응답: {news_res.status_code})"
            
        news_data = news_res.json()
        raw_news = ""
        
        # 최신 뉴스 10개 추출
        for post in news_data.get('Data', [])[:10]:
            raw_news += f"Title: {post['title']}\nLink: {post['url']}\n\n"

        if not raw_news:
            return "현재 새로운 핫 뉴스가 없습니다."

        # 2. OpenAI API 호출 (AI 요약)
        prompt = f"당신은 가상자산 전문가입니다. 아래 뉴스를 한국어로 핵심만 7개 요약하세요. 제목은 굵게 처리하고 이모지를 사용하세요. 각 뉴스 끝에 [원문] 링크를 포함하세요.\n\n{raw_news}"
        
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
        
        # 서버 응답 확인
        if response.status_code != 200:
            return f"⚠️ AI 요약 서비스 일시 지연 (OpenAI 에러: {response.status_code})\n충전 잔액이 아직 시스템에 반영되지 않았을 수 있습니다."
            
        return response.json()['choices'][0]['message']['content']
        
    except Exception as e:
        return f"뉴스 요약 서비스 준비 중입니다. (사유: {e})"

def get_crypto_report():
    """모든 데이터를 취합하여 최종 리포트를 작성합니다."""
    try:
        # 1. 글로벌 시황 (시총, 도미넌스)
        cmc_url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        cmc_res = requests.get(cmc_url, headers={"X-CMC_PRO_API_KEY": CMC_API_KEY}).json()
        btc_dom = cmc_res['data']['btc_dominance']
        total_mcap = cmc_res['data']['quote']['USD']['total_market_cap']

        # 2. 업비트 비트코인 시세
        upbit_res = requests.get("https://api.upbit.com/v1/ticker?markets=KRW-BTC").json()
        upbit_price = float(upbit_res[0]['trade_price'])
        
        # 3. 공포탐욕지수
        fng_res = requests.get("https://api.alternative.me/fng/").json()
        fng_value = fng_res['data'][0]['value']
        fng_status = fng_res['data'][0]['value_classification']

        # 리포트 양식 구성
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
        return f"데이터 수집 중 오류 발생: {e}"

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

# 메인 실행부
if __name__ == "__main__":
    final_msg = get_crypto_report()
    send_telegram(final_msg)
