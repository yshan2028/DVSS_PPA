package fabric

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/hyperledger/fabric-gateway/pkg/client"
	"github.com/hyperledger/fabric-protos-go-apiv2/common"
	bolt "go.etcd.io/bbolt"
)

const (
	_BlocksBucket = "blocks"        // 存储区块数据
	_LatestBucket = "latest_blocks" // 存储最新区块信息

	_RetryInterval = 30 * time.Second // 重试间隔时间
)

// BlockData 区块数据结构
type BlockData struct {
	BlockNum  uint64    `json:"block_num"`
	BlockHash string    `json:"block_hash"`
	DataHash  string    `json:"data_hash"`
	PrevHash  string    `json:"prev_hash"`
	TxCount   int       `json:"tx_count"`
	SaveTime  time.Time `json:"save_time"`
}

// LatestBlock 最新区块信息
type LatestBlock struct {
	BlockNum uint64    `json:"block_num"`
	SaveTime time.Time `json:"save_time"`
}

// BlockQueryResult 区块查询结果
type BlockQueryResult struct {
	Blocks   []*BlockData `json:"blocks"`
	Total    int          `json:"total"`
	PageSize int          `json:"page_size"`
	PageNum  int          `json:"page_num"`
	HasMore  bool         `json:"has_more"`
}

// blockEventListener 区块事件监听器
type blockEventListener struct {
	sync.RWMutex
	networks map[string]*client.Network
	ctx      context.Context
	cancel   context.CancelFunc
	dataDir  string
	db       *bolt.DB
}

var (
	listener     *blockEventListener
	listenerOnce sync.Once
	initErr      error
)

// initBlockListener 初始化区块监听器
func initBlockListener(dataDir string) error {
	var initErr error
	listenerOnce.Do(func() {
		// 创建数据目录
		if err := os.MkdirAll(dataDir, 0755); err != nil {
			initErr = fmt.Errorf("创建数据目录失败：%w", err)
			return
		}

		// 打开BBolt数据库
		dbPath := filepath.Join(dataDir, "blocks.db")
		db, err := bolt.Open(dbPath, 0600, &bolt.Options{Timeout: 10 * time.Second})
		if err != nil {
			initErr = fmt.Errorf("打开数据库失败：%w", err)
			return
		}

		// 创建Buckets
		if err := db.Update(func(tx *bolt.Tx) error {
			if _, err := tx.CreateBucketIfNotExists([]byte(_BlocksBucket)); err != nil {
				return fmt.Errorf("创建blocks bucket失败: %w", err)
			}
			if _, err := tx.CreateBucketIfNotExists([]byte(_LatestBucket)); err != nil {
				return fmt.Errorf("创建latest_blocks bucket失败: %w", err)
			}
			return nil
		}); err != nil {
			db.Close()
			initErr = fmt.Errorf("初始化数据库失败：%w", err)
			return
		}

		ctx, cancel := context.WithCancel(context.Background())
		listener = &blockEventListener{
			networks: make(map[string]*client.Network),
			ctx:      ctx,
			cancel:   cancel,
			dataDir:  dataDir,
			db:       db,
		}
	})

	return initErr
}

// addNetwork 添加网络
func addNetwork(orgName string, network *client.Network) error {
	if listener == nil {
		return fmt.Errorf("区块监听器未初始化")
	}

	listener.Lock()
	defer listener.Unlock()

	listener.networks[orgName] = network
	go listener.startBlockListener(orgName)

	return nil
}

// GetBlockListener 获取区块监听器实例
func GetBlockListener() *blockEventListener {
	return listener
}

// startBlockListener 启动区块监听
func (l *blockEventListener) startBlockListener(orgName string) {
	for {
		select {
		case <-l.ctx.Done():
			return
		default:
			l.listenBlocks(orgName)
			time.Sleep(_RetryInterval)
		}
	}
}

// listenBlocks 监听区块事件
func (l *blockEventListener) listenBlocks(orgName string) {
	l.RLock()
	network := l.networks[orgName]
	l.RUnlock()

	if network == nil {
		fmt.Printf("组织[%s]的网络未找到\n", orgName)
		return
	}

	// 获取区块事件通道
	events, err := network.BlockEvents(l.ctx, client.WithStartBlock(0))
	if err != nil {
		fmt.Printf("获取组织[%s]的区块事件失败：%v\n", orgName, err)
		return
	}

	fmt.Printf("开始监听组织[%s]的区块事件\n", orgName)

	for {
		select {
		case <-l.ctx.Done():
			return
		case blockEvent, ok := <-events:
			if !ok {
				fmt.Printf("组织[%s]的区块事件通道已关闭\n", orgName)
				return
			}
			l.saveBlock(orgName, blockEvent)
		}
	}
}

// saveBlock 保存区块数据
func (l *blockEventListener) saveBlock(orgName string, block *common.Block) {
	blockNum := block.Header.Number
	blockHash := fmt.Sprintf("%x", sha256.Sum256([]byte(fmt.Sprintf("%v", block.Header))))
	dataHash := fmt.Sprintf("%x", block.Header.DataHash)
	prevHash := fmt.Sprintf("%x", block.Header.PreviousHash)
	txCount := len(block.Data.Data)

	blockData := BlockData{
		BlockNum:  blockNum,
		BlockHash: blockHash,
		DataHash:  dataHash,
		PrevHash:  prevHash,
		TxCount:   txCount,
		SaveTime:  time.Now(),
	}

	err := l.db.Update(func(tx *bolt.Tx) error {
		blocksBucket := tx.Bucket([]byte(_BlocksBucket))
		if blocksBucket == nil {
			return fmt.Errorf("blocks bucket不存在")
		}

		// 保存区块数据
		blockKey := fmt.Sprintf("%s_%d", orgName, blockNum)
		blockJSON, err := json.Marshal(blockData)
		if err != nil {
			return fmt.Errorf("序列化区块数据失败：%v", err)
		}
		if err := blocksBucket.Put([]byte(blockKey), blockJSON); err != nil {
			return fmt.Errorf("保存区块数据失败：%v", err)
		}

		// 更新最新区块信息
		_LatestBucket := tx.Bucket([]byte(_LatestBucket))
		latestBlock := LatestBlock{
			BlockNum: blockNum,
			SaveTime: time.Now(),
		}
		latestJSON, err := json.Marshal(latestBlock)
		if err != nil {
			return fmt.Errorf("序列化最新区块信息失败：%v", err)
		}
		if err := _LatestBucket.Put([]byte(orgName), latestJSON); err != nil {
			return fmt.Errorf("保存最新区块信息失败：%v", err)
		}

		return nil
	})

	if err != nil {
		fmt.Printf("保存区块失败：%v\n", err)
		return
	}

	fmt.Printf("已保存组织[%s]的区块[%d]\n", orgName, blockNum)
}

// GetBlocksByOrg 分页查询组织的区块列表（按区块号降序）
func (l *blockEventListener) GetBlocksByOrg(orgName string, pageSize, pageNum int) (*BlockQueryResult, error) {
	if pageSize <= 0 {
		pageSize = 10
	}
	if pageNum <= 0 {
		pageNum = 1
	}

	var result BlockQueryResult
	result.PageSize = pageSize
	result.PageNum = pageNum

	err := l.db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(_BlocksBucket))
		if b == nil {
			return fmt.Errorf("blocks bucket不存在")
		}

		// 获取组织的最新区块号
		_LatestBucket := tx.Bucket([]byte(_LatestBucket))
		if _LatestBucket == nil {
			return fmt.Errorf("latest_blocks bucket不存在")
		}

		var latestBlock LatestBlock
		latestData := _LatestBucket.Get([]byte(orgName))
		if latestData == nil {
			return fmt.Errorf("组织数据不存在")
		}
		if err := json.Unmarshal(latestData, &latestBlock); err != nil {
			return err
		}

		// 计算总记录数和分页参数
		result.Total = int(latestBlock.BlockNum) + 1 // 从0开始，所以要加1

		// 计算起始和结束区块号
		startIdx := result.Total - (pageNum * pageSize)
		endIdx := startIdx + pageSize
		if startIdx < 0 {
			startIdx = 0
		}
		if endIdx > result.Total {
			endIdx = result.Total
		}

		// 判断是否还有更多数据
		result.HasMore = startIdx > 0

		// 收集区块数据
		blocks := make([]*BlockData, 0, pageSize)
		for i := endIdx - 1; i >= startIdx; i-- {
			blockKey := fmt.Sprintf("%s_%d", orgName, i)
			data := b.Get([]byte(blockKey))
			if data != nil {
				var block BlockData
				if err := json.Unmarshal(data, &block); err != nil {
					return err
				}
				blocks = append(blocks, &block)
			}
		}
		result.Blocks = blocks

		return nil
	})

	if err != nil {
		return nil, err
	}

	return &result, nil
}
