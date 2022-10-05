from fastapi import FastAPI, BackgroundTasks
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi_users import FastAPIUsers
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse

from app.api import api_router
from app.core.config import settings
from app.core.logger import logger
from app.deps.users import fastapi_users, jwt_authentication, member_authentication

import firebase_admin

def create_app():
    description = f"{settings.PROJECT_NAME} API"
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_PATH}/openapi.json",
        docs_url="/docs/",
        description=description,
        redoc_url=None,
    )
    setup_routers(app)
    init_firebase()
    init_db_hooks(app)
    setup_cors_middleware(app)
    serve_static_app(app)
    return app


def setup_routers(app: FastAPI) -> None:
    app.include_router(api_router, prefix=settings.API_PATH)
    app.include_router(
        fastapi_users.get_auth_router(
            jwt_authentication,
            requires_verification=False,
        ),
        prefix=f"{settings.API_PATH}/auth/jwt",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(),
        prefix=f"{settings.API_PATH}/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_verify_router(),
        prefix=f"{settings.API_PATH}/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix=f"{settings.API_PATH}/auth",
        tags=["auth"],
    )
#     # app.include_router(
#     #     fastapi_users.get_users_router(requires_verification=True),
#     #     prefix=f"{settings.API_PATH}/users",
#     #     tags=["users"],
#     # )
#     # The following operation needs to be at the end of this function
    use_route_names_as_operation_ids(app)


def serve_static_app(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # @app.middleware("http")
    # async def _add_404_middleware(request: Request, call_next):
    #     print(request.__dict__)
    #     response = await call_next(request)
    #     path = request["path"]
    #     if path.startswith(settings.API_PATH) or path.startswith("/docs") or path.startswith("/static"):
    #         return response
    #     if response.status_code == 404:
    #         return FileResponse("static/index.html")
    #     return response


def setup_cors_middleware(app):
    # if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        expose_headers=["Content-Range", "Range"],
        allow_headers=["Authorization", "Range", "Content-Range"],
    )


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    route_names = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in route_names:
                raise Exception("Route function names should be unique")
            route.operation_id = route.name
            route_names.add(route.name)

def init_firebase():
    firebase_cred = firebase_admin.credentials.Certificate(settings.FIREBASE_CERT)
    firebase_admin.initialize_app(firebase_cred)

def init_db_hooks(app: FastAPI) -> None:
    from app.db import database

    @app.on_event("startup")
    async def startup():
        await database.connect()

    @app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()