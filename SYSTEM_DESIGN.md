# DVSS-PPA 系统详细设计文档

## 1. 系统概述

### 1.1 系统架构
基于微服务架构的动态可验证秘密共享与隐私保护认证系统，包含以下核心组件：
- **Python 后端服务**：基于 FastAPI 的业务逻辑处理
- **Go 后端服务**：基于 Gin 的 Fabric 区块链操作
- **Vue 前端**：基于 Vue 3 的用户界面
- **Hyperledger Fabric**：区块链网络用于审计日志
- **MySQL**：关系型数据库存储
- **MongoDB**：分片数据存储
- **Redis**：缓存和动态阈值存储

### 1.2 技术栈
- **Python Backend**: FastAPI 3.12+ + SQLAlchemy + Pydantic
- **Go Backend**: Gin 1.24 + Hyperledger Fabric SDK
- **Frontend**: Vue 3 + Vite + Element Plus
- **Database**: MySQL 8.0 + MongoDB 6.0 + Redis 7.0
- **Blockchain**: Hyperledger Fabric 2.x
- **Deployment**: Docker + Docker Compose

## 2. Python 后端服务设计 (FastAPI)

### 2.1 目录结构（基于 Dash-FastAPI-Admin）
```
backend-python/
├── server.py                    # 主启动文件
├── requirements.txt             # 依赖包
├── Dockerfile                   # Docker 配置
├── config/                      # 配置模块
│   ├── __init__.py
│   ├── database.py             # 数据库配置
│   ├── env.py                  # 环境变量
│   ├── get_db.py               # 数据库连接
│   ├── get_redis.py            # redis连接
│   └── settings.py             # 应用设置
├── core/                        # 核心模块
│   ├── __init__.py
│   ├── security.py             # 安全工具
│   └── deps.py                 # 依赖注入
├── exceptions/                  # 异常处理
│   ├── __init__.py
│   ├── exception.py     # 自定义异常
│   └── handle.py               # 异常处理器
├── middlewares/                 # 中间件
│   ├── __init__.py
│   ├── cors_middleware.py      # CORS 中间件
│   ├── gzip_middleware.py      # GZIP 中间件
│   └── auth_middleware.py      # 认证中间件
├── module_dvss/                 # DVSS 业务模块
│   ├── __init__.py
│   ├── controller/             # 控制器层
│   │   ├── __init__.py
│   │   ├── auth_controller.py          # 认证控制器
│   │   ├── user_controller.py          # 用户管理
│   │   ├── role_controller.py          # 角色管理
│   │   ├── field_controller.py         # 字段管理
│   │   ├── order_controller.py         # 订单管理
│   │   ├── shard_controller.py         # 分片管理
│   │   ├── log_controller.py           # 日志管理
│   │   └── dvss_controller.py          # DVSS 核心
│   ├── entity/                 # 实体层（数据模型）
│   │   ├── __init__.py
│   │   ├── user.py                     # 用户实体
│   │   ├── role.py                     # 角色实体
│   │   ├── order_field.py              # 订单字段实体
│   │   ├── original_order.py           # 原始订单实体
│   │   ├── encrypted_order.py          # 加密订单实体
│   │   ├── shard_info.py               # 分片信息实体
│   │   ├── operation_log.py            # 操作日志实体
│   │   └── sensitivity_config.py       # 敏感度配置实体
│   ├── dao/                    # 数据访问层
│   │   ├── __init__.py
│   │   ├── user_dao.py                 # 用户数据访问
│   │   ├── role_dao.py                 # 角色数据访问
│   │   ├── field_dao.py                # 字段数据访问
│   │   ├── order_dao.py                # 订单数据访问
│   │   ├── shard_dao.py                # 分片数据访问
│   │   └── log_dao.py                  # 日志数据访问
│   ├── service/                # 服务层
│   │   ├── __init__.py
│   │   ├── auth_service.py             # 认证服务
│   │   ├── user_service.py             # 用户服务
│   │   ├── role_service.py             # 角色服务
│   │   ├── field_service.py            # 字段服务
│   │   ├── order_service.py            # 订单服务
│   │   ├── encryption_service.py       # 加密服务
│   │   ├── shard_service.py            # 分片服务
│   │   ├── sensitivity_service.py      # 敏感度分析服务
│   │   ├── monitoring_service.py       # 系统监控服务
│   │   └── audit_service.py            # 审计服务
│   └── schemas/                # Pydantic 模式
│       ├── __init__.py
│       ├── user_schema.py              # 用户模式
│       ├── role_schema.py              # 角色模式
│       ├── field_schema.py             # 字段模式
│       ├── order_schema.py             # 订单模式
│       ├── shard_schema.py             # 分片模式
│       ├── log_schema.py               # 日志模式
│       └── common_schema.py            # 通用模式
├── utils/                       # 工具类
│   ├── __init__.py
│   ├── log_util.py             # 日志工具
│   ├── response_util.py        # 响应工具
│   ├── pwd_util.py             # 密码工具
│   ├── page_util.py            # 分页工具
│   ├── crypto_util.py          # 加密工具
│   ├── file_util.py            # 文件处理工具
│   └── validation_util.py      # 验证工具
└── logs/                        # 日志文件
    └── dvss-python.log
```

### 2.2 核心功能模块

#### 2.2.1 用户管理模块
**实体字段 (User)**:
```python
class User(Base):
    id: int                    # 主键
    username: str              # 用户名
    email: str                 # 邮箱
    password_hash: str         # 密码哈希
    full_name: str             # 全名
    phone: str                 # 电话
    is_active: bool            # 是否激活
    is_superuser: bool         # 是否超级用户
    role_id: int               # 角色ID (外键)
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
    last_login: datetime       # 最后登录时间
```

**API 接口**:
- `POST /api/v1/users` - 创建用户
- `GET /api/v1/users` - 用户列表（分页）
- `GET /api/v1/users/{id}` - 获取用户详情
- `PUT /api/v1/users/{id}` - 更新用户
- `DELETE /api/v1/users/{id}` - 删除用户
- `POST /api/v1/users/{id}/reset-password` - 重置密码
- `PUT /api/v1/users/{id}/status` - 启用/禁用用户

#### 2.2.2 角色管理模块
**实体字段 (Role)**:
```python
class Role(Base):
    id: int                    # 主键
    name: str                  # 角色名称
    description: str           # 角色描述
    is_active: bool            # 是否激活
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间

class RoleFieldPermission(Base):
    id: int                    # 主键
    role_id: int               # 角色ID (外键)
    field_id: int              # 字段ID (外键)
    can_view: bool             # 可查看
    can_decrypt: bool          # 可解密
    created_at: datetime       # 创建时间
```

**API 接口**:
- `POST /api/v1/roles` - 创建角色
- `GET /api/v1/roles` - 角色列表
- `GET /api/v1/roles/{id}` - 获取角色详情
- `PUT /api/v1/roles/{id}` - 更新角色
- `DELETE /api/v1/roles/{id}` - 删除角色
- `POST /api/v1/roles/{id}/permissions` - 设置角色字段权限
- `GET /api/v1/roles/{id}/permissions` - 获取角色权限

#### 2.2.3 订单字段管理模块
**实体字段 (OrderField)**:
```python
class OrderField(Base):
    id: int                    # 主键
    field_name: str            # 字段名称
    field_type: str            # 字段类型 (string, number, date, etc.)
    sensitivity_level: str     # 敏感度等级 (low, medium, high, critical)
    sensitivity_score: float  # 敏感度分值 (0.0-1.0)
    category: str              # 字段分类 (pii, financial, location, business)
    description: str           # 字段描述
    is_required: bool          # 是否必填
    is_active: bool            # 是否激活
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

**API 接口**:
- `POST /api/v1/fields` - 创建字段
- `GET /api/v1/fields` - 字段列表
- `GET /api/v1/fields/{id}` - 获取字段详情
- `PUT /api/v1/fields/{id}` - 更新字段
- `DELETE /api/v1/fields/{id}` - 删除字段
- `POST /api/v1/fields/batch-update` - 批量更新字段敏感度

#### 2.2.4 原始订单管理模块
**实体字段 (OriginalOrder)**:
```python
class OriginalOrder(Base):
    id: int                    # 主键
    order_id: str              # 订单编号
    user_id: str               # 用户ID
    name: str                  # 姓名
    phone: str                 # 电话
    email: str                 # 邮箱
    address: str               # 地址
    shipping_address: str      # 配送地址
    billing_address: str       # 账单地址
    zip_code: str              # 邮编
    city: str                  # 城市
    state: str                 # 州/省
    country: str               # 国家
    payment_info: str          # 支付信息
    credit_card: str           # 信用卡号
    bank_account: str          # 银行账户
    payment_method: str        # 支付方式
    item_list: str             # 商品列表 (JSON)
    item_name: str             # 商品名称
    item_price: decimal        # 商品价格
    quantity: int              # 数量
    total_amount: decimal      # 总金额
    tax_amount: decimal        # 税额
    shipping_cost: decimal     # 运费
    discount: decimal          # 折扣
    sensitivity_score: float   # 整体敏感度分值
    status: str                # 状态 (active, deleted)
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

**API 接口**:
- `POST /api/v1/orders` - 创建订单
- `POST /api/v1/orders/upload` - 上传订单文件 (CSV/JSON)
- `GET /api/v1/orders` - 订单列表（带权限过滤）
- `GET /api/v1/orders/{id}` - 获取订单详情
- `PUT /api/v1/orders/{id}` - 更新订单
- `DELETE /api/v1/orders/{id}` - 软删除订单
- `POST /api/v1/orders/{id}/encrypt` - 加密订单
- `POST /api/v1/orders/batch-encrypt` - 批量加密
- `GET /api/v1/orders/{id}/sensitivity` - 获取敏感度分析

#### 2.2.5 加密订单管理模块
**实体字段 (EncryptedOrder)**:
```python
class EncryptedOrder(Base):
    id: int                    # 主键
    original_order_id: int     # 原始订单ID (外键)
    order_id: str              # 订单编号
    encrypted_data: str        # 加密后的数据 (JSON)
    encryption_algorithm: str  # 加密算法
    k_value: int               # 分片阈值
    n_value: int               # 分片总数
    data_hash: str             # 数据哈希值
    status: str                # 状态 (encrypted, sharded, deleted)
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

**API 接口**:
- `GET /api/v1/encrypted-orders` - 加密订单列表
- `GET /api/v1/encrypted-orders/{id}` - 获取加密订单详情
- `POST /api/v1/encrypted-orders/{id}/decrypt` - 解密订单
- `DELETE /api/v1/encrypted-orders/{id}` - 删除加密订单

#### 2.2.6 分片管理模块
**实体字段 (ShardInfo)**:
```python
class ShardInfo(Base):
    id: int                    # 主键
    encrypted_order_id: int    # 加密订单ID (外键)
    shard_id: str              # 分片ID
    shard_index: int           # 分片索引
    shard_data: str            # 分片数据
    storage_node: str          # 存储节点
    checksum: str              # 校验和
    status: str                # 状态 (active, corrupted, deleted)
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间

class StorageNode(Base):
    id: int                    # 主键
    node_name: str             # 节点名称
    node_address: str          # 节点地址
    node_type: str             # 节点类型 (mongodb, backup)
    is_active: bool            # 是否激活
    capacity_used: int         # 已用容量
    capacity_total: int        # 总容量
    last_health_check: datetime # 最后健康检查时间
    created_at: datetime       # 创建时间
```

**API 接口**:
- `GET /api/v1/shards` - 分片列表
- `GET /api/v1/shards/{id}` - 获取分片详情
- `POST /api/v1/shards/{id}/verify` - 验证分片完整性
- `POST /api/v1/shards/reconstruct` - 重构数据
- `GET /api/v1/storage-nodes` - 存储节点列表
- `POST /api/v1/storage-nodes` - 添加存储节点
- `PUT /api/v1/storage-nodes/{id}` - 更新节点信息
- `DELETE /api/v1/storage-nodes/{id}` - 删除节点

#### 2.2.7 操作日志模块
**实体字段 (OperationLog)**:
```python
class OperationLog(Base):
    id: int                    # 主键
    user_id: int               # 操作用户ID (外键)
    operation_type: str        # 操作类型 (create, read, update, delete, encrypt, decrypt)
    resource_type: str         # 资源类型 (user, role, order, shard)
    resource_id: str           # 资源ID
    operation_detail: str      # 操作详情 (JSON)
    ip_address: str            # IP地址
    user_agent: str            # 用户代理
    status: str                # 状态 (success, failure)
    error_message: str         # 错误信息
    created_at: datetime       # 创建时间
```

**API 接口**:
- `GET /api/v1/logs/operations` - 操作日志列表
- `GET /api/v1/logs/operations/{id}` - 获取日志详情
- `GET /api/v1/logs/operations/export` - 导出日志
- `GET /api/v1/logs/operations/stats` - 操作统计

### 2.3 公共 API

#### 2.3.1 认证 API
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新 Token
- `GET /api/v1/auth/profile` - 获取用户信息
- `PUT /api/v1/auth/profile` - 更新用户信息
- `POST /api/v1/auth/change-password` - 修改密码

#### 2.3.2 前台公开 API
- `POST /api/v1/public/encrypt` - 公开加密接口
- `POST /api/v1/public/upload` - 公开上传接口
- `GET /api/v1/public/fields` - 获取可用字段

## 3. Go 后端服务设计 (Gin + Fabric)

### 3.1 目录结构（基于 fabric-realty）
```
backend-go/
├── main.go                     # 主启动文件
├── go.mod                      # Go 模块文件
├── go.sum                      # 依赖校验文件
├── Dockerfile                  # Docker 配置
├── config/                     # 配置模块
│   ├── config.go              # 配置结构
│   ├── config.yaml            # 配置文件
│   └── config-local.yaml      # 本地配置
├── api/                        # API 层
│   ├── handler.go             # 通用处理器
│   ├── audit_handler.go       # 审计日志处理器
│   ├── encryption_handler.go  # 加密日志处理器
│   ├── decryption_handler.go  # 解密日志处理器
│   └── query_handler.go       # 查询日志处理器
├── service/                    # 服务层
│   ├── audit_service.go       # 审计服务
│   ├── encryption_service.go  # 加密服务
│   ├── decryption_service.go  # 解密服务
│   └── query_service.go       # 查询服务
├── model/                      # 数据模型
│   ├── audit_log.go           # 审计日志模型
│   ├── encryption_log.go      # 加密日志模型
│   ├── decryption_log.go      # 解密日志模型
│   └── query_log.go           # 查询日志模型
├── pkg/                        # 包模块
│   ├── fabric/                # Fabric 客户端
│   │   ├── client.go          # Fabric 客户端
│   │   ├── chaincode.go       # 链码操作
│   │   └── event.go           # 事件监听
│   ├── utils/                 # 工具包
│   │   ├── response.go        # 响应工具
│   │   ├── crypto.go          # 加密工具
│   │   └── logger.go          # 日志工具
│   └── middleware/            # 中间件
│       ├── cors.go            # CORS 中间件
│       ├── auth.go            # 认证中间件
│       └── logger.go          # 日志中间件
└── logs/                       # 日志文件
```

### 3.2 核心功能模块

#### 3.2.1 加密日志模块
**结构体定义**:
```go
type EncryptionLog struct {
    ID            string    `json:"id"`
    OrderID       string    `json:"order_id"`
    UserID        string    `json:"user_id"`
    Algorithm     string    `json:"algorithm"`
    KValue        int       `json:"k_value"`
    NValue        int       `json:"n_value"`
    DataHash      string    `json:"data_hash"`
    ShardHashes   []string  `json:"shard_hashes"`
    OperatorID    string    `json:"operator_id"`
    OperatorIP    string    `json:"operator_ip"`
    Status        string    `json:"status"`
    ErrorMessage  string    `json:"error_message,omitempty"`
    Timestamp     time.Time `json:"timestamp"`
    TxID          string    `json:"tx_id"`
}
```

**API 接口**:
- `POST /api/v1/fabric/encryption/log` - 记录加密日志
- `GET /api/v1/fabric/encryption/logs` - 获取加密日志列表
- `GET /api/v1/fabric/encryption/logs/{id}` - 获取加密日志详情
- `GET /api/v1/fabric/encryption/logs/order/{order_id}` - 按订单查询加密日志

#### 3.2.2 解密日志模块
**结构体定义**:
```go
type DecryptionLog struct {
    ID            string    `json:"id"`
    OrderID       string    `json:"order_id"`
    UserID        string    `json:"user_id"`
    RequestedBy   string    `json:"requested_by"`
    ShardsUsed    []string  `json:"shards_used"`
    FieldsAccessed []string `json:"fields_accessed"`
    AccessReason  string    `json:"access_reason"`
    OperatorID    string    `json:"operator_id"`
    OperatorIP    string    `json:"operator_ip"`
    Status        string    `json:"status"`
    ErrorMessage  string    `json:"error_message,omitempty"`
    Timestamp     time.Time `json:"timestamp"`
    TxID          string    `json:"tx_id"`
}
```

**API 接口**:
- `POST /api/v1/fabric/decryption/log` - 记录解密日志
- `GET /api/v1/fabric/decryption/logs` - 获取解密日志列表
- `GET /api/v1/fabric/decryption/logs/{id}` - 获取解密日志详情
- `GET /api/v1/fabric/decryption/logs/order/{order_id}` - 按订单查询解密日志

#### 3.2.3 查询日志模块
**结构体定义**:
```go
type QueryLog struct {
    ID            string    `json:"id"`
    UserID        string    `json:"user_id"`
    QueryType     string    `json:"query_type"`
    QueryParams   string    `json:"query_params"`
    ResultCount   int       `json:"result_count"`
    FieldsViewed  []string  `json:"fields_viewed"`
    OperatorID    string    `json:"operator_id"`
    OperatorIP    string    `json:"operator_ip"`
    Status        string    `json:"status"`
    ErrorMessage  string    `json:"error_message,omitempty"`
    Timestamp     time.Time `json:"timestamp"`
    TxID          string    `json:"tx_id"`
}
```

**API 接口**:
- `POST /api/v1/fabric/query/log` - 记录查询日志
- `GET /api/v1/fabric/query/logs` - 获取查询日志列表
- `GET /api/v1/fabric/query/logs/{id}` - 获取查询日志详情
- `GET /api/v1/fabric/query/logs/user/{user_id}` - 按用户查询日志

#### 3.2.4 审计统计模块
**API 接口**:
- `GET /api/v1/fabric/audit/stats` - 获取审计统计
- `GET /api/v1/fabric/audit/stats/encryption` - 加密操作统计
- `GET /api/v1/fabric/audit/stats/decryption` - 解密操作统计
- `GET /api/v1/fabric/audit/stats/query` - 查询操作统计
- `GET /api/v1/fabric/audit/timeline` - 操作时间线
- `GET /api/v1/fabric/audit/export` - 导出审计报告

### 3.3 区块链操作

#### 3.3.1 智能合约功能
```go
// 链码函数列表
const (
    // 加密相关
    RecordEncryption = "RecordEncryption"
    QueryEncryption  = "QueryEncryption"
    
    // 解密相关
    RecordDecryption = "RecordDecryption"
    QueryDecryption  = "QueryDecryption"
    
    // 查询相关
    RecordQuery = "RecordQuery"
    QueryLogs   = "QueryLogs"
    
    // 审计相关
    GetAuditTrail = "GetAuditTrail"
    GetStatistics = "GetStatistics"
)
```

## 4. Vue 前端设计

### 4.1 目录结构
```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── Dockerfile
├── nginx.conf
├── public/
│   └── vite.svg
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── api/                    # API 调用
│   │   ├── index.js
│   │   ├── auth.js
│   │   ├── user.js
│   │   ├── role.js
│   │   ├── field.js
│   │   ├── order.js
│   │   ├── shard.js
│   │   ├── log.js
│   │   └── fabric.js
│   ├── components/             # 公共组件
│   │   ├── Layout/
│   │   ├── Table/
│   │   ├── Form/
│   │   ├── Upload/
│   │   └── Chart/
│   ├── router/                 # 路由配置
│   │   └── index.js
│   ├── stores/                 # 状态管理
│   │   ├── index.js
│   │   ├── auth.js
│   │   ├── user.js
│   │   └── app.js
│   ├── utils/                  # 工具函数
│   │   ├── request.js
│   │   ├── auth.js
│   │   ├── format.js
│   │   └── validation.js
│   └── views/                  # 页面组件
│       ├── public/            # 前台页面
│       │   ├── Home.vue
│       │   ├── Encrypt.vue
│       │   ├── Login.vue
│       │   └── Query.vue
│       └── admin/             # 后台页面
│           ├── Dashboard.vue
│           ├── User/
│           ├── Role/
│           ├── Field/
│           ├── Order/
│           ├── Shard/
│           └── Log/
```

### 4.2 前台页面功能

#### 4.2.1 首页 (Home.vue)
- 系统介绍
- 功能说明
- 加密流程展示

#### 4.2.2 数据加密页面 (Encrypt.vue)
**功能**:
- 手动输入订单数据加密
- CSV/JSON 文件上传加密
- 批量数据处理
- 加密进度显示
- 加密结果下载

**组件结构**:
- 数据输入区域
- 文件上传区域  
- 敏感度预览
- 加密配置选项
- 结果展示区域

#### 4.2.3 用户登录页面 (Login.vue)
**功能**:
- 用户名/邮箱登录
- 密码登录
- 记住登录状态
- 忘记密码链接

#### 4.2.4 数据查询页面 (Query.vue)
**功能（需登录）**:
- 按角色权限显示字段
- 高级搜索功能
- 解密数据查看
- 敏感字段遮罩提示
- 操作日志记录

### 4.3 后台管理功能

#### 4.3.1 仪表盘 (Dashboard.vue)
**功能**:
- 系统概览统计
- 最近操作日志
- 系统监控图表
- 快捷操作入口

**统计指标**:
- 用户总数
- 订单总数
- 加密订单数
- 分片总数
- 今日操作次数
- 系统负载状态

#### 4.3.2 用户管理 (User/)
**页面列表**:
- `UserList.vue` - 用户列表
- `UserForm.vue` - 用户表单
- `UserDetail.vue` - 用户详情

**功能**:
- 用户CRUD操作
- 角色分配
- 状态管理
- 密码重置
- 批量操作

#### 4.3.3 角色管理 (Role/)
**页面列表**:
- `RoleList.vue` - 角色列表
- `RoleForm.vue` - 角色表单
- `RolePermission.vue` - 权限配置

**功能**:
- 角色CRUD操作
- 字段权限配置
- 权限矩阵视图
- 批量权限设置

#### 4.3.4 字段管理 (Field/)
**页面列表**:
- `FieldList.vue` - 字段列表
- `FieldForm.vue` - 字段表单
- `SensitivityConfig.vue` - 敏感度配置

**功能**:
- 字段CRUD操作
- 敏感度等级设置
- 分值配置
- 批量更新
- 配置导入/导出

#### 4.3.5 订单管理 (Order/)
**页面列表**:
- `OrderList.vue` - 订单列表
- `OrderDetail.vue` - 订单详情
- `OrderUpload.vue` - 批量上传
- `OrderEncryption.vue` - 加密管理

**功能**:
- 订单查看（按权限）
- 批量导入
- 加密操作
- 敏感度分析
- 数据导出

#### 4.3.6 分片管理 (Shard/)
**页面列表**:
- `ShardList.vue` - 分片列表
- `ShardDetail.vue` - 分片详情
- `NodeManagement.vue` - 节点管理
- `ShardReconstruction.vue` - 数据重构

**功能**:
- 分片信息查看
- 存储节点管理
- 完整性验证
- 数据重构
- 节点健康检查

#### 4.3.7 日志管理 (Log/)
**页面列表**:
- `OperationLog.vue` - 操作日志
- `EncryptionLog.vue` - 加密日志
- `DecryptionLog.vue` - 解密日志
- `QueryLog.vue` - 查询日志
- `AuditReport.vue` - 审计报告

**功能**:
- 日志查询和过滤
- 时间范围搜索
- 用户操作追踪
- 日志导出
- 统计图表展示
- 区块链日志同步

## 5. 数据库设计

### 5.1 MySQL 表结构

#### 5.1.1 用户相关表
```sql
-- 用户表
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
    last_login TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role_id (role_id)
);

-- 角色表
CREATE TABLE roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 角色字段权限表
CREATE TABLE role_field_permissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_id BIGINT NOT NULL,
    field_id BIGINT NOT NULL,
    can_view BOOLEAN DEFAULT FALSE,
    can_decrypt BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_role_field (role_id, field_id),
    INDEX idx_role_id (role_id),
    INDEX idx_field_id (field_id)
);
```

#### 5.1.2 订单相关表
```sql
-- 订单字段表
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

-- 原始订单表
CREATE TABLE original_orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(50),
    name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    shipping_address TEXT,
    billing_address TEXT,
    zip_code VARCHAR(20),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    payment_info TEXT,
    credit_card VARCHAR(20),
    bank_account VARCHAR(50),
    payment_method VARCHAR(20),
    item_list TEXT,
    item_name VARCHAR(200),
    item_price DECIMAL(10,2),
    quantity INT,
    total_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    discount DECIMAL(10,2),
    sensitivity_score DECIMAL(3,2),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- 加密订单表
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_original_order_id (original_order_id),
    INDEX idx_order_id (order_id),
    INDEX idx_status (status)
);
```

#### 5.1.3 分片相关表
```sql
-- 存储节点表
CREATE TABLE storage_nodes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    node_name VARCHAR(50) UNIQUE NOT NULL,
    node_address VARCHAR(100) NOT NULL,
    node_type VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    capacity_used BIGINT DEFAULT 0,
    capacity_total BIGINT DEFAULT 0,
    last_health_check TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 分片信息表
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_encrypted_order_id (encrypted_order_id),
    INDEX idx_shard_id (shard_id),
    INDEX idx_storage_node_id (storage_node_id)
);
```

#### 5.1.4 日志相关表
```sql
-- 操作日志表
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_resource_type (resource_type),
    INDEX idx_created_at (created_at)
);
```

### 5.2 MongoDB 集合设计

#### 5.2.1 分片数据集合
```javascript
// shards 集合
{
  _id: ObjectId,
  shard_id: String,           // 分片ID
  encrypted_order_id: Number, // 加密订单ID
  shard_index: Number,        // 分片索引
  shard_data: String,         // 分片数据
  checksum: String,           // 校验和
  metadata: {
    algorithm: String,        // 加密算法
    k_value: Number,          // 阈值
    n_value: Number,          // 总数
    created_by: String,       // 创建者
    created_at: Date          // 创建时间
  },
  status: String,             // 状态
  created_at: Date,
  updated_at: Date
}
```

## 6. API 接口规范

### 6.1 响应格式标准
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2025-07-06T10:00:00Z"
}
```

### 6.2 错误码定义
```json
{
  "200": "成功",
  "400": "请求参数错误",
  "401": "未授权",
  "403": "权限不足",
  "404": "资源不存在",
  "500": "服务器内部错误",
  "1001": "用户名或密码错误",
  "1002": "用户已被禁用",
  "1003": "Token已过期",
  "2001": "订单不存在",
  "2002": "订单已加密",
  "3001": "分片数据损坏",
  "3002": "存储节点不可用"
}
```

## 7. 部署架构

### 7.1 Docker Compose 配置
```yaml
version: '3.8'
services:
  # Python 后端
  python-backend:
    build: ./backend-python
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis
      - mongodb
    
  # Go 后端  
  go-backend:
    build: ./backend-go
    ports:
      - "8080:8080"
    depends_on:
      - fabric-peer
    
  # Vue 前端
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - python-backend
      - go-backend
    
  # 数据库服务
  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    
  redis:
    image: redis:7.0
    ports:
      - "6379:6379"
```

## 8. 开发计划

### 8.1 开发阶段划分
1. **阶段一**：基础框架搭建
   - Python 后端基础架构
   - Go 后端基础架构  
   - Vue 前端基础架构
   - 数据库表结构设计

2. **阶段二**：核心功能开发
   - 用户管理模块
   - 角色权限模块
   - 订单字段管理
   - 基础认证功能

3. **阶段三**：加密分片功能
   - 数据加密服务
   - 分片管理功能
   - 存储节点管理
   - 完整性验证

4. **阶段四**：区块链集成
   - Fabric 网络搭建
   - 智能合约开发
   - 审计日志上链
   - Go 后端集成

5. **阶段五**：前端界面开发
   - 前台加密页面
   - 后台管理界面
   - 权限控制实现
   - 数据可视化

6. **阶段六**：系统集成测试
   - 功能测试
   - 性能测试
   - 安全测试
   - 部署测试

### 8.2 技术难点
1. **动态阈值计算**：系统负载监控与 k 值动态调整
2. **权限细粒度控制**：字段级权限与角色绑定
3. **分片完整性验证**：多节点数据一致性保证
4. **区块链性能优化**：大量日志上链的性能考虑
5. **前端权限渲染**：基于角色的动态字段显示

## 9. 安全考虑

### 9.1 数据安全
- 敏感数据加密存储
- 传输过程 HTTPS 加密
- 数据库访问权限控制
- 定期安全审计

### 9.2 访问安全
- JWT Token 认证
- 角色权限控制
- IP 白名单限制
- 操作日志记录

### 9.3 系统安全
- 输入参数验证
- SQL 注入防护
- XSS 攻击防护
- CSRF 攻击防护

本设计文档涵盖了 DVSS-PPA 系统的完整架构设计，包括后端服务、前端界面、数据库设计和部署方案。所有功能模块都有明确的职责划分，API 接口设计完整，数据库表结构合理，可以作为系统开发的详细指导文档。
