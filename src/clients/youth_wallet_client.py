
# src/clients/youth_wallet_client.py

from __future__ import annotations

import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, Optional


class YouthWalletClientError(Exception):
    """온통청년 API 호출 중 발생한 오류."""


class YouthWalletClient:
    """
    온통청년 Open API 클라이언트.

    역할:
    - 온통청년 API 호출
    - XML 응답 파싱
    - raw dict 형태로 반환

    주의:
    - 정책 검색 로직, 필터링, 추천 판단은 service에서 처리한다.
    - 이 client는 API 통신만 담당한다.
    """

    def __init__(
        self,
        api_key: Optional[str] = "90a3a65c-d8d7-46f5-b97e-e232d7058772",
        base_url: str = "https://www.youthcenter.go.kr/opi",
        timeout: int = 10,
    ) -> None:
        self.api_key = api_key or os.getenv("YOUTH_CENTER_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            raise YouthWalletClientError(
                "온통청년 API 인증키가 없습니다. "
                "환경변수 YOUTH_CENTER_API_KEY를 설정하거나 api_key를 직접 전달하세요."
            )

    def search_policies(
        self,
        query: Optional[str] = None,
        page: int = 1,
        display: int = 10,
        biz_type_codes: Optional[list[str]] = None,
        policy_area_codes: Optional[list[str]] = None,
        keywords: Optional[list[str]] = None,
        extra_params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        청년정책 목록을 조회한다.

        온통청년 예시 파라미터:
        - openApiVlak: 인증키
        - pageIndex: 페이지 번호
        - display: 출력 개수
        - query: 검색어
        - bizTycdSel: 정책 유형 코드
        - srchPolyBizSecd: 정책 분야 코드
        - keyword: 키워드
        """

        params: dict[str, Any] = {
            "openApiVlak": self.api_key,
            "pageIndex": page,
            "display": display,
        }

        if query:
            params["query"] = query

        if biz_type_codes:
            params["bizTycdSel"] = self._to_csv(biz_type_codes)

        if policy_area_codes:
            params["srchPolyBizSecd"] = self._to_csv(policy_area_codes)

        if keywords:
            params["keyword"] = self._to_csv(keywords)

        if extra_params:
            params.update(extra_params)

        return self._get_xml(
            endpoint="youthPlcyList.do",
            params=params,
        )

    def get_policy_list_raw(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        온통청년 정책 목록 API에 raw params를 그대로 전달한다.

        아직 정확한 파라미터 매핑이 확정되지 않았거나,
        API 문서의 추가 파라미터를 실험할 때 사용한다.
        """

        merged_params = {
            "openApiVlak": self.api_key,
            **params,
        }

        return self._get_xml(
            endpoint="youthPlcyList.do",
            params=merged_params,
        )

    def _get_xml(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        GET 요청을 보내고 XML 응답을 dict로 변환한다.
        """

        url = self._build_url(endpoint, params)

        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "youth-wallet-mcp/0.1",
                    "Accept": "application/xml,text/xml,*/*",
                },
                method="GET",
            )

            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                status_code = response.status
                body = response.read().decode("utf-8", errors="replace")

        except Exception as exc:
            raise YouthWalletClientError(f"온통청년 API 요청 실패: {exc}") from exc

        if status_code < 200 or status_code >= 300:
            raise YouthWalletClientError(
                f"온통청년 API 응답 오류: HTTP {status_code}"
            )

        parsed = self._parse_xml(body)

        return {
            "ok": True,
            "status_code": status_code,
            "endpoint": endpoint,
            "request": {
                "url": self._safe_url(url),
                "params": self._safe_params(params),
            },
            "raw_xml": body,
            "data": parsed,
        }

    def _build_url(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> str:
        query_string = urllib.parse.urlencode(params, doseq=False)
        return f"{self.base_url}/{endpoint}?{query_string}"

    def _parse_xml(
        self,
        xml_text: str,
    ) -> dict[str, Any]:
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            raise YouthWalletClientError(f"XML 파싱 실패: {exc}") from exc

        return {
            root.tag: self._element_to_dict(root)
        }

    def _element_to_dict(
        self,
        element: ET.Element,
    ) -> Any:
        """
        XML Element를 dict/list/text로 변환한다.

        같은 태그가 여러 번 나오면 list로 묶는다.
        """

        children = list(element)

        if not children:
            text = element.text.strip() if element.text else ""
            return text

        result: dict[str, Any] = {}

        for child in children:
            child_value = self._element_to_dict(child)

            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_value)
            else:
                result[child.tag] = child_value

        return result

    def _to_csv(
        self,
        values: list[str],
    ) -> str:
        return ",".join(str(value).strip() for value in values if str(value).strip())

    def _safe_params(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        safe = dict(params)

        if "openApiVlak" in safe:
            safe["openApiVlak"] = "***"

        return safe

    def _safe_url(
        self,
        url: str,
    ) -> str:
        parsed = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(parsed.query)

        if "openApiVlak" in query:
            query["openApiVlak"] = ["***"]

        safe_query = urllib.parse.urlencode(query, doseq=True)

        return urllib.parse.urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                safe_query,
                parsed.fragment,
            )
        )


def create_youth_wallet_client(
    api_key: Optional[str] = None,
) -> YouthWalletClient:
    """
    service에서 간단히 client를 생성하기 위한 헬퍼 함수.
    """

    return YouthWalletClient(api_key=api_key)


__all__ = [
    "YouthWalletClient",
    "YouthWalletClientError",
    "create_youth_wallet_client",
]