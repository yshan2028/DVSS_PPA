-- 初始化 DVSS MySQL 数据库
-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS dvss_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dvss_db;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role_id VARCHAR(36),
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_users_username (username),
    INDEX idx_users_email (email),
    INDEX idx_users_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSON,
    field_access JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_roles_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    shipping_address TEXT,
    billing_address TEXT,
    item_list JSON,
    payment_info JSON,
    total_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    discount DECIMAL(10,2),
    sensitivity_score DECIMAL(5,4),
    sensitivity_level VARCHAR(20) DEFAULT 'medium',
    data_source VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_orders_order_id (order_id),
    INDEX idx_orders_user_id (user_id),
    INDEX idx_orders_sensitivity (sensitivity_score),
    INDEX idx_orders_status (status),
    INDEX idx_orders_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 分片索引表
CREATE TABLE IF NOT EXISTS shard_index (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    shard_id VARCHAR(100) UNIQUE NOT NULL,
    order_id VARCHAR(36),
    shard_sequence INTEGER,
    total_shards INTEGER,
    threshold_k INTEGER,
    node_ip VARCHAR(50),
    storage_path TEXT,
    checksum VARCHAR(64),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_shard_index_order_id (order_id),
    INDEX idx_shard_index_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 敏感度配置表
CREATE TABLE IF NOT EXISTS sensitivity_config (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    field_name VARCHAR(100) NOT NULL,
    weight DECIMAL(3,2) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sensitivity_field_name (field_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 系统负载记录表
CREATE TABLE IF NOT EXISTS system_load (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_io DECIMAL(5,2),
    network_io DECIMAL(5,2),
    active_connections INTEGER,
    load_score DECIMAL(5,4),
    threshold_k INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_system_load_recorded_at (recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 审计日志表
CREATE TABLE IF NOT EXISTS audit_log (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    blockchain_tx_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_log_user_id (user_id),
    INDEX idx_audit_log_action (action),
    INDEX idx_audit_log_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 区块链交易记录表
CREATE TABLE IF NOT EXISTS blockchain_transactions (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    tx_id VARCHAR(100) UNIQUE NOT NULL,
    channel_name VARCHAR(50),
    chaincode_name VARCHAR(50),
    function_name VARCHAR(50),
    args JSON,
    response JSON,
    block_number BIGINT,
    tx_timestamp TIMESTAMP,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_blockchain_tx_id (tx_id),
    INDEX idx_blockchain_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 加密日志表
CREATE TABLE IF NOT EXISTS encryption_log (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_id VARCHAR(36),
    user_id VARCHAR(36),
    action VARCHAR(50) NOT NULL,
    algorithm VARCHAR(50),
    key_id VARCHAR(100),
    shard_count INTEGER,
    threshold_k INTEGER,
    processing_time INTEGER,
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_encryption_log_order_id (order_id),
    INDEX idx_encryption_log_user_id (user_id),
    INDEX idx_encryption_log_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 解密日志表
CREATE TABLE IF NOT EXISTS decryption_log (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_id VARCHAR(36),
    user_id VARCHAR(36),
    action VARCHAR(50) NOT NULL,
    algorithm VARCHAR(50),
    shard_count INTEGER,
    threshold_k INTEGER,
    processing_time INTEGER,
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_decryption_log_order_id (order_id),
    INDEX idx_decryption_log_user_id (user_id),
    INDEX idx_decryption_log_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 查询日志表
CREATE TABLE IF NOT EXISTS query_log (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36),
    query_type VARCHAR(50),
    query_params JSON,
    result_count INTEGER,
    processing_time INTEGER,
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_query_log_user_id (user_id),
    INDEX idx_query_log_type (query_type),
    INDEX idx_query_log_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入默认角色
INSERT INTO roles (id, name, description, permissions, field_access) VALUES
(UUID(), 'admin', '系统管理员', 
 JSON_OBJECT('all', true), 
 JSON_OBJECT('all_fields', true)),
(UUID(), 'analyst', '数据分析师', 
 JSON_OBJECT('read', true, 'analyze', true), 
 JSON_OBJECT('allowed_fields', JSON_ARRAY('order_id', 'item_list', 'total_amount', 'timestamp'), 'denied_fields', JSON_ARRAY('customer_name', 'phone', 'email', 'address', 'payment_info'))),
(UUID(), 'viewer', '查看者', 
 JSON_OBJECT('read', true), 
 JSON_OBJECT('allowed_fields', JSON_ARRAY('order_id', 'item_list', 'timestamp'), 'denied_fields', JSON_ARRAY('customer_name', 'phone', 'email', 'address', 'payment_info', 'total_amount'))),
(UUID(), 'finance', '财务人员', 
 JSON_OBJECT('read', true, 'financial', true), 
 JSON_OBJECT('allowed_fields', JSON_ARRAY('order_id', 'total_amount', 'tax_amount', 'payment_method', 'timestamp'), 'denied_fields', JSON_ARRAY('customer_name', 'phone', 'email', 'address', 'payment_info')));

-- 插入默认用户（密码都是 admin123）
INSERT INTO users (id, username, email, password_hash, full_name, role_id, department) 
SELECT 
    UUID(),
    'admin',
    'admin@dvss.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkCR9g8wD8Y7W9e',
    '系统管理员',
    r.id,
    'IT'
FROM roles r WHERE r.name = 'admin' LIMIT 1;

INSERT INTO users (id, username, email, password_hash, full_name, role_id, department) 
SELECT 
    UUID(),
    'analyst',
    'analyst@dvss.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkCR9g8wD8Y7W9e',
    '数据分析师',
    r.id,
    'Analytics'
FROM roles r WHERE r.name = 'analyst' LIMIT 1;

INSERT INTO users (id, username, email, password_hash, full_name, role_id, department) 
SELECT 
    UUID(),
    'viewer',
    'viewer@dvss.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkCR9g8wD8Y7W9e',
    '查看者',
    r.id,
    'Business'
FROM roles r WHERE r.name = 'viewer' LIMIT 1;

INSERT INTO users (id, username, email, password_hash, full_name, role_id, department) 
SELECT 
    UUID(),
    'finance',
    'finance@dvss.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkCR9g8wD8Y7W9e',
    '财务人员',
    r.id,
    'Finance'
FROM roles r WHERE r.name = 'finance' LIMIT 1;

-- 插入敏感度配置
INSERT INTO sensitivity_configs (field_name, weight, category, description) VALUES
('order_id', 0.1, 'business', '订单ID'),
('user_id', 0.8, 'pii', '用户ID'),
('customer_name', 0.9, 'pii', '客户姓名'),
('phone', 0.9, 'pii', '电话号码'),
('email', 0.8, 'pii', '电子邮件'),
('address', 0.9, 'location', '地址'),
('shipping_address', 0.9, 'location', '收货地址'),
('billing_address', 0.8, 'location', '账单地址'),
('payment_info', 1.0, 'financial', '支付信息'),
('total_amount', 0.6, 'financial', '总金额'),
('tax_amount', 0.4, 'financial', '税额'),
('item_list', 0.3, 'business', '商品列表'),
('timestamp', 0.1, 'business', '时间戳');

-- 插入示例订单数据
INSERT INTO original_orders (order_id, user_id, name, email, phone, address, item_list, payment_info, total_amount, tax_amount, sensitivity_score, status) VALUES
('ALI001', 'user001', '张三', 'zhangsan@example.com', '13800138001', '北京市朝阳区xxx路123号', 
 JSON_ARRAY(JSON_OBJECT('name', '商品A', 'quantity', 2, 'price', 100)), 
 JSON_OBJECT('method', 'credit_card', 'last4', '1234'), 
 220.00, 20.00, 0.75, 'completed'),
('WEEE001', 'user002', '李四', 'lisi@example.com', '13800138002', '上海市浦东新区yyy街456号', 
 JSON_ARRAY(JSON_OBJECT('name', '商品B', 'quantity', 1, 'price', 150)), 
 JSON_OBJECT('method', 'alipay'), 
 165.00, 15.00, 0.72, 'completed'),
('ALI002', 'user003', '王五', 'wangwu@example.com', '13800138003', '广州市天河区zzz大道789号', 
 JSON_ARRAY(JSON_OBJECT('name', '商品C', 'quantity', 3, 'price', 80)), 
 JSON_OBJECT('method', 'wechat_pay'), 
 264.00, 24.00, 0.68, 'completed');

-- 提交事务
COMMIT;
