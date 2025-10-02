import time
import json
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeepsearchDocCrawler:
    """Deepsearch API 문서 전문 크롤러"""
    
    def __init__(self, output_dir: str = "deepsearch_docs"):
        self.driver = None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # API 문서 섹션 구조
        self.sections = {
            "시작하기": "/api/#section/%EC%8B%9C%EC%9E%91%ED%95%98%EA%B8%B0",
            "API 사용방법": "/api/#section/API-%EC%82%AC%EC%9A%A9%EB%B0%A9%EB%B2%95",
            "국내 기사": "/api/#section/%EA%B5%AD%EB%82%B4-%EA%B8%B0%EC%82%AC",
            "해외 기사": "/api/#section/%ED%95%B4%EC%99%B8-%EA%B8%B0%EC%82%AC",
            "국내 토픽": "/api/#section/%EA%B5%AD%EB%82%B4-%ED%86%A0%ED%94%BD",
            "해외 토픽": "/api/#section/%ED%95%B4%EC%99%B8-%ED%86%A0%ED%94%BD",
            "브리핑": "/api/#section/%EB%B8%8C%EB%A6%AC%ED%95%91",
            "해외 공시": "/api/#section/%ED%95%B4%EC%99%B8-%EA%B3%B5%EC%8B%9C",
            "국내 문서": "/api/#section/%EA%B5%AD%EB%82%B4-%EB%AC%B8%EC%84%9C"
        }
        
        self.base_url = "https://news.deepsearch.com"
    
    def setup_driver(self):
        """Selenium WebDriver 설정"""
        chrome_options = Options()
        # 헤드리스 모드 비활성화 (디버깅용)
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--lang=ko-KR')
        
        # User-Agent 설정
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info("✅ Selenium WebDriver 설정 완료")
    
    def crawl_all_sections(self) -> Dict:
        """모든 API 문서 섹션 크롤링"""
        
        if not self.driver:
            self.setup_driver()
        
        all_docs = {
            "metadata": {
                "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "base_url": self.base_url,
                "total_sections": len(self.sections)
            },
            "sections": {}
        }
        
        logger.info(f"🚀 {len(self.sections)}개 섹션 크롤링 시작")
        
        for section_name, section_path in self.sections.items():
            logger.info(f"\n📄 [{section_name}] 크롤링 중...")
            
            try:
                section_data = self.crawl_section(section_name, section_path)
                all_docs["sections"][section_name] = section_data
                
                logger.info(f"✅ [{section_name}] 완료 - {len(section_data.get('endpoints', []))}개 엔드포인트")
                
                # 각 섹션을 개별 파일로 저장
                self.save_section_to_file(section_name, section_data)
                
                # 서버 부하 방지
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ [{section_name}] 크롤링 실패: {e}")
                all_docs["sections"][section_name] = {"error": str(e)}
        
        # 전체 문서를 하나의 JSON 파일로 저장
        self.save_all_docs(all_docs)
        
        # Markdown 형식으로도 저장
        self.generate_markdown_docs(all_docs)
        
        logger.info(f"\n✅ 전체 크롤링 완료!")
        logger.info(f"📂 저장 위치: {self.output_dir.absolute()}")
        
        return all_docs
    
    def crawl_section(self, section_name: str, section_path: str) -> Dict:
        """특정 섹션 크롤링"""
        
        url = f"{self.base_url}{section_path}"
        
        try:
            # 페이지 로드
            self.driver.get(url)
            
            # JavaScript 렌더링 대기
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 추가 대기 (동적 콘텐츠 로딩)
            time.sleep(5)
            
            # 페이지 소스 가져오기
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 섹션 데이터 추출
            section_data = {
                "url": url,
                "title": section_name,
                "description": "",
                "endpoints": [],
                "examples": [],
                "parameters": {},
                "raw_content": ""
            }
            
            # 콘텐츠 추출 (여러 가능한 선택자 시도)
            content_selectors = [
                '.api-content',
                '.swagger-ui',
                '.documentation',
                'article',
                'main',
                '.content',
                '#api-docs'
            ]
            
            content_element = None
            for selector in content_selectors:
                try:
                    content_element = soup.select_one(selector)
                    if content_element:
                        break
                except:
                    continue
            
            if not content_element:
                # 전체 body에서 추출
                content_element = soup.find('body')
            
            if content_element:
                # 설명 추출
                description = self._extract_description(content_element)
                section_data["description"] = description
                
                # API 엔드포인트 추출
                endpoints = self._extract_endpoints(content_element)
                section_data["endpoints"] = endpoints
                
                # 예제 코드 추출
                examples = self._extract_code_examples(content_element)
                section_data["examples"] = examples
                
                # 파라미터 정보 추출
                parameters = self._extract_parameters(content_element)
                section_data["parameters"] = parameters
                
                # 전체 텍스트 추출
                section_data["raw_content"] = content_element.get_text(separator="\n", strip=True)
            
            return section_data
            
        except Exception as e:
            logger.error(f"섹션 크롤링 오류: {e}")
            raise
    
    def _extract_description(self, element) -> str:
        """섹션 설명 추출"""
        description = ""
        
        # 설명 패턴 찾기
        desc_selectors = [
            'p:first-of-type',
            '.description',
            '.intro',
            'h2 + p',
            'h1 + p'
        ]
        
        for selector in desc_selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                description = desc_elem.get_text(strip=True)
                if len(description) > 20:  # 유효한 설명
                    break
        
        return description
    
    def _extract_endpoints(self, element) -> List[Dict]:
        """API 엔드포인트 추출"""
        endpoints = []
        
        # HTTP 메서드 패턴
        method_pattern = re.compile(r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s]+)')
        
        # 코드 블록에서 엔드포인트 찾기
        code_blocks = element.find_all(['code', 'pre'])
        
        for code in code_blocks:
            text = code.get_text()
            matches = method_pattern.findall(text)
            
            for method, path in matches:
                endpoint = {
                    "method": method,
                    "path": path,
                    "description": self._find_nearby_description(code),
                    "full_url": f"{self.base_url}{path}" if not path.startswith('http') else path
                }
                endpoints.append(endpoint)
        
        # 테이블에서 엔드포인트 찾기
        tables = element.find_all('table')
        for table in tables:
            rows = table.find_all('tr')[1:]  # 헤더 제외
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    # 첫 번째 셀에 메서드, 두 번째 셀에 경로
                    method_text = cells[0].get_text(strip=True)
                    path_text = cells[1].get_text(strip=True)
                    
                    if any(m in method_text.upper() for m in ['GET', 'POST', 'PUT', 'DELETE']):
                        endpoint = {
                            "method": method_text.upper(),
                            "path": path_text,
                            "description": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                            "full_url": f"{self.base_url}{path_text}" if not path_text.startswith('http') else path_text
                        }
                        endpoints.append(endpoint)
        
        # 중복 제거
        unique_endpoints = []
        seen = set()
        for ep in endpoints:
            key = f"{ep['method']}:{ep['path']}"
            if key not in seen:
                seen.add(key)
                unique_endpoints.append(ep)
        
        return unique_endpoints
    
    def _extract_code_examples(self, element) -> List[Dict]:
        """예제 코드 추출"""
        examples = []
        
        # 코드 블록 찾기
        code_blocks = element.find_all(['pre', 'code'])
        
        for i, code in enumerate(code_blocks):
            text = code.get_text(strip=True)
            
            if len(text) > 10:  # 유효한 코드
                # 언어 감지
                language = "unknown"
                if 'curl' in text.lower() or text.startswith('curl'):
                    language = "bash"
                elif 'python' in text.lower() or 'import' in text or 'def ' in text:
                    language = "python"
                elif 'javascript' in text.lower() or 'const ' in text or 'function' in text:
                    language = "javascript"
                elif '{' in text and '"' in text:
                    language = "json"
                
                example = {
                    "id": f"example_{i+1}",
                    "language": language,
                    "code": text,
                    "description": self._find_nearby_description(code)
                }
                examples.append(example)
        
        return examples
    
    def _extract_parameters(self, element) -> Dict:
        """파라미터 정보 추출"""
        parameters = {}
        
        # 테이블에서 파라미터 찾기
        tables = element.find_all('table')
        
        for table in tables:
            headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
            
            # 파라미터 테이블인지 확인
            if any(keyword in ' '.join(headers) for keyword in ['parameter', 'param', '파라미터', 'name', 'type']):
                rows = table.find_all('tr')[1:]  # 헤더 제외
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        param_name = cells[0].get_text(strip=True)
                        param_type = cells[1].get_text(strip=True) if len(cells) > 1 else "string"
                        param_desc = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                        param_required = "required" in row.get_text().lower()
                        
                        parameters[param_name] = {
                            "type": param_type,
                            "description": param_desc,
                            "required": param_required
                        }
        
        return parameters
    
    def _find_nearby_description(self, element) -> str:
        """요소 근처의 설명 텍스트 찾기"""
        description = ""
        
        # 이전 형제 요소에서 설명 찾기
        prev = element.find_previous(['p', 'div', 'span'])
        if prev:
            text = prev.get_text(strip=True)
            if len(text) > 10 and len(text) < 500:
                description = text
        
        return description
    
    def save_section_to_file(self, section_name: str, section_data: Dict):
        """섹션 데이터를 개별 파일로 저장"""
        
        # 파일명에서 특수문자 제거
        safe_name = re.sub(r'[^\w\s-]', '', section_name).strip().replace(' ', '_')
        
        # JSON 저장
        json_path = self.output_dir / f"{safe_name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(section_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"  💾 저장: {json_path.name}")
    
    def save_all_docs(self, all_docs: Dict):
        """전체 문서를 하나의 파일로 저장"""
        
        json_path = self.output_dir / "deepsearch_api_complete.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_docs, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📦 전체 문서 저장: {json_path.name}")
    
    def generate_markdown_docs(self, all_docs: Dict):
        """Markdown 형식으로 문서 생성"""
        
        md_path = self.output_dir / "DEEPSEARCH_API_DOCS.md"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Deepsearch API 문서\n\n")
            f.write(f"**크롤링 날짜**: {all_docs['metadata']['crawled_at']}\n\n")
            f.write("---\n\n")
            
            for section_name, section_data in all_docs['sections'].items():
                if 'error' in section_data:
                    f.write(f"## {section_name} ❌\n\n")
                    f.write(f"오류: {section_data['error']}\n\n")
                    continue
                
                f.write(f"## {section_name}\n\n")
                
                # URL
                f.write(f"**URL**: {section_data.get('url', 'N/A')}\n\n")
                
                # 설명
                if section_data.get('description'):
                    f.write(f"### 📝 설명\n\n")
                    f.write(f"{section_data['description']}\n\n")
                
                # 엔드포인트
                if section_data.get('endpoints'):
                    f.write(f"### 🔗 API 엔드포인트\n\n")
                    for ep in section_data['endpoints']:
                        f.write(f"#### `{ep['method']}` {ep['path']}\n\n")
                        if ep.get('description'):
                            f.write(f"{ep['description']}\n\n")
                        f.write(f"**Full URL**: `{ep.get('full_url', 'N/A')}`\n\n")
                
                # 파라미터
                if section_data.get('parameters'):
                    f.write(f"### 📋 파라미터\n\n")
                    f.write("| 파라미터 | 타입 | 필수 | 설명 |\n")
                    f.write("|----------|------|------|------|\n")
                    for param_name, param_info in section_data['parameters'].items():
                        required = "✅" if param_info.get('required') else "❌"
                        f.write(f"| `{param_name}` | {param_info.get('type', 'string')} | {required} | {param_info.get('description', '')} |\n")
                    f.write("\n")
                
                # 예제
                if section_data.get('examples'):
                    f.write(f"### 💻 예제 코드\n\n")
                    for ex in section_data['examples'][:3]:  # 최대 3개
                        if ex.get('description'):
                            f.write(f"**{ex['description']}**\n\n")
                        f.write(f"```{ex.get('language', 'bash')}\n")
                        f.write(f"{ex['code']}\n")
                        f.write("```\n\n")
                
                f.write("---\n\n")
        
        logger.info(f"📄 Markdown 문서 생성: {md_path.name}")
    
    def close(self):
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver 종료")


# ========================================
# 메인 실행 함수
# ========================================

def main():
    """Deepsearch API 문서 크롤링 실행"""
    
    print("="*60)
    print("🚀 Deepsearch API 문서 크롤러")
    print("="*60)
    
    crawler = DeepsearchDocCrawler(output_dir="deepsearch_docs")
    
    try:
        # 모든 섹션 크롤링
        all_docs = crawler.crawl_all_sections()
        
        print("\n" + "="*60)
        print("✅ 크롤링 완료!")
        print("="*60)
        print(f"\n📊 통계:")
        print(f"  - 총 섹션: {len(all_docs['sections'])}개")
        
        total_endpoints = sum(
            len(section.get('endpoints', []))
            for section in all_docs['sections'].values()
            if 'error' not in section
        )
        print(f"  - 총 엔드포인트: {total_endpoints}개")
        
        total_examples = sum(
            len(section.get('examples', []))
            for section in all_docs['sections'].values()
            if 'error' not in section
        )
        print(f"  - 총 예제: {total_examples}개")
        
        print(f"\n📂 저장 위치: {crawler.output_dir.absolute()}")
        print("\n파일 목록:")
        for file in sorted(crawler.output_dir.glob("*")):
            print(f"  - {file.name}")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        crawler.close()


if __name__ == "__main__":
    main()