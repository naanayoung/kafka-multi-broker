from rest_framework import serializers
from .models import Coupon
from events.models import Event
from users.models import User

class CouponSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    username = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Coupon
        fields = ['id', 'code', 'user', 'event', 'issued_at', 'is_used', 'event_title', 'username']
        read_only_fields = ['issued_at']  # 자동 생성 필드는 읽기 전용
