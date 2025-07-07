"""
分片管理控制器
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_current_user, get_db
from exceptions.custom_exception import AuthorizationError, NotFoundError, ValidationError
from module_dvss.schemas.common_schema import ApiResponse
from module_dvss.schemas.shard_schema import (
    ShardInfoCreate,
    ShardInfoResponse,
    ShardInfoUpdate,
    ShardListResponse,
    ShardStatsResponse,
    # 移除未使用的导入
    # ShardReconstructRequest,
    # ShardReconstructResponse,
)
from module_dvss.service.shard_service import ShardService
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/api/v1/shards', tags=['分片管理'])


@router.get('', response_model=ApiResponse[ShardListResponse])
async def get_shards(
    page: int = Query(1, ge=1, description='页码'),
    size: int = Query(20, ge=1, le=100, description='每页大小'),
    order_id: Optional[str] = Query(None, description='订单ID'),
    status: Optional[str] = Query(None, description='分片状态'),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取分片列表"""
    try:
        shard_service = ShardService(db)

        result = await shard_service.get_shard_list(user_id=current_user.id, page=page, size=size)

        return ResponseUtil.success(data=result, message='获取分片列表成功')
    except Exception as e:
        return ResponseUtil.error(message=f'获取分片列表失败: {str(e)}')


@router.post('', response_model=ApiResponse[ShardInfoResponse])
async def create_shard(
    shard_data: ShardInfoCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    """创建分片"""
    try:
        shard_service = ShardService(db)
        result = await shard_service.create_shard(shard_data, current_user.id)

        return ResponseUtil.success(data=result, message='分片创建成功')
    except ValidationError as e:
        return ResponseUtil.error(message=str(e), code=400)
    except Exception as e:
        return ResponseUtil.error(message=f'创建分片失败: {str(e)}')


@router.get('/{shard_id}', response_model=ApiResponse[ShardInfoResponse])
async def get_shard_detail(shard_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    """获取分片详情"""
    try:
        shard_service = ShardService(db)
        result = await shard_service.get_shard_by_id(shard_id, current_user.id)

        return ResponseUtil.success(data=result, message='获取分片详情成功')
    except NotFoundError as e:
        return ResponseUtil.error(message=str(e), code=404)
    except AuthorizationError as e:
        return ResponseUtil.error(message=str(e), code=403)
    except Exception as e:
        return ResponseUtil.error(message=f'获取分片详情失败: {str(e)}')


@router.put('/{shard_id}', response_model=ApiResponse[ShardInfoResponse])
async def update_shard(
    shard_id: int,
    shard_data: ShardInfoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """更新分片信息"""
    try:
        shard_service = ShardService(db)
        result = await shard_service.update_shard(shard_id, shard_data, current_user.id)

        return ResponseUtil.success(data=result, message='分片更新成功')
    except NotFoundError as e:
        return ResponseUtil.error(message=str(e), code=404)
    except AuthorizationError as e:
        return ResponseUtil.error(message=str(e), code=403)
    except ValidationError as e:
        return ResponseUtil.error(message=str(e), code=400)
    except Exception as e:
        return ResponseUtil.error(message=f'更新分片失败: {str(e)}')


@router.delete('/{shard_id}', response_model=ApiResponse[bool])
async def delete_shard(shard_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    """删除分片"""
    try:
        shard_service = ShardService(db)
        result = await shard_service.delete_shard(shard_id, current_user.id)

        return ResponseUtil.success(data=result, message='分片删除成功')
    except NotFoundError as e:
        return ResponseUtil.error(message=str(e), code=404)
    except AuthorizationError as e:
        return ResponseUtil.error(message=str(e), code=403)
    except ValidationError as e:
        return ResponseUtil.error(message=str(e), code=400)
    except Exception as e:
        return ResponseUtil.error(message=f'删除分片失败: {str(e)}')


@router.get('/{shard_id}/download')
async def download_shard(shard_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    """下载分片数据"""
    try:
        shard_service = ShardService(db)
        shard_data = await shard_service.download_shard(shard_id, current_user.id)

        def iter_file():
            yield shard_data

        return StreamingResponse(
            iter_file(),
            media_type='application/octet-stream',
            headers={'Content-Disposition': f'attachment; filename=shard_{shard_id}.bin'},
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'下载分片失败: {str(e)}')


@router.post('/batch-delete', response_model=ApiResponse[bool])
async def batch_delete_shards(
    shard_ids: List[str], db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    """批量删除分片"""
    try:
        shard_service = ShardService(db)
        success_count = 0

        for shard_id in shard_ids:
            try:
                await shard_service.delete_shard(shard_id, current_user.id)
                success_count += 1
            except Exception:
                continue

        return ResponseUtil.success(data=True, message=f'批量删除成功，共删除 {success_count}/{len(shard_ids)} 个分片')
    except Exception as e:
        return ResponseUtil.error(message=f'批量删除分片失败: {str(e)}')


@router.get('/stats/overview', response_model=ApiResponse[ShardStatsResponse])
async def get_shard_stats(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    """获取分片统计信息"""
    try:
        shard_service = ShardService(db)
        result = await shard_service.get_shard_stats(current_user.id)

        return ResponseUtil.success(data=result, message='获取分片统计成功')
    except Exception as e:
        return ResponseUtil.error(message=f'获取分片统计失败: {str(e)}')


@router.post('/{shard_id}/validate', response_model=ApiResponse[bool])
async def validate_shard(shard_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    """验证分片完整性"""
    try:
        shard_service = ShardService(db)
        result = await shard_service.validate_shard(shard_id, current_user.id)

        return ResponseUtil.success(data=result, message='分片验证完成' if result else '分片验证失败，数据可能已损坏')
    except NotFoundError as e:
        return ResponseUtil.error(message=str(e), code=404)
    except AuthorizationError as e:
        return ResponseUtil.error(message=str(e), code=403)
    except Exception as e:
        return ResponseUtil.error(message=f'验证分片失败: {str(e)}')


@router.post('/{shard_id}/reprocess', response_model=ApiResponse[bool])
async def reprocess_shard(shard_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    """重新处理分片"""
    try:
        shard_service = ShardService(db)

        # 更新分片状态为待处理
        update_request = ShardInfoUpdate(status='pending')
        await shard_service.update_shard(shard_id, update_request, current_user.id)

        return ResponseUtil.success(data=True, message='分片已标记为重新处理')
    except NotFoundError as e:
        return ResponseUtil.error(message=str(e), code=404)
    except AuthorizationError as e:
        return ResponseUtil.error(message=str(e), code=403)
    except Exception as e:
        return ResponseUtil.error(message=f'重新处理分片失败: {str(e)}')
