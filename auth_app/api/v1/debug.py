import redis
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.backends.cache import SessionStore


# Подключение к Redis
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=settings.REDIS_DECODE_RESPONSES,
)


@csrf_exempt
@api_view(["GET"])
def debug_redis_sessions(request):
    """
    Распечатать базу redis
    """
    session_keys = redis_client.keys(":1:session:*")
    sessions = {}

    for raw_key in session_keys:
        try:
            session_key = raw_key.split(":")[-1]
            store = SessionStore(session_key=session_key)
            data = store.load()
            sessions[session_key] = data
        except Exception as e:
            sessions[raw_key] = f"[ERROR: {str(e)}]"

    return JsonResponse({"sessions": sessions}, json_dumps_params={"indent": 2})

