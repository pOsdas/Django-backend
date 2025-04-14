# Backend на django-rest-framework
Переписанный FastAPI backend: https://github.com/pOsdas/FastAPI-backend на django и DRF
> На столько, на сколько это возможно

Асинхронный запуск с использованием uvicorn:
```shell
uvicorn auth_app.auth_app_project.asgi:application --host 127.0.0.1 --port 8005 --reload
```
```shell
uvicorn user_app.user_app_project.asgi:application --host 127.0.0.1 --port 8006 --reload
```
