# Backend на django-rest-framework
## Часть с auth service
AUTH SERVICE часть backend'a на FastAPI: https://github.com/pOsdas/FastAPI-backend переписанная на django и DRF
> На столько, на сколько это возможно.

- Вторая часть: https://github.com/pOsdas/Django-backend-2part

Асинхронный запуск с использованием uvicorn:
```shell
poetry run uvicorn auth_app_project.asgi:application --host 127.0.0.1 --port 8005 --reload
```
