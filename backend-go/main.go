package main

import (
	"dvss-ppa-go-backend/api"
	"dvss-ppa-go-backend/config"
	"dvss-ppa-go-backend/pkg/fabric"
	"fmt"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

func main() {
	// 初始化配置
	if err := config.InitConfig(); err != nil {
		log.Printf("配置初始化警告：%v", err)
		// 继续运行，使用默认配置
	}

	// 初始化 Fabric 客户端（可选）
	if err := fabric.InitFabric(); err != nil {
		log.Printf("Fabric客户端初始化警告：%v", err)
		// 继续运行，某些功能可能不可用
	}

	// 创建 Gin 路由
	gin.SetMode(gin.DebugMode)
	r := gin.Default()

	// 配置CORS中间件
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "*")
		c.Header("Access-Control-Allow-Credentials", "true")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// 健康检查端点
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": "DVSS Go Backend",
			"version": "1.0.0",
		})
	})

	// API路由组
	apiGroup := r.Group("/api/v1")

	// 注册处理器
	dvssHandler := api.NewDVSSHandler()

	// 区块链相关接口
	blockchain := apiGroup.Group("/blockchain")
	{
		// 记录操作到区块链
		blockchain.POST("/record", dvssHandler.RecordToBlockchain)
		// 查询区块链交易
		blockchain.GET("/transaction/:txId", dvssHandler.QueryTransaction)
		// 查询区块列表
		blockchain.GET("/blocks", dvssHandler.QueryBlockList)
		// 查询链码调用历史
		blockchain.GET("/chaincode/history", dvssHandler.QueryChaincodeHistory)
	}

	// DVSS 核心接口（与Python后端交互）
	dvss := apiGroup.Group("/dvss")
	{
		// 分片上链
		dvss.POST("/shard/upload", dvssHandler.UploadShardToBlockchain)
		// 查询分片信息
		dvss.GET("/shard/:shardId", dvssHandler.QueryShardFromBlockchain)
		// 验证分片完整性
		dvss.POST("/shard/verify", dvssHandler.VerifyShardIntegrity)
		// 审计日志上链
		dvss.POST("/audit/upload", dvssHandler.UploadAuditLog)
	}

	// Fabric网络管理接口
	network := apiGroup.Group("/network")
	{
		// 网络状态
		network.GET("/status", dvssHandler.GetNetworkStatus)
		// 节点信息
		network.GET("/peers", dvssHandler.GetPeerInfo)
		// 通道信息
		network.GET("/channels", dvssHandler.GetChannelInfo)
	}

	// 启动服务器
	port := 8001
	addr := fmt.Sprintf(":%d", port)
	log.Printf("Go backend server starting on %s", addr)
	
	if err := r.Run(addr); err != nil {
		log.Fatalf("服务器启动失败：%v", err)
	}
}
