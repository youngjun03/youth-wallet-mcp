# Python 3.11이 설치된 가벼운 이미지 사용
FROM python:3.11-slim

# 컨테이너 안에서 작업할 폴더 설정
WORKDIR /app

# 파이썬이 .pyc 캐시 파일을 만들지 않게 설정
ENV PYTHONDONTWRITEBYTECODE=1

# 파이썬 로그가 바로 출력되게 설정
ENV PYTHONUNBUFFERED=1

# src 구조를 사용하므로 PYTHONPATH를 src로 설정
ENV PYTHONPATH=/app/src

# 의존성 설치를 위해 pyproject.toml 먼저 복사
COPY pyproject.toml ./

# 프로젝트 전체 복사
COPY src ./src

# 필요한 패키지 설치
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# FastMCP 서버가 사용하는 포트
EXPOSE 8000

# 컨테이너가 시작될 때 MCP 서버 실행
CMD ["python", "-m", "ontong_youth_policy_mcp.server"]
