from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Coupon
from .serializers import CouponSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from kafka import KafkaProducer
import json
from utils.kafka_producer import send_coupon_issue
import uuid

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    #permission_classes = [] # 로그인 안해도 (개발용)
    permission_classes = [permissions.IsAuthenticated]  # 로그인한 사용자만 쿠폰 발급할 수 있도록

# EventDetail에서 랜덤 쿠폰 발급할 때
class IssueCouponView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # 인증된 사용자만

    def post(self, request, *args, **kwargs):
        event_id = request.data.get("event_id")
        user_id = request.user.id if request.user and request.user.is_authenticated else None

        if not event_id:
            return Response({"error": "event_id is required"}, status=400)
        
        # 요청 ID 생성(추후 상태 조회/ 멱등성 체크용)
        request_id = str(uuid.uuid4())

        try:
            # Kafka 메시지 전송
            send_coupon_issue({
                "request_id": request_id,
                "event_id": int(event_id),
                "user_id": int(user_id),
            })
        except Exception as e:
            import traceback, sys
            print("[coupon-issue] kafka send failed:", repr(e), file=sys.stderr)
            traceback.print_exc()
            return Response({"error": f"Kafka send failed: {e}"}, status=502)
        
        # 비동기 처리
        return Response({"message": "쿠폰 발급 요청 완료", "request_id":request_id},
                status=202)


# MyPage에서 발급된 쿠폰 목록 불러올 때
class UserCouponList(APIView):
    permission_classes = [permissions.IsAuthenticated] # 인증된 사용자만

    def get(self, request, *args, **kwargs):
        # id로 필터링해서 가져오기
        coupons = (Coupon.objects.filter(user=request.user).select_related('event', 'user'))
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)
