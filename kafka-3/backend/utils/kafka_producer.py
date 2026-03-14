import json
import time
import os
import threading
from typing import Optional, Dict, Any
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
COUPON_ISSUE_TOPIC = os.getenv("COUPON_ISSUE_TOPIC")

_producer: Optional[KafkaProducer] = None
_lock = threading.Lock()

def build_producer() -> KafkaProducer:
    return KafkaProducer(
            bootstrap_servers=[s.strip() for s in BOOTSTRAP.split(",")],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all", # 저장됐는지, 복제본 저장됐는지 모두 응답 받음
            linger_ms=5,
            retries=3,  # 전송 재시도
            max_in_flight_requests_per_connection=1, # 순서 보장 강화
            enable_idempotence=True # 중복 방지
    )

def get_producer() -> KafkaProducer:
    global _producer
    if _producer is not None:
        return _producer
    with _lock:
        if _producer is not None:
            return _producer
        last_err = None
        for attempt in range(1,11):
            try:
                _producer = build_producer()
                print(f"KafkaProducer 연결 성공 : {BOOTSTRAP}")
                break
            except NoBrokersAvailable as e:
                last_err = e
                print(f"Kafka 브로커 연결 실패 (시도 {attempt+1}/10), 5초 후 재시도...")
                time.sleep(5)
        if _producer is None:
            raise last_err or RuntimeError("Kafka Producer init Failed")
        return _producer

# 랜덤 쿠폰 발급 요청 이벤트 생성시 사용
def send_coupon_issue(data: dict):
    p = get_producer()
    fut = p.send(COUPON_ISSUE_TOPIC, value=data)
    fut.get(timeout=10) # 전송 보장 (ACK 대기)

