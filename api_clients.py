"""
API 클라이언트 모듈
Deepsearch, Finnhub, Slack API를 위한 클라이언트들을 포함합니다.
"""

import requests
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from config import get_api_key, get_endpoint


class DeepsearchClient:
    """Deepsearch API 클라이언트"""
    
    def __init__(self):
        self.api_key = get_api_key("DEEPSEARCH_API_KEY")
        self.base_url = "https://api-v2.deepsearch.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """API 요청을 수행합니다."""
        if params is None:
            params = {}
        
        # API 키를 파라미터에 추가
        params["api_key"] = self.api_key
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            return {"error": str(e)}
    
    def get_articles(self, 
                    keyword: str = None,
                    company_name: str = None,
                    symbols: str = None,
                    date_from: str = None,
                    date_to: str = None,
                    page: int = 1,
                    page_size: int = 10,
                    highlight: str = None,
                    clustering: bool = None) -> Dict[str, Any]:
        """
        국내 기사 검색
        
        Args:
            keyword: 검색 키워드
            company_name: 기업명
            symbols: 종목코드 (예: KRX:005930)
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            page: 페이지 번호
            page_size: 페이지 크기
            highlight: 하이라이트 타입 (unified, unified_non_tags)
            clustering: 클러스터링 포함 여부
        """
        params = {}
        if keyword:
            params["keyword"] = keyword
        if company_name:
            params["company_name"] = company_name
        if symbols:
            params["symbols"] = symbols
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
        if highlight:
            params["highlight"] = highlight
        if clustering is not None:
            params["clustering"] = clustering
            
        return self._make_request("/articles", params)
    
    def get_articles_by_section(self, 
                               sections: str,
                               keyword: str = None,
                               company_name: str = None,
                               symbols: str = None,
                               date_from: str = None,
                               date_to: str = None,
                               page: int = 1,
                               page_size: int = 10) -> Dict[str, Any]:
        """
        섹션별 기사 검색 (economy, tech, politics 등)
        
        Args:
            sections: 섹션명 (쉼표로 구분, 예: "economy,tech")
        """
        params = {}
        if keyword:
            params["keyword"] = keyword
        if company_name:
            params["company_name"] = company_name
        if symbols:
            params["symbols"] = symbols
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
            
        return self._make_request(f"/articles/{sections}", params)
    
    def get_global_articles(self, 
                           keyword: str = None,
                           company_name: str = None,
                           symbols: str = None,
                           date_from: str = None,
                           date_to: str = None,
                           page: int = 1,
                           page_size: int = 10) -> Dict[str, Any]:
        """
        해외 기사 검색
        
        Args:
            keyword: 검색 키워드
            company_name: 기업명
            symbols: 종목코드 (예: NYSE:AAPL)
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            page: 페이지 번호
            page_size: 페이지 크기
        """
        params = {}
        if keyword:
            params["keyword"] = keyword
        if company_name:
            params["company_name"] = company_name
        if symbols:
            params["symbols"] = symbols
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
            
        return self._make_request("/global-articles", params)
    
    def get_global_articles_by_section(self, 
                                      sections: str,
                                      keyword: str = None,
                                      company_name: str = None,
                                      symbols: str = None,
                                      date_from: str = None,
                                      date_to: str = None,
                                      page: int = 1,
                                      page_size: int = 10) -> Dict[str, Any]:
        """
        해외 섹션별 기사 검색 (business, technology, economy 등)
        
        Args:
            sections: 섹션명 (쉼표로 구분, 예: "business,technology")
        """
        params = {}
        if keyword:
            params["keyword"] = keyword
        if company_name:
            params["company_name"] = company_name
        if symbols:
            params["symbols"] = symbols
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
            
        return self._make_request(f"/global-articles/{sections}", params)
    
    def get_topics(self, 
                  company_name: str = None,
                  symbols: str = None,
                  date_from: str = None,
                  date_to: str = None,
                  page: int = 1,
                  page_size: int = 10) -> Dict[str, Any]:
        """
        토픽 검색
        
        Args:
            company_name: 기업명
            symbols: 종목코드
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            page: 페이지 번호
            page_size: 페이지 크기
        """
        params = {}
        if company_name:
            params["company_name"] = company_name
        if symbols:
            params["symbols"] = symbols
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
            
        return self._make_request("/articles/topics", params)
    
    def get_trending_topics(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """트렌딩 토픽 조회"""
        params = {
            "page": page,
            "page_size": page_size
        }
        return self._make_request("/articles/topics/trending", params)
    
    def get_topic_detail(self, topic_id: str) -> Dict[str, Any]:
        """특정 토픽 상세 조회"""
        return self._make_request(f"/articles/topics/trending/{topic_id}")
    
    def get_aggregation(self, 
                       keyword: str,
                       groupby: str,
                       date_from: str = None,
                       date_to: str = None,
                       page: int = 1,
                       page_size: int = 10) -> Dict[str, Any]:
        """
        집계 데이터 조회
        
        Args:
            keyword: 검색 키워드
            groupby: 그룹핑 필드 (companies.name, publisher, sections 등)
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            page: 페이지 번호
            page_size: 페이지 크기
        """
        params = {
            "keyword": keyword,
            "groupby": groupby,
            "page": page,
            "page_size": page_size
        }
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
            
        return self._make_request("/articles/aggregation", params)
    
    def get_global_aggregation(self, 
                              keyword: str,
                              groupby: str,
                              date_from: str = None,
                              date_to: str = None,
                              page: int = 1,
                              page_size: int = 10) -> Dict[str, Any]:
        """
        해외 집계 데이터 조회
        
        Args:
            keyword: 검색 키워드
            groupby: 그룹핑 필드 (company.company_name, publisher, sections 등)
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            page: 페이지 번호
            page_size: 페이지 크기
        """
        params = {
            "keyword": keyword,
            "groupby": groupby,
            "page": page,
            "page_size": page_size
        }
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
            
        return self._make_request("/global-articles/aggregation", params)
    
    def get_filings(self, 
                   keyword: str = None,
                   company_name: str = None,
                   symbol: str = None,
                   date_from: str = None,
                   date_to: str = None,
                   page: int = 1,
                   page_size: int = 10) -> Dict[str, Any]:
        """
        해외 공시 검색
        
        Args:
            keyword: 검색 키워드
            company_name: 기업명
            symbol: 종목코드 (예: AAPL)
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            page: 페이지 번호
            page_size: 페이지 크기
        """
        params = {}
        if keyword:
            params["keyword"] = keyword
        if company_name:
            params["company_name"] = company_name
        if symbol:
            params["symbol"] = symbol
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
            
        return self._make_request("/filings", params)
    
    def get_filing_detail(self, accession_number: str) -> Dict[str, Any]:
        """특정 공시 상세 조회"""
        return self._make_request(f"/filings/{accession_number}")
    
    def get_filing_summary(self, accession_number: str) -> Dict[str, Any]:
        """특정 공시 요약 조회"""
        return self._make_request(f"/filings/{accession_number}/summary")
    
    def get_filing_aggregation(self, 
                              keyword: str,
                              groupby: str,
                              date_from: str = None,
                              date_to: str = None,
                              size: int = 10) -> Dict[str, Any]:
        """
        공시 집계 데이터 조회
        
        Args:
            keyword: 검색 키워드
            groupby: 그룹핑 필드 (company, filling_type 등)
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            size: 결과 크기
        """
        params = {
            "keyword": keyword,
            "groupby": groupby,
            "size": size
        }
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
            
        return self._make_request("/filings/aggregation", params)
    
    def get_disclosure_documents(self, 
                                keyword: str = None,
                                company_name: str = None,
                                symbols: str = None,
                                date_from: str = None,
                                date_to: str = None,
                                page: int = 1,
                                page_size: int = 10) -> Dict[str, Any]:
        """
        국내 공시 문서 검색
        
        Args:
            keyword: 검색 키워드
            company_name: 기업명
            symbols: 종목코드 (예: KRX:005930)
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            page: 페이지 번호
            page_size: 페이지 크기
        """
        params = {}
        if keyword:
            params["keyword"] = keyword
        if company_name:
            params["company_name"] = company_name
        if symbols:
            params["symbols"] = symbols
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
            
        return self._make_request("/articles/documents/disclosure", params)
    
    def download_briefing_csv(self, 
                             briefing_type: str,
                             date: str) -> bytes:
        """
        브리핑 CSV 다운로드
        
        Args:
            briefing_type: 브리핑 타입 (stock, etf, global-stock, global-etf)
            date: 날짜 (YYYYMMDD)
        """
        params = {
            "date": date,
            "api_key": self.api_key
        }
        
        try:
            response = requests.get(f"{self.base_url}/briefings/csv/{briefing_type}", params=params)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"CSV 다운로드 실패: {e}")
            return None


class FinnhubClient:
    """Finnhub API 클라이언트"""
    
    def __init__(self):
        self.api_key = get_api_key("FINNHUB_API_KEY")
        self.base_url = "https://finnhub.io/api/v1"
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """API 요청을 수행합니다."""
        if params is None:
            params = {}
        
        params["token"] = self.api_key
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Finnhub API 요청 실패: {e}")
            return {"error": str(e)}
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """주식 현재가 조회"""
        return self._make_request("/quote", {"symbol": symbol})
    
    def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """회사 프로필 조회"""
        return self._make_request("/stock/profile2", {"symbol": symbol})
    
    def get_company_news(self, symbol: str, from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """회사 뉴스 조회"""
        params = {
            "symbol": symbol,
            "from": from_date,
            "to": to_date
        }
        result = self._make_request("/company-news", params)
        return result if isinstance(result, list) else []
    
    def get_market_news(self, category: str = "general") -> List[Dict[str, Any]]:
        """시장 뉴스 조회"""
        params = {"category": category}
        result = self._make_request("/news", params)
        return result if isinstance(result, list) else []
    
    def get_earnings_calendar(self, from_date: str, to_date: str) -> Dict[str, Any]:
        """실적 발표 일정 조회"""
        params = {
            "from": from_date,
            "to": to_date
        }
        return self._make_request("/calendar/earnings", params)
    
    def get_economic_calendar(self, from_date: str, to_date: str) -> Dict[str, Any]:
        """경제 지표 일정 조회"""
        params = {
            "from": from_date,
            "to": to_date
        }
        return self._make_request("/calendar/economic", params)


class SlackClient:
    """Slack API 클라이언트"""
    
    def __init__(self):
        self.token = get_api_key("SLACK_BOT_TOKEN")  # Bot Token 사용
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """API 요청을 수행합니다."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                response = requests.get(url, headers=self.headers, params=data)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Slack API 요청 실패: {e}")
            return {"error": str(e)}
    
    def send_message(self, channel: str, text: str, blocks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """메시지 전송"""
        data = {
            "channel": channel,
            "text": text
        }
        if blocks:
            data["blocks"] = blocks
            
        return self._make_request("POST", "/chat.postMessage", data)
    
    def upload_file(self, channels: str, file_content: bytes, filename: str, title: str = None) -> Dict[str, Any]:
        """파일 업로드"""
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        data = {
            "channels": channels,
            "filename": filename
        }
        if title:
            data["title"] = title
        
        files = {
            "file": (filename, file_content)
        }
        
        try:
            response = requests.post(f"{self.base_url}/files.upload", headers=headers, data=data, files=files)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"파일 업로드 실패: {e}")
            return {"error": str(e)}
    
    def get_channels(self) -> Dict[str, Any]:
        """채널 목록 조회"""
        return self._make_request("GET", "/conversations.list")


# 사용 예제
if __name__ == "__main__":
    # Deepsearch 클라이언트 테스트
    deepsearch = DeepsearchClient()
    
    # 삼성전자 관련 뉴스 검색
    articles = deepsearch.get_articles(
        company_name="삼성전자",
        date_from="2024-01-01",
        date_to="2024-01-31",
        page_size=5
    )
    print("삼성전자 뉴스:", json.dumps(articles, ensure_ascii=False, indent=2))
    
    # Apple 관련 해외 뉴스 검색
    global_articles = deepsearch.get_global_articles(
        company_name="Apple",
        date_from="2024-01-01",
        date_to="2024-01-31",
        page_size=5
    )
    print("Apple 해외 뉴스:", json.dumps(global_articles, ensure_ascii=False, indent=2))
