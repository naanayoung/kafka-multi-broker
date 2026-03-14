from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Event                  # ./backend/events/models.py
from .serializers import EventSerializer   # ./backend/events/serializers.py
# from utils.kafka_producer import send_event_message

# ModelsViewSet은 CRUD 기본 동작 자동 제공-> GET, POST, PUT, DELETE

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()       # DB에서 전체 이벤트 조회
    serializer_class = EventSerializer   # 데이터를 JSON으로 변환할 직렬화 클래스 지정
    permission_classes = [permissions.AllowAny]  # 로그인 안 해도 접근 가능
    '''def perform_create(self, serializer):  # Kafka Producer 코드 정리중
        event = serializer.save()
        # Kafka로 메시지 전송
        send_event_message({
            'event_id': event.id,
            'title': event.title,
            'status': 'created'
        })'''
