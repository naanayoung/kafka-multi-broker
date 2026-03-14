from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
import json
from kafka.errors import KafkaError
from coupons.models import Coupon, CouponIssueRequest
import os, sys, json
from django.db import transaction

#BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
#TOPIC = (
#        os.getenv("COUPON_ISSUE_TOPIC")
#        or os.getenv("KAFKA_TOPIC_NAME")
#        or os.getenv("EVENT_TOPIC")
#        or os.getenv("COUPON_TOPIC")
#)
#GROUP = os.getenv("COUPON_CONSUMER_GROUP", "coupon-consumer-group")

class Command(BaseCommand):
    help = 'Kafka에서 메시지를 소비하고 DB에 저장합니다.'
    
    def add_arguments(self, parser):
        parser.add_argument("--topic", dest="topic",
                            default=os.getenv("KAFKA_TOPIC"))
        parser.add_argument("--group", dest="group",
                            default=os.getenv("KAFKA_CONSUMER_GROUP", "coupon-consumer-group"))
        parser.add_argument("--bootstrap", dest="bootstrap",
                            default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", ""))

    running =True

    def handle(self, *args, **options):
        
        topic = options["topic"]
        group = options["group"]
        bootstrap = [x for x in (options["bootstrap"] or "").split(",") if x]

        if not topic:
            self.stderr.write("ERROR: KAFKA_TOPIC is not set and --topic not provided")
            sys.exit(1)
        if not bootstrap:
            self.stderr.write("ERROR: KAFKA_BOOTSTRAP_SERVERS/--bootstrap is missing")
            sys.exit(1)

        self.stdout.write(f"Coupon Consumer start (topic={topic}, group={group})")
       
        # consumer 객체 생성
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap,
            group_id=group,
            auto_offset_reset='latest',
            enable_auto_commit=True,  # 수동 커밋
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            max_poll_records=50,
        )
        '''
        # Consumer 멈추기
        def stop(sig, frame):
            self.stdout.write(" Stopping Consumer ... ")
            self.running = False
        '''
        try:
            while self.running:
                records = consumer.poll(timeout_ms=1000)
                if not records:
                    continue

                # tp: 토픽,파티션 정보 msgs: tp에 해당하는 메세지 리스트
                # TopicPartions 객체   ConsumerRecord 객체
                for tp, msgs in records.items():
                    for msg in msgs:
                        data = msg.value

                        try:
                            request_id = data["request_id"]
                            user_id = int(data["user_id"])
                            event_id = int(data["event_id"])
                        except KeyError:
                            self.stderr.write(f" invalid payload: {data}")
                            continue

                        try:
                            with transaction.atomic():
                                req, created  = CouponIssueRequest.objects.select_for_update().get_or_create(
                                    request_id=request_id, defaults={"user_id":user_id, "event_id": event_id, "status": "REQUESTED"},
                                )

                                # 이미 처리됨
                                if req.status == "ISSUED":
                                    self.stdout.write(f" already issued")
                                # 처리 x, 쿠폰 생성 로직
                                else:
                                    Coupon.objects.create(user_id=user_id, event_id=event_id, code=self._make_code())
                                    req.status = "ISSUED"
                                    req.save(update_fields=["status", "updated_at"])
                            # 처리 성공한 메세지만 커밋
                            consumer.commit()
                        except Exception as e:
                            self.stderr.write(f" processing failed")
                            CouponIssueRequest.objects.filter(request_id=request_id).update(
                                    status="FAILED", message=str(e)
                            )

                        # 커밋하지 않은 메세지는 재시도 대상
        except KafkaError as e:
            self.stderr.write(f"Kafka error: {e}")
    
        finally:
            consumer.close()
            self.stdout.write("consumer closed.")

    def _make_code(self) -> str:
        from uuid import uuid4
        return uuid4().hex[:12].upper()

