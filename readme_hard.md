🏗️ 해외주식 투자 제안 에이전트 아키텍처
📊 시스템 아키텍처 다이어그램

┌─────────────────────────────────────────────────────────────────┐
│                        스케줄러 (APScheduler)                      │
│                    (매일 오전 9시, 주말 제외)                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                  메인 오케스트레이터 에이전트                        │
│            (전체 워크플로우 관리 및 조정)                           │
└──────┬───────────────┬───────────────┬──────────────┬───────────┘
       │               │               │              │
       ▼               ▼               ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Data     │   │ Parsing  │   │ Analysis │   │ Report   │
│ Agent    │──▶│ Agent    │──▶│ Agent    │──▶│ Agent    │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
       │               │               │              │
       ▼               ▼               ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│Deepsearch│   │Coordinator│  │Investment │   │  PDF     │
│  API     │   │  Agent   │   │  Analyst  │   │Generator │
│Finnhub   │   │Sub-Agents│   │  Finance  │   │          │
│  API     │   │(병렬처리) │   │  Analyst  │   │          │
└──────────┘   └──────────┘   │ Summarizer│   └──────────┘
                               └──────────┘          │
                                                     ▼
                                              ┌──────────┐
                                              │ Slack    │
                                              │  Agent   │
                                              └──────────┘


🗂️ 프로젝트 폴더 구조
investment-agent/
│
├── config/
│   ├── __init__.py
│   ├── settings.py              # 환경변수 및 설정 관리
│   └── api_keys.py              # API 키 관리 (암호화 권장)
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py          # 메인 오케스트레이터
│   ├── data_agent.py            # 데이터 수집 에이전트
│   ├── parsing_agent.py         # 파싱 코디네이터
│   ├── analysis_agent.py        # 분석 에이전트
│   └── report_agent.py          # 리포트 생성 에이전트
│
├── sub_agents/
│   ├── __init__.py
│   ├── news_parser.py           # 뉴스 파싱 하위 에이전트
│   ├── macro_parser.py          # 거시경제 파싱
│   ├── stock_parser.py          # 주식 데이터 파싱
│   └── editor_agent.py          # 편집자 에이전트
│
├── analyzers/
│   ├── __init__.py
│   ├── investment_analyst.py    # 투자 전문가
│   ├── finance_analyst.py       # 재무 분석가
│   └── summarizer.py            # 최종 요약 에이전트
│
├── integrations/
│   ├── __init__.py
│   ├── deepsearch_client.py     # Deepsearch API 클라이언트
│   ├── finnhub_client.py        # Finnhub API 클라이언트
│   ├── slack_client.py          # Slack API 클라이언트
│   └── pdf_generator.py         # PDF 생성
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                # 로깅 유틸
│   ├── error_handler.py         # 에러 핸들링
│   ├── cache_manager.py         # 캐싱 관리
│   └── validators.py            # 데이터 검증
│
├── data/
│   ├── raw/                     # 원본 데이터
│   ├── processed/               # 처리된 데이터
│   └── reports/                 # 생성된 리포트
│
├── tests/
│   ├── test_agents.py
│   ├── test_integrations.py
│   └── test_utils.py
│
├── main.py                      # 메인 실행 파일
├── scheduler.py                 # 스케줄러
├── requirements.txt
├── .env.example
└── README.md

파일: requirements.txt
langchain==0.1.0
langchain-openai==0.0.5
openai==1.12.0
python-dotenv==1.0.0
requests==2.31.0
pandas==2.2.0
slack-sdk==3.27.0
apscheduler==3.10.4
reportlab==4.1.0
aiohttp==3.9.3
asyncio==3.4.3
python-dateutil==2.8.2
pydantic==2.6.1