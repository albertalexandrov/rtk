from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("")
async def list_users():
    return


@router.get("/{user_id}")
async def get_user(user_id: int):
    return


@router.post("")
async def create_user():
    return


@router.patch("/{user_id}")
async def update_user(user_id: int):
    return


@router.delete("/user_id")
async def delete_user(user_id: int):
    return
