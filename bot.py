def get_ai_news_briefing():
    if not OPENAI_API_KEY:
        return "⚠️ OpenAI API 키가 설정되지 않았습니다."
    
    try:
        news_url = "https://cryptopanic.com/api/v1/posts/?auth_token=PUBLIC&filter=hot"
        news_data = requests.get(news_url).json()
        raw_news = ""
        for post in news_data['results'][:10]:
            raw_news += f"Title: {post['title']}\nLink: {post['url']}\n\n"

        prompt = f"가상자산 전문가로서 아래 뉴스를 한국어로 핵심만 7개 요약하세요. 제목 굵게, 이모지 포함, [원문] 링크 필수.\n\n{raw_news}"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5}
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        
        # [수정된 부분] 응답이 비어있는지 확인합니다.
        if response.status_code != 200:
            return f"⚠️ AI 요약 일시 중단 (OpenAI 서버 응답 없음: {response.status_code})\n결제 잔액 확인이 필요할 수 있습니다."
            
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        # 에러가 나더라도 어떤 에러인지 정확히 알려줍니다.
        return f"뉴스 요약 서비스 준비 중입니다. (사유: {e})"
