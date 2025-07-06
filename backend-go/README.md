# DVSS Go Backend

基于 Gin 框架的 Go 后端服务，负责 Hyperledger Fabric 区块链操作和审计日志管理。

## 项目结构

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
│   │   ├── fabric.go          # 原有fabric实现
│   │   └── block_listener.go  # 事件监听
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

## 核心功能

### 1. 审计日志管理
- 记录系统操作审计日志到区块链
- 查询审计日志和统计信息
- 支持按用户、操作类型、时间范围查询

### 2. 加密操作日志
- 记录数据加密操作到区块链
- 支持秘密共享参数记录（K值、N值）
- 记录分片哈希值和数据哈希值

### 3. 解密操作日志
- 记录数据解密访问到区块链
- 记录访问的字段和使用的分片
- 记录访问原因和请求者信息

### 4. 查询操作日志
- 记录数据查询操作到区块链
- 记录查询类型和参数
- 记录查看的字段信息

## API 接口

### 审计日志 (/api/v1/fabric/audit)
- `POST /log` - 记录审计日志
- `GET /logs` - 查询审计日志列表
- `GET /logs/:id` - 获取审计日志详情
- `GET /stats` - 获取审计统计
- `GET /timeline` - 获取操作时间线
- `GET /export` - 导出审计报告

### 加密日志 (/api/v1/fabric/encryption)
- `POST /log` - 记录加密日志
- `GET /logs` - 查询加密日志列表
- `GET /logs/:id` - 获取加密日志详情
- `GET /logs/order/:order_id` - 按订单查询加密日志
- `GET /stats` - 获取加密统计

### 解密日志 (/api/v1/fabric/decryption)
- `POST /log` - 记录解密日志
- `GET /logs` - 查询解密日志列表
- `GET /logs/:id` - 获取解密日志详情
- `GET /logs/order/:order_id` - 按订单查询解密日志
- `GET /stats` - 获取解密统计

### 查询日志 (/api/v1/fabric/query)
- `POST /log` - 记录查询日志
- `GET /logs` - 查询日志列表
- `GET /logs/:id` - 获取查询日志详情
- `GET /logs/user/:user_id` - 按用户查询日志
- `GET /stats` - 获取查询统计

## 编译和运行

### 开发环境
```bash
# 安装依赖
go mod tidy

# 编译
go build -o dvss-go-backend .

# 运行
./dvss-go-backend
```

### Docker环境
```bash
# 构建镜像
docker build -t dvss-go-backend .

# 运行容器
docker run -p 8001:8001 dvss-go-backend
```

## 配置说明

配置文件位于 `config/config.yaml`，主要包含：
- 服务端口配置
- Fabric网络配置
- 数据库连接配置
- 日志级别配置

## 依赖项

主要依赖包：
- `github.com/gin-gonic/gin` - Web框架
- `github.com/hyperledger/fabric-gateway` - Fabric客户端SDK
- `google.golang.org/grpc` - gRPC通信

## 注意事项

1. 当前Fabric客户端为模拟实现，实际部署时需要配置真实的Fabric网络
2. 认证中间件目前为简单实现，生产环境需要集成JWT验证
3. 所有日志操作都会记录到区块链，确保审计的不可篡改性
