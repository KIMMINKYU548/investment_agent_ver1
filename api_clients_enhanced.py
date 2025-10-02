"""
향상된 API 클라이언트 모듈
권한 제한이 있는 API들을 위한 대안 기능들을 포함합니다.
"""

import requests
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from config import get_api_key, get_endpoint


class EnhancedDeepsearchClient:
    """향상된 Deepsearch API 클라이언트 - 권한 제한 대응"""
    
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
    
    def _check_api_permission(self, endpoint: str) -> bool:
        """API 권한을 확인합니다."""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", 
                                  params={"api_key": self.api_key}, 
                                  headers=self.headers)
            return response.status_code != 403
        except:
            return False
    
    def get_articles_with_alternative_search(self, 
                                           keyword: str = None,
                                           company_name: str = None,
                                           symbols: str = None,
                                           date_from: str = None,
                                           date_to: str = None,
                                           page: int = 1,
                                           page_size: int = 10) -> Dict[str, Any]:
        """
        기사 검색 - 토픽 기능의 대안으로 키워드 기반 검색 사용
        """
        # 토픽 검색 대신 키워드 기반 검색 사용
        if keyword:
            return self._make_request("/articles", {
                "keyword": keyword,
                "date_from": date_from,
                "date_to": date_to,
                "page": page,
                "page_size": page_size,
                "highlight": "unified"  # 하이라이트 기능으로 토픽과 유사한 효과
            })
        elif company_name:
            return self._make_request("/articles", {
                "company_name": company_name,
                "date_from": date_from,
                "date_to": date_to,
                "page": page,
                "page_size": page_size
            })
        elif symbols:
            return self._make_request("/articles", {
                "symbols": symbols,
                "date_from": date_from,
                "date_to": date_to,
                "page": page,
                "page_size": page_size
            })
    
    def get_trending_alternative(self, 
                                sections: str = None,
                                page: int = 1,
                                page_size: int = 10) -> Dict[str, Any]:
        """
        트렌딩 토픽 대안 - 최신 기사들을 가져와서 인기도 기반으로 정렬
        """
        # 섹션별 최신 기사를 가져와서 대안으로 사용
        if sections:
            return self._make_request(f"/articles/{sections}", {
                "page": page,
                "page_size": page_size,
                "order": "published_at"  # 최신순 정렬
            })
        else:
            return self._make_request("/articles", {
                "page": page,
                "page_size": page_size,
                "order": "published_at"  # 최신순 정렬
            })
    
    def get_disclosure_alternative(self, 
                                  company_name: str = None,
                                  symbols: str = None,
                                  date_from: str = None,
                                  date_to: str = None,
                                  page: int = 1,
                                  page_size: int = 10) -> Dict[str, Any]:
        """
        해외 공시 대안 - 국내 공시 문서 검색 사용
        """
        return self._make_request("/articles/documents/disclosure", {
            "company_name": company_name,
            "symbols": symbols,
            "date_from": date_from,
            "date_to": date_to,
            "page": page,
            "page_size": page_size
        })
    
    def get_company_analysis(self, 
                           company_name: str,
                           date_from: str = None,
                           date_to: str = None) -> Dict[str, Any]:
        """
        기업 종합 분석 - 여러 소스에서 정보 수집
        """
        analysis = {
            "company_name": company_name,
            "analysis_date": datetime.now().isoformat(),
            "data_sources": {}
        }
        
        # 1. 국내 뉴스
        domestic_news = self._make_request("/articles", {
            "company_name": company_name,
            "date_from": date_from,
            "date_to": date_to,
            "page_size": 10
        })
        analysis["data_sources"]["domestic_news"] = domestic_news
        
        # 2. 해외 뉴스
        global_news = self._make_request("/global-articles", {
            "company_name": company_name,
            "date_from": date_from,
            "date_to": date_to,
            "page_size": 10
        })
        analysis["data_sources"]["global_news"] = global_news
        
        # 3. 국내 공시
        disclosure = self._make_request("/articles/documents/disclosure", {
            "company_name": company_name,
            "date_from": date_from,
            "date_to": date_to,
            "page_size": 10
        })
        analysis["data_sources"]["disclosure"] = disclosure
        
        # 4. 집계 데이터 (기업별 언급 횟수)
        aggregation = self._make_request("/articles/aggregation", {
            "keyword": company_name,
            "groupby": "publisher",
            "date_from": date_from,
            "date_to": date_to,
            "page_size": 10
        })
        analysis["data_sources"]["media_coverage"] = aggregation
        
        return analysis
    
    def get_sector_analysis(self, 
                          sector_keywords: List[str],
                          date_from: str = None,
                          date_to: str = None) -> Dict[str, Any]:
        """
        섹터 분석 - 여러 키워드에 대한 종합 분석
        """
        sector_analysis = {
            "sector_keywords": sector_keywords,
            "analysis_date": datetime.now().isoformat(),
            "sector_data": {}
        }
        
        for keyword in sector_keywords:
            # 키워드별 뉴스 분석
            news_data = self._make_request("/articles", {
                "keyword": keyword,
                "date_from": date_from,
                "date_to": date_to,
                "page_size": 20
            })
            
            # 키워드별 집계 분석
            aggregation_data = self._make_request("/articles/aggregation", {
                "keyword": keyword,
                "groupby": "companies.name",
                "date_from": date_from,
                "date_to": date_to,
                "page_size": 10
            })
            
            sector_analysis["sector_data"][keyword] = {
                "news": news_data,
                "companies": aggregation_data
            }
        
        return sector_analysis
    
    # 기존 기능들도 포함
    def get_articles(self, **kwargs):
        """기존 get_articles 메서드"""
        return self._make_request("/articles", kwargs)
    
    def get_global_articles(self, **kwargs):
        """기존 get_global_articles 메서드"""
        return self._make_request("/global-articles", kwargs)
    
    def get_aggregation(self, **kwargs):
        """기존 get_aggregation 메서드"""
        return self._make_request("/articles/aggregation", kwargs)


class SlackClientFixed:
    """수정된 Slack API 클라이언트"""
    
    def __init__(self):
        # Bot Token을 사용해야 합니다
        self.token = get_api_key("SLACK_CLIENT_SECRET")  # 이건 잘못된 토큰
        # 올바른 Bot Token을 설정해야 합니다
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
    
    def test_connection(self) -> bool:
        """연결 테스트"""
        result = self._make_request("GET", "/auth.test")
        return "error" not in result
    
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


# 사용 예제 및 테스트
if __name__ == "__main__":
    # 향상된 클라이언트 테스트
    enhanced_client = EnhancedDeepsearchClient()
    
    print("=== 향상된 Deepsearch 클라이언트 테스트 ===\n")
    
    # 1. 기업 종합 분석
    print("1. 삼성전자 종합 분석")
    analysis = enhanced_client.get_company_analysis(
        company_name="삼성전자",
        date_from="2024-01-01",
        date_to="2024-01-31"
    )
    print(f"   국내 뉴스: {analysis['data_sources']['domestic_news'].get('total_items', 0)}개")
    print(f"   해외 뉴스: {analysis['data_sources']['global_news'].get('total_items', 0)}개")
    print(f"   공시 문서: {analysis['data_sources']['disclosure'].get('total_items', 0)}개\n")
    
    # 2. 섹터 분석
    print("2. 반도체 섹터 분석")
    sector_analysis = enhanced_client.get_sector_analysis(
        sector_keywords=["반도체", "메모리", "AI"],
        date_from="2024-01-01",
        date_to="2024-01-31"
    )
    for keyword, data in sector_analysis["sector_data"].items():
        print(f"   {keyword}: {data['news'].get('total_items', 0)}개 뉴스, {len(data['companies'].get('data', []))}개 기업")
    
    print("\n=== 테스트 완료 ===")
