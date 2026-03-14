"""관리자 페이지"""

from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'user', 'event', 'issued_at', 'is_used']
    search_fields = ['code']
