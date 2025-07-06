-- 初始化 DVSS 数据库
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role_id UUID,
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB,
    field_access JSONB, -- 字段级别权限
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    shipping_address TEXT,
    billing_address TEXT,
    item_list JSONB,
    payment_info JSONB,
    total_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    discount DECIMAL(10,2),
    sensitivity_score DECIMAL(5,4),
    data_source VARCHAR(50), -- alibaba, weee
    status VARCHAR(20) DEFAULT 'active', -- active, deleted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 分片索引表
CREATE TABLE IF NOT EXISTS shard_index (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shard_id VARCHAR(100) UNIQUE NOT NULL,
    order_id UUID REFERENCES orders(id),
    shard_sequence INTEGER, -- 分片序号
    total_shards INTEGER,   -- 总分片数
    threshold_k INTEGER,    -- 重构阈值
    node_ip VARCHAR(50),
    storage_path TEXT,
    checksum VARCHAR(64),   -- SHA256
    status VARCHAR(20) DEFAULT 'active', -- active, deleted, corrupted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 敏感度配置表
CREATE TABLE IF NOT EXISTS sensitivity_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_name VARCHAR(100) NOT NULL,
    weight DECIMAL(3,2) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 系统负载记录表
CREATE TABLE IF NOT EXISTS system_load (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_io DECIMAL(5,2),
    network_io DECIMAL(5,2),
    active_connections INTEGER,
    load_score DECIMAL(5,4),
    threshold_k INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 审计日志表
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL, -- CREATE, READ, UPDATE, DELETE, ENCRYPT, DECRYPT
    resource_type VARCHAR(50), -- ORDER, SHARD, USER
    resource_id VARCHAR(100),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    blockchain_tx_id VARCHAR(100), -- 区块链交易ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 区块链交易记录表
CREATE TABLE IF NOT EXISTS blockchain_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tx_id VARCHAR(100) UNIQUE NOT NULL,
    channel_name VARCHAR(50),
    chaincode_name VARCHAR(50),
    function_name VARCHAR(50),
    args JSONB,
    response JSONB,
    block_number BIGINT,
    tx_timestamp TIMESTAMP,
    status VARCHAR(20), -- success, failed, pending
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_sensitivity ON orders(sensitivity_score);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_shard_index_order_id ON shard_index(order_id);
CREATE INDEX IF NOT EXISTS idx_shard_index_status ON shard_index(status);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_blockchain_tx_id ON blockchain_transactions(tx_id);

-- 插入默认角色
INSERT INTO roles (id, name, description, permissions, field_access) VALUES
(uuid_generate_v4(), 'admin', '系统管理员', 
 '{"all": true}', 
 '{"all_fields": true}'),
(uuid_generate_v4(), 'analyst', '数据分析师', 
 '{"read": true, "analyze": true}', 
 '{"allowed_fields": ["order_id", "item_list", "total_amount", "timestamp"], "denied_fields": ["name", "phone", "email", "address", "payment_info"]}'),
(uuid_generate_v4(), 'viewer', '查看者', 
 '{"read": true}', 
 '{"allowed_fields": ["order_id", "item_list", "timestamp"], "denied_fields": ["name", "phone", "email", "address", "payment_info", "total_amount"]}'),
(uuid_generate_v4(), 'finance', '财务人员', 
 '{"read": true, "financial": true}', 
 '{"allowed_fields": ["order_id", "total_amount", "tax_amount", "payment_method", "timestamp"], "denied_fields": ["name", "phone", "email", "address", "payment_info"]}');

-- 插入默认用户
INSERT INTO users (id, username, email, password_hash, full_name, role_id, department) 
SELECT 
    uuid_generate_v4(),
    'admin',
    'admin@dvss.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkCR9g8wD8Y7W9e', -- password: admin123
    '系统管理员',
    r.id,
    'IT'
FROM roles r WHERE r.name = 'admin';

INSERT INTO users (id, username, email, password_hash, full_name, role_id, department) 
SELECT 
    uuid_generate_v4(),
    'analyst',
    'analyst@dvss.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkCR9g8wD8Y7W9e', -- password: analyst123
    '数据分析师',
    r.id,
    'Analytics'
FROM roles r WHERE r.name = 'analyst';

INSERT INTO users (id, username, email, password_hash, full_name, role_id, department) 
SELECT 
    uuid_generate_v4(),
    'viewer',
    'viewer@dvss.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkCR9g8wD8Y7W9e', -- password: viewer123
    '查看者',
    r.id,
    'Business'
FROM roles r WHERE r.name = 'viewer';

INSERT INTO users (id, username, email, password_hash, full_name, role_id, department) 
SELECT 
    uuid_generate_v4(),
    'finance',
    'finance@dvss.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkCR9g8wD8Y7W9e', -- password: finance123
    '财务人员',
    r.id,
    'Finance'
FROM roles r WHERE r.name = 'finance';

-- 插入敏感度配置
INSERT INTO sensitivity_config (field_name, weight, category, description) VALUES
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
INSERT INTO orders (order_id, user_id, customer_name, email, phone, address, item_list, payment_info, total_amount, tax_amount, sensitivity_score, data_source) VALUES
('ALI001', 'user001', '张三', 'zhangsan@example.com', '13800138001', '北京市朝阳区xxx路123号', 
 '[{"name": "商品A", "quantity": 2, "price": 100}]', 
 '{"method": "credit_card", "last4": "1234"}', 
 220.00, 20.00, 0.75, 'alibaba'),
('WEEE001', 'user002', '李四', 'lisi@example.com', '13800138002', '上海市浦东新区yyy街456号', 
 '[{"name": "商品B", "quantity": 1, "price": 150}]', 
 '{"method": "alipay"}', 
 165.00, 15.00, 0.72, 'weee'),
('ALI002', 'user003', '王五', 'wangwu@example.com', '13800138003', '广州市天河区zzz大道789号', 
 '[{"name": "商品C", "quantity": 3, "price": 80}]', 
 '{"method": "wechat_pay"}', 
 264.00, 24.00, 0.68, 'alibaba');
