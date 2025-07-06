package service

import (
	"dvss-ppa-go-backend/pkg/fabric"
	"encoding/json"
	"fmt"
	"time"
)

type DVSSService struct{}

const DVSS_ORG = "org1" // DVSS 主组织

// CreateSecretShare 创建秘密分享
func (s *DVSSService) CreateSecretShare(shareID, data, threshold string) error {
	contract := fabric.GetContract(DVSS_ORG)
	now := time.Now().Format(time.RFC3339)
	_, err := contract.SubmitTransaction("CreateSecretShare", shareID, data, threshold, now)
	if err != nil {
		return fmt.Errorf("创建秘密分享失败：%s", fabric.ExtractErrorMessage(err))
	}
	return nil
}

// QuerySecretShare 查询秘密分享
func (s *DVSSService) QuerySecretShare(shareID string) (map[string]interface{}, error) {
	contract := fabric.GetContract(DVSS_ORG)
	result, err := contract.EvaluateTransaction("QuerySecretShare", shareID)
	if err != nil {
		return nil, fmt.Errorf("查询秘密分享失败：%s", fabric.ExtractErrorMessage(err))
	}

	var secretShare map[string]interface{}
	if err := json.Unmarshal(result, &secretShare); err != nil {
		return nil, fmt.Errorf("解析秘密分享数据失败：%v", err)
	}

	return secretShare, nil
}

// QuerySecretShareList 分页查询秘密分享列表
func (s *DVSSService) QuerySecretShareList(pageSize int32, bookmark string, status string) (map[string]interface{}, error) {
	contract := fabric.GetContract(DVSS_ORG)
	result, err := contract.EvaluateTransaction("QuerySecretShareList", fmt.Sprintf("%d", pageSize), bookmark, status)
	if err != nil {
		return nil, fmt.Errorf("查询秘密分享列表失败：%s", fabric.ExtractErrorMessage(err))
	}

	var queryResult map[string]interface{}
	if err := json.Unmarshal(result, &queryResult); err != nil {
		return nil, fmt.Errorf("解析查询结果失败：%v", err)
	}

	return queryResult, nil
}

// RecoverSecret 恢复秘密
func (s *DVSSService) RecoverSecret(secretID string, shares []string) (map[string]interface{}, error) {
	contract := fabric.GetContract(DVSS_ORG)

	// 将 shares 数组转换为 JSON 字符串
	sharesJSON, err := json.Marshal(shares)
	if err != nil {
		return nil, fmt.Errorf("序列化分享数据失败：%v", err)
	}

	result, err := contract.SubmitTransaction("RecoverSecret", secretID, string(sharesJSON))
	if err != nil {
		return nil, fmt.Errorf("恢复秘密失败：%s", fabric.ExtractErrorMessage(err))
	}

	var recoveryResult map[string]interface{}
	if err := json.Unmarshal(result, &recoveryResult); err != nil {
		return nil, fmt.Errorf("解析恢复结果失败：%v", err)
	}

	return recoveryResult, nil
}

// QueryBlockList 分页查询区块列表
func (s *DVSSService) QueryBlockList(pageSize int, pageNum int) (*fabric.BlockQueryResult, error) {
	result, err := fabric.GetBlockListener().GetBlocksByOrg(DVSS_ORG, pageSize, pageNum)
	if err != nil {
		return nil, fmt.Errorf("查询区块列表失败：%v", err)
	}
	return result, nil
}

// 区块链操作相关方法

// RecordToBlockchain 记录操作到区块链
func (s *DVSSService) RecordToBlockchain(action string, data interface{}, timestamp string) (string, error) {
	contract := fabric.GetContract(DVSS_ORG)

	// 将数据序列化为JSON
	dataJSON, err := json.Marshal(data)
	if err != nil {
		return "", fmt.Errorf("序列化数据失败：%v", err)
	}

	result, err := contract.SubmitTransaction("RecordOperation", action, string(dataJSON), timestamp)
	if err != nil {
		return "", fmt.Errorf("记录到区块链失败：%s", fabric.ExtractErrorMessage(err))
	}

	return string(result), nil
}

// QueryTransaction 查询区块链交易
func (s *DVSSService) QueryTransaction(txID string) (map[string]interface{}, error) {
	contract := fabric.GetContract(DVSS_ORG)
	result, err := contract.EvaluateTransaction("QueryTransaction", txID)
	if err != nil {
		return nil, fmt.Errorf("查询交易失败：%s", fabric.ExtractErrorMessage(err))
	}

	var transaction map[string]interface{}
	if err := json.Unmarshal(result, &transaction); err != nil {
		return nil, fmt.Errorf("解析交易数据失败：%v", err)
	}

	return transaction, nil
}

// QueryChaincodeHistory 查询链码调用历史
func (s *DVSSService) QueryChaincodeHistory(page, size int) (map[string]interface{}, error) {
	contract := fabric.GetContract(DVSS_ORG)
	result, err := contract.EvaluateTransaction("QueryChaincodeHistory", fmt.Sprintf("%d", page), fmt.Sprintf("%d", size))
	if err != nil {
		return nil, fmt.Errorf("查询链码历史失败：%s", fabric.ExtractErrorMessage(err))
	}

	var history map[string]interface{}
	if err := json.Unmarshal(result, &history); err != nil {
		return nil, fmt.Errorf("解析历史数据失败：%v", err)
	}

	return history, nil
}

// UploadShardToBlockchain 分片上链
func (s *DVSSService) UploadShardToBlockchain(shardID, orderID, shardHash string, metadata interface{}) (string, error) {
	contract := fabric.GetContract(DVSS_ORG)

	metadataJSON, err := json.Marshal(metadata)
	if err != nil {
		return "", fmt.Errorf("序列化元数据失败：%v", err)
	}

	now := time.Now().Format(time.RFC3339)
	result, err := contract.SubmitTransaction("UploadShard", shardID, orderID, shardHash, string(metadataJSON), now)
	if err != nil {
		return "", fmt.Errorf("分片上链失败：%s", fabric.ExtractErrorMessage(err))
	}

	return string(result), nil
}

// QueryShardFromBlockchain 查询分片信息
func (s *DVSSService) QueryShardFromBlockchain(shardID string) (map[string]interface{}, error) {
	contract := fabric.GetContract(DVSS_ORG)
	result, err := contract.EvaluateTransaction("QueryShard", shardID)
	if err != nil {
		return nil, fmt.Errorf("查询分片信息失败：%s", fabric.ExtractErrorMessage(err))
	}

	var shardInfo map[string]interface{}
	if err := json.Unmarshal(result, &shardInfo); err != nil {
		return nil, fmt.Errorf("解析分片数据失败：%v", err)
	}

	return shardInfo, nil
}

// VerifyShardIntegrity 验证分片完整性
func (s *DVSSService) VerifyShardIntegrity(shardID, currentHash string) (bool, error) {
	contract := fabric.GetContract(DVSS_ORG)
	result, err := contract.EvaluateTransaction("VerifyShardIntegrity", shardID, currentHash)
	if err != nil {
		return false, fmt.Errorf("验证分片完整性失败：%s", fabric.ExtractErrorMessage(err))
	}

	return string(result) == "true", nil
}

// UploadAuditLog 审计日志上链
func (s *DVSSService) UploadAuditLog(userID, action, resourceType, resourceID string, details interface{}, timestamp string) (string, error) {
	contract := fabric.GetContract(DVSS_ORG)

	detailsJSON, err := json.Marshal(details)
	if err != nil {
		return "", fmt.Errorf("序列化详情数据失败：%v", err)
	}

	result, err := contract.SubmitTransaction("UploadAuditLog", userID, action, resourceType, resourceID, string(detailsJSON), timestamp)
	if err != nil {
		return "", fmt.Errorf("审计日志上链失败：%s", fabric.ExtractErrorMessage(err))
	}

	return string(result), nil
}

// 网络管理相关方法

// GetNetworkStatus 获取网络状态
func (s *DVSSService) GetNetworkStatus() (map[string]interface{}, error) {
	// 这里可以实现实际的网络状态检查逻辑
	// 暂时返回模拟数据
	status := map[string]interface{}{
		"network_id": "dvss-network",
		"status":     "active",
		"peers":      []string{"peer0.org1.example.com", "peer1.org1.example.com"},
		"orderers":   []string{"orderer.example.com"},
		"channels":   []string{"dvss-channel"},
		"timestamp":  time.Now().Format(time.RFC3339),
	}

	return status, nil
}

// GetPeerInfo 获取节点信息
func (s *DVSSService) GetPeerInfo() ([]map[string]interface{}, error) {
	// 这里可以实现实际的节点信息查询逻辑
	// 暂时返回模拟数据
	peers := []map[string]interface{}{
		{
			"name":      "peer0.org1.example.com",
			"org":       "org1",
			"status":    "active",
			"endpoint":  "grpc://peer0.org1.example.com:7051",
			"timestamp": time.Now().Format(time.RFC3339),
		},
		{
			"name":      "peer1.org1.example.com",
			"org":       "org1",
			"status":    "active",
			"endpoint":  "grpc://peer1.org1.example.com:7051",
			"timestamp": time.Now().Format(time.RFC3339),
		},
	}

	return peers, nil
}

// GetChannelInfo 获取通道信息
func (s *DVSSService) GetChannelInfo() ([]map[string]interface{}, error) {
	// 这里可以实现实际的通道信息查询逻辑
	// 暂时返回模拟数据
	channels := []map[string]interface{}{
		{
			"name":        "dvss-channel",
			"height":      100,
			"peers":       []string{"peer0.org1.example.com", "peer1.org1.example.com"},
			"chaincodes":  []string{"dvss-chaincode"},
			"last_block":  time.Now().Add(-time.Minute * 5).Format(time.RFC3339),
			"timestamp":   time.Now().Format(time.RFC3339),
		},
	}

	return channels, nil
}
