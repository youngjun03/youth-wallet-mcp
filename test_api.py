from src.services.region_code_service import RegionCodeService


service = RegionCodeService()

print(service.find_region_code("서울"))
print(service.find_region_code("서울특별시"))
print(service.find_region_code("경기"))
print(service.find_region_code("경기도"))
print(service.find_region_code("중구"))