from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_shards():
    return {"message": "分片列表"}

@router.get("/health")
def shard_health():
    return {"message": "分片模块正常"}

