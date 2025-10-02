"""
투자 에이전트 설정 파일 예제
실제 사용시 이 파일을 config.py로 복사하고 API 키를 입력하세요.
"""

import os
from typing import Dict, Any

# API 키 설정 (실제 키로 교체 필요)
API_KEYS = {
    "OPENAI_API_KEY": "your-openai-api-key-here",
    "DEEPSEARCH_API_KEY": "your-deepsearch-api-key-here",
    "NEWSAPI_KEY": "your-newsapi-key-here",
    "FINNHUB_API_KEY": "your-finnhub-api-key-here",
    "SLACK_APP_ID": "your-slack-app-id",
    "SLACK_CLIENT_ID": "your-slack-client-id",
    "SLACK_CLIENT_SECRET": "your-slack-client-secret",
    "SLACK_SIGNING_SECRET": "your-slack-signing-secret",
    "SLACK_VERIFICATION_TOKEN": "your-slack-verification-token",
    "SLACK_BOT_TOKEN": "your-slack-bot-token-here"
}

# 애플리케이션 설정
APP_CONFIG = {
    "SCHEDULE_TIME": "09:00",  # 매일 오전 9시 실행
    "TIMEZONE": "Asia/Seoul",
    "DATA_DIR": "data",
    "RAW_DATA_DIR": "data/raw",
    "REPORTS_DIR": "data/reports",
    "DEEPSEARCH_DOCS_DIR": "deepsearch_docs"
}

# API 엔드포인트 설정
API_ENDPOINTS = {
    "OPENAI_BASE_URL": "https://api.openai.com/v1",
    "DEEPSEARCH_BASE_URL": "https://api.deepsearch.kr",
    "NEWSAPI_BASE_URL": "https://newsapi.org/v2",
    "FINNHUB_BASE_URL": "https://finnhub.io/api/v1",
    "SLACK_BASE_URL": "https://slack.com/api"
}

# 모델 설정
MODEL_CONFIG = {
    "OPENAI_MODEL": "gpt-4o",  # gpt-5가 아직 공개되지 않았으므로 gpt-4o 사용
    "TEMPERATURE": 0.7,
    "MAX_TOKENS": 4000
}

def get_api_key(key_name: str) -> str:
    """API 키를 반환합니다."""
    return API_KEYS.get(key_name, "")

def get_config(config_name: str) -> Any:
    """설정값을 반환합니다."""
    return APP_CONFIG.get(config_name, "")

def get_endpoint(endpoint_name: str) -> str:
    """API 엔드포인트를 반환합니다."""
    return API_ENDPOINTS.get(endpoint_name, "")

def get_model_config(config_name: str) -> Any:
    """모델 설정을 반환합니다."""
    return MODEL_CONFIG.get(config_name, "")

# 환경 변수로 오버라이드 가능
def load_from_env():
    """환경 변수에서 설정을 로드합니다."""
    for key in API_KEYS:
        env_value = os.getenv(key)
        if env_value:
            API_KEYS[key] = env_value

# 초기화 시 환경 변수 로드
load_from_env()
