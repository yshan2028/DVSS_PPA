# DVSS-PPA Go Backend - 基于 Fabric Gateway 的现代实现

本项目已完成从传统的 `fabric-sdk-go` 到现代的 `fabric-gateway` 的重构，参考了 [fabric-realty](https://github.com/togettoyou/fabric-realty.git) 项目的最佳实践。

## 🚀 主要改进

### 1. 现代化的 Fabric 连接方式
- ✅ 使用 `fabric-gateway v1.7.0` 替代传统的 `fabric-sdk-go`
- ✅ 使用 `fabric-protos-go-apiv2 v0.3.4` 处理协议消息
- ✅ 支持多组织配置和证书管理
- ✅ 集成区块监听器和本地 BoltDB 存储

### 2. 重构的架构设计
```
backend-go/
├── api/                    # API 层 (Handler)
│   └── dvss_handler.go    # DVSS 相关接口处理
├── config/                # 配置管理
│   ├── config.go         # 配置结构和初始化
│   ├── config.yaml       # 生产环境配置
│   └── config-local.yaml # 本地开发配置
├── pkg/fabric/           # Fabric 连接层
│   ├── fabric.go         # 主要连接逻辑
│   └── block_listener.go # 区块监听和存储
├── service/              # 业务逻辑层
│   └── dvss_service.go   # DVSS 业务服务
├── utils/                # 工具包
│   └── response.go       # 统一响应格式
└── main.go              # 应用入口
```

### 3. 核心功能

#### Fabric 连接管理
- **InitFabric()**: 初始化多组织 Fabric 客户端
- **GetContract(orgName)**: 获取指定组织的合约客户端
- **ExtractErrorMessage()**: 提取 gRPC 错误详情

#### 区块监听与存储
- **initBlockListener()**: 初始化区块监听器
- **saveBlock()**: 保存区块到本地 BoltDB
- **GetBlocksByOrg()**: 分页查询组织区块列表

#### API 接口设计
```
/api/dvss
├── POST /secret-share/create    # 创建秘密分享
├── GET  /secret-share/:id       # 查询秘密分享
├── GET  /secret-share/list      # 分页查询分享列表
├── POST /secret/recover         # 恢复秘密
└── GET  /block/list            # 分页查询区块列表
```

## 📦 依赖管理

### 核心依赖
```go
require (
    github.com/gin-gonic/gin v1.10.0                    // Web 框架
    github.com/hyperledger/fabric-gateway v1.7.0       // Fabric Gateway
    github.com/hyperledger/fabric-protos-go-apiv2 v0.3.4 // Fabric 协议
    go.etcd.io/bbolt v1.3.10                           // 本地数据库
    go.uber.org/zap v1.26.0                            // 日志库
    gopkg.in/yaml.v3 v3.0.1                           // YAML 解析
)
```

## 🔧 配置管理

### 多组织配置示例
```yaml
server:
  port: 8001

fabric:
  channelName: "dvss-channel"
  chaincodeName: "dvss-ppa"
  organizations:
    org1:
      mspID: "Org1MSP"
      certPath: "./crypto-config/peerOrganizations/org1.dvss.com/users/Admin@org1.dvss.com/msp/signcerts"
      keyPath: "./crypto-config/peerOrganizations/org1.dvss.com/users/Admin@org1.dvss.com/msp/keystore"
      tlsCertPath: "./crypto-config/peerOrganizations/org1.dvss.com/peers/peer0.org1.dvss.com/tls/ca.crt"
      peerEndpoint: "localhost:7051"
      gatewayPeer: "peer0.org1.dvss.com"
```

## 🎯 使用方式

### 1. 编译项目
```bash
cd backend-go
go mod tidy
go build -o app .
```

### 2. 运行应用
```bash
# 使用默认配置
./app

# 服务将在 8001 端口启动
```

### 3. API 测试
```bash
# 创建秘密分享
curl -X POST http://localhost:8001/api/dvss/secret-share/create \
  -H "Content-Type: application/json" \
  -d '{"shareId":"test-001","data":"secret-data","threshold":"3"}'

# 查询秘密分享
curl http://localhost:8001/api/dvss/secret-share/test-001

# 查询区块列表
curl http://localhost:8001/api/dvss/block/list?pageSize=10&pageNum=1
```

## ✨ 与 fabric-realty 对比

| 功能特性 | fabric-realty | DVSS-PPA | 
|---------|---------------|----------|
| Fabric 连接 | ✅ fabric-gateway | ✅ fabric-gateway |
| 多组织支持 | ✅ 3个组织 | ✅ 3个组织 |
| 区块监听 | ✅ BoltDB存储 | ✅ BoltDB存储 |
| API 路由分组 | ✅ 按组织分组 | ✅ 按业务分组 |
| 配置管理 | ✅ YAML配置 | ✅ YAML配置 |
| 错误处理 | ✅ gRPC状态提取 | ✅ gRPC状态提取 |

## 🔮 下一步计划

1. **链码集成**: 部署 DVSS-PPA 链码到 Fabric 网络
2. **证书配置**: 配置生产环境的组织证书
3. **测试覆盖**: 添加单元测试和集成测试
4. **监控集成**: 集成 Prometheus 监控
5. **文档完善**: 添加 API 文档和部署指南

## 📝 参考项目

本项目重构参考了 [fabric-realty](https://github.com/togettoyou/fabric-realty.git) 的架构设计和最佳实践，采用了相同的：
- `fabric-gateway` 连接方式
- 多组织配置模式
- 区块监听机制
- API 路由设计
- 错误处理策略

---

**✅ 重构完成！** 现在 DVSS-PPA Go 后端已采用现代的 fabric-gateway 架构，完全对齐了 fabric-realty 的设计模式。
