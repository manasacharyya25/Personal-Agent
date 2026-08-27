from fastapi import APIRouter, Depends

from dependencies import verify_api_key

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(verify_api_key)]
)

@router.get("/{user_id}")
async def get_user_by_id(user_id: str):
    return f"Querying for user with id {user_id}"