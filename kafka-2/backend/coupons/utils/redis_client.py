import redis

# Redis 연결 객체를 하나 만들어 둠
redis_client = redis.Redis(
    host='127.0.0.1',  # 도커 외부에서 접근하니까 127.0.0.1
    port=6379,
    db=0,
    decode_responses=True  # 문자열 자동 디코딩 (편리)
)

