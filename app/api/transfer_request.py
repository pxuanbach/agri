import math
from typing import Any, List
import uuid
from sqlalchemy import select
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import role_key, transfer_status, role_authen, product_transfer_status, resource_type
from app.core.firebase import _firebase
from app.core.msg import msg
from app import crud
from app.deps.db import get_async_session
from app.deps.users import AuthorizeCurrentUser
from app.models.users import User
from app.models.transfer_request import TransferRequests
from app.schemas.transfer import (
    TransferRequest as TransferRequestSchema,
    TransferRequestCreate,
)
from app.schemas.transfer import (
    ProductHistory as ProductHistorySchema,
    ProductHistoryCreate,
    ProductHistoryUpdate
)
from app.schemas.request_params import RequestParamsTransferRequest
from app.deps.request_params import parse_filter_search_params_transfer_request
from app.schemas.responses import ResponsePagination
from app.models.resource import Resource
from app.models.item_resources import ItemResources


name = "transfer-request"
router = APIRouter(prefix=f"/{name}")


@router.get(
    "",
    name=f"{name}:list",
)
async def get_list_transfer_request(
    request_params: RequestParamsTransferRequest = Depends(
        parse_filter_search_params_transfer_request(TransferRequests)
    ),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all))
) -> Any:
    """
    Get list transfer request
    """
    total = await crud.transfer_request.total_transfer_requests_by_product(session, request_params)
    transfer_request = await crud.transfer_request.list_transfer_requests_by_product(session, request_params)
    if not transfer_request:
        return ResponsePagination(
            page_total=1,
            page_size=request_params.limit,
            page=request_params.skip / request_params.limit + 1,
            data=transfer_request,
        )
    return ResponsePagination(
        page_total=math.ceil(total/ request_params.limit),
        page_size=request_params.limit,
        page=request_params.skip / request_params.limit + 1,
        data=transfer_request,
    )


@router.post(
    "",
    name=f"{name}:create",
    status_code=201,
)
async def create_transfer_request(
    background_tasks: BackgroundTasks,
    transfer_request_in: TransferRequestCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
) -> Any:
    """
    Create a transfer 
    """
    product = await crud.product.get(session, transfer_request_in.product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )
    if product.updated_by == transfer_request_in.transfer_to_user_id:
        raise HTTPException(
            status_code=403,
            detail="User can not request user's own products."
        )
    if product.updated_by != transfer_request_in.transfer_from_user_id:
        raise HTTPException(
            status_code=403,
            detail=f"User with id {transfer_request_in.transfer_from_user_id} does not own this product."
        )
    check_exist = await crud.product.check_pending_product_status_of_requester(session, product.id, user.id)
    if check_exist:
        raise HTTPException(
            status_code=403,
            detail=f"User have already requested for this product."
        )
    status_id = await crud.transfer_request.get_status(session, transfer_status.PENDING)
    transfer_request = await crud.transfer_request.create(
        session, transfer_request_in, status_id=status_id, updated_by=user.id
    )
    # Update product status of owner
    await crud.product.update_product_status(
        session, transfer_request_in.product_id, product_status=product_transfer_status.PENDING, updated_by=transfer_request.transfer_from_user_id
    )
    # Update product status of buyer
    await crud.product.update_product_status(
        session, transfer_request_in.product_id, product_status=product_transfer_status.PENDING, updated_by=transfer_request.transfer_to_user_id
    )

    first_image_path = (
        await session.execute(
            select(Resource.file_path)
            .filter(ItemResources.item_id == product.id)
            .filter(ItemResources.item_type == resource_type.PRODUCT)
            .filter(Resource.id == ItemResources.resource_id)
        )
    ).scalars().first()

    # Send notification to requester
    background_tasks.add_task(
        _firebase.send_to_topics,
        title=msg.YOU_HAVE_CREATED_A_NEW_TRANSFER_REQUEST,
        body=f"you have created a new transfer request for product {product.name}",
        data={"event": "add_transfer_request", "product_id": str(product.id), "to_user_id": str(transfer_request_in.transfer_to_user_id), "from_user_id": str(transfer_request_in.transfer_from_user_id)},
        topics=[f"user_{transfer_request_in.transfer_to_user_id}"],
        imageUrl=first_image_path,
    )

    # Send notification to owner
    background_tasks.add_task(
        _firebase.send_to_topics,
        title=msg.YOU_HAVE_A_NEW_TRANSFER_REQUEST,
        body=f"Product {product.name} has been requested for transfer",
        data={"event": "receive_transfer_request", "product_id": str(product.id), "to_user_id": str(transfer_request_in.transfer_to_user_id), "from_user_id": str(transfer_request_in.transfer_from_user_id)},
        topics=[f"user_{transfer_request_in.transfer_from_user_id}"],
        imageUrl=first_image_path,
    )

    return transfer_request


@router.get(
    "/{transfer_request_id}",
    name=f"{name}:one",
)
async def get_transfer_request_by_id(
    transfer_request_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """
    Get transfer request by id
    """
    transfer_request = await crud.transfer_request.get_transfer_request(session, transfer_request_id)
    if not transfer_request:
        raise HTTPException(
            status_code=404,
            detail="The transfer request not found."
        )
    return transfer_request


@router.patch(
    "/{transfer_request_id}",
    name=f"{name}:update",
)
async def update_transfer_request_by_id(
    background_tasks: BackgroundTasks,
    transfer_request_id: uuid.UUID,
    transfer_request_status: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
) -> Any:
    """
    Update transfer request by id
    - status: accepted/ denied
    """
    transfer_request = await crud.transfer_request.get(session, transfer_request_id)
    if not transfer_request:
        raise HTTPException(
            status_code=404,
            detail="The transfer request not found."
        )

    # Only admin and people involve can update transfer request
    current_user_role = await crud.user.get_role_by_id(
        session, user.role_id
    )
    if not current_user_role:
        raise HTTPException(
            status_code=404,
            detail="User role of current user not found.",
        )
    if current_user_role.key != role_key.ADMIN:
        if user.id != transfer_request.transfer_to_user_id and user.id != transfer_request.transfer_from_user_id:
            raise HTTPException(
                status_code=401,
                detail="User do not have permission.",
            )
    
    pending_id = await crud.transfer_request.get_status(session, product_transfer_status .PENDING)
    if transfer_request.transfer_status_id == pending_id:
        new_status_id = await crud.transfer_request.get_status(session, transfer_request_status)
        if not new_status_id:
            raise HTTPException(
                status_code=404,
                detail="Transfer status not found."
            )

        product = await crud.product.get(session, transfer_request.product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found or was deleted."
            )
        first_image_path = (
            await session.execute(
                select(Resource.file_path)
                .filter(ItemResources.item_id == product.id)
                .filter(ItemResources.item_type == resource_type.PRODUCT)
                .filter(Resource.id == ItemResources.resource_id)
            )
        ).scalars().first()   

        # Request accepted then update request status and product status, owner
        # And change all other pending requests to failed
        if transfer_request_status == transfer_status.ACCEPTED: 
            await crud.product.update_product_owner(session, product, updated_by=transfer_request.transfer_to_user_id)
            # Update product status of buyer
            await crud.product.update_product_status(session, product.id, product_status=product_transfer_status.NORMAL , updated_by=transfer_request.transfer_to_user_id)
            # Update product status of seller
            await crud.product.update_product_status(session, product.id, product_status=product_transfer_status.ACCEPTED , updated_by=transfer_request.transfer_from_user_id)
            transfer_history = ProductHistoryCreate(
                id = uuid.uuid4(),
                product_id = transfer_request.product_id,
                transfer_from_user_id = transfer_request.transfer_from_user_id,
                transfer_to_user_id =transfer_request.transfer_to_user_id
            )
            await crud.product_history.create(session, transfer_history, user.id)

            denied_id = await crud.transfer_request.get_status(session, transfer_status.DENIED)
            # Update transfer request status of product
            updated_requests = await crud.transfer_request.update_transfer_requests_status_by_product(
                session, product.id, denied_id, updated_by=transfer_request.transfer_to_user_id
            )
            transfer_request = await crud.transfer_request.update_transfer_request_status(
                session, transfer_request, new_status_id, updated_by=user.id
            )
            await crud.product.update_products_status(
                session, product.id, from_status=product_transfer_status.PENDING, to_status=product_transfer_status.DENIED
            )

            # Send notification to seller who can't buy
            topics = []
            for request in updated_requests:
                topics.append(f"user_{request.transfer_to_user_id}")

            # Send notification to seller
            background_tasks.add_task(
                _firebase.send_to_topics,
                title=msg.A_TRANSFER_REQUEST_HAVE_BEEN_DENIED,
                body=f"Product {product.name} has been denied",
                data={"event": "denied_transfer_request", "product_id": str(product.id), "from_user_id": str(transfer_request.transfer_from_user_id)},
                topics=topics,
                imageUrl=first_image_path,
            )
            
            # Send notification to seller
            background_tasks.add_task(
                _firebase.send_to_topics,
                title=msg.YOU_HAVE_ACCEPTED_A_TRANSFER_REQUEST,
                body=f"Product {product.name} has been successfully transfered",
                data={"event": "accepted_transfer_request", "product_id": str(product.id), "to_user_id": str(transfer_request.transfer_to_user_id), "from_user_id": str(transfer_request.transfer_from_user_id)},
                topics=[f"user_{transfer_request.transfer_from_user_id}"],
                imageUrl=first_image_path,
            )

            # Send notification to buyer
            background_tasks.add_task(
                _firebase.send_to_topics,
                title=msg.YOUR_TRANSFER_REQUEST_HAVE_BEEN_ACCEPTED,
                body=f"Product {product.name} has been successfully transfered",
                data={"event": "accepted_transfer_request", "product_id": str(product.id), "to_user_id": str(transfer_request.transfer_to_user_id), "from_user_id": str(transfer_request.transfer_from_user_id)},
                topics=[f"user_{transfer_request.transfer_to_user_id}"],
                imageUrl=first_image_path,
            )

        elif transfer_request_status == transfer_status.DENIED:
            transfer_request = await crud.transfer_request.update_transfer_request_status(
                session, transfer_request, new_status_id, updated_by=user.id
            )

            # Update product status of buyer
            await crud.product.update_product_status(session, product.id, product_status=product_transfer_status.DENIED ,updated_by=transfer_request.transfer_to_user_id)
            product_status = await crud.product.check_pending_product_status(session, product.id)
            if not product_status:
                # Update product status of seller
                await crud.product.update_product_status(session, product.id, product_status=product_transfer_status.NORMAL ,updated_by=transfer_request.transfer_from_user_id)

            # Send notification to seller and buyer
            background_tasks.add_task(
                _firebase.send_to_topics,
                title=msg.A_TRANSFER_REQUEST_HAVE_BEEN_DENIED,
                body=f"Product {product.name} has been denied",
                data={"event": "denied_transfer_request", "product_id": str(product.id), "to_user_id": str(transfer_request.transfer_to_user_id), "from_user_id": str(transfer_request.transfer_from_user_id)},
                topics=[f"user_{transfer_request.transfer_from_user_id}", f"user_{transfer_request.transfer_to_user_id}"],
                imageUrl=first_image_path,
            )

        else:
            pass
    else:
        raise HTTPException(
            status_code=403,
            detail="Transfer request is no longer available."
        )
    return transfer_request


@router.delete(
    "/{transfer_request_id}",
    name=f"{name}:delete",
    include_in_schema=False,
)
async def delete_transfer_request_by_id(
    transfer_request_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_admin))
) -> Any:
    """
    Delete transfer request by id
    - updated_by
    - deleted_at
    """
    current_user_role = await crud.user.get_role_by_id(
        session, user.role_id
    )
    if not current_user_role:
        raise HTTPException(
            status_code=404,
            detail="User role of current user not found.",
        )
    if current_user_role.key != role_key.ADMIN:
        raise HTTPException(
            status_code=401,
            detail="User do not have permission.",
        )

    transfer_request = await crud.transfer_request.get(session, transfer_request_id)
    if not transfer_request:
        raise HTTPException(
            status_code=404,
            detail="The transfer request not found."
        )
    await crud.transfer_request.delete(session, transfer_request, updated_by=user.id)
    return "The transfer request deleted successfully!"