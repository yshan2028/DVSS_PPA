"""
字段管理服务层
"""

from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from module_dvss.dao.field_dao import FieldDAO
from module_dvss.schemas.field_schema import (
    FieldBatchUpdate,
    FieldCreate,
    FieldList,
    FieldPermission,
    FieldResponse,
    FieldSensitivityAnalysis,
    FieldUpdate,
)
from utils.log_util import LogUtil

logger = LogUtil.get_logger(__name__)


class FieldService:
    """字段管理服务"""

    def __init__(self, db: AsyncSession):
        self.field_dao = FieldDAO(db)

    async def create_field(self, field_data: FieldCreate) -> FieldResponse:
        """创建字段"""
        try:
            # 检查字段名是否已存在
            existing_field = await self.field_dao.get_field_by_name(field_data.field_name)
            if existing_field:
                raise ValueError(f"字段名 '{field_data.field_name}' 已存在")

            field = await self.field_dao.create_field(field_data)
            logger.info(f'成功创建字段: {field.field_name}')

            return FieldResponse.model_validate(field)
        except Exception as e:
            logger.error(f'创建字段失败: {str(e)}')
            raise

    async def get_field_by_id(self, field_id: int) -> Optional[FieldResponse]:
        """根据ID获取字段"""
        field = await self.field_dao.get_field_by_id(field_id)
        if field:
            return FieldResponse.model_validate(field)
        return None

    async def get_fields_list(
        self,
        page: int = 1,
        size: int = 20,
        category: Optional[str] = None,
        sensitivity_level: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[FieldList], int]:
        """获取字段列表"""
        skip = (page - 1) * size
        fields, total = await self.field_dao.get_fields_list(
            skip=skip,
            limit=size,
            category=category,
            sensitivity_level=sensitivity_level,
            is_active=is_active,
            search=search,
        )

        field_list = [FieldList.model_validate(field) for field in fields]
        return field_list, total

    async def update_field(self, field_id: int, field_data: FieldUpdate) -> Optional[FieldResponse]:
        """更新字段"""
        try:
            # 如果更新字段名，检查是否重复
            if field_data.field_name:
                existing_field = await self.field_dao.get_field_by_name(field_data.field_name)
                if existing_field and existing_field.id != field_id:
                    raise ValueError(f"字段名 '{field_data.field_name}' 已存在")

            field = await self.field_dao.update_field(field_id, field_data)
            if field:
                logger.info(f'成功更新字段: {field.field_name}')
                return FieldResponse.model_validate(field)
            return None
        except Exception as e:
            logger.error(f'更新字段失败: {str(e)}')
            raise

    async def delete_field(self, field_id: int) -> bool:
        """删除字段"""
        try:
            success = await self.field_dao.delete_field(field_id)
            if success:
                logger.info(f'成功删除字段: {field_id}')
            return success
        except Exception as e:
            logger.error(f'删除字段失败: {str(e)}')
            raise

    async def batch_update_fields(self, batch_data: FieldBatchUpdate) -> int:
        """批量更新字段"""
        try:
            count = await self.field_dao.batch_update_fields(batch_data)
            logger.info(f'批量更新字段成功，影响 {count} 条记录')
            return count
        except Exception as e:
            logger.error(f'批量更新字段失败: {str(e)}')
            raise

    async def get_sensitivity_analysis(self) -> FieldSensitivityAnalysis:
        """获取敏感度分析"""
        try:
            analysis_data = await self.field_dao.get_sensitivity_analysis()
            return FieldSensitivityAnalysis(**analysis_data)
        except Exception as e:
            logger.error(f'获取敏感度分析失败: {str(e)}')
            raise

    async def get_fields_by_category(self, category: str) -> List[FieldResponse]:
        """根据分类获取字段"""
        fields = await self.field_dao.get_fields_by_category(category)
        return [FieldResponse.model_validate(field) for field in fields]

    async def get_active_fields(self) -> List[FieldResponse]:
        """获取所有激活的字段"""
        fields = await self.field_dao.get_active_fields()
        return [FieldResponse.model_validate(field) for field in fields]

    async def get_role_field_permissions(self, role_id: int) -> List[FieldPermission]:
        """获取角色的字段权限"""
        try:
            permissions = await self.field_dao.get_field_permissions_by_role(role_id)
            result = []

            for perm in permissions:
                result.append(
                    FieldPermission(
                        field_id=perm.field_id,
                        field_name=perm.field.field_name,
                        can_view=perm.can_view,
                        can_decrypt=perm.can_decrypt,
                    )
                )

            return result
        except Exception as e:
            logger.error(f'获取角色字段权限失败: {str(e)}')
            raise

    async def set_role_field_permissions(self, role_id: int, permissions: List[dict]) -> bool:
        """设置角色字段权限"""
        try:
            success = await self.field_dao.set_role_field_permissions(role_id, permissions)
            if success:
                logger.info(f'成功设置角色 {role_id} 的字段权限')
            return success
        except Exception as e:
            logger.error(f'设置角色字段权限失败: {str(e)}')
            raise

    async def validate_field_access(self, user_role_id: int, field_id: int, access_type: str = 'view') -> bool:
        """验证字段访问权限"""
        try:
            permissions = await self.field_dao.get_field_permissions_by_role(user_role_id)

            for perm in permissions:
                if perm.field_id == field_id:
                    if access_type == 'view':
                        return perm.can_view
                    elif access_type == 'decrypt':
                        return perm.can_decrypt
                    break

            return False
        except Exception as e:
            logger.error(f'验证字段访问权限失败: {str(e)}')
            return False

    async def get_accessible_fields(self, user_role_id: int, access_type: str = 'view') -> List[int]:
        """获取用户可访问的字段ID列表"""
        try:
            permissions = await self.field_dao.get_field_permissions_by_role(user_role_id)
            accessible_fields = []

            for perm in permissions:
                if access_type == 'view' and perm.can_view or access_type == 'decrypt' and perm.can_decrypt:
                    accessible_fields.append(perm.field_id)

            return accessible_fields
        except Exception as e:
            logger.error(f'获取可访问字段失败: {str(e)}')
            return []

    async def calculate_order_sensitivity_score(self, field_values: dict) -> float:
        """计算订单的敏感度分值"""
        try:
            total_score = 0.0
            field_count = 0

            # 获取所有字段信息
            all_fields = await self.field_dao.get_active_fields()
            field_scores = {field.field_name: field.sensitivity_score for field in all_fields}

            # 计算加权平均敏感度
            for field_name, value in field_values.items():
                if field_name in field_scores and value is not None and value != '':
                    total_score += field_scores[field_name]
                    field_count += 1

            return total_score / field_count if field_count > 0 else 0.0
        except Exception as e:
            logger.error(f'计算订单敏感度分值失败: {str(e)}')
            return 0.0
