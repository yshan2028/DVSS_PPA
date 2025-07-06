"""
订单数据访问层
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..entity.original_order import OriginalOrder
from ..entity.encrypted_order import EncryptedOrder
from core.deps import get_db_session


class OrderDAO:
    """订单数据访问对象"""
    
    def __init__(self):
        self.session = None
    
    async def get_session(self) -> Session:
        """获取数据库会话"""
        if not self.session:
            self.session = next(get_db_session())
        return self.session
    
    async def create(self, order: OriginalOrder) -> OriginalOrder:
        """创建订单"""
        session = await self.get_session()
        try:
            session.add(order)
            session.commit()
            session.refresh(order)
            return order
        except Exception as e:
            session.rollback()
            raise e
    
    async def get_by_id(self, order_id: int) -> Optional[OriginalOrder]:
        """根据ID获取订单"""
        session = await self.get_session()
        return session.query(OriginalOrder).filter(
            and_(
                OriginalOrder.id == order_id,
                OriginalOrder.status != 'deleted'
            )
        ).first()
    
    async def get_by_order_id(self, order_id: str) -> Optional[OriginalOrder]:
        """根据订单号获取订单"""
        session = await self.get_session()
        return session.query(OriginalOrder).filter(
            and_(
                OriginalOrder.order_id == order_id,
                OriginalOrder.status != 'deleted'
            )
        ).first()
    
    async def get_list(self, page: int = 1, size: int = 10, 
                      filters: Optional[Dict[str, Any]] = None,
                      order_by: str = 'created_at',
                      order_direction: str = 'desc') -> Tuple[List[OriginalOrder], int]:
        """获取订单列表"""
        session = await self.get_session()
        
        query = session.query(OriginalOrder).filter(OriginalOrder.status != 'deleted')
        
        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if hasattr(OriginalOrder, key) and value is not None:
                    if key == 'user_id':
                        query = query.filter(OriginalOrder.user_id == value)
                    elif key == 'status':
                        query = query.filter(OriginalOrder.status == value)
                    elif key == 'start_date':
                        query = query.filter(OriginalOrder.created_at >= value)
                    elif key == 'end_date':
                        query = query.filter(OriginalOrder.created_at <= value)
                    elif key == 'keyword':
                        # 模糊搜索
                        query = query.filter(
                            or_(
                                OriginalOrder.order_id.like(f'%{value}%'),
                                OriginalOrder.name.like(f'%{value}%'),
                                OriginalOrder.phone.like(f'%{value}%'),
                                OriginalOrder.email.like(f'%{value}%')
                            )
                        )
                    elif key == 'min_amount':
                        query = query.filter(OriginalOrder.total_amount >= value)
                    elif key == 'max_amount':
                        query = query.filter(OriginalOrder.total_amount <= value)
                    elif key == 'sensitivity_level':
                        # 根据敏感度级别过滤
                        if value == 'low':
                            query = query.filter(OriginalOrder.sensitivity_score < 0.3)
                        elif value == 'medium':
                            query = query.filter(
                                and_(
                                    OriginalOrder.sensitivity_score >= 0.3,
                                    OriginalOrder.sensitivity_score < 0.7
                                )
                            )
                        elif value == 'high':
                            query = query.filter(OriginalOrder.sensitivity_score >= 0.7)
        
        # 获取总数
        total = query.count()
        
        # 排序
        if hasattr(OriginalOrder, order_by):
            if order_direction.lower() == 'desc':
                query = query.order_by(desc(getattr(OriginalOrder, order_by)))
            else:
                query = query.order_by(asc(getattr(OriginalOrder, order_by)))
        
        # 分页
        orders = query.offset((page - 1) * size).limit(size).all()
        
        return orders, total
    
    async def update(self, order_id: int, update_data: Dict[str, Any]) -> Optional[OriginalOrder]:
        """更新订单"""
        session = await self.get_session()
        try:
            order = session.query(OriginalOrder).filter(OriginalOrder.id == order_id).first()
            if not order:
                return None
            
            for key, value in update_data.items():
                if hasattr(order, key):
                    setattr(order, key, value)
            
            order.updated_at = datetime.now()
            session.commit()
            session.refresh(order)
            return order
        except Exception as e:
            session.rollback()
            raise e
    
    async def delete(self, order_id: int) -> bool:
        """删除订单（物理删除）"""
        session = await self.get_session()
        try:
            order = session.query(OriginalOrder).filter(OriginalOrder.id == order_id).first()
            if not order:
                return False
            
            session.delete(order)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
    
    async def soft_delete(self, order_id: int) -> bool:
        """软删除订单"""
        return await self.update(order_id, {'status': 'deleted'}) is not None
    
    async def get_orders_by_user(self, user_id: str, page: int = 1, size: int = 10) -> Tuple[List[OriginalOrder], int]:
        """获取用户的订单列表"""
        return await self.get_list(
            page=page, 
            size=size, 
            filters={'user_id': user_id}
        )
    
    async def get_orders_by_status(self, status: str, page: int = 1, size: int = 10) -> Tuple[List[OriginalOrder], int]:
        """根据状态获取订单列表"""
        return await self.get_list(
            page=page, 
            size=size, 
            filters={'status': status}
        )
    
    async def get_sensitive_orders(self, threshold: float = 0.7, page: int = 1, size: int = 10) -> Tuple[List[OriginalOrder], int]:
        """获取高敏感度订单"""
        session = await self.get_session()
        
        query = session.query(OriginalOrder).filter(
            and_(
                OriginalOrder.sensitivity_score >= threshold,
                OriginalOrder.status != 'deleted'
            )
        ).order_by(desc(OriginalOrder.sensitivity_score))
        
        total = query.count()
        orders = query.offset((page - 1) * size).limit(size).all()
        
        return orders, total
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取订单统计信息"""
        session = await self.get_session()
        
        # 基础统计
        total_orders = session.query(func.count(OriginalOrder.id)).filter(
            OriginalOrder.status != 'deleted'
        ).scalar()
        
        active_orders = session.query(func.count(OriginalOrder.id)).filter(
            OriginalOrder.status == 'active'
        ).scalar()
        
        encrypted_orders = session.query(func.count(OriginalOrder.id)).filter(
            OriginalOrder.status == 'encrypted'
        ).scalar()
        
        # 平均敏感度
        avg_sensitivity = session.query(func.avg(OriginalOrder.sensitivity_score)).filter(
            OriginalOrder.status != 'deleted'
        ).scalar() or 0.0
        
        # 高风险订单数（敏感度 >= 0.7）
        high_risk_orders = session.query(func.count(OriginalOrder.id)).filter(
            and_(
                OriginalOrder.sensitivity_score >= 0.7,
                OriginalOrder.status != 'deleted'
            )
        ).scalar()
        
        # 敏感度分布
        sensitivity_distribution = {
            'low': session.query(func.count(OriginalOrder.id)).filter(
                and_(
                    OriginalOrder.sensitivity_score < 0.3,
                    OriginalOrder.status != 'deleted'
                )
            ).scalar(),
            'medium': session.query(func.count(OriginalOrder.id)).filter(
                and_(
                    OriginalOrder.sensitivity_score >= 0.3,
                    OriginalOrder.sensitivity_score < 0.7,
                    OriginalOrder.status != 'deleted'
                )
            ).scalar(),
            'high': session.query(func.count(OriginalOrder.id)).filter(
                and_(
                    OriginalOrder.sensitivity_score >= 0.7,
                    OriginalOrder.status != 'deleted'
                )
            ).scalar()
        }
        
        # 每日订单数量（最近30天）
        thirty_days_ago = datetime.now() - timedelta(days=30)
        daily_stats = session.query(
            func.date(OriginalOrder.created_at).label('date'),
            func.count(OriginalOrder.id).label('count')
        ).filter(
            and_(
                OriginalOrder.created_at >= thirty_days_ago,
                OriginalOrder.status != 'deleted'
            )
        ).group_by(func.date(OriginalOrder.created_at)).all()
        
        daily_stats_dict = [
            {
                'date': stat.date.strftime('%Y-%m-%d'),
                'count': stat.count
            }
            for stat in daily_stats
        ]
        
        return {
            'total_orders': total_orders,
            'active_orders': active_orders,
            'encrypted_orders': encrypted_orders,
            'average_sensitivity': round(avg_sensitivity, 2),
            'high_risk_orders': high_risk_orders,
            'sensitivity_distribution': sensitivity_distribution,
            'daily_stats': daily_stats_dict
        }
    
    # 加密订单相关方法
    async def create_encrypted_order(self, encrypted_order: EncryptedOrder) -> EncryptedOrder:
        """创建加密订单"""
        session = await self.get_session()
        try:
            session.add(encrypted_order)
            session.commit()
            session.refresh(encrypted_order)
            return encrypted_order
        except Exception as e:
            session.rollback()
            raise e
    
    async def get_encrypted_order_by_id(self, encrypted_order_id: int) -> Optional[EncryptedOrder]:
        """根据ID获取加密订单"""
        session = await self.get_session()
        return session.query(EncryptedOrder).filter(
            EncryptedOrder.id == encrypted_order_id
        ).first()
    
    async def get_encrypted_order_by_original_id(self, original_order_id: int) -> Optional[EncryptedOrder]:
        """根据原始订单ID获取加密订单"""
        session = await self.get_session()
        return session.query(EncryptedOrder).filter(
            EncryptedOrder.original_order_id == original_order_id
        ).first()
    
    async def get_encrypted_orders_list(self, page: int = 1, size: int = 10,
                                       filters: Optional[Dict[str, Any]] = None) -> Tuple[List[EncryptedOrder], int]:
        """获取加密订单列表"""
        session = await self.get_session()
        
        query = session.query(EncryptedOrder)
        
        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if hasattr(EncryptedOrder, key) and value is not None:
                    if key == 'status':
                        query = query.filter(EncryptedOrder.status == value)
                    elif key == 'algorithm':
                        query = query.filter(EncryptedOrder.encryption_algorithm == value)
                    elif key == 'start_date':
                        query = query.filter(EncryptedOrder.created_at >= value)
                    elif key == 'end_date':
                        query = query.filter(EncryptedOrder.created_at <= value)
        
        # 获取总数
        total = query.count()
        
        # 排序和分页
        encrypted_orders = query.order_by(desc(EncryptedOrder.created_at)).offset(
            (page - 1) * size
        ).limit(size).all()
        
        return encrypted_orders, total
    
    async def update_encrypted_order(self, encrypted_order_id: int, 
                                   update_data: Dict[str, Any]) -> Optional[EncryptedOrder]:
        """更新加密订单"""
        session = await self.get_session()
        try:
            encrypted_order = session.query(EncryptedOrder).filter(
                EncryptedOrder.id == encrypted_order_id
            ).first()
            if not encrypted_order:
                return None
            
            for key, value in update_data.items():
                if hasattr(encrypted_order, key):
                    setattr(encrypted_order, key, value)
            
            encrypted_order.updated_at = datetime.now()
            session.commit()
            session.refresh(encrypted_order)
            return encrypted_order
        except Exception as e:
            session.rollback()
            raise e
    
    async def search_orders(self, keyword: str, page: int = 1, size: int = 10) -> Tuple[List[OriginalOrder], int]:
        """搜索订单"""
        session = await self.get_session()
        
        query = session.query(OriginalOrder).filter(
            and_(
                OriginalOrder.status != 'deleted',
                or_(
                    OriginalOrder.order_id.like(f'%{keyword}%'),
                    OriginalOrder.name.like(f'%{keyword}%'),
                    OriginalOrder.phone.like(f'%{keyword}%'),
                    OriginalOrder.email.like(f'%{keyword}%'),
                    OriginalOrder.item_name.like(f'%{keyword}%')
                )
            )
        ).order_by(desc(OriginalOrder.created_at))
        
        total = query.count()
        orders = query.offset((page - 1) * size).limit(size).all()
        
        return orders, total
    
    async def get_orders_by_date_range(self, start_date: datetime, end_date: datetime,
                                      page: int = 1, size: int = 10) -> Tuple[List[OriginalOrder], int]:
        """根据日期范围获取订单"""
        return await self.get_list(
            page=page,
            size=size,
            filters={
                'start_date': start_date,
                'end_date': end_date
            }
        )
