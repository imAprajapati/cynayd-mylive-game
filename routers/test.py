from fastapi import APIRouter, HTTPException
router = APIRouter()


@router.get("/test")
async def read_item():
    return {"message": "jokhendra"}


@router.get("/")
async def read_root():
    print( await read_item())
    return {"message": "Hello World"}
