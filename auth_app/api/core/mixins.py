from rest_framework.views import APIView


class AsyncAPIView(APIView):
    async_capable = True

    async def __call__(self, request, *args, **kwargs):
        return await self.dispatch(request, *args, **kwargs)

    async def dispatch(self, request, *args, **kwargs):
        # Аналог обычного dispatch, только async
        handler = self.get_handler(request)
        if handler is None:
            raise Exception(f"Метод {request.method} не допустим")
        return await handler(request, *args, **kwargs)

    def get_handler(self, request):
        method = request.method.lower()
        return getattr(self, method, None)
