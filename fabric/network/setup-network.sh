#!/bin/bash

# DVSS-PPA Fabric网络设置脚本
# 自动创建通道、加入peer、部署链码

set -e

# 配置
CHANNEL_NAME="dvss-channel"
CHAINCODE_NAME="dvss-ppa"
CHAINCODE_VERSION="1.0"
CHAINCODE_PATH="../chaincode"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# 检查必要条件
check_prerequisites() {
    log "检查前置条件..."
    
    if ! docker --version > /dev/null 2>&1; then
        error "Docker未安装或未运行"
        exit 1
    fi
    
    if ! docker-compose --version > /dev/null 2>&1; then
        error "Docker Compose未安装"
        exit 1
    fi
    
    log "前置条件检查完成"
}

# 检查容器状态
check_containers() {
    log "检查Fabric容器状态..."
    
    REQUIRED_CONTAINERS=(
        "network-orderer.dvss-ppa.com-1"
        "network-peer0.org1.dvss-ppa.com-1"
        "network-peer0.org2.dvss-ppa.com-1"
        "network-cli-1"
    )
    
    for container in "${REQUIRED_CONTAINERS[@]}"; do
        if ! docker ps | grep -q "$container"; then
            error "容器 $container 未运行"
            echo "请先启动Fabric网络: docker-compose -f docker-compose-fabric.yml up -d"
            exit 1
        fi
    done
    
    log "所有必要容器都在运行"
}

# 创建通道
create_channel() {
    log "创建通道 $CHANNEL_NAME..."
    
    # 生成通道配置
    docker exec network-cli-1 configtxgen -profile DVSSChannel -outputCreateChannelTx ./channel-artifacts/${CHANNEL_NAME}.tx -channelID $CHANNEL_NAME
    
    # 创建通道
    docker exec network-cli-1 peer channel create -o orderer.dvss-ppa.com:7050 -c $CHANNEL_NAME -f ./channel-artifacts/${CHANNEL_NAME}.tx --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/dvss-ppa.com/orderers/orderer.dvss-ppa.com/msp/tlscacerts/tlsca.dvss-ppa.com-cert.pem
    
    log "通道 $CHANNEL_NAME 创建成功"
}

# Peer加入通道
join_channel() {
    log "Peer加入通道..."
    
    # Org1 Peer加入通道
    log "Org1 Peer0加入通道..."
    docker exec -e CORE_PEER_LOCALMSPID=Org1MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/peers/peer0.org1.dvss-ppa.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/users/Admin@org1.dvss-ppa.com/msp -e CORE_PEER_ADDRESS=peer0.org1.dvss-ppa.com:7051 network-cli-1 peer channel join -b ${CHANNEL_NAME}.block
    
    # Org2 Peer加入通道
    log "Org2 Peer0加入通道..."
    docker exec -e CORE_PEER_LOCALMSPID=Org2MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.dvss-ppa.com/peers/peer0.org2.dvss-ppa.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.dvss-ppa.com/users/Admin@org2.dvss-ppa.com/msp -e CORE_PEER_ADDRESS=peer0.org2.dvss-ppa.com:9051 network-cli-1 peer channel join -b ${CHANNEL_NAME}.block
    
    log "所有Peer都已加入通道"
}

# 更新锚点Peer
update_anchor_peers() {
    log "更新锚点Peer..."
    
    # 生成Org1锚点Peer配置
    docker exec network-cli-1 configtxgen -profile DVSSChannel -outputAnchorPeersUpdate ./channel-artifacts/Org1MSPanchors.tx -channelID $CHANNEL_NAME -asOrg Org1MSP
    
    # 生成Org2锚点Peer配置
    docker exec network-cli-1 configtxgen -profile DVSSChannel -outputAnchorPeersUpdate ./channel-artifacts/Org2MSPanchors.tx -channelID $CHANNEL_NAME -asOrg Org2MSP
    
    # 更新Org1锚点Peer
    docker exec -e CORE_PEER_LOCALMSPID=Org1MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/peers/peer0.org1.dvss-ppa.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/users/Admin@org1.dvss-ppa.com/msp -e CORE_PEER_ADDRESS=peer0.org1.dvss-ppa.com:7051 network-cli-1 peer channel update -o orderer.dvss-ppa.com:7050 -c $CHANNEL_NAME -f ./channel-artifacts/Org1MSPanchors.tx --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/dvss-ppa.com/orderers/orderer.dvss-ppa.com/msp/tlscacerts/tlsca.dvss-ppa.com-cert.pem
    
    # 更新Org2锚点Peer
    docker exec -e CORE_PEER_LOCALMSPID=Org2MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.dvss-ppa.com/peers/peer0.org2.dvss-ppa.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.dvss-ppa.com/users/Admin@org2.dvss-ppa.com/msp -e CORE_PEER_ADDRESS=peer0.org2.dvss-ppa.com:9051 network-cli-1 peer channel update -o orderer.dvss-ppa.com:7050 -c $CHANNEL_NAME -f ./channel-artifacts/Org2MSPanchors.tx --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/dvss-ppa.com/orderers/orderer.dvss-ppa.com/msp/tlscacerts/tlsca.dvss-ppa.com-cert.pem
    
    log "锚点Peer更新完成"
}

# 部署链码
deploy_chaincode() {
    log "部署链码 $CHAINCODE_NAME..."
    
    if [ ! -d "$CHAINCODE_PATH" ]; then
        warning "链码目录 $CHAINCODE_PATH 不存在，跳过链码部署"
        return
    fi
    
    # 打包链码 (这里假设是Go链码)
    log "打包链码..."
    docker exec network-cli-1 peer lifecycle chaincode package ${CHAINCODE_NAME}.tar.gz --path ${CHAINCODE_PATH} --lang golang --label ${CHAINCODE_NAME}_${CHAINCODE_VERSION}
    
    # 在Org1上安装链码
    log "在Org1上安装链码..."
    docker exec -e CORE_PEER_LOCALMSPID=Org1MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/peers/peer0.org1.dvss-ppa.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/users/Admin@org1.dvss-ppa.com/msp -e CORE_PEER_ADDRESS=peer0.org1.dvss-ppa.com:7051 network-cli-1 peer lifecycle chaincode install ${CHAINCODE_NAME}.tar.gz
    
    # 在Org2上安装链码
    log "在Org2上安装链码..."
    docker exec -e CORE_PEER_LOCALMSPID=Org2MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.dvss-ppa.com/peers/peer0.org2.dvss-ppa.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.dvss-ppa.com/users/Admin@org2.dvss-ppa.com/msp -e CORE_PEER_ADDRESS=peer0.org2.dvss-ppa.com:9051 network-cli-1 peer lifecycle chaincode install ${CHAINCODE_NAME}.tar.gz
    
    # 获取包ID
    PACKAGE_ID=$(docker exec -e CORE_PEER_LOCALMSPID=Org1MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/peers/peer0.org1.dvss-ppa.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/users/Admin@org1.dvss-ppa.com/msp -e CORE_PEER_ADDRESS=peer0.org1.dvss-ppa.com:7051 network-cli-1 peer lifecycle chaincode queryinstalled --output json | jq -r ".installed_chaincodes[0].package_id")
    
    log "链码包ID: $PACKAGE_ID"
    
    # Org1批准链码定义
    log "Org1批准链码定义..."
    docker exec -e CORE_PEER_LOCALMSPID=Org1MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/peers/peer0.org1.dvss-ppa.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/users/Admin@org1.dvss-ppa.com/msp -e CORE_PEER_ADDRESS=peer0.org1.dvss-ppa.com:7051 network-cli-1 peer lifecycle chaincode approveformyorg -o orderer.dvss-ppa.com:7050 --channelID $CHANNEL_NAME --name $CHAINCODE_NAME --version $CHAINCODE_VERSION --package-id $PACKAGE_ID --sequence 1 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/dvss-ppa.com/orderers/orderer.dvss-ppa.com/msp/tlscacerts/tlsca.dvss-ppa.com-cert.pem
    
    # Org2批准链码定义
    log "Org2批准链码定义..."
    docker exec -e CORE_PEER_LOCALMSPID=Org2MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.dvss-ppa.com/peers/peer0.org2.dvss-ppa.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.dvss-ppa.com/users/Admin@org2.dvss-ppa.com/msp -e CORE_PEER_ADDRESS=peer0.org2.dvss-ppa.com:9051 network-cli-1 peer lifecycle chaincode approveformyorg -o orderer.dvss-ppa.com:7050 --channelID $CHANNEL_NAME --name $CHAINCODE_NAME --version $CHAINCODE_VERSION --package-id $PACKAGE_ID --sequence 1 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/dvss-ppa.com/orderers/orderer.dvss-ppa.com/msp/tlscacerts/tlsca.dvss-ppa.com-cert.pem
    
    # 提交链码定义
    log "提交链码定义..."
    docker exec -e CORE_PEER_LOCALMSPID=Org1MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/peers/peer0.org1.dvss-ppa.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/users/Admin@org1.dvss-ppa.com/msp -e CORE_PEER_ADDRESS=peer0.org1.dvss-ppa.com:7051 network-cli-1 peer lifecycle chaincode commit -o orderer.dvss-ppa.com:7050 --channelID $CHANNEL_NAME --name $CHAINCODE_NAME --version $CHAINCODE_VERSION --sequence 1 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/dvss-ppa.com/orderers/orderer.dvss-ppa.com/msp/tlscacerts/tlsca.dvss-ppa.com-cert.pem --peerAddresses peer0.org1.dvss-ppa.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/peers/peer0.org1.dvss-ppa.com/tls/ca.crt --peerAddresses peer0.org2.dvss-ppa.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.dvss-ppa.com/peers/peer0.org2.dvss-ppa.com/tls/ca.crt
    
    log "链码部署完成"
}

# 验证部署
verify_deployment() {
    log "验证部署..."
    
    # 查询已提交的链码
    docker exec -e CORE_PEER_LOCALMSPID=Org1MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/peers/peer0.org1.dvss-ppa.com/tls/ca.crt -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.dvss-ppa.com/users/Admin@org1.dvss-ppa.com/msp -e CORE_PEER_ADDRESS=peer0.org1.dvss-ppa.com:7051 network-cli-1 peer lifecycle chaincode querycommitted --channelID $CHANNEL_NAME
    
    log "部署验证完成"
}

# 主函数
main() {
    log "开始设置DVSS-PPA Fabric网络..."
    
    check_prerequisites
    check_containers
    
    # 如果通道不存在则创建
    if ! docker exec network-cli-1 peer channel list | grep -q "$CHANNEL_NAME"; then
        create_channel
        join_channel
        update_anchor_peers
    else
        log "通道 $CHANNEL_NAME 已存在，跳过创建"
    fi
    
    # 部署链码（如果链码目录存在）
    if [ -d "$CHAINCODE_PATH" ]; then
        deploy_chaincode
        verify_deployment
    else
        warning "链码目录不存在，跳过链码部署"
    fi
    
    log "Fabric网络设置完成！"
    log "通道名称: $CHANNEL_NAME"
    log "链码名称: $CHAINCODE_NAME"
    log "现在可以启动Go后端应用了"
}

# 脚本参数处理
case "${1:-}" in
    "clean")
        log "清理现有网络..."
        docker exec network-cli-1 rm -f ${CHANNEL_NAME}.block ${CHAINCODE_NAME}.tar.gz || true
        log "清理完成"
        ;;
    "channel-only")
        log "仅创建通道..."
        check_prerequisites
        check_containers
        create_channel
        join_channel
        update_anchor_peers
        log "通道创建完成"
        ;;
    *)
        main
        ;;
esac
