#################################
# 정책명 기반 정책 상세 조회 서비스 #
#################################

import httpx
from config import settings


class PolicyDetailService:
    """
    정책 이름을 입력받아 온통청년 API에서 해당 정책의 상세 정보를 가져오는 서비스

    흐름:
    1. 정책명으로 목록 검색
    2. 검색 결과에서 정책번호 plcyNo 추출
    3. 정책번호로 상세 조회
    4. 상세 정보를 보기 좋은 형태로 정리
    """

    def __init__(self):
        self.base_url = settings.YOUTH_POLICY_API_URL
        self.api_key = settings.YOUTH_POLICY_API_KEY
        self.end_point = "/go/ythip/getPlcy"
        self.timeout = 10.0

    def _extract_policy_list(self, response_json: dict) -> list[dict]:
        """
        목록 조회 응답에서 정책 리스트를 꺼냅니다.
        """

        result = response_json.get("result", {})

        if not isinstance(result, dict):
            return []

        policy_list = result.get("youthPolicyList", [])

        if isinstance(policy_list, dict):
            policy_list = [policy_list]

        if not isinstance(policy_list, list):
            return []

        return policy_list

    def _extract_policy_detail(self, response_json: dict) -> dict:
        """
        상세 조회 응답에서 정책 상세 정보를 꺼냅니다.

        API 응답 구조가 조금 다를 수 있어서 여러 경우를 안전하게 처리합니다.
        """

        result = response_json.get("result", {})

        if not isinstance(result, dict):
            return {}

        # 경우 1: result 안에 youthPolicy가 있는 경우
        policy = result.get("youthPolicy")

        if isinstance(policy, dict):
            return policy

        # 경우 2: result 안에 youthPolicyList가 있는 경우
        policy_list = result.get("youthPolicyList")

        if isinstance(policy_list, dict):
            return policy_list

        if isinstance(policy_list, list) and len(policy_list) > 0:
            first_policy = policy_list[0]

            if isinstance(first_policy, dict):
                return first_policy

        # 경우 3: result 자체가 정책 상세 정보인 경우
        if result.get("plcyNo") or result.get("plcyNm"):
            return result

        return {}

    def _format_policy_detail(self, policy: dict) -> dict:
        """
        온통청년 API 원본 필드를 우리가 쓰기 좋은 이름으로 정리합니다.
        """

        return {
            "policy_id": policy.get("plcyNo"),
            "title": policy.get("plcyNm"),
            "summary": policy.get("plcyExplnCn"),
            "keywords": policy.get("plcyKywdNm"),

            "category_major": policy.get("lclsfNm"),
            "category_middle": policy.get("mclsfNm"),

            "support_content": policy.get("plcySprtCn"),
            "support_target": policy.get("sprtTrgtCn"),
            "support_scale": policy.get("sprtSclCnt"),

            "min_age": policy.get("sprtTrgtMinAge"),
            "max_age": policy.get("sprtTrgtMaxAge"),

            "income_condition": policy.get("earnCndCn"),
            "education_condition": policy.get("schoolCdNm"),
            "employment_condition": policy.get("jobCdNm"),
            "special_condition": policy.get("sBizCdNm"),

            "application_period": policy.get("aplyYmd"),
            "application_method": policy.get("plcyAplyMthdCn"),
            "screening_method": policy.get("srngMthdCn"),
            "required_documents": policy.get("sbmsnDcmntCn"),

            "application_url": policy.get("aplyUrlAddr"),
            "reference_url": policy.get("refUrlAddr"),

            "supervising_institution": policy.get("sprvsnInstCdNm"),
            "operating_institution": policy.get("operInstCdNm"),

            # 나중에 필요한 필드가 있으면 확인할 수 있도록 원본도 같이 반환
            "raw": policy,
        }

    def _search_policy_by_name(
        self,
        policy_name: str,
        page_size: int = 5,
    ) -> list[dict]:
        """
        정책명으로 정책 목록을 검색합니다.

        여기서는 상세 조회가 아니라,
        정책번호 plcyNo를 찾기 위한 1차 검색입니다.
        """

        url = f"{self.base_url}{self.end_point}"

        params = {
            "apiKeyNm": self.api_key,
            "plcyNm": policy_name,
            "pageNum": 1,
            "pageSize": page_size,
            "pageType": "1",
            "rtnType": "json",
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params)

        response.raise_for_status()

        response_json = response.json()

        return self._extract_policy_list(response_json)

    def _fetch_policy_detail_by_id(self, policy_id: str) -> dict:
        """
        정책번호로 정책 상세 정보를 조회합니다.
        """

        url = f"{self.base_url}{self.end_point}"

        params = {
            "apiKeyNm": self.api_key,
            "plcyNo": policy_id,
            "pageType": "2",
            "rtnType": "json",
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params)

        response.raise_for_status()

        response_json = response.json()

        return self._extract_policy_detail(response_json)

    def _select_best_policy(
        self,
        policies: list[dict],
        policy_name: str,
    ) -> dict | None:
        """
        정책명 검색 결과 중 가장 적절한 정책 하나를 고릅니다.

        1순위: 정책명이 정확히 같은 것
        2순위: 정책명 안에 사용자가 입력한 이름이 포함된 것
        3순위: 첫 번째 검색 결과
        """

        if not policies:
            return None

        # 1순위: 완전 일치
        for policy in policies:
            title = policy.get("plcyNm", "")

            if title == policy_name:
                return policy

        # 2순위: 포함 관계
        for policy in policies:
            title = policy.get("plcyNm", "")

            if policy_name in title:
                return policy

        # 3순위: 첫 번째 결과
        return policies[0]

    def get_policy_detail_by_name(
        self,
        policy_name: str,
    ) -> dict:
        """
        정책 이름을 받아서 해당 정책의 상세 정보를 반환합니다.

        Args:
            policy_name:
                사용자가 입력한 정책명

        Returns:
            정책 상세 정보 dict
        """

        if not policy_name or not policy_name.strip():
            return {
                "success": False,
                "message": "정책 이름이 비어 있습니다.",
                "policy_name": policy_name,
                "policy": None,
            }

        policy_name = policy_name.strip()

        # 1. 정책명으로 검색
        candidates = self._search_policy_by_name(
            policy_name=policy_name,
            page_size=5,
        )

        if not candidates:
            return {
                "success": False,
                "message": "해당 정책명으로 검색된 정책이 없습니다.",
                "policy_name": policy_name,
                "candidates": [],
                "policy": None,
            }

        # 2. 검색 결과 중 가장 적절한 정책 선택
        selected_policy = self._select_best_policy(
            policies=candidates,
            policy_name=policy_name,
        )

        if selected_policy is None:
            return {
                "success": False,
                "message": "검색 결과에서 적절한 정책을 선택하지 못했습니다.",
                "policy_name": policy_name,
                "candidates": candidates,
                "policy": None,
            }

        policy_id = selected_policy.get("plcyNo")

        if policy_id is None:
            return {
                "success": False,
                "message": "검색된 정책에서 정책번호를 찾을 수 없습니다.",
                "policy_name": policy_name,
                "selected_policy": selected_policy,
                "policy": None,
            }

        # 3. 정책번호로 상세 조회
        policy_detail = self._fetch_policy_detail_by_id(
            policy_id=policy_id,
        )

        if not policy_detail:
            return {
                "success": False,
                "message": "정책 상세 정보를 찾을 수 없습니다.",
                "policy_name": policy_name,
                "policy_id": policy_id,
                "selected_policy": selected_policy,
                "policy": None,
            }

        # 4. 최종 반환
        return {
            "success": True,
            "message": "정책 상세 정보를 조회했습니다.",
            "policy_name": policy_name,
            "policy_id": policy_id,
            "selected_policy": {
                "policy_id": selected_policy.get("plcyNo"),
                "title": selected_policy.get("plcyNm"),
                "summary": selected_policy.get("plcyExplnCn"),
            },
            "policy": self._format_policy_detail(policy_detail),
        }

        def get_policy_detail_by_id(
            self,
            policy_id: str,
        ) -> dict:
            """
            정책번호를 기준으로 정책 상세 정보를 조회합니다.

            Args:
                policy_id:
                    온통청년 정책번호입니다.

            Returns:
                정책 상세 정보 dict
            """

        if not policy_id or not policy_id.strip():
            return {
                "success": False,
                "message": "정책번호가 비어 있습니다.",
                "policy_id": policy_id,
                "policy": None,
            }

        policy_id = policy_id.strip()

        policy_detail = self._fetch_policy_detail_by_id(
            policy_id=policy_id,
        )

        if not policy_detail:
            return {
                "success": False,
                "message": "정책 상세 정보를 찾을 수 없습니다.",
                "policy_id": policy_id,
                "policy": None,
            }

        return {
            "success": True,
            "message": "정책 상세 정보를 조회했습니다.",
            "policy_id": policy_id,
            "policy": self._format_policy_detail(policy_detail),
        }