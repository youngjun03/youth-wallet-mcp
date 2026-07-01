###############################
# API 호출해서 정책 목록 가져오기 #
###############################

import httpx
from config import settings

class PolicyAPIService:
    """
    온통청년 청년정책 API 호출 서비스

    역할:
    1. 검색 조건을 온통청년 API 파라미터로 변환
    2. 온통청년 API 호출
    3. API 응답을 MCP에서 쓰기 좋은 형태로 정리
    """

    def __init__(self):
        # API 호출에 필요한 기본 URL과 API 키를 설정
        self.base_url = settings.YOUTH_POLICY_API_URL

        self.api_key = settings.YOUTH_POLICY_API_KEY

        self.end_point = "/go/ythip/getPlcy"

        self.timeout = 10.0
    
    def _build_params(
        self,
        keyword: str | None = None,
        policy_name: str | None = None,
        description_keyword: str | None = None,
        region_code: str | None = None,
        category_major: str | None = None,
        category_middle: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        """
        MCP 파라미터를 온통청년 API 파라미터로 변환

        MCP 파라미터        -> API 파라미터
        keyword            -> plcyKywdNm
        policy_name        -> plcyNm
        description_keyword -> plcyExplnCn
        region_code        -> zipCd
        category_major     -> lclsfNm
        category_middle    -> mclsfNm
        page               -> pageNum
        page_size          -> pageSize
        """

        # 기본 요청 파라미터
        params ={
            "apiKeyNm": self.api_key,
            "pageNum": page,
            "pageSize": page_size,
            "pageType": "1", # 1 = 목록 조회
            "rtnType": "json",
        }

        # 검색 조건이 있으면 추가
        if keyword:
            params["plcyKywdNm"] = keyword
        if policy_name:
            params["plcyNm"] = policy_name
        if description_keyword:
            params["plcyExplnCn"] = description_keyword
        if region_code:
            params["zipCd"] = region_code
        if category_major:
            params["lclsfNm"] = category_major
        if category_middle:
            params["mclsfNm"] = category_middle

        return params
    
    def _extract_policy_list(self, response_json: dict) -> list[dict]:
        """
        API 응답 JSON에서 정책 목록만 꺼내는 함수입니다.
        """

        # result 가져오기
        result = response_json.get("result", {})

        # result가 dict가 아니면 잘못된 응답이므로 빈 리스트 반환
        if not isinstance(result, dict):
            return []

        # 정책 목록 가져오기
        policy_list = result.get("youthPolicyList", [])

        # 정책이 1개만 올 때 dict로 올 가능성 처리
        if isinstance(policy_list, dict):
            policy_list = [policy_list]

        # list가 아니면 빈 리스트 반환
        if not isinstance(policy_list, list):
            return []

        return policy_list
    
    def _format_policy(self, policy: dict) -> dict:
        """
        온통청년 API 원본 필드를 우리가 사용할 출력 필드로 바꾸는 함수입니다.

        API 원본 필드 -> 출력 필드
        plcyNo       -> policy_id
        plcyNm       -> title
        plcyKywdNm   -> keywords
        plcyExplnCn  -> summary
        lclsfNm      -> category_major
        mclsfNm      -> category_middle
        plcySprtCn   -> support_content
        bizPrdBgngYmd -> start_date
        bizPrdEndYmd  -> end_date
        """

        return {
            "policy_id": policy.get("plcyNo"),
            "title": policy.get("plcyNm"),
            "keywords": policy.get("plcyKywdNm"),
            "summary": policy.get("plcyExplnCn"),
            "category_major": policy.get("lclsfNm"),
            "category_middle": policy.get("mclsfNm"),
            "support_content": policy.get("plcySprtCn"),
            "start_date": policy.get("bizPrdBgngYmd"),
            "end_date": policy.get("bizPrdEndYmd"),
        }
    
    def search_youth_policies(
        self,
        keyword: str | None = None,
        policy_name: str | None = None,
        description_keyword: str | None = None,
        region_code: str | None = None,
        category_major: str | None = None,
        category_middle: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        """
        청년정책을 키워드, 정책명, 설명, 지역, 분야 조건으로 검색

        Args:
            keyword: 정책 키워드명
            policy_name: 정책명
            description_keyword: 정책 설명 검색어
            region_code: 법정시군구코드
            category_major: 정책 대분류명
            category_middle: 정책 중분류명
            page: 페이지 번호
            page_size: 페이지 크기

        Returns:
            MCP tool에서 반환하기 좋은 형태의 dict
        """

        # 최종 API URL 구성
        url = f"{self.base_url}{self.end_point}"

        # MCP 파라미터를 API 파라미터로 변환
        params = self._build_params(
            keyword=keyword,
            policy_name=policy_name,
            description_keyword=description_keyword,
            region_code=region_code,
            category_major=category_major,
            category_middle=category_middle,
            page=page,
            page_size=page_size,
        )

        # API 호출
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params)

        # 요청 실패 시 예외 발생
        response.raise_for_status()

        # JSON 응답 파싱
        response_json = response.json()

        # 정책 목록 추출
        policy_list = self._extract_policy_list(response_json)

        # 정책 목록을 우리가 정한 출력 형태로 변환
        formatted_policies = []

        for policy in policy_list:
            formatted_policy = self._format_policy(policy)
            formatted_policies.append(formatted_policy)

        # 최종 출력 형태
        return {
            "query": {
                "keyword": keyword,
                "policy_name": policy_name,
                "description_keyword": description_keyword,
                "region_code": region_code,
                "category_major": category_major,
                "category_middle": category_middle,
                "page": page,
                "page_size": page_size,
            },
            "result": {
                "count": len(formatted_policies),
            },
            "policies": formatted_policies,
        }