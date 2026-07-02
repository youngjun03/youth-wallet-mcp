########################
# 지역명 -> 지역코드 변환 #
#########################

import csv
from pathlib import Path


class RegionCodeService:
    """
    지역명을 입력받아 온통청년 API에서 사용하는 지역코드로 변환하는 서비스입니다.

    예:
        "서울" -> "11000"
        "서울특별시" -> "11000"
        "서울 강남구" -> "11680"
        "강남구" -> "11680"
        "경기" -> "41000"
        "경기도" -> "41000"
    """

    # CSV에 없거나, 사용자가 자주 축약해서 입력하는 지역명 처리용
    REGION_ALIASES = {
        "서울": "11000",
        "서울특별시": "11000",

        "부산": "26000",
        "부산광역시": "26000",

        "대구": "27000",
        "대구광역시": "27000",

        "인천": "28000",
        "인천광역시": "28000",

        "광주": "29000",
        "광주광역시": "29000",

        "대전": "30000",
        "대전광역시": "30000",

        "울산": "31000",
        "울산광역시": "31000",

        "세종": "36110",
        "세종시": "36110",
        "세종특별자치시": "36110",

        "경기": "41000",
        "경기도": "41000",

        "충북": "43000",
        "충청북도": "43000",

        "충남": "44000",
        "충청남도": "44000",

        "전남": "46000",
        "전라남도": "46000",

        "경북": "47000",
        "경상북도": "47000",

        "경남": "48000",
        "경상남도": "48000",

        "제주": "50000",
        "제주도": "50000",
        "제주특별자치도": "50000",

        "강원": "51000",
        "강원도": "51000",
        "강원특별자치도": "51000",

        "전북": "52000",
        "전라북도": "52000",
        "전북특별자치도": "52000",
    }

    def __init__(self):
        # 현재 파일 위치:
        # src/services/region_code_service.py
        #
        # parents[0] = src/services
        # parents[1] = src
        # parents[2] = 프로젝트 루트
        project_root = Path(__file__).resolve().parents[2]

        self.csv_path = project_root / "data" / "region_codes.csv"

        # CSV 내용을 메모리에 저장
        self.regions = self._load_region_codes()

    def _load_region_codes(self) -> list[dict]:
        """
        region_codes.csv 파일을 읽어서 리스트로 변환합니다.
        """

        regions = []

        with open(self.csv_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                region_code = row["region_code"].strip()
                region_name = row["region_name"].strip()

                regions.append(
                    {
                        "region_code": region_code,
                        "region_name": region_name,
                        "normalized_name": self._normalize(region_name),
                        "last_token": self._get_last_token(region_name),
                    }
                )

        return regions

    def _normalize(self, text: str) -> str:
        """
        비교를 쉽게 하기 위해 공백을 제거합니다.

        예:
            "서울특별시 강남구" -> "서울특별시강남구"
            "서울 강남구" -> "서울강남구"
        """

        return text.strip().replace(" ", "")

    def _get_last_token(self, region_name: str) -> str:
        """
        지역명에서 마지막 행정구역 이름만 추출합니다.

        예:
            "서울특별시 강남구" -> "강남구"
            "경기도 수원시 장안구" -> "장안구"
            "경기도 수원시" -> "수원시"
        """

        return region_name.strip().split()[-1]

    def _remove_suffix(self, text: str) -> str:
        """
        사용자가 '강남구' 대신 '강남'이라고 입력해도 찾기 위한 처리입니다.

        예:
            "강남구" -> "강남"
            "수원시" -> "수원"
            "가평군" -> "가평"
        """

        suffixes = [
            "특별자치시",
            "특별자치도",
            "특별시",
            "광역시",
            "자치도",
            "도",
            "시",
            "군",
            "구",
        ]

        result = text.strip()

        for suffix in suffixes:
            if result.endswith(suffix):
                result = result[: -len(suffix)]
                break

        return result

    def find_region_code(self, region_name: str | None) -> str | None:
        """
        지역명을 받아서 해당 지역코드를 반환합니다.

        Args:
            region_name:
                사용자가 입력한 지역명

        Returns:
            region_code 또는 None
        """

        if region_name is None:
            return None

        user_input = region_name.strip()

        if not user_input:
            return None

        normalized_user_input = self._normalize(user_input)

        # 1. 자주 쓰는 별칭 먼저 확인
        # 예: 서울, 경기, 충북, 전북, 제주
        if normalized_user_input in self.REGION_ALIASES:
            return self.REGION_ALIASES[normalized_user_input]

        # 2. CSV의 전체 지역명과 정확히 일치하는지 확인
        # 예: "서울특별시 강남구" -> 11680
        for region in self.regions:
            if normalized_user_input == region["normalized_name"]:
                return region["region_code"]

        # 3. 사용자가 공백만 다르게 입력한 경우 확인
        # 예: "서울 강남구" -> "서울특별시 강남구" 매칭
        exact_candidates = []

        for region in self.regions:
            if normalized_user_input in region["normalized_name"]:
                exact_candidates.append(region)

        # 후보가 1개면 바로 반환
        # 예: "서울강남구" -> 서울특별시 강남구
        if len(exact_candidates) == 1:
            return exact_candidates[0]["region_code"]

        # 4. 마지막 지역명 기준으로 매칭
        # 예: "강남구" -> 서울특별시 강남구
        # 예: "수원시" -> 경기도 수원시
        last_token_candidates = []

        user_without_suffix = self._remove_suffix(user_input)

        for region in self.regions:
            last_token = region["last_token"]
            last_token_without_suffix = self._remove_suffix(last_token)

            if user_input == last_token:
                last_token_candidates.append(region)
            elif user_without_suffix == last_token_without_suffix:
                last_token_candidates.append(region)

        # 후보가 하나면 반환
        if len(last_token_candidates) == 1:
            return last_token_candidates[0]["region_code"]

        # 5. 후보가 여러 개면 애매하므로 None 반환
        # 예: "중구"는 서울, 부산, 대구, 인천, 대전, 울산에 모두 있음
        return None




