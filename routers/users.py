from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/{user_id}")
async def get_user_by_id(user_id: str):
    return f"Querying for user with id {user_id}"