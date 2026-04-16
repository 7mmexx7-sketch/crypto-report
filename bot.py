import requests
from datetime import datetime
import os
import xml.etree.ElementTree as ET

# --- [정보 입력] ---
TELEGRAM_TOKEN = "8548489549:AAHkc7-PZrGHWPk-7EpyhK7CpiD4ZOu8bQ4"
CHAT_IDS = ["-1003807258780"] 

CMC_API_KEY = "c59e814980984b0c9fdd8c1429c70fcd"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
# ------------------

def fetch_rss_news(url, limit=5):
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

def get_market_briefing():
    if not OPENAI_API_KEY:
        return "분석 엔진 동기화가 진행 중입니다. 잠시 후 다시 확인해 주세요."
    
    ct_news = fetch_rss_news("https://cointelegraph.com/rss", limit=5)
    cd_news = fetch_rss_news("https://www.coindesk.com/arc/outboundfeeds/rss/", limit=5)
    
    combined_news = f"[Source: CoinTelegraph]\n{ct_news}\n[Source: CoinDesk]\n{cd_news}"

    if not ct_news and not cd_news:
        return "현재 글로벌 외신망 동기화 지연으로 인해 데이터를 불러올 수 없습니다."

    prompt = (
        "당신은 가상자산 리서치 수석 분석가입니다. 제공된 뉴스 목록을 바탕으로 두 가지 섹션을 작성하십시오. "
        "모든 답변에서 'AI' 또는 '인공지능'이라는 단어를 절대 사용하지 마십시오.\n\n"
        "섹션 1. 주요 뉴스 요약:\n"
        "가장 중요한 소식 6개를 선정하여 요약하십시오. 반드시 CoinTelegraph에서 3개, CoinDesk에서 3개를 선정하십시오. "
        "제목은 <b>제목</b> 형태로 작성하고, 뉴스 끝에 <a href=\"URL\">[상세 리포트 원문]</a> 링크를 포함하십시오.\n\n"
        "섹션 2. 시장 종합 분석 및 전망:\n"
        "위 6개 뉴스를 토대로 현재 가상자산 시장의 전체적인 동향과 핵심 트렌드를 3~4문장으로 요약하여 브리핑하십시오. "
        "전문적이고 객관적인 시각을 유지하십시오.\n\n"
        "【준수 사항】\n"
        "1. 모든 이모티콘을 절대 사용하지 마십시오.\n"
        "2. 격식 있고 전문적인 문체로 작성하십시오.\n"
        "3. Markdown 기호 대신 텔레그램 HTML 태그(<b>, <a>)만 사용하십시오.\n\n"
        f"분석 데이터:\n{combined_news}"
    )
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code != 200:
            return "분석 엔진 트래픽 과부하로 인해 요약 작업이 지연되었습니다."
            
        return response.json()['choices'][0]['message']['content']
    except:
        return "글로벌 뉴스망 동기화 지연으로 인해 요약 서비스가 일시 제한되었습니다."

def get_crypto_report():
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
        ai_briefing = get_market_briefing()
        
        msg = []
        msg.append("■ <b>MY COIN DAILY REPORT</b>")
        msg.append(f"발행일시: {today}")
        msg.append("━━━━━━━━━━━━━━━━━━")
        msg.append("")
        msg.append("<b>[비트코인 실시간 시세]</b>")
        msg.append(f"KRW: <b>{upbit_price:,.0f}원</b>")
        msg.append("")
        msg.append("<b>[시장 주요 지표]</b>")
        msg.append(f"공포탐욕지수: {fng_value} ({fng_status})")
        msg.append(f"BTC 점유율: {btc_dom:.1f}%")
        msg.append(f"글로벌 시총: ${total_mcap/1e12:.2f}T")
        msg.append("")
        msg.append("<b>[글로벌 크립토 인사이트 브리핑]</b>")
        msg.append(ai_briefing)
        msg.append("")
        msg.append("━━━━━━━━━━━━━━━━━━")
        msg.append("<b>[프라이빗 트레이딩 데스크]</b>")
        msg.append("기관급 실시간 매매 시그널 및 1:1 심층 포트폴리오 상담을 경험하실 수 있는 특별 무료 체험 라운지를 운영 중입니다.")
        msg.append("아래 링크를 통해 전용 채널로 입장하시어 프리미엄 혜택을 무료로 누려보십시오.")
        msg.append("<a href=\"https://t.me/crestlab77\">[프라이빗 라이브 타점 무료 체험 및 상담 신청]</a>")
        msg.append("━━━━━━━━━━━━━━━━━━")
        msg.append("<b>외신 인텔리전스 파이낸셜 인텔리전스 센터</b>")
        
        return "\n".join(msg)
    except:
        return "데이터 수집 서버 점검 중입니다. 잠시 후 다시 확인해 주세요."

def send_telegram(text):
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
