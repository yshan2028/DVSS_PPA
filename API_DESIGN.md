# DVSS-PPA API 接口设计文档

## Python 后端 API (FastAPI) - Port 8000

### 认证相关接口

#### POST /api/v1/auth/login
用户登录

**请求参数:**
```json
{
  "username": "string",
  "password": "string"
}
```

**响应数据:**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "user_info": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "full_name": "管理员",
      "role": {
        "id": 1,
        "name": "管理员"
      }
    }
  }
}
```

#### POST /api/v1/auth/logout
用户登出

#### GET /api/v1/auth/profile
获取当前用户信息

### 用户管理接口

#### GET /api/v1/users
获取用户列表

**查询参数:**
- page: 页码
- size: 每页数量
- search: 搜索关键词
- role_id: 角色ID筛选
- is_active: 状态筛选

#### POST /api/v1/users
创建用户

**请求参数:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string",
  "phone": "string",
  "role_id": 1,
  "is_active": true
}
```

#### PUT /api/v1/users/{id}
更新用户信息

#### DELETE /api/v1/users/{id}
删除用户

### 角色管理接口

#### GET /api/v1/roles
获取角色列表

#### POST /api/v1/roles
创建角色

**请求参数:**
```json
{
  "name": "string",
  "description": "string",
  "is_active": true
}
```

#### PUT /api/v1/roles/{id}/permissions
设置角色权限

**请求参数:**
```json
{
  "field_permissions": [
    {
      "field_id": 1,
      "can_view": true,
      "can_decrypt": false
    }
  ]
}
```

### 字段管理接口

#### GET /api/v1/fields
获取字段列表

#### POST /api/v1/fields
创建字段

**请求参数:**
```json
{
  "field_name": "name",
  "field_type": "string",
  "sensitivity_level": "high",
  "sensitivity_score": 0.9,
  "category": "pii",
  "description": "客户姓名",
  "is_required": true
}
```

### 订单管理接口

#### GET /api/v1/orders
获取订单列表（按权限过滤字段）

#### POST /api/v1/orders/upload
上传订单文件

**请求参数:**
- file: 上传的CSV/JSON文件
- file_type: 文件类型

#### POST /api/v1/orders/{id}/encrypt
加密订单

**请求参数:**
```json
{
  "k_value": 3,
  "n_value": 5,
  "algorithm": "secretsharing"
}
```

### 分片管理接口

#### GET /api/v1/shards
获取分片列表

#### POST /api/v1/shards/reconstruct
重构数据

**请求参数:**
```json
{
  "encrypted_order_id": 1,
  "shard_ids": ["shard1", "shard2", "shard3"]
}
```

#### GET /api/v1/storage-nodes
获取存储节点列表

### 日志管理接口

#### GET /api/v1/logs/operations
获取操作日志

**查询参数:**
- start_date: 开始时间
- end_date: 结束时间
- user_id: 用户ID
- operation_type: 操作类型

### 公开接口

#### POST /api/v1/public/encrypt
公开加密接口（无需登录）

**请求参数:**
```json
{
  "data": {
    "order_id": "ORD001",
    "name": "张三",
    "phone": "13800138000"
  },
  "k_value": 3,
  "n_value": 5
}
```

## Go 后端 API (Gin + Fabric) - Port 8080

### 加密日志接口

#### POST /api/v1/fabric/encryption/log
记录加密日志到区块链

**请求参数:**
```json
{
  "order_id": "ORD001",
  "user_id": "user123",
  "algorithm": "secretsharing",
  "k_value": 3,
  "n_value": 5,
  "data_hash": "hash123",
  "shard_hashes": ["hash1", "hash2", "hash3"],
  "operator_id": "admin",
  "operator_ip": "192.168.1.100"
}
```

#### GET /api/v1/fabric/encryption/logs
获取加密日志列表

**查询参数:**
- page: 页码
- size: 每页数量
- order_id: 订单ID
- start_date: 开始时间
- end_date: 结束时间

### 解密日志接口

#### POST /api/v1/fabric/decryption/log
记录解密日志到区块链

**请求参数:**
```json
{
  "order_id": "ORD001",
  "user_id": "user123",
  "requested_by": "user456",
  "shards_used": ["shard1", "shard2", "shard3"],
  "fields_accessed": ["name", "phone"],
  "access_reason": "业务查询",
  "operator_id": "admin",
  "operator_ip": "192.168.1.100"
}
```

#### GET /api/v1/fabric/decryption/logs
获取解密日志列表

### 查询日志接口

#### POST /api/v1/fabric/query/log
记录查询日志到区块链

**请求参数:**
```json
{
  "user_id": "user123",
  "query_type": "order_search",
  "query_params": "{\"name\": \"张三\"}",
  "result_count": 5,
  "fields_viewed": ["order_id", "name"],
  "operator_id": "admin",
  "operator_ip": "192.168.1.100"
}
```

#### GET /api/v1/fabric/query/logs
获取查询日志列表

### 审计统计接口

#### GET /api/v1/fabric/audit/stats
获取审计统计

**响应数据:**
```json
{
  "code": 200,
  "data": {
    "total_encryptions": 1000,
    "total_decryptions": 500,
    "total_queries": 2000,
    "today_operations": 50,
    "active_users": 20,
    "encryption_stats": {
      "today": 10,
      "this_week": 70,
      "this_month": 300
    }
  }
}
```

#### GET /api/v1/fabric/audit/timeline
获取操作时间线

**查询参数:**
- days: 天数范围
- operation_type: 操作类型

## 数据库表结构对应

### MySQL 主要表

#### users 表
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    role_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

#### roles 表
```sql
CREATE TABLE roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### order_fields 表
```sql
CREATE TABLE order_fields (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    field_name VARCHAR(50) UNIQUE NOT NULL,
    field_type VARCHAR(20) NOT NULL,
    sensitivity_level VARCHAR(20) NOT NULL,
    sensitivity_score DECIMAL(3,2) NOT NULL,
    category VARCHAR(20) NOT NULL,
    description TEXT,
    is_required BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### original_orders 表
```sql
CREATE TABLE original_orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50),
    name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    payment_info TEXT,
    item_list TEXT,
    total_amount DECIMAL(10,2),
    sensitivity_score DECIMAL(3,2),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### encrypted_orders 表
```sql
CREATE TABLE encrypted_orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    original_order_id BIGINT NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    encrypted_data LONGTEXT NOT NULL,
    encryption_algorithm VARCHAR(50) NOT NULL,
    k_value INT NOT NULL,
    n_value INT NOT NULL,
    data_hash VARCHAR(64) NOT NULL,
    status VARCHAR(20) DEFAULT 'encrypted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### shard_info 表
```sql
CREATE TABLE shard_info (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    encrypted_order_id BIGINT NOT NULL,
    shard_id VARCHAR(64) UNIQUE NOT NULL,
    shard_index INT NOT NULL,
    shard_data LONGTEXT NOT NULL,
    storage_node_id BIGINT,
    checksum VARCHAR(64) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### operation_logs 表
```sql
CREATE TABLE operation_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    operation_type VARCHAR(20) NOT NULL,
    resource_type VARCHAR(20) NOT NULL,
    resource_id VARCHAR(50),
    operation_detail TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 前端路由设计

### 前台路由
```javascript
const publicRoutes = [
  { path: '/', component: Home },
  { path: '/encrypt', component: Encrypt },
  { path: '/login', component: Login },
  { path: '/query', component: Query, meta: { requiresAuth: true } }
]
```

### 后台路由
```javascript
const adminRoutes = [
  { path: '/admin/dashboard', component: Dashboard },
  { path: '/admin/users', component: UserList },
  { path: '/admin/users/create', component: UserForm },
  { path: '/admin/users/:id/edit', component: UserForm },
  { path: '/admin/roles', component: RoleList },
  { path: '/admin/roles/create', component: RoleForm },
  { path: '/admin/roles/:id/permissions', component: RolePermission },
  { path: '/admin/fields', component: FieldList },
  { path: '/admin/fields/create', component: FieldForm },
  { path: '/admin/orders', component: OrderList },
  { path: '/admin/orders/upload', component: OrderUpload },
  { path: '/admin/shards', component: ShardList },
  { path: '/admin/nodes', component: NodeManagement },
  { path: '/admin/logs/operations', component: OperationLog },
  { path: '/admin/logs/encryption', component: EncryptionLog },
  { path: '/admin/logs/decryption', component: DecryptionLog },
  { path: '/admin/logs/query', component: QueryLog },
  { path: '/admin/audit', component: AuditReport }
]
```

## 权限控制设计

### 字段级权限控制
```javascript
// 前端根据用户角色过滤字段
const filterFieldsByPermission = (fields, userRole) => {
  return fields.filter(field => {
    const permission = userRole.permissions.find(p => p.field_id === field.id)
    return permission && permission.can_view
  })
}
```

### API 权限验证
```python
# Python 后端权限装饰器
@require_permission("view_orders")
async def get_orders(current_user: User):
    # 根据用户角色过滤字段
    allowed_fields = get_allowed_fields(current_user.role_id)
    return filter_order_fields(orders, allowed_fields)
```

这个 API 设计确保了：
1. 接口功能完整覆盖
2. 数据结构清晰定义
3. 权限控制精细化
4. 前后端职责分离
5. 区块链审计完整
