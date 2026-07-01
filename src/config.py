from pydantic_settings import BaseSettings, SettingsConfigDict
import pydantic_settings

class Settings(BaseSettings):
    """
    프로젝트 전체 설정값을 관리하는 클래스
    """

    # 온통청년 API 키
    YOUTH_POLICY_API_KEY: str

    # 온통청년 API URL
    YOUTH_POLICY_API_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

# 다른 모듈에서 settings을 import해서 사용
settings = Settings()