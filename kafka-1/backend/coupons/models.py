from django.db import models
from users.models import User
from events.models import Event
from django.conf import settings

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, related_name="coupons", on_delete=models.CASCADE, db_column="user_id")
    event = models.ForeignKey(Event, related_name="coupons", on_delete=models.CASCADE, db_column="event_id")
    issued_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):     # 쿠폰 유효기간 지났는지 확인
        return self.issued_at > self.event.end_date

    def __str__(self):
        return f"{self.code} ({'used' if self.is_used else 'unused'})"

# status가 실행중/전/후 인지를 나타내기 위함.
# 만약 실행 중이라면 code가 없기 때문에 Coupon 에 속성으로 넣긴 부자연스러움. 
class CouponIssueRequest(models.Model):
    request_id = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_column="event_id")
    status = models.CharField(max_length=16, default="REQUESTED")  # REQUESTED/ISSUED/FAILED
    message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    '''
    Consumer는 처리 성공 시 Coupon 객체 생성
                + Event.toal_coupons 증가 + status='ISSUED'
    '''
