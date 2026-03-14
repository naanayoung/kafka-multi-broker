# settings: SIMPLE_JWT 써야 함. users.User 모델 경로/필드명은 네 프로젝트에 맞춰 수정.
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.hashers import make_password
import csv, sys

User = get_user_model()

# 사용자 대량으로 만들건데 비번 해시함수 처리하면 너어무 오래 걸림

class Command(BaseCommand):
    help = "Create N test users and output CSV: user_id,token"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10000)
        parser.add_argument("--prefix", type=str, default="ltuser")

    def handle(self, *args, **opts):
        count = opts["count"]; prefix = opts["prefix"]

        writer = csv.writer(sys.stdout)
        writer.writerow(["user_id","token"])
        
        for i in range(count):
            username = f"{prefix}{i:05d}"
            user, created = User.objects.get_or_create(
                    username=username, 
                    defaults={"is_active":True},
            )
            
            if created:
                user.set_unusable_password()
                user.save(update_fields=["password"])

            token = str(AccessToken.for_user(user))
            writer.writerow([user.id, token])

            if i and i%1000 == 0:
                self.stderr.write(f"[progress] {i} users done")

