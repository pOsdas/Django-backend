from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from django.contrib.sessions.backends.cache import SessionStore
from rest_framework.decorators import api_view, permission_classes

from auth_app.redis_client import redis_client


@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
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

