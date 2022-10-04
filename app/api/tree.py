from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.utils import upload_multiple_file
from app.core.constants import role_key, resource_type
from app.deps.db import get_async_session
from app.deps.request_params import parse_filter_search_params_trees
from app.deps.users import AuthorizeCurrentUser
from app.models.users import User
from app.schemas.request_params import RequestParamsTree
from app.schemas.trees import (
    Tree as TreeSchema,
    TreeCreate,
    TreeUpdate
)
from app.core.constants import role_authen

name = "tree"
router = APIRouter(prefix=f"/{name}s")
# The role can access API


@router.get(
    "",
    name=f"{name}:list",
)
async def get_list_trees(
    request_params: RequestParamsTree = Depends(parse_filter_search_params_trees()),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
) -> Any:
    """
    Get list trees
    """
    trees = await crud.tree.list_tree(session, request_params)
    responses = []
    for tree in trees:
        response = {**tree}
        response.update({"resources": await crud.tree.get_resources(session, tree.Trees.id, resource_type.TREE)})
        responses.append(response)
    return responses


@router.post(
    "",
    name=f"{name}:create",
    status_code=201,
    response_model=TreeSchema,
)
async def create_tree(
    files: Optional[List[UploadFile]] = File(None),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
) -> Any:
    """
    Create a tree
    """
    tree_in = TreeCreate(name=name, description=description)
    tree = await crud.tree.create(
        session, tree_in, updated_by=user.id
    )
    response = TreeSchema.from_orm(tree)
    if files:
        resources = await upload_multiple_file(session, files, updated_by=user.id)
        await crud.tree.add_resources(session, resources, tree.id, resource_type.TREE)
        response.resources = resources
    return response


@router.get(
    "/{tree_id}",
    name=f"{name}:one",
)
async def get_tree_by_id(
    tree_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
) -> Any:
    """
    Get tree by id
    """
    tree = await crud.tree.get_tree(session, tree_id)
    if not tree:
        raise HTTPException(
            status_code=404,
            detail="The tree not found."
        )
    response = {**tree}
    response.update({"resources": await crud.tree.get_resources(session, tree_id, resource_type.TREE)})
    return response


@router.patch(
    "/{tree_id}",
    name=f"{name}:update",
    response_model=TreeSchema,
)
async def update_tree_by_id(
    tree_id: uuid.UUID,
    tree_in: TreeUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
) -> Any:
    """
    Update tree by id
    - updated_by
    """
    tree = await crud.tree.get(session, tree_id)
    if not tree:
        raise HTTPException(
            status_code=404,
            detail="The tree not found."
        )
    tree = await crud.tree.update(
        session, tree, tree_in, updated_by=user.id
    )
    response = TreeSchema.from_orm(tree)
    response.resources = await crud.tree.get_resources(session, tree_id, resource_type.TREE)
    return response


@router.delete(
    "/{tree_id}",
    name=f"{name}:delete",
)
async def delete_tree_by_id(
    tree_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
) -> Any:
    """
    Delete tree by id
    - updated_by
    - deleted_at
    """
    tree = await crud.tree.get(session, tree_id)
    if not tree:
        raise HTTPException(
            status_code=404,
            detail="The tree not found."
        )
    await crud.tree.delete(session, tree, updated_by=user.id)
    return "The tree deleted successfully!"