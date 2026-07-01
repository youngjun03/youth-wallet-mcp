from src.services.policy_search_service import PolicyAPIService


service = PolicyAPIService()

result = service.search_youth_policies(
    keyword="주거",
    policy_name="드림",
    page=1,
    page_size=5,
)

print("검색 조건:", result["query"])
print("정책 개수:", result["result"]["count"])

for policy in result["policies"]:
    print("정책번호:", policy["policy_id"])
    print("정책명:", policy["title"])
    print("키워드:", policy["keywords"])
    print("설명:", policy["summary"])
    print("대분류:", policy["category_major"])
    print("중분류:", policy["category_middle"])
    print("지원내용:", policy["support_content"])
    print("-" * 50)