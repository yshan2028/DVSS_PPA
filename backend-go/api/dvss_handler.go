package api

import (
	"dvss-ppa-go-backend/service"
	"dvss-ppa-go-backend/utils"
	"strconv"

	"github.com/gin-gonic/gin"
)

type DVSSHandler struct {
	dvssService *service.DVSSService
}

func NewDVSSHandler() *DVSSHandler {
	return &DVSSHandler{
		dvssService: &service.DVSSService{},
	}
}

// CreateSecretShare 创建秘密分享
func (h *DVSSHandler) CreateSecretShare(c *gin.Context) {
	var req struct {
		ShareID   string `json:"shareId"`
		Data      string `json:"data"`
		Threshold string `json:"threshold"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		utils.BadRequest(c, "秘密分享信息格式错误")
		return
	}

	err := h.dvssService.CreateSecretShare(req.ShareID, req.Data, req.Threshold)
	if err != nil {
		utils.ServerError(c, "创建秘密分享失败："+err.Error())
		return
	}

	utils.SuccessWithMessage(c, "秘密分享创建成功", nil)
}

// QuerySecretShare 查询秘密分享
func (h *DVSSHandler) QuerySecretShare(c *gin.Context) {
	shareID := c.Param("id")
	secretShare, err := h.dvssService.QuerySecretShare(shareID)
	if err != nil {
		utils.ServerError(c, "查询秘密分享失败："+err.Error())
		return
	}

	utils.Success(c, secretShare)
}

// QuerySecretShareList 分页查询秘密分享列表
func (h *DVSSHandler) QuerySecretShareList(c *gin.Context) {
	pageSize, _ := strconv.Atoi(c.DefaultQuery("pageSize", "10"))
	bookmark := c.DefaultQuery("bookmark", "")
	status := c.DefaultQuery("status", "")

	result, err := h.dvssService.QuerySecretShareList(int32(pageSize), bookmark, status)
	if err != nil {
		utils.ServerError(c, err.Error())
		return
	}

	utils.Success(c, result)
}

// RecoverSecret 恢复秘密
func (h *DVSSHandler) RecoverSecret(c *gin.Context) {
	var req struct {
		SecretID string   `json:"secretId"`
		Shares   []string `json:"shares"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		utils.BadRequest(c, "恢复秘密请求格式错误")
		return
	}

	result, err := h.dvssService.RecoverSecret(req.SecretID, req.Shares)
	if err != nil {
		utils.ServerError(c, "恢复秘密失败："+err.Error())
		return
	}

	utils.Success(c, result)
}

// QueryBlockList 分页查询区块列表
func (h *DVSSHandler) QueryBlockList(c *gin.Context) {
	pageSize, _ := strconv.Atoi(c.DefaultQuery("pageSize", "10"))
	pageNum, _ := strconv.Atoi(c.DefaultQuery("pageNum", "1"))

	result, err := h.dvssService.QueryBlockList(pageSize, pageNum)
	if err != nil {
		utils.ServerError(c, err.Error())
		return
	}

	utils.Success(c, result)
}

// 区块链相关操作

// RecordToBlockchain 记录操作到区块链
func (h *DVSSHandler) RecordToBlockchain(c *gin.Context) {
	var req struct {
		Action    string      `json:"action"`
		Data      interface{} `json:"data"`
		Timestamp string      `json:"timestamp"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		utils.BadRequest(c, "请求数据格式错误")
		return
	}

	txID, err := h.dvssService.RecordToBlockchain(req.Action, req.Data, req.Timestamp)
	if err != nil {
		utils.ServerError(c, "记录到区块链失败："+err.Error())
		return
	}

	utils.SuccessWithMessage(c, "记录到区块链成功", gin.H{
		"transaction_id": txID,
	})
}

// QueryTransaction 查询区块链交易
func (h *DVSSHandler) QueryTransaction(c *gin.Context) {
	txID := c.Param("txId")

	transaction, err := h.dvssService.QueryTransaction(txID)
	if err != nil {
		utils.ServerError(c, "查询交易失败："+err.Error())
		return
	}

	utils.SuccessWithData(c, transaction)
}

// QueryChaincodeHistory 查询链码调用历史
func (h *DVSSHandler) QueryChaincodeHistory(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	size, _ := strconv.Atoi(c.DefaultQuery("size", "20"))

	history, err := h.dvssService.QueryChaincodeHistory(page, size)
	if err != nil {
		utils.ServerError(c, "查询链码历史失败："+err.Error())
		return
	}

	utils.SuccessWithData(c, history)
}

// UploadShardToBlockchain 分片上链
func (h *DVSSHandler) UploadShardToBlockchain(c *gin.Context) {
	var req struct {
		ShardID   string      `json:"shard_id"`
		OrderID   string      `json:"order_id"`
		ShardHash string      `json:"shard_hash"`
		Metadata  interface{} `json:"metadata"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		utils.BadRequest(c, "分片数据格式错误")
		return
	}

	txID, err := h.dvssService.UploadShardToBlockchain(req.ShardID, req.OrderID, req.ShardHash, req.Metadata)
	if err != nil {
		utils.ServerError(c, "分片上链失败："+err.Error())
		return
	}

	utils.SuccessWithMessage(c, "分片上链成功", gin.H{
		"transaction_id": txID,
		"shard_id":      req.ShardID,
	})
}

// QueryShardFromBlockchain 查询分片信息
func (h *DVSSHandler) QueryShardFromBlockchain(c *gin.Context) {
	shardID := c.Param("shardId")

	shardInfo, err := h.dvssService.QueryShardFromBlockchain(shardID)
	if err != nil {
		utils.ServerError(c, "查询分片信息失败："+err.Error())
		return
	}

	utils.SuccessWithData(c, shardInfo)
}

// VerifyShardIntegrity 验证分片完整性
func (h *DVSSHandler) VerifyShardIntegrity(c *gin.Context) {
	var req struct {
		ShardID      string `json:"shard_id"`
		CurrentHash  string `json:"current_hash"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		utils.BadRequest(c, "验证数据格式错误")
		return
	}

	isValid, err := h.dvssService.VerifyShardIntegrity(req.ShardID, req.CurrentHash)
	if err != nil {
		utils.ServerError(c, "验证分片完整性失败："+err.Error())
		return
	}

	utils.SuccessWithMessage(c, "分片完整性验证完成", gin.H{
		"shard_id": req.ShardID,
		"is_valid": isValid,
	})
}

// UploadAuditLog 审计日志上链
func (h *DVSSHandler) UploadAuditLog(c *gin.Context) {
	var req struct {
		UserID       string      `json:"user_id"`
		Action       string      `json:"action"`
		ResourceType string      `json:"resource_type"`
		ResourceID   string      `json:"resource_id"`
		Details      interface{} `json:"details"`
		Timestamp    string      `json:"timestamp"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		utils.BadRequest(c, "审计日志格式错误")
		return
	}

	txID, err := h.dvssService.UploadAuditLog(req.UserID, req.Action, req.ResourceType, req.ResourceID, req.Details, req.Timestamp)
	if err != nil {
		utils.ServerError(c, "审计日志上链失败："+err.Error())
		return
	}

	utils.SuccessWithMessage(c, "审计日志上链成功", gin.H{
		"transaction_id": txID,
	})
}

// 网络管理相关操作

// GetNetworkStatus 获取网络状态
func (h *DVSSHandler) GetNetworkStatus(c *gin.Context) {
	status, err := h.dvssService.GetNetworkStatus()
	if err != nil {
		utils.ServerError(c, "获取网络状态失败："+err.Error())
		return
	}

	utils.SuccessWithData(c, status)
}

// GetPeerInfo 获取节点信息
func (h *DVSSHandler) GetPeerInfo(c *gin.Context) {
	peers, err := h.dvssService.GetPeerInfo()
	if err != nil {
		utils.ServerError(c, "获取节点信息失败："+err.Error())
		return
	}

	utils.SuccessWithData(c, peers)
}

// GetChannelInfo 获取通道信息
func (h *DVSSHandler) GetChannelInfo(c *gin.Context) {
	channels, err := h.dvssService.GetChannelInfo()
	if err != nil {
		utils.ServerError(c, "获取通道信息失败："+err.Error())
		return
	}

	utils.SuccessWithData(c, channels)
}
