from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from events.views import EventViewSet
from users.views import UserViewSet
from coupons.views import CouponViewSet
from coupons.views import IssueCouponView
from coupons.views import UserCouponList
from rest_framework_simplejwt.views import (
        TokenObtainPairView,
        TokenRefreshView,
)

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'users', UserViewSet)
router.register(r'coupons', CouponViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),  # 하나의 router만 등록
    path('api/coupon-issue/', IssueCouponView.as_view()),  # EventDetial에서 랜덤쿠폰 발급할 때
    path('api/coupon-list/', UserCouponList.as_view(), name='user-coupons'),  # MyPage에서 발급된 쿠폰 목록 불러올 떄
]
