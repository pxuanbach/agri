from fastapi import APIRouter

from app.api import (
    user,
    farm,
    resource,
    fertilizer,
    tree,
    product,
    transfer_status,
    transfer_request
)

api_router = APIRouter()

api_router.include_router(user.router, tags=["user"])
api_router.include_router(farm.router, tags=["farm"])
api_router.include_router(resource.router, tags=["resource"])
api_router.include_router(fertilizer.router, tags=["fertilizer"])
api_router.include_router(tree.router, tags=["tree"])
api_router.include_router(product.router, tags=["product"])
api_router.include_router(transfer_status.router, tags=["transfer status"])
api_router.include_router(transfer_request.router, tags=["transfer request"])
