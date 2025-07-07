package main

import (
	"dvss-ppa-go-backend/api"
	"dvss-ppa-go-backend/config"
	_ "dvss-ppa-go-backend/docs" // swagger docs
	"dvss-ppa-go-backend/pkg/fabric"
	"dvss-ppa-go-backend/pkg/middleware"
	"dvss-ppa-go-backend/pkg/utils"
	"fmt"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/swaggo/files" // gin-swagger middleware
	ginSwagger "github.com/swaggo/gin-swagger"
)

// @title DVSS-PPA Go Backend API
// @version 1.0
// @description DVSS-PPA项目的Go后端API，提供Fabric区块链集成功能
// @termsOfService http://swagger.io/terms/

// @contact.name API Support
// @contact.url http://www.swagger.io/support
// @contact.email support@swagger.io

// @license.name Apache 2.0
// @license.url http://www.apache.org/licenses/LICENSE-2.0.html

// @host localhost:8001
// @BasePath /api/v1
// @schemes http

// @securityDefinitions.basic BasicAuth

// @securityDefinitions.apikey ApiKeyAuth
// @in header
// @name Authorization

func main() {
	// 初始化配置
	if err := config.InitConfig(); err != nil {
		log.Printf("配置初始化警告：%v", err)
		// 继续运行，使用默认配置
	}

	// 初始化 Fabric 客户端（可选）
	if err := fabric.InitClient(); err != nil {
		log.Printf("Fabric客户端初始化警告：%v", err)
		// 继续运行，某些功能可能不可用
	}

	// 创建 Gin 路由
	gin.SetMode(gin.DebugMode)
	r := gin.Default()

	// 配置中间件
	r.Use(middleware.CORSMiddleware())
	r.Use(middleware.RequestLoggerMiddleware())

	// 健康检查端点
	r.GET("/health", func(c *gin.Context) {
		utils.SuccessResponse(c, "服务健康", gin.H{
			"status":  "healthy",
			"service": "DVSS Go Backend",
			"version": "1.0.0",
		})
	})

	// Swagger文档端点
	r.GET("/swagger/*any", ginSwagger.WrapHandler(files.Handler))

	// Prometheus metrics端点
	r.GET("/metrics", func(c *gin.Context) {
		c.String(http.StatusOK, `# HELP dvss_go_backend_health Health status of DVSS Go Backend
# TYPE dvss_go_backend_health gauge
dvss_go_backend_health 1
# HELP dvss_go_backend_version Version info
# TYPE dvss_go_backend_version gauge
dvss_go_backend_version{version="1.0.0"} 1
`)
	})

	// API路由组
	apiGroup := r.Group("/api/v1")

	// 注册Fabric相关的处理器
	fabricGroup := apiGroup.Group("/fabric")
	fabricGroup.Use(middleware.OptionalAuthMiddleware())
	{
		// 注册审计日志处理器
		auditHandler := api.NewAuditHandler()
		auditHandler.RegisterRoutes(fabricGroup)

		// 注册加密日志处理器
		encryptionHandler := api.NewEncryptionHandler()
		encryptionHandler.RegisterRoutes(fabricGroup)

		// 注册解密日志处理器
		decryptionHandler := api.NewDecryptionHandler()
		decryptionHandler.RegisterRoutes(fabricGroup)

		// 注册查询日志处理器
		queryHandler := api.NewQueryHandler()
		queryHandler.RegisterRoutes(fabricGroup)
	}

	// 需要认证的路由组
	authGroup := apiGroup.Group("/secure")
	authGroup.Use(middleware.AuthMiddleware())
	{
		// 这里可以添加需要认证的特殊接口
		authGroup.GET("/status", func(c *gin.Context) {
			userID := c.GetString("user_id")
			utils.SuccessResponse(c, "认证成功", gin.H{
				"user_id": userID,
				"message": "您已通过认证",
			})
		})
	}

	// 启动服务器
	port := 8001
	addr := fmt.Sprintf(":%d", port)
	utils.LogInfof("Go backend server starting on %s", addr)

	if err := r.Run(addr); err != nil {
		utils.LogErrorf("服务器启动失败：%v", err)
		log.Fatalf("服务器启动失败：%v", err)
	}
}
