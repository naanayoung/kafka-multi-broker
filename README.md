 # Kafka 기반 분산 시스템 운영·관측·부하 검증

쿠폰 발급 요청을 Kafka로 비동기 처리하는 시스템을 직접 구축하고, 지표 기반으로 문제를 발견·개선하는 사이클을 경험한 프로젝트입니다.

---

## Architecture

| EC2 | 구성 요소 |
|-----|-----------|
| EC2-1 | Kafka Broker 1, Consumer 1·2, Django API, React(Nginx), 모니터링 스택 |
| EC2-2 | Kafka Broker 2, Consumer 3·4 |
| EC2-3 | Kafka Broker 3, Consumer 5·6 |

**요청 흐름**  
React → Nginx → Django API → Kafka → Consumer → MySQL

---

## Tech Stack

| 분류 | 기술 |
|------|------|
| Backend | Django, Django REST Framework, MySQL |
| Frontend | React, Nginx |
| Messaging | Kafka (KRaft), kafka-python |
| Monitoring | VictoriaMetrics, vmagent, Grafana, kafka-exporter, cAdvisor |
| Load Test | k6 |
| Infra | AWS EC2, Docker Compose |
| CI/CD 확장 | EKS, Strimzi, GitHub Actions |

---

## Key Design Decisions

**Kafka 클러스터**
- KRaft 모드 사용 (Zookeeper 없음)
- `replication.factor=3`, `min.insync.replicas=2`, `acks=all`
- 파티션 3개, 컨슈머 6개를 EC2 3대에 균등 분산 배치

**멱등성 보장**
- 요청마다 UUID `request_id` 생성
- `CouponIssueRequest` 테이블에서 상태 관리 (REQUESTED → ISSUED / FAILED)
- 재시도·중복 요청에도 쿠폰 중복 발급 방지

**모니터링**
- vmagent로 지표 수집 → VictoriaMetrics 저장 → Grafana 시각화
- kafka-exporter(Lag), cAdvisor(컨테이너 리소스)를 단일 대시보드로 통합

---

## Load Test Results

k6 `constant-arrival-rate`로 동일 조건(180초, 15,000건)에서  
컨슈머 분산 배치 전후 성능을 비교했습니다.

| 구분 | p95 응답 지연 |
|------|--------------|
| 분산 배치 전 (컨슈머 편중) | 2.06s |
| 분산 배치 후 (균등 분산) | 33.3ms |

> 분산 배치 전, 컨슈머 6개가 모두 EC2-1에 몰려 있었고 특정 인스턴스 CPU가 78%까지 치솟았습니다.  
> 각 EC2에 브로커 1개 + 컨슈머 2개씩 균등 배치 후 응답 지연이 약 98% 단축됐습니다.

---

## How to Run

### 사전 준비 (EC2 공통)
- Docker, Docker Compose 설치
- EC2 보안 그룹에서 9092, 29092, 29093 포트 허용
- 각 `docker-compose.yml`의 EC2 IP를 실제 Private IP로 교체

### EC2-1 (브로커1 + 백엔드 + 모니터링)
```bash
cd kafka-1/infra
docker compose up -d
```

```bash
cd kafka-1/monitoring
docker compose up -d
# Grafana: http://<EC2-1-IP>:3000
```

### EC2-2 (브로커2)
```bash
cd kafka-2/broker-2
docker compose up -d
```

### EC2-3 (브로커3)
```bash
cd kafka-3/broker-3
docker compose up -d
```

### 부하 테스트 (k6)

테스트 유저 생성 및 CSV 저장
```bash
cd kafka-1
python manage.py bulk_make_test_users --count 15000 > infra/users.csv
```

k6 실행 (EC2-1에서)
```bash
cd kafka-1/infra
docker compose run --rm k6
# 기본값: 15,000건, 180초, EVENT_ID=1
```

환경변수로 조정 가능
```bash
docker compose run --rm -e TOTAL=10000 -e DURATION=120s k6
```

---

## Directory Structure

```
kafka-multi-broker/
├── kafka-1/               # EC2-1
│   ├── backend/           # Django API + Consumer 1·2
│   ├── frontend/          # React
│   ├── infra/             # Docker Compose (브로커1 + 백엔드 + 프론트)
│   ├── monitoring/        # VictoriaMetrics, vmagent, Grafana
│   └── scripts/           # k6 부하 테스트 스크립트
├── kafka-2/               # EC2-2
│   ├── backend/           # Consumer 3·4
│   └── broker-2/          # Docker Compose (브로커2)
└── kafka-3/               # EC2-3
    ├── backend/           # Consumer 5·6
    └── broker-3/          # Docker Compose (브로커3)
```
