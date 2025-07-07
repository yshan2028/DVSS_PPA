"""
字段数据访问层
"""

from typing import List, Optional

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from module_dvss.entity.order_field import OrderField, RoleFieldPermission
from module_dvss.schemas.field_schema import FieldBatchUpdate, FieldCreate, FieldUpdate


class FieldDAO:
    """字段数据访问层"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_field(self, field_data: FieldCreate) -> OrderField:
        """创建字段"""
        field = OrderField(**field_data.model_dump())
        self.db.add(field)
        await self.db.commit()
        await self.db.refresh(field)
        return field

    async def get_field_by_id(self, field_id: int) -> Optional[OrderField]:
        """根据ID获取字段"""
        result = await self.db.execute(
            select(OrderField).options(selectinload(OrderField.role_permissions)).where(OrderField.id == field_id)
        )
        return result.scalar_one_or_none()

    async def get_field_by_name(self, field_name: str) -> Optional[OrderField]:
        """根据字段名获取字段"""
        result = await self.db.execute(select(OrderField).where(OrderField.field_name == field_name))
        return result.scalar_one_or_none()

    async def get_fields_list(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        sensitivity_level: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[OrderField], int]:
        """获取字段列表"""
        # 构建查询条件
        conditions = []

        if category:
            conditions.append(OrderField.category == category)
        if sensitivity_level:
            conditions.append(OrderField.sensitivity_level == sensitivity_level)
        if is_active is not None:
            conditions.append(OrderField.is_active == is_active)
        if search:
            conditions.append(OrderField.field_name.contains(search) | OrderField.description.contains(search))

        # 查询总数
        count_query = select(func.count(OrderField.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # 查询数据
        query = select(OrderField).order_by(OrderField.created_at.desc())
        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        fields = result.scalars().all()

        return list(fields), total

    async def update_field(self, field_id: int, field_data: FieldUpdate) -> Optional[OrderField]:
        """更新字段"""
        field = await self.get_field_by_id(field_id)
        if not field:
            return None

        update_data = field_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(field, key, value)

        await self.db.commit()
        await self.db.refresh(field)
        return field

    async def delete_field(self, field_id: int) -> bool:
        """删除字段"""
        field = await self.get_field_by_id(field_id)
        if not field:
            return False

        await self.db.delete(field)
        await self.db.commit()
        return True

    async def batch_update_fields(self, batch_data: FieldBatchUpdate) -> int:
        """批量更新字段"""
        update_data = batch_data.model_dump(exclude={'field_ids'}, exclude_unset=True)
        if not update_data:
            return 0

        query = update(OrderField).where(OrderField.id.in_(batch_data.field_ids)).values(**update_data)

        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount

    async def get_sensitivity_analysis(self) -> dict:
        """获取敏感度分析"""
        # 按敏感度等级统计
        level_stats = await self.db.execute(
            select(OrderField.sensitivity_level, func.count(OrderField.id).label('count'))
            .where(OrderField.is_active)
            .group_by(OrderField.sensitivity_level)
        )

        level_counts = {row.sensitivity_level: row.count for row in level_stats}

        # 按分类统计
        category_stats = await self.db.execute(
            select(OrderField.category, func.count(OrderField.id).label('count'))
            .where(OrderField.is_active)
            .group_by(OrderField.category)
        )

        category_counts = {row.category: row.count for row in category_stats}

        # 总体统计
        total_result = await self.db.execute(
            select(
                func.count(OrderField.id).label('total'), func.avg(OrderField.sensitivity_score).label('avg_score')
            ).where(OrderField.is_active)
        )

        total_stats = total_result.first()

        return {
            'total_fields': total_stats.total or 0,
            'low_sensitivity': level_counts.get('low', 0),
            'medium_sensitivity': level_counts.get('medium', 0),
            'high_sensitivity': level_counts.get('high', 0),
            'critical_sensitivity': level_counts.get('critical', 0),
            'average_score': float(total_stats.avg_score or 0),
            'category_distribution': category_counts,
        }

    async def get_fields_by_category(self, category: str) -> List[OrderField]:
        """根据分类获取字段"""
        result = await self.db.execute(
            select(OrderField)
            .where(and_(OrderField.category == category, OrderField.is_active))
            .order_by(OrderField.sensitivity_score.desc())
        )
        return list(result.scalars().all())

    async def get_active_fields(self) -> List[OrderField]:
        """获取所有激活的字段"""
        result = await self.db.execute(select(OrderField).where(OrderField.is_active).order_by(OrderField.field_name))
        return list(result.scalars().all())

    async def get_field_permissions_by_role(self, role_id: int) -> List[RoleFieldPermission]:
        """获取角色的字段权限"""
        result = await self.db.execute(
            select(RoleFieldPermission)
            .options(selectinload(RoleFieldPermission.field))
            .where(RoleFieldPermission.role_id == role_id)
        )
        return list(result.scalars().all())

    async def set_role_field_permissions(self, role_id: int, permissions: List[dict]) -> bool:
        """设置角色字段权限"""
        try:
            # 删除现有权限
            await self.db.execute(delete(RoleFieldPermission).where(RoleFieldPermission.role_id == role_id))

            # 创建新权限
            for perm in permissions:
                permission = RoleFieldPermission(
                    role_id=role_id,
                    field_id=perm['field_id'],
                    can_view=perm.get('can_view', False),
                    can_decrypt=perm.get('can_decrypt', False),
                )
                self.db.add(permission)

            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
