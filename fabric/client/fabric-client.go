package main

import (
	"context"
	"crypto/x509"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/hyperledger/fabric-gateway/pkg/client"
	"github.com/hyperledger/fabric-gateway/pkg/hash"
	"github.com/hyperledger/fabric-gateway/pkg/identity"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/status"
	"gopkg.in/yaml.v3"
)

// Config 配置结构
type Config struct {
	Server   ServerConfig         `yaml:"server"`
	Fabric   FabricConfig         `yaml:"fabric"`
	Security SecurityConfig       `yaml:"security"`
	Pool     ConnectionPoolConfig `yaml:"pool"`
}

// ServerConfig 服务器配置
type ServerConfig struct {
	Port         int `yaml:"port"`
	ReadTimeout  int `yaml:"readTimeout"`
	WriteTimeout int `yaml:"writeTimeout"`
	IdleTimeout  int `yaml:"idleTimeout"`
}

// SecurityConfig 安全配置
type SecurityConfig struct {
	TLSEnabled     bool     `yaml:"tlsEnabled"`
	AllowedOrigins []string `yaml:"allowedOrigins"`
	RateLimit      int      `yaml:"rateLimit"`
	APIKeyRequired bool     `yaml:"apiKeyRequired"`
}

// ConnectionPoolConfig 连接池配置
type ConnectionPoolConfig struct {
	MaxConnections    int `yaml:"maxConnections"`
	IdleTimeout       int `yaml:"idleTimeout"`
	MaxRetries        int `yaml:"maxRetries"`
	HealthCheckPeriod int `yaml:"healthCheckPeriod"`
}

// FabricConfig Fabric配置
type FabricConfig struct {
	ChannelName   string                        `yaml:"channelName"`
	ChaincodeName string                        `yaml:"chaincodeName"`
	Organizations map[string]OrganizationConfig `yaml:"organizations"`
}

// OrganizationConfig 组织配置
type OrganizationConfig struct {
	MSPID        string `yaml:"mspID"`
	CertPath     string `yaml:"certPath"`
	KeyPath      string `yaml:"keyPath"`
	TLSCertPath  string `yaml:"tlsCertPath"`
	PeerEndpoint string `yaml:"peerEndpoint"`
	GatewayPeer  string `yaml:"gatewayPeer"`
}

// PerformanceMetrics 性能指标
type PerformanceMetrics struct {
	TotalRequests     int64     `json:"total_requests"`
	SuccessRequests   int64     `json:"success_requests"`
	FailedRequests    int64     `json:"failed_requests"`
	AverageLatency    int64     `json:"average_latency_ms"`
	ActiveConnections int32     `json:"active_connections"`
	LastResetTime     time.Time `json:"last_reset_time"`
}

// ConnectionInfo 连接信息
type ConnectionInfo struct {
	OrgName      string        `json:"org_name"`
	Status       string        `json:"status"`
	LastUsed     time.Time     `json:"last_used"`
	RequestCount int64         `json:"request_count"`
	ErrorCount   int64         `json:"error_count"`
	Latency      time.Duration `json:"latency"`
}

var globalConfig Config
var performanceMetrics PerformanceMetrics

// DVSSFabricClient 提供与Hyperledger Fabric交互的客户端
type DVSSFabricClient struct {
	contracts      map[string]*client.Contract
	gateways       map[string]*client.Gateway
	connections    map[string]*ConnectionInfo
	mu             sync.RWMutex
	ctx            context.Context
	cancel         context.CancelFunc
	healthTicker   *time.Ticker
	metricsEnabled bool
	retryCount     int
}

// ConnectionPool 连接池管理 (为未来扩展保留)
// type ConnectionPool struct {
//	clients        map[string]*DVSSFabricClient
//	mu             sync.RWMutex
//	maxConnections int
//	activeCount    int32
// }

// var globalConnectionPool *ConnectionPool

// Transaction 交易结构
type Transaction struct {
	TxID      string                 `json:"tx_id"`
	DataID    string                 `json:"data_id"`
	Operation string                 `json:"operation"`
	UserID    string                 `json:"user_id"`
	Timestamp string                 `json:"timestamp"`
	ShareInfo ShareInfo              `json:"share_info,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
	Signature string                 `json:"signature"`
}

// ShareInfo 分片信息
type ShareInfo struct {
	ShareIndices []int `json:"share_indices"`
	Threshold    int   `json:"threshold"`
	TotalShares  int   `json:"total_shares"`
}

// AccessLog 访问日志
type AccessLog struct {
	LogID      string                 `json:"log_id"`
	DataID     string                 `json:"data_id"`
	UserID     string                 `json:"user_id"`
	Action     string                 `json:"action"`
	Permission string                 `json:"permission"`
	Result     string                 `json:"result"`
	Timestamp  string                 `json:"timestamp"`
	IPAddress  string                 `json:"ip_address,omitempty"`
	Metadata   map[string]interface{} `json:"metadata,omitempty"`
}

// BlockInfo 区块信息结构
type BlockInfo struct {
	BlockNumber      uint64                 `json:"block_number"`
	PreviousHash     string                 `json:"previous_hash"`
	DataHash         string                 `json:"data_hash"`
	TransactionCount int                    `json:"transaction_count"`
	Timestamp        string                 `json:"timestamp"`
	Transactions     []TransactionInfo      `json:"transactions"`
	Metadata         map[string]interface{} `json:"metadata,omitempty"`
}

// TransactionInfo 交易信息结构
type TransactionInfo struct {
	TxID          string                 `json:"tx_id"`
	ChaincodeName string                 `json:"chaincode_name"`
	FunctionName  string                 `json:"function_name"`
	Args          []string               `json:"args"`
	Creator       string                 `json:"creator"`
	Timestamp     string                 `json:"timestamp"`
	Status        string                 `json:"status"`
	Endorsements  []EndorsementInfo      `json:"endorsements"`
	Metadata      map[string]interface{} `json:"metadata,omitempty"`
}

// EndorsementInfo 背书信息结构
type EndorsementInfo struct {
	Endorser  string `json:"endorser"`
	Signature string `json:"signature"`
	Timestamp string `json:"timestamp"`
}

// ChainInfo 链信息结构
type ChainInfo struct {
	Height       uint64 `json:"height"`
	CurrentHash  string `json:"current_hash"`
	PreviousHash string `json:"previous_hash"`
	ChannelName  string `json:"channel_name"`
}

// BlockchainExplorer 区块链浏览器接口
type BlockchainExplorer interface {
	GetChainInfo(orgName string) (*ChainInfo, error)
	GetBlockByNumber(orgName string, blockNumber uint64) (*BlockInfo, error)
	GetBlockByHash(orgName string, blockHash string) (*BlockInfo, error)
	GetTransactionByID(orgName string, txID string) (*TransactionInfo, error)
	GetRecentBlocks(orgName string, count int) ([]*BlockInfo, error)
	GetRecentTransactions(orgName string, count int) ([]*TransactionInfo, error)
	SearchTransactions(orgName, query string, limit int) ([]*TransactionInfo, error)
}

var fabricClient *DVSSFabricClient

// initConfig 初始化配置
func initConfig() error {
	configPath := os.Getenv("CONFIG_PATH")
	if configPath == "" {
		configPath = "config/config.yaml"
	}

	data, err := os.ReadFile(configPath)
	if err != nil {
		return fmt.Errorf("读取配置文件失败：%v", err)
	}

	err = yaml.Unmarshal(data, &globalConfig)
	if err != nil {
		return fmt.Errorf("解析配置文件失败：%v", err)
	}

	return nil
}

// NewDVSSFabricClient 创建新的Fabric客户端
func NewDVSSFabricClient() (*DVSSFabricClient, error) {
	ctx, cancel := context.WithCancel(context.Background())

	fabricClient := &DVSSFabricClient{
		contracts:      make(map[string]*client.Contract),
		gateways:       make(map[string]*client.Gateway),
		connections:    make(map[string]*ConnectionInfo),
		ctx:            ctx,
		cancel:         cancel,
		metricsEnabled: true,
		retryCount:     globalConfig.Pool.MaxRetries,
	}

	// 为每个组织创建连接
	for orgName, orgConfig := range globalConfig.Fabric.Organizations {
		// 记录连接信息
		fabricClient.connections[orgName] = &ConnectionInfo{
			OrgName:  orgName,
			Status:   "connecting",
			LastUsed: time.Now(),
		}

		// 创建gRPC连接（带重试）
		var clientConnection *grpc.ClientConn
		var err error

		for i := 0; i < fabricClient.retryCount; i++ {
			clientConnection, err = newGrpcConnection(orgConfig)
			if err == nil {
				break
			}
			log.Printf("⚠️  连接组织[%s]失败，重试 %d/%d: %v", orgName, i+1, fabricClient.retryCount, err)
			time.Sleep(time.Duration(i+1) * time.Second)
		}

		if err != nil {
			fabricClient.connections[orgName].Status = "failed"
			return nil, fmt.Errorf("创建组织[%s]的gRPC连接失败：%v", orgName, err)
		}

		// 创建身份
		id, err := newIdentity(orgConfig)
		if err != nil {
			clientConnection.Close()
			fabricClient.connections[orgName].Status = "failed"
			return nil, fmt.Errorf("创建组织[%s]身份失败：%v", orgName, err)
		}

		// 创建签名函数
		sign, err := newSign(orgConfig)
		if err != nil {
			clientConnection.Close()
			fabricClient.connections[orgName].Status = "failed"
			return nil, fmt.Errorf("创建组织[%s]签名函数失败：%v", orgName, err)
		}

		// 创建Gateway连接
		gw, err := client.Connect(
			id,
			client.WithSign(sign),
			client.WithHash(hash.SHA256),
			client.WithClientConnection(clientConnection),
			client.WithEvaluateTimeout(5*time.Second),
			client.WithEndorseTimeout(15*time.Second),
			client.WithSubmitTimeout(5*time.Second),
			client.WithCommitStatusTimeout(1*time.Minute),
		)
		if err != nil {
			clientConnection.Close()
			fabricClient.connections[orgName].Status = "failed"
			return nil, fmt.Errorf("连接组织[%s]的Fabric网关失败：%v", orgName, err)
		}

		network := gw.GetNetwork(globalConfig.Fabric.ChannelName)
		contract := network.GetContract(globalConfig.Fabric.ChaincodeName)

		fabricClient.gateways[orgName] = gw
		fabricClient.contracts[orgName] = contract
		fabricClient.connections[orgName].Status = "connected"

		atomic.AddInt32(&performanceMetrics.ActiveConnections, 1)
		log.Printf("✅ 组织[%s]连接成功", orgName)
	}

	// 启动健康检查
	fabricClient.startHealthCheck()

	// 初始化性能指标
	performanceMetrics.LastResetTime = time.Now()

	return fabricClient, nil
}

// startHealthCheck 启动健康检查
func (c *DVSSFabricClient) startHealthCheck() {
	if globalConfig.Pool.HealthCheckPeriod > 0 {
		c.healthTicker = time.NewTicker(time.Duration(globalConfig.Pool.HealthCheckPeriod) * time.Second)
		go func() {
			for {
				select {
				case <-c.ctx.Done():
					return
				case <-c.healthTicker.C:
					c.performHealthCheck()
				}
			}
		}()
	}
}

// performHealthCheck 执行健康检查
func (c *DVSSFabricClient) performHealthCheck() {
	c.mu.Lock()
	defer c.mu.Unlock()

	for orgName, connInfo := range c.connections {
		if time.Since(connInfo.LastUsed) > time.Duration(globalConfig.Pool.IdleTimeout)*time.Second {
			// 连接空闲超时，可能需要重连
			log.Printf("🔄 组织[%s]连接空闲超时，检查状态", orgName)

			// 尝试ping操作来验证连接
			if contract := c.contracts[orgName]; contract != nil {
				start := time.Now()
				_, err := contract.EvaluateTransaction("HealthCheck")
				latency := time.Since(start)

				if err != nil {
					connInfo.Status = "unhealthy"
					connInfo.ErrorCount++
					log.Printf("⚠️  组织[%s]健康检查失败: %v", orgName, err)
				} else {
					connInfo.Status = "healthy"
					connInfo.Latency = latency
					connInfo.LastUsed = time.Now()
				}
			}
		}
	}
}

// newGrpcConnection 创建gRPC连接
func newGrpcConnection(orgConfig OrganizationConfig) (*grpc.ClientConn, error) {
	certificatePEM, err := os.ReadFile(orgConfig.TLSCertPath)
	if err != nil {
		return nil, fmt.Errorf("读取TLS证书文件失败：%w", err)
	}

	certificate, err := identity.CertificateFromPEM(certificatePEM)
	if err != nil {
		return nil, fmt.Errorf("解析TLS证书失败：%w", err)
	}

	certPool := x509.NewCertPool()
	certPool.AddCert(certificate)
	transportCredentials := credentials.NewClientTLSFromCert(certPool, orgConfig.GatewayPeer)

	connection, err := grpc.NewClient(orgConfig.PeerEndpoint, grpc.WithTransportCredentials(transportCredentials))
	if err != nil {
		return nil, fmt.Errorf("创建gRPC连接失败：%w", err)
	}

	return connection, nil
}

// newIdentity 创建身份
func newIdentity(orgConfig OrganizationConfig) (*identity.X509Identity, error) {
	certificatePEM, err := readFirstFile(orgConfig.CertPath)
	if err != nil {
		return nil, fmt.Errorf("读取证书文件失败：%w", err)
	}

	certificate, err := identity.CertificateFromPEM(certificatePEM)
	if err != nil {
		return nil, err
	}

	id, err := identity.NewX509Identity(orgConfig.MSPID, certificate)
	if err != nil {
		return nil, err
	}

	return id, nil
}

// newSign 创建签名函数
func newSign(orgConfig OrganizationConfig) (identity.Sign, error) {
	privateKeyPEM, err := readFirstFile(orgConfig.KeyPath)
	if err != nil {
		return nil, fmt.Errorf("读取私钥文件失败：%w", err)
	}

	privateKey, err := identity.PrivateKeyFromPEM(privateKeyPEM)
	if err != nil {
		return nil, err
	}

	sign, err := identity.NewPrivateKeySign(privateKey)
	if err != nil {
		return nil, err
	}

	return sign, nil
}

// readFirstFile 读取目录中的第一个文件
func readFirstFile(dirPath string) ([]byte, error) {
	dir, err := os.Open(dirPath)
	if err != nil {
		return nil, err
	}
	defer dir.Close()

	fileNames, err := dir.Readdirnames(1)
	if err != nil {
		return nil, err
	}

	return os.ReadFile(path.Join(dirPath, fileNames[0]))
}

// GetContract 获取指定组织的合约
func (c *DVSSFabricClient) GetContract(orgName string) *client.Contract {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.contracts[orgName]
}

// Close 关闭所有连接
func (c *DVSSFabricClient) Close() {
	c.mu.Lock()
	defer c.mu.Unlock()

	// 停止健康检查
	if c.healthTicker != nil {
		c.healthTicker.Stop()
	}

	// 取消上下文
	if c.cancel != nil {
		c.cancel()
	}

	// 关闭所有连接
	for orgName, gw := range c.gateways {
		gw.Close()
		if connInfo := c.connections[orgName]; connInfo != nil {
			connInfo.Status = "closed"
		}
		atomic.AddInt32(&performanceMetrics.ActiveConnections, -1)
	}
}

// GetConnectionStatus 获取连接状态
func (c *DVSSFabricClient) GetConnectionStatus() map[string]*ConnectionInfo {
	c.mu.RLock()
	defer c.mu.RUnlock()

	status := make(map[string]*ConnectionInfo)
	for orgName, connInfo := range c.connections {
		// 创建副本避免并发问题
		status[orgName] = &ConnectionInfo{
			OrgName:      connInfo.OrgName,
			Status:       connInfo.Status,
			LastUsed:     connInfo.LastUsed,
			RequestCount: connInfo.RequestCount,
			ErrorCount:   connInfo.ErrorCount,
			Latency:      connInfo.Latency,
		}
	}
	return status
}

// GetPerformanceMetrics 获取性能指标
func (c *DVSSFabricClient) GetPerformanceMetrics() PerformanceMetrics {
	return PerformanceMetrics{
		TotalRequests:     atomic.LoadInt64(&performanceMetrics.TotalRequests),
		SuccessRequests:   atomic.LoadInt64(&performanceMetrics.SuccessRequests),
		FailedRequests:    atomic.LoadInt64(&performanceMetrics.FailedRequests),
		AverageLatency:    atomic.LoadInt64(&performanceMetrics.AverageLatency),
		ActiveConnections: atomic.LoadInt32(&performanceMetrics.ActiveConnections),
		LastResetTime:     performanceMetrics.LastResetTime,
	}
}

// recordMetrics 记录性能指标
func (c *DVSSFabricClient) recordMetrics(orgName string, latency time.Duration, success bool) {
	if !c.metricsEnabled {
		return
	}

	atomic.AddInt64(&performanceMetrics.TotalRequests, 1)

	if success {
		atomic.AddInt64(&performanceMetrics.SuccessRequests, 1)
	} else {
		atomic.AddInt64(&performanceMetrics.FailedRequests, 1)
	}

	// 更新平均延迟（简化计算）
	currentAvg := atomic.LoadInt64(&performanceMetrics.AverageLatency)
	newAvg := (currentAvg + latency.Milliseconds()) / 2
	atomic.StoreInt64(&performanceMetrics.AverageLatency, newAvg)

	// 更新连接信息
	c.mu.Lock()
	if connInfo := c.connections[orgName]; connInfo != nil {
		connInfo.RequestCount++
		connInfo.LastUsed = time.Now()
		connInfo.Latency = latency
		if !success {
			connInfo.ErrorCount++
		}
	}
	c.mu.Unlock()
}

// ExtractErrorMessage 从错误中提取详细信息
func (c *DVSSFabricClient) ExtractErrorMessage(err error) string {
	if err == nil {
		return ""
	}
	// 尝试获取 gRPC 状态
	if st, ok := status.FromError(err); ok {
		// 获取详细信息
		msg := st.Message()
		details := st.Details()
		code := st.Code()

		// 构建完整的错误信息
		fullError := fmt.Sprintf("错误码: %v, 消息: %v", code, msg)
		if len(details) > 0 {
			fullError += fmt.Sprintf(", 详情: %+v", details)
		}
		return fullError
	}
	return err.Error()
}

// SubmitTransaction 提交交易到区块链（使用指定组织）
func (c *DVSSFabricClient) SubmitTransaction(orgName, dataID, operation, userID, signature string, shareInfo ShareInfo, metadata map[string]interface{}) (string, error) {
	start := time.Now()
	var success bool
	defer func() {
		c.recordMetrics(orgName, time.Since(start), success)
	}()

	contract := c.GetContract(orgName)
	if contract == nil {
		return "", fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	txID := fmt.Sprintf("tx_%d_%s", time.Now().UnixNano(), orgName)
	timestamp := time.Now().Format(time.RFC3339)

	// 构建交易参数
	args := []string{
		txID,
		dataID,
		operation,
		userID,
		timestamp,
		signature,
	}

	// 添加分片信息（如果有）
	if shareInfo.TotalShares > 0 {
		shareInfoJSON, _ := json.Marshal(shareInfo)
		args = append(args, string(shareInfoJSON))
	} else {
		args = append(args, "")
	}

	// 添加元数据（如果有）
	if len(metadata) > 0 {
		metadataJSON, _ := json.Marshal(metadata)
		args = append(args, string(metadataJSON))
	} else {
		args = append(args, "")
	}

	// 提交交易（带重试机制）
	var err error
	for i := 0; i < c.retryCount; i++ {
		_, err = contract.SubmitTransaction("RecordTransaction", args...)
		if err == nil {
			success = true
			break
		}

		log.Printf("⚠️  提交交易失败，重试 %d/%d: %v", i+1, c.retryCount, c.ExtractErrorMessage(err))
		time.Sleep(time.Duration(i+1) * time.Second)
	}

	if err != nil {
		return "", fmt.Errorf("提交交易失败: %v", c.ExtractErrorMessage(err))
	}

	return txID, nil
}

// LogAccess 记录访问日志（使用指定组织）
func (c *DVSSFabricClient) LogAccess(orgName, dataID, userID, action, permission, result, ipAddress string, metadata map[string]interface{}) error {
	contract := c.GetContract(orgName)
	if contract == nil {
		return fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	logID := fmt.Sprintf("log_%d", time.Now().Unix())
	timestamp := time.Now().Format(time.RFC3339)

	args := []string{
		logID,
		dataID,
		userID,
		action,
		permission,
		result,
		timestamp,
		ipAddress,
	}

	// 添加元数据
	if len(metadata) > 0 {
		metadataJSON, _ := json.Marshal(metadata)
		args = append(args, string(metadataJSON))
	} else {
		args = append(args, "")
	}

	// 记录访问日志
	_, err := contract.SubmitTransaction("LogAccess", args...)
	if err != nil {
		return fmt.Errorf("记录访问日志失败: %v", c.ExtractErrorMessage(err))
	}

	return nil
}

// GetTransactionHistory 获取交易历史（使用指定组织）
func (c *DVSSFabricClient) GetTransactionHistory(orgName, dataID string) ([]Transaction, error) {
	contract := c.GetContract(orgName)
	if contract == nil {
		return nil, fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	result, err := contract.EvaluateTransaction("GetTransactionHistory", dataID)
	if err != nil {
		return nil, fmt.Errorf("获取交易历史失败: %v", c.ExtractErrorMessage(err))
	}

	var transactions []Transaction
	if err := json.Unmarshal(result, &transactions); err != nil {
		return nil, fmt.Errorf("反序列化交易数据失败: %w", err)
	}

	return transactions, nil
}

// GetAccessLogs 获取访问日志（使用指定组织）
func (c *DVSSFabricClient) GetAccessLogs(orgName, dataID string) ([]AccessLog, error) {
	contract := c.GetContract(orgName)
	if contract == nil {
		return nil, fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	result, err := contract.EvaluateTransaction("GetAccessLogs", dataID)
	if err != nil {
		return nil, fmt.Errorf("获取访问日志失败: %v", c.ExtractErrorMessage(err))
	}

	var logs []AccessLog
	if err := json.Unmarshal(result, &logs); err != nil {
		return nil, fmt.Errorf("反序列化访问日志失败: %w", err)
	}

	return logs, nil
}

// VerifyDataIntegrity 验证数据完整性（使用指定组织）
func (c *DVSSFabricClient) VerifyDataIntegrity(orgName, dataID, expectedHash string) (bool, error) {
	contract := c.GetContract(orgName)
	if contract == nil {
		return false, fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	result, err := contract.EvaluateTransaction("VerifyDataIntegrity", dataID, expectedHash)
	if err != nil {
		return false, fmt.Errorf("验证数据完整性失败: %v", c.ExtractErrorMessage(err))
	}

	return string(result) == "true", nil
}

// GetStatistics 获取统计信息（使用指定组织）
func (c *DVSSFabricClient) GetStatistics(orgName string) (map[string]interface{}, error) {
	contract := c.GetContract(orgName)
	if contract == nil {
		return nil, fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	result, err := contract.EvaluateTransaction("GetStatistics")
	if err != nil {
		return nil, fmt.Errorf("获取统计信息失败: %v", c.ExtractErrorMessage(err))
	}

	var stats map[string]interface{}
	if err := json.Unmarshal(result, &stats); err != nil {
		return nil, fmt.Errorf("反序列化统计信息失败: %w", err)
	}

	return stats, nil
}

// HTTP API 处理函数
type DVSSAPIHandler struct {
	client *DVSSFabricClient
}

func NewDVSSAPIHandler(client *DVSSFabricClient) *DVSSAPIHandler {
	return &DVSSAPIHandler{client: client}
}

// setupRouter 设置路由器
func setupRouter(client *DVSSFabricClient) *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	// 添加CORS中间件
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	handler := NewDVSSAPIHandler(client)

	// API路由 - 支持多组织
	api := r.Group("/api/v1")
	{
		// 区块链交互API
		api.POST("/transactions", handler.SubmitTransaction)
		api.POST("/access-logs", handler.LogAccess)
		api.GET("/transactions/:data_id", handler.GetTransactionHistory)
		api.GET("/access-logs/:data_id", handler.GetAccessLogs)
		api.GET("/verify/:data_id", handler.VerifyDataIntegrity)
		api.GET("/statistics", handler.GetStatistics)
		api.GET("/health", handler.HealthCheck)

		// 性能监控API
		monitoring := api.Group("/monitoring")
		{
			monitoring.GET("/metrics", handler.GetMetrics)
			monitoring.GET("/connections", handler.GetConnections)
			monitoring.GET("/performance", handler.GetPerformance)
			monitoring.POST("/reset-metrics", handler.ResetMetrics)
		}

		// 区块浏览器API
		browser := api.Group("/browser")
		{
			browser.GET("/blocks", handler.GetBlocks)
			browser.GET("/transactions", handler.GetTransactions)
			browser.GET("/search", handler.Search)
			browser.GET("/chaininfo", handler.GetChainInfo)
		}
	}

	// 添加blockchain explorer相关的API端点
	setupBlockchainExplorerRoutes(r, client)

	// 静态文件服务
	r.Static("/static", "./frontend")
	r.StaticFile("/monitoring.html", "./frontend/monitoring.html")

	return r
}

// 提交交易 API
func (h *DVSSAPIHandler) SubmitTransaction(c *gin.Context) {
	var req struct {
		OrgName   string                 `json:"org_name"`
		DataID    string                 `json:"data_id"`
		Operation string                 `json:"operation"`
		UserID    string                 `json:"user_id"`
		Signature string                 `json:"signature"`
		ShareInfo ShareInfo              `json:"share_info"`
		Metadata  map[string]interface{} `json:"metadata"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if req.OrgName == "" {
		req.OrgName = "org1" // 默认组织
	}

	txID, err := h.client.SubmitTransaction(req.OrgName, req.DataID, req.Operation, req.UserID, req.Signature, req.ShareInfo, req.Metadata)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"tx_id": txID})
}

// 记录访问日志 API
func (h *DVSSAPIHandler) LogAccess(c *gin.Context) {
	var req struct {
		OrgName    string                 `json:"org_name"`
		DataID     string                 `json:"data_id"`
		UserID     string                 `json:"user_id"`
		Action     string                 `json:"action"`
		Permission string                 `json:"permission"`
		Result     string                 `json:"result"`
		IPAddress  string                 `json:"ip_address"`
		Metadata   map[string]interface{} `json:"metadata"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if req.OrgName == "" {
		req.OrgName = "org1" // 默认组织
	}

	err := h.client.LogAccess(req.OrgName, req.DataID, req.UserID, req.Action, req.Permission, req.Result, req.IPAddress, req.Metadata)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "success"})
}

// 获取交易历史 API
func (h *DVSSAPIHandler) GetTransactionHistory(c *gin.Context) {
	orgName := c.Query("org_name")
	dataID := c.Param("data_id")

	if orgName == "" {
		orgName = "org1" // 默认组织
	}

	transactions, err := h.client.GetTransactionHistory(orgName, dataID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"transactions": transactions})
}

// 获取访问日志 API
func (h *DVSSAPIHandler) GetAccessLogs(c *gin.Context) {
	orgName := c.Query("org_name")
	dataID := c.Param("data_id")

	if orgName == "" {
		orgName = "org1" // 默认组织
	}

	logs, err := h.client.GetAccessLogs(orgName, dataID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"logs": logs})
}

// 验证数据完整性 API
func (h *DVSSAPIHandler) VerifyDataIntegrity(c *gin.Context) {
	orgName := c.Query("org_name")
	dataID := c.Param("data_id")
	expectedHash := c.Query("expected_hash")

	if orgName == "" {
		orgName = "org1" // 默认组织
	}

	isValid, err := h.client.VerifyDataIntegrity(orgName, dataID, expectedHash)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"is_valid": isValid})
}

// 获取统计信息 API
func (h *DVSSAPIHandler) GetStatistics(c *gin.Context) {
	orgName := c.Query("org_name")

	if orgName == "" {
		orgName = "org1" // 默认组织
	}

	stats, err := h.client.GetStatistics(orgName)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, stats)
}

// 健康检查 API
func (h *DVSSAPIHandler) HealthCheck(c *gin.Context) {
	connections := h.client.GetConnectionStatus()
	metrics := h.client.GetPerformanceMetrics()

	// 检查所有连接状态
	allHealthy := true
	healthyCount := 0
	for _, conn := range connections {
		if conn.Status == "connected" || conn.Status == "healthy" {
			healthyCount++
		} else {
			allHealthy = false
		}
	}

	status := "healthy"
	if !allHealthy {
		status = "degraded"
	}
	if healthyCount == 0 {
		status = "unhealthy"
	}

	c.JSON(http.StatusOK, gin.H{
		"status":    status,
		"timestamp": time.Now().Format(time.RFC3339),
		"version":   "1.0.0",
		"uptime":    time.Since(metrics.LastResetTime).String(),
		"summary": gin.H{
			"total_organizations": len(globalConfig.Fabric.Organizations),
			"healthy_connections": healthyCount,
			"total_requests":      metrics.TotalRequests,
			"success_rate": func() float64 {
				if metrics.TotalRequests > 0 {
					return float64(metrics.SuccessRequests) / float64(metrics.TotalRequests) * 100
				}
				return 0
			}(),
			"average_latency_ms": metrics.AverageLatency,
		},
		"organizations": func() []gin.H {
			var orgs []gin.H
			for orgName, conn := range connections {
				orgs = append(orgs, gin.H{
					"name":          orgName,
					"status":        conn.Status,
					"last_used":     conn.LastUsed.Format(time.RFC3339),
					"request_count": conn.RequestCount,
					"error_count":   conn.ErrorCount,
					"latency_ms":    conn.Latency.Milliseconds(),
				})
			}
			return orgs
		}(),
	})
}

// 获取性能指标 API
func (h *DVSSAPIHandler) GetMetrics(c *gin.Context) {
	metrics := h.client.GetPerformanceMetrics()
	c.JSON(http.StatusOK, gin.H{
		"metrics":   metrics,
		"timestamp": time.Now().Format(time.RFC3339),
	})
}

// 获取连接状态 API
func (h *DVSSAPIHandler) GetConnections(c *gin.Context) {
	connections := h.client.GetConnectionStatus()
	c.JSON(http.StatusOK, gin.H{
		"connections": connections,
		"total":       len(connections),
		"timestamp":   time.Now().Format(time.RFC3339),
	})
}

// 获取性能报告 API
func (h *DVSSAPIHandler) GetPerformance(c *gin.Context) {
	metrics := h.client.GetPerformanceMetrics()
	connections := h.client.GetConnectionStatus()

	// 计算成功率
	var successRate float64
	if metrics.TotalRequests > 0 {
		successRate = float64(metrics.SuccessRequests) / float64(metrics.TotalRequests) * 100
	}

	// 统计健康连接数
	healthyConnections := 0
	for _, conn := range connections {
		if conn.Status == "connected" || conn.Status == "healthy" {
			healthyConnections++
		}
	}

	performance := gin.H{
		"summary": gin.H{
			"total_requests":      metrics.TotalRequests,
			"success_rate":        successRate,
			"average_latency_ms":  metrics.AverageLatency,
			"active_connections":  metrics.ActiveConnections,
			"healthy_connections": healthyConnections,
			"uptime_hours":        time.Since(metrics.LastResetTime).Hours(),
		},
		"connections": connections,
		"metrics":     metrics,
		"timestamp":   time.Now().Format(time.RFC3339),
	}

	c.JSON(http.StatusOK, performance)
}

// 重置性能指标 API
func (h *DVSSAPIHandler) ResetMetrics(c *gin.Context) {
	atomic.StoreInt64(&performanceMetrics.TotalRequests, 0)
	atomic.StoreInt64(&performanceMetrics.SuccessRequests, 0)
	atomic.StoreInt64(&performanceMetrics.FailedRequests, 0)
	atomic.StoreInt64(&performanceMetrics.AverageLatency, 0)
	performanceMetrics.LastResetTime = time.Now()

	// 重置连接统计
	h.client.mu.Lock()
	for _, connInfo := range h.client.connections {
		connInfo.RequestCount = 0
		connInfo.ErrorCount = 0
	}
	h.client.mu.Unlock()

	c.JSON(http.StatusOK, gin.H{
		"status":    "success",
		"message":   "性能指标已重置",
		"timestamp": time.Now().Format(time.RFC3339),
	})
}

// 区块浏览器 API
func (h *DVSSAPIHandler) GetBlocks(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	size, _ := strconv.Atoi(c.DefaultQuery("size", "10"))

	// 模拟区块数据
	blocks := []map[string]interface{}{}
	for i := 0; i < size; i++ {
		blockNum := (page-1)*size + i + 1
		blocks = append(blocks, map[string]interface{}{
			"block_number":      blockNum,
			"block_hash":        fmt.Sprintf("hash_%d", blockNum),
			"previous_hash":     fmt.Sprintf("prev_hash_%d", blockNum-1),
			"timestamp":         time.Now().Add(-time.Duration(blockNum) * time.Minute).Format(time.RFC3339),
			"transaction_count": 5,
			"data_hash":         fmt.Sprintf("data_hash_%d", blockNum),
		})
	}

	c.JSON(http.StatusOK, gin.H{
		"blocks": blocks,
		"pagination": gin.H{
			"page":  page,
			"size":  size,
			"total": 1000,
		},
	})
}

func (h *DVSSAPIHandler) GetTransactions(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	size, _ := strconv.Atoi(c.DefaultQuery("size", "20"))
	blockNumber := c.Query("block_number")

	// 模拟交易数据
	transactions := []map[string]interface{}{}
	for i := 0; i < size; i++ {
		txNum := (page-1)*size + i + 1
		blockNum := txNum/5 + 1
		if blockNumber != "" {
			if parsed, err := strconv.Atoi(blockNumber); err == nil {
				blockNum = parsed
			}
		}

		transactions = append(transactions, map[string]interface{}{
			"tx_id":        fmt.Sprintf("tx_%d", txNum),
			"block_number": blockNum,
			"timestamp":    time.Now().Add(-time.Duration(txNum) * time.Minute).Format(time.RFC3339),
			"operation":    "encrypt",
			"data_id":      fmt.Sprintf("data_%d", txNum),
			"user_id":      fmt.Sprintf("user_%d", txNum%5+1),
			"status":       "committed",
		})
	}

	c.JSON(http.StatusOK, gin.H{
		"transactions": transactions,
		"pagination": gin.H{
			"page":  page,
			"size":  size,
			"total": 5000,
		},
	})
}

func (h *DVSSAPIHandler) Search(c *gin.Context) {
	query := c.Query("q")
	searchType := c.Query("type")

	if query == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Search query required"})
		return
	}

	results := []map[string]interface{}{
		{
			"type":        searchType,
			"id":          query,
			"description": "Search result for " + query,
			"timestamp":   time.Now().Format(time.RFC3339),
		},
	}

	c.JSON(http.StatusOK, gin.H{
		"query":   query,
		"type":    searchType,
		"results": results,
		"total":   len(results),
	})
}

func (h *DVSSAPIHandler) GetChainInfo(c *gin.Context) {
	chainInfo := map[string]interface{}{
		"chain_name":          globalConfig.Fabric.ChannelName,
		"network_name":        "dvss-ppa-network",
		"height":              1000,
		"current_block_hash":  "current_hash_001",
		"previous_block_hash": "prev_hash_001",
		"organizations":       len(globalConfig.Fabric.Organizations),
		"chaincode":           globalConfig.Fabric.ChaincodeName,
	}

	c.JSON(http.StatusOK, chainInfo)
}

// =============== 区块链浏览器功能实现 ===============

// GetChainInfo 获取链信息
func (c *DVSSFabricClient) GetChainInfo(orgName string) (*ChainInfo, error) {
	// 在 mock 模式下，返回模拟数据
	if c.contracts == nil {
		return &ChainInfo{
			Height:       100,
			CurrentHash:  "0x123456789abcdef",
			PreviousHash: "0x987654321fedcba",
			ChannelName:  "dvss-channel",
		}, nil
	}

	contract := c.GetContract(orgName)
	if contract == nil {
		return nil, fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	// 获取区块链信息
	result, err := contract.EvaluateTransaction("GetChainInfo")
	if err != nil {
		return nil, fmt.Errorf("获取链信息失败: %v", c.ExtractErrorMessage(err))
	}

	var chainInfo ChainInfo
	if err := json.Unmarshal(result, &chainInfo); err != nil {
		return nil, fmt.Errorf("反序列化链信息失败: %w", err)
	}

	return &chainInfo, nil
}

// GetBlockByNumber 根据区块号获取区块
func (c *DVSSFabricClient) GetBlockByNumber(orgName string, blockNumber uint64) (*BlockInfo, error) {
	// 在 mock 模式下，返回模拟数据
	if c.contracts == nil {
		return &BlockInfo{
			BlockNumber:      blockNumber,
			PreviousHash:     "0x987654321fedcba",
			DataHash:         "0x123456789abcdef",
			TransactionCount: 3,
			Timestamp:        time.Now().Format(time.RFC3339),
			Transactions: []TransactionInfo{
				{
					TxID:          "tx123456789",
					ChaincodeName: "dvss-chaincode",
					FunctionName:  "RecordTransaction",
					Args:          []string{"data1", "process", "user1"},
					Creator:       "org1",
					Timestamp:     time.Now().Format(time.RFC3339),
					Status:        "VALID",
				},
			},
		}, nil
	}

	contract := c.GetContract(orgName)
	if contract == nil {
		return nil, fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	result, err := contract.EvaluateTransaction("GetBlockByNumber", fmt.Sprintf("%d", blockNumber))
	if err != nil {
		return nil, fmt.Errorf("获取区块失败: %v", c.ExtractErrorMessage(err))
	}

	var blockInfo BlockInfo
	if err := json.Unmarshal(result, &blockInfo); err != nil {
		return nil, fmt.Errorf("反序列化区块数据失败: %w", err)
	}

	return &blockInfo, nil
}

// GetBlockByHash 根据区块哈希获取区块
func (c *DVSSFabricClient) GetBlockByHash(orgName string, blockHash string) (*BlockInfo, error) {
	// 在 mock 模式下，返回模拟数据
	if c.contracts == nil {
		return &BlockInfo{
			BlockNumber:      50,
			PreviousHash:     "0x987654321fedcba",
			DataHash:         blockHash,
			TransactionCount: 2,
			Timestamp:        time.Now().Format(time.RFC3339),
			Transactions: []TransactionInfo{
				{
					TxID:          "tx987654321",
					ChaincodeName: "dvss-chaincode",
					FunctionName:  "LogAccess",
					Args:          []string{"data2", "user2", "read"},
					Creator:       "org2",
					Timestamp:     time.Now().Format(time.RFC3339),
					Status:        "VALID",
				},
			},
		}, nil
	}

	contract := c.GetContract(orgName)
	if contract == nil {
		return nil, fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	result, err := contract.EvaluateTransaction("GetBlockByHash", blockHash)
	if err != nil {
		return nil, fmt.Errorf("获取区块失败: %v", c.ExtractErrorMessage(err))
	}

	var blockInfo BlockInfo
	if err := json.Unmarshal(result, &blockInfo); err != nil {
		return nil, fmt.Errorf("反序列化区块数据失败: %w", err)
	}

	return &blockInfo, nil
}

// GetTransactionByID 根据交易ID获取交易
func (c *DVSSFabricClient) GetTransactionByID(orgName string, txID string) (*TransactionInfo, error) {
	// 在 mock 模式下，返回模拟数据
	if c.contracts == nil {
		return &TransactionInfo{
			TxID:          txID,
			ChaincodeName: "dvss-chaincode",
			FunctionName:  "RecordTransaction",
			Args:          []string{"data1", "process", "user1"},
			Creator:       orgName,
			Timestamp:     time.Now().Format(time.RFC3339),
			Status:        "VALID",
			Endorsements: []EndorsementInfo{
				{
					Endorser:  "peer0." + orgName + ".dvss-ppa.com",
					Signature: "sig123456789",
					Timestamp: time.Now().Format(time.RFC3339),
				},
			},
		}, nil
	}

	contract := c.GetContract(orgName)
	if contract == nil {
		return nil, fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	result, err := contract.EvaluateTransaction("GetTransactionByID", txID)
	if err != nil {
		return nil, fmt.Errorf("获取交易失败: %v", c.ExtractErrorMessage(err))
	}

	var txInfo TransactionInfo
	if err := json.Unmarshal(result, &txInfo); err != nil {
		return nil, fmt.Errorf("反序列化交易数据失败: %w", err)
	}

	return &txInfo, nil
}

// GetRecentBlocks 获取最近的区块
func (c *DVSSFabricClient) GetRecentBlocks(orgName string, count int) ([]*BlockInfo, error) {
	// 在 mock 模式下，返回模拟数据
	if c.contracts == nil {
		var blocks []*BlockInfo
		for i := 0; i < count; i++ {
			blocks = append(blocks, &BlockInfo{
				BlockNumber:      uint64(100 - i),
				PreviousHash:     fmt.Sprintf("0x%x", 987654321-i),
				DataHash:         fmt.Sprintf("0x%x", 123456789+i),
				TransactionCount: (i % 3) + 1,
				Timestamp:        time.Now().Add(-time.Duration(i) * time.Minute).Format(time.RFC3339),
				Transactions:     []TransactionInfo{},
			})
		}
		return blocks, nil
	}

	contract := c.GetContract(orgName)
	if contract == nil {
		return nil, fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	result, err := contract.EvaluateTransaction("GetRecentBlocks", fmt.Sprintf("%d", count))
	if err != nil {
		return nil, fmt.Errorf("获取最近区块失败: %v", c.ExtractErrorMessage(err))
	}

	var blocks []*BlockInfo
	if err := json.Unmarshal(result, &blocks); err != nil {
		return nil, fmt.Errorf("反序列化区块数据失败: %w", err)
	}

	return blocks, nil
}

// GetRecentTransactions 获取最近的交易
func (c *DVSSFabricClient) GetRecentTransactions(orgName string, count int) ([]*TransactionInfo, error) {
	// 在 mock 模式下，返回模拟数据
	if c.contracts == nil {
		var transactions []*TransactionInfo
		for i := 0; i < count; i++ {
			transactions = append(transactions, &TransactionInfo{
				TxID:          fmt.Sprintf("tx%09d", 999999999-i),
				ChaincodeName: "dvss-chaincode",
				FunctionName:  []string{"RecordTransaction", "LogAccess", "VerifyProof"}[i%3],
				Args:          []string{fmt.Sprintf("data%d", i), fmt.Sprintf("user%d", i)},
				Creator:       orgName,
				Timestamp:     time.Now().Add(-time.Duration(i) * time.Minute).Format(time.RFC3339),
				Status:        "VALID",
			})
		}
		return transactions, nil
	}

	contract := c.GetContract(orgName)
	if contract == nil {
		return nil, fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	result, err := contract.EvaluateTransaction("GetRecentTransactions", fmt.Sprintf("%d", count))
	if err != nil {
		return nil, fmt.Errorf("获取最近交易失败: %v", c.ExtractErrorMessage(err))
	}

	var transactions []*TransactionInfo
	if err := json.Unmarshal(result, &transactions); err != nil {
		return nil, fmt.Errorf("反序列化交易数据失败: %w", err)
	}

	return transactions, nil
}

// SearchTransactions 搜索交易
func (c *DVSSFabricClient) SearchTransactions(orgName, query string, limit int) ([]*TransactionInfo, error) {
	// 在 mock 模式下，返回模拟数据
	if c.contracts == nil {
		var transactions []*TransactionInfo
		for i := 0; i < limit && i < 10; i++ {
			if strings.Contains(fmt.Sprintf("tx%09d", i), query) ||
				strings.Contains("RecordTransaction", query) {
				transactions = append(transactions, &TransactionInfo{
					TxID:          fmt.Sprintf("tx%09d", i),
					ChaincodeName: "dvss-chaincode",
					FunctionName:  "RecordTransaction",
					Args:          []string{fmt.Sprintf("data%d", i), "process", fmt.Sprintf("user%d", i)},
					Creator:       orgName,
					Timestamp:     time.Now().Add(-time.Duration(i) * time.Hour).Format(time.RFC3339),
					Status:        "VALID",
				})
			}
		}
		return transactions, nil
	}

	contract := c.GetContract(orgName)
	if contract == nil {
		return nil, fmt.Errorf("组织[%s]的合约未找到", orgName)
	}

	result, err := contract.EvaluateTransaction("SearchTransactions", query, fmt.Sprintf("%d", limit))
	if err != nil {
		return nil, fmt.Errorf("搜索交易失败: %v", c.ExtractErrorMessage(err))
	}

	var transactions []*TransactionInfo
	if err := json.Unmarshal(result, &transactions); err != nil {
		return nil, fmt.Errorf("反序列化交易数据失败: %w", err)
	}

	return transactions, nil
}

// setupMockRouter 设置模拟路由器（开发模式）
func setupMockRouter() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	// 添加CORS中间件
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// API路由 - 模拟版本
	api := r.Group("/api/v1")
	{
		api.GET("/health", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"status":    "healthy",
				"mode":      "development",
				"fabric":    "disconnected",
				"timestamp": time.Now().Format(time.RFC3339),
				"version":   "1.0.0",
				"message":   "开发模式 - Fabric 连接不可用",
			})
		})

		api.POST("/transactions", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"tx_id":   fmt.Sprintf("mock_tx_%d", time.Now().Unix()),
				"status":  "simulated",
				"message": "模拟交易提交成功",
			})
		})

		api.GET("/transactions/:data_id", func(c *gin.Context) {
			dataID := c.Param("data_id")
			c.JSON(http.StatusOK, gin.H{
				"data_id": dataID,
				"transactions": []gin.H{
					{
						"tx_id":     fmt.Sprintf("mock_tx_%s", dataID),
						"operation": "encrypt",
						"timestamp": time.Now().Format(time.RFC3339),
						"status":    "simulated",
					},
				},
			})
		})

		api.GET("/statistics", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"total_transactions": 100,
				"active_users":       10,
				"system_uptime":      "99.9%",
				"mode":               "development",
				"timestamp":          time.Now().Format(time.RFC3339),
			})
		})
	}

	// 区块浏览器 API - 模拟版本
	browser := r.Group("/api/browser")
	{
		browser.GET("/blocks", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"blocks": []gin.H{
					{
						"block_number": 1,
						"block_hash":   "mock_hash_001",
						"timestamp":    time.Now().Format(time.RFC3339),
						"tx_count":     5,
					},
				},
				"total": 1,
				"mode":  "development",
			})
		})

		browser.GET("/chaininfo", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"chain_name":   "dvss-ppa-dev",
				"network_name": "development",
				"height":       1,
				"mode":         "development",
				"status":       "simulated",
			})
		})
	}

	// 静态文件服务
	r.Static("/static", "./frontend")
	r.StaticFile("/monitoring.html", "./frontend/monitoring.html")

	// 主页 - 开发模式版本
	r.GET("/", func(c *gin.Context) {
		html := `
<!DOCTYPE html>
<html>
<head>
    <title>DVSS-PPA Fabric 客户端 - 开发模式</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .header { background: #fff3cd; padding: 20px; border-radius: 5px; border-left: 4px solid #ffc107; }
        .nav { margin: 20px 0; }
        .nav a { margin-right: 20px; text-decoration: none; color: #007bff; padding: 10px 15px; background: #e9ecef; border-radius: 5px; }
        .nav a:hover { background: #007bff; color: white; }
        .content { background: #fff; padding: 20px; border: 1px solid #ddd; border-radius: 5px; margin-top: 20px; }
        .warning { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .api-list { list-style: none; padding: 0; }
        .api-list li { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px; }
        .monitoring-link { background: #28a745; color: white; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0; }
        .monitoring-link a { color: white; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 DVSS-PPA Fabric 客户端 - 开发模式</h1>
        <p>模拟 Hyperledger Fabric 区块链浏览器和API服务</p>
    </div>
    
    <div class="monitoring-link">
        <a href="/monitoring.html">📊 访问监控台 - 实时系统状态</a>
    </div>
    
    <div class="warning">
        <strong>⚠️ 注意:</strong> 当前运行在开发模式下，Fabric 网络连接不可用。所有 API 返回模拟数据。
    </div>
    
    <div class="nav">
        <a href="/api/browser/blocks">区块列表 (模拟)</a>
        <a href="/api/browser/chaininfo">链信息 (模拟)</a>
        <a href="/api/v1/statistics">统计信息 (模拟)</a>
        <a href="/api/v1/health">健康检查</a>
        <a href="/api/v1/monitoring/performance">性能监控</a>
    </div>
    
    <div class="content">
        <h2>可用 API 端点</h2>
        <ul class="api-list">
            <li><strong>GET /api/v1/health</strong> - 健康检查</li>
            <li><strong>POST /api/v1/transactions</strong> - 提交交易 (模拟)</li>
            <li><strong>GET /api/v1/transactions/{data_id}</strong> - 查询交易 (模拟)</li>
            <li><strong>GET /api/v1/statistics</strong> - 统计信息 (模拟)</li>
            <li><strong>GET /api/v1/monitoring/metrics</strong> - 性能指标</li>
            <li><strong>GET /api/v1/monitoring/connections</strong> - 连接状态</li>
            <li><strong>GET /api/v1/monitoring/performance</strong> - 性能报告</li>
            <li><strong>GET /api/browser/blocks</strong> - 浏览区块 (模拟)</li>
            <li><strong>GET /api/browser/chaininfo</strong> - 链信息 (模拟)</li>
        </ul>
        
        <h2>部署说明</h2>
        <p><strong>要启用完整功能:</strong></p>
        <ol>
            <li>确保 Hyperledger Fabric 网络正在运行</li>
            <li>配置正确的证书文件路径</li>
            <li>检查网络连接和端口配置</li>
            <li>重启服务以连接到真实的 Fabric 网络</li>
        </ol>
        
        <h2>系统信息</h2>
        <p><strong>模式:</strong> 开发模式</p>
        <p><strong>Fabric 状态:</strong> 已断开</p>
        <p><strong>启动时间:</strong> ` + time.Now().Format(time.RFC3339) + `</p>
    </div>
</body>
</html>
		`
		c.Header("Content-Type", "text/html")
		c.String(http.StatusOK, html)
	})

	return r
}

// setupBlockchainExplorerRoutes 设置blockchain explorer相关路由
func setupBlockchainExplorerRoutes(r *gin.Engine, client *DVSSFabricClient) {
	explorer := r.Group("/api/explorer")

	// 获取链信息
	explorer.GET("/chain/info", func(c *gin.Context) {
		chainInfo, err := client.GetChainInfo("org1")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, chainInfo)
	})

	// 获取区块列表
	explorer.GET("/blocks", func(c *gin.Context) {
		pageStr := c.DefaultQuery("page", "1")
		limitStr := c.DefaultQuery("limit", "10")

		page, _ := strconv.Atoi(pageStr)
		limit, _ := strconv.Atoi(limitStr)

		blocks, err := client.GetRecentBlocks("org1", limit)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, gin.H{
			"blocks": blocks,
			"page":   page,
			"limit":  limit,
		})
	})

	// 获取指定区块
	explorer.GET("/block/:number", func(c *gin.Context) {
		blockNumberStr := c.Param("number")
		blockNumber, err := strconv.ParseUint(blockNumberStr, 10, 64)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid block number"})
			return
		}

		block, err := client.GetBlockByNumber("org1", blockNumber)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, block)
	})

	// 获取交易列表
	explorer.GET("/transactions", func(c *gin.Context) {
		pageStr := c.DefaultQuery("page", "1")
		limitStr := c.DefaultQuery("limit", "10")

		page, _ := strconv.Atoi(pageStr)
		limit, _ := strconv.Atoi(limitStr)

		transactions, err := client.GetRecentTransactions("org1", limit)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, gin.H{
			"transactions": transactions,
			"page":         page,
			"limit":        limit,
		})
	})

	// 获取指定交易
	explorer.GET("/transaction/:txid", func(c *gin.Context) {
		txID := c.Param("txid")

		transaction, err := client.GetTransactionByID("org1", txID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, transaction)
	})

	// 搜索交易
	explorer.GET("/search", func(c *gin.Context) {
		query := c.Query("q")
		if query == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Search query is required"})
			return
		}

		results, err := client.SearchTransactions("org1", query, 50)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, gin.H{
			"query":   query,
			"results": results,
		})
	})
}

func main() {
	// 初始化配置
	if err := initConfig(); err != nil {
		log.Printf("⚠️  初始化配置失败：%v", err)
		log.Println("🧪 启动开发模式（无 Fabric 连接）...")
		startDevelopmentMode()
		return
	}

	// 尝试创建Fabric客户端
	client, err := NewDVSSFabricClient()
	if err != nil {
		log.Printf("⚠️  创建Fabric客户端失败：%v", err)
		log.Println("🧪 启动开发模式（无 Fabric 连接）...")
		startDevelopmentMode()
		return
	}
	defer client.Close()

	// 设置路由器
	r := setupRouter(client)

	// 启动服务器
	port := globalConfig.Server.Port
	if port == 0 {
		port = 8080
	}

	log.Printf("🚀 DVSS-PPA Fabric客户端启动成功")
	log.Printf("📡 监听端口: %d", port)
	log.Printf("🌐 访问地址: http://localhost:%d", port)
	log.Printf("📊 API文档: http://localhost:%d/api/v1/", port)
	log.Printf("🔍 健康检查: http://localhost:%d/api/v1/health", port)

	if err := r.Run(fmt.Sprintf(":%d", port)); err != nil {
		log.Fatalf("启动服务器失败：%v", err)
	}
}

// startDevelopmentMode 启动开发模式（不连接 Fabric）
func startDevelopmentMode() {
	// 创建模拟路由器
	r := setupMockRouter()

	// 启动服务器
	port := 8080
	if envPort := os.Getenv("PORT"); envPort != "" {
		if p, err := strconv.Atoi(envPort); err == nil {
			port = p
		}
	}

	log.Printf("🧪 开发模式启动")
	log.Printf("📡 监听端口: %d", port)
	log.Printf("🌐 访问地址: http://localhost:%d", port)
	log.Printf("⚠️  注意: Fabric 连接不可用，仅提供模拟 API")

	if err := r.Run(fmt.Sprintf(":%d", port)); err != nil {
		log.Fatalf("启动服务器失败：%v", err)
	}
}
