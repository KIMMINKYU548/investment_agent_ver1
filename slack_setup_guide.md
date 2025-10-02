# Slack API 설정 가이드

## 🔧 Slack Bot Token 생성 방법

### 1단계: Slack 앱 생성
1. [Slack API 페이지](https://api.slack.com/apps)에 접속
2. "Create New App" 클릭
3. "From scratch" 선택
4. 앱 이름 입력 (예: "Investment Agent")
5. 워크스페이스 선택 후 "Create App" 클릭

### 2단계: Bot 권한 설정
1. 좌측 메뉴에서 "OAuth & Permissions" 클릭
2. "Bot Token Scopes" 섹션에서 다음 권한들 추가:
   - `chat:write` - 메시지 전송
   - `chat:write.public` - 공개 채널에 메시지 전송
   - `files:write` - 파일 업로드
   - `channels:read` - 채널 목록 조회
   - `users:read` - 사용자 정보 조회

### 3단계: 앱 설치 및 토큰 획득
1. "Install to Workspace" 버튼 클릭
2. 권한 승인
3. 설치 완료 후 "Bot User OAuth Token" 복사
   - 형태: `xoxb-xxxxxxxxxx-xxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx`

### 4단계: config.py 업데이트
```python
# config.py에서 SLACK_CLIENT_SECRET을 올바른 Bot Token으로 변경
API_KEYS = {
    # ... 다른 키들 ...
    "SLACK_BOT_TOKEN": "xoxb-your-actual-bot-token-here",
}
```

## 🔍 현재 문제점과 해결책

### 문제 1: 잘못된 토큰 타입
- **현재**: `SLACK_CLIENT_SECRET` (앱 시크릿)
- **올바른**: `SLACK_BOT_TOKEN` (봇 토큰)

### 문제 2: 권한 부족
- 봇이 필요한 권한을 가지고 있지 않음
- 위의 2단계에서 권한을 추가해야 함

## 📝 테스트 방법

### 1. 토큰 테스트
```python
from api_clients_enhanced import SlackClientFixed

client = SlackClientFixed()
if client.test_connection():
    print("✅ Slack 연결 성공!")
else:
    print("❌ Slack 연결 실패")
```

### 2. 메시지 전송 테스트
```python
# 테스트 메시지 전송
result = client.send_message("#general", "안녕하세요! 투자 에이전트입니다.")
print(result)
```

### 3. 채널 목록 조회 테스트
```python
channels = client.get_channels()
print(f"사용 가능한 채널: {len(channels.get('channels', []))}개")
```

## 🚨 주의사항

1. **토큰 보안**: Bot Token은 절대 공개하지 마세요
2. **권한 최소화**: 필요한 최소한의 권한만 부여하세요
3. **테스트**: 먼저 테스트 채널에서 기능을 확인하세요
4. **Rate Limit**: API 호출 제한을 고려하세요

## 🔄 설정 완료 후

1. `config.py`에서 올바른 Bot Token 설정
2. `api_clients.py`에서 `SLACK_CLIENT_SECRET` → `SLACK_BOT_TOKEN` 변경
3. 테스트 실행하여 연결 확인
4. 투자 에이전트에서 Slack 알림 기능 활성화
