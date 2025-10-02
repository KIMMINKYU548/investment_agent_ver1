import json
from pathlib import Path
from typing import Dict, List
import re

class DeepsearchAPIAnalyzer:
    """크롤링한 API 문서 분석"""
    
    def __init__(self, docs_dir: str = "deepsearch_docs"):
        self.docs_dir = Path(docs_dir)
        self.complete_doc_path = self.docs_dir / "deepsearch_api_complete.json"
        
        if not self.complete_doc_path.exists():
            raise FileNotFoundError(f"API 문서를 찾을 수 없습니다: {self.complete_doc_path}")
        
        # 문서 로드
        with open(self.complete_doc_path, 'r', encoding='utf-8') as f:
            self.api_docs = json.load(f)
        
        print(f"✅ API 문서 로드 완료: {self.complete_doc_path}")
    
    def analyze_structure(self) -> Dict:
        """API 구조 분석"""
        
        analysis = {
            "sections": {},
            "total_endpoints": 0,
            "endpoint_summary": [],
            "base_url": "",
            "common_parameters": set()
        }
        
        print("\n" + "="*60)
        print("📊 Deepsearch API 구조 분석")
        print("="*60)
        
        for section_name, section_data in self.api_docs.get('sections', {}).items():
            if 'error' in section_data:
                print(f"\n❌ [{section_name}] 오류: {section_data['error']}")
                continue
            
            print(f"\n📁 [{section_name}]")
            print(f"   URL: {section_data.get('url', 'N/A')}")
            
            # 엔드포인트 정보
            endpoints = section_data.get('endpoints', [])
            print(f"   엔드포인트: {len(endpoints)}개")
            
            analysis['total_endpoints'] += len(endpoints)
            
            section_summary = {
                "name": section_name,
                "endpoint_count": len(endpoints),
                "endpoints": [],
                "parameters": section_data.get('parameters', {}),
                "examples": section_data.get('examples', [])
            }
            
            # 각 엔드포인트 출력
            for ep in endpoints:
                print(f"      - {ep['method']:6s} {ep['path']}")
                
                endpoint_info = {
                    "method": ep['method'],
                    "path": ep['path'],
                    "description": ep.get('description', ''),
                    "full_url": ep.get('full_url', '')
                }
                
                section_summary['endpoints'].append(endpoint_info)
                analysis['endpoint_summary'].append({
                    "section": section_name,
                    **endpoint_info
                })
            
            # 파라미터 정보
            params = section_data.get('parameters', {})
            if params:
                print(f"   파라미터: {len(params)}개")
                for param_name, param_info in list(params.items())[:3]:  # 최대 3개만 출력
                    required = "필수" if param_info.get('required') else "선택"
                    print(f"      - {param_name} ({param_info.get('type', 'string')}) - {required}")
                
                # 공통 파라미터 수집
                analysis['common_parameters'].update(params.keys())
            
            # 예제 정보
            examples = section_data.get('examples', [])
            if examples:
                print(f"   예제: {len(examples)}개")
            
            analysis['sections'][section_name] = section_summary
        
        # 공통 파라미터를 리스트로 변환
        analysis['common_parameters'] = sorted(list(analysis['common_parameters']))
        
        print("\n" + "="*60)
        print(f"📈 총 {len(analysis['sections'])}개 섹션, {analysis['total_endpoints']}개 엔드포인트")
        print("="*60)
        
        # 분석 결과 저장
        output_path = self.docs_dir / "api_analysis.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 분석 결과 저장: {output_path}")
        
        return analysis
    
    def extract_base_url(self) -> str:
        """Base URL 추출"""
        base_url = ""
        
        for section_data in self.api_docs.get('sections', {}).values():
            if 'error' in section_data:
                continue
            
            endpoints = section_data.get('endpoints', [])
            if endpoints and endpoints[0].get('full_url'):
                full_url = endpoints[0]['full_url']
                # base_url 추출 (프로토콜 + 도메인)
                match = re.match(r'(https?://[^/]+)', full_url)
                if match:
                    base_url = match.group(1)
                    break
        
        return base_url
    
    def generate_client_template(self):
        """클라이언트 코드 템플릿 자동 생성"""
        
        analysis = self.analyze_structure()
        base_url = self.extract_base_url() or "https://news.deepsearch.com"
        
        template = f'''"""
Deepsearch API 클라이언트 (자동 생성)
생성 날짜: {self.api_docs['metadata']['crawled_at']}
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DeepsearchAPIClient:
    """Deepsearch News API 클라이언트"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "{base_url}"
        self.headers = {{
            "Authorization": f"Bearer {{self.api_key}}",
            "Content-Type": "application/json"
        }}
    
    def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict:
        """API 요청 실행"""
        
        url = f"{{self.base_url}}{{endpoint}}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
            elif method.upper() == "POST":
                response = requests.post(
                    url,
                    headers=self.headers,
                    params=params,
                    json=data,
                    timeout=30
                )
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {{method}}")
            
            response.raise_for_status()
            logger.info(f"✅ API 요청 성공: {{endpoint}}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API 요청 실패: {{e}}")
            raise

'''
        
        # 각 섹션별 메서드 생성
        for section_name, section_info in analysis['sections'].items():
            template += f"\n    # {'='*50}\n"
            template += f"    # {section_name}\n"
            template += f"    # {'='*50}\n\n"
            
            for endpoint in section_info['endpoints']:
                method_name = self._generate_method_name(section_name, endpoint)
                method_code = self._generate_method_code(section_name, endpoint, section_info)
                template += method_code + "\n"
        
        # 파일로 저장
        output_path = self.docs_dir / "deepsearch_client_generated.py"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"\n🎉 클라이언트 코드 생성 완료: {output_path}")
        return output_path
    
    def _generate_method_name(self, section: str, endpoint: Dict) -> str:
        """메서드 이름 생성"""
        
        # 경로에서 메서드 이름 추출
        path = endpoint['path']
        parts = [p for p in path.split('/') if p and not p.startswith('{')]
        
        # HTTP 메서드에 따라 접두사 결정
        method = endpoint['method'].lower()
        
        if method == 'get':
            if 'search' in path:
                prefix = 'search'
            elif 'aggregate' in path:
                prefix = 'aggregate'
            else:
                prefix = 'get'
        elif method == 'post':
            prefix = 'create'
        elif method == 'put':
            prefix = 'update'
        elif method == 'delete':
            prefix = 'delete'
        else:
            prefix = method
        
        # 경로의 마지막 부분을 이름으로 사용
        name_parts = [prefix] + parts[-2:]
        method_name = '_'.join(name_parts).replace('-', '_')
        
        return method_name
    
    def _generate_method_code(self, section: str, endpoint: Dict, section_info: Dict) -> str:
        """메서드 코드 생성"""
        
        method_name = self._generate_method_name(section, endpoint)
        path = endpoint['path']
        http_method = endpoint['method']
        description = endpoint.get('description', f"{section} API")
        
        # 파라미터 추출
        params = section_info.get('parameters', {})
        
        # 메서드 시그니처 생성
        args = ["self"]
        
        # 필수 파라미터
        required_params = [name for name, info in params.items() if info.get('required')]
        for param in required_params[:5]:  # 최대 5개
            args.append(f"{param}: str")
        
        # 선택 파라미터
        optional_params = [name for name, info in params.items() if not info.get('required')]
        for param in optional_params[:5]:  # 최대 5개
            args.append(f"{param}: Optional[str] = None")
        
        method_signature = f"    def {method_name}({', '.join(args)}) -> Dict:"
        
        # Docstring 생성
        docstring = f'''        """
        {description}
        
        Args:
'''
        
        for param, info in list(params.items())[:5]:
            docstring += f"            {param}: {info.get('description', 'N/A')}\n"
        
        docstring += '''            
        Returns:
            API 응답 데이터
        """'''
        
        # 메서드 본문 생성
        body = f'''
        endpoint = "{path}"
        
        params = {{}}
'''
        
        # 파라미터 추가
        for param in (required_params + optional_params)[:10]:
            body += f'''        if {param}:
            params['{param}'] = {param}
'''
        
        body += f'''        
        logger.info(f"📡 {{endpoint}} 호출")
        return self._make_request(endpoint, method="{http_method}", params=params)
'''
        
        return method_signature + "\n" + docstring + body


def main():
    """분석 실행"""
    
    try:
        analyzer = DeepsearchAPIAnalyzer()
        
        # 구조 분석
        analysis = analyzer.analyze_structure()
        
        # 클라이언트 코드 자동 생성
        print("\n" + "="*60)
        print("🤖 클라이언트 코드 자동 생성")
        print("="*60)
        
        client_path = analyzer.generate_client_template()
        
        print("\n✅ 완료!")
        print("\n다음 파일들이 생성되었습니다:")
        print(f"  1. api_analysis.json - API 구조 분석 결과")
        print(f"  2. deepsearch_client_generated.py - 자동 생성된 클라이언트")
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()