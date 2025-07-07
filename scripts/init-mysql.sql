-- DVSS MySQL 数据库初始化脚本
-- 说明：表结构由SQLAlchemy ORM自动创建，此脚本仅负责插入演示数据

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 等待SQLAlchemy创建表结构后，插入演示数据

-- 插入演示角色
INSERT IGNORE INTO roles (name, description, is_active) VALUES
('admin', '系统管理员，拥有所有权限', TRUE),
('seller', '卖家，可查看基本订单信息', TRUE),
('payment', '支付服务商，可查看支付相关信息', TRUE),
('logistics', '物流，可查看配送相关信息', TRUE),
('auditor', '审计员，可查看审计相关信息', TRUE),
('platform', '平台管理员，拥有管理权限', TRUE);

-- 插入订单字段定义（与ORM模型一致）
INSERT IGNORE INTO order_fields (field_name, field_type, sensitivity_level, sensitivity_score, category, description, is_required, is_active) VALUES
('order_id', 'String', 'low', 0.1, 'basic', '订单唯一标识', TRUE, TRUE),
('user_id', 'String', 'medium', 0.5, 'basic', '用户ID', TRUE, TRUE),
('name', 'String', 'high', 0.8, 'personal', '客户真实姓名', FALSE, TRUE),
('phone', 'String', 'high', 0.8, 'personal', '客户联系电话', FALSE, TRUE),
('email', 'String', 'medium', 0.6, 'personal', '客户电子邮箱', FALSE, TRUE),
('address', 'Text', 'high', 0.8, 'location', '客户详细地址', FALSE, TRUE),
('shipping_address', 'Text', 'medium', 0.6, 'location', '商品配送地址', FALSE, TRUE),
('billing_address', 'Text', 'medium', 0.6, 'location', '账单地址', FALSE, TRUE),
('zip_code', 'String', 'low', 0.3, 'location', '邮政编码', FALSE, TRUE),
('city', 'String', 'low', 0.3, 'location', '城市', FALSE, TRUE),
('state', 'String', 'low', 0.3, 'location', '州/省', FALSE, TRUE),
('country', 'String', 'low', 0.2, 'location', '国家', FALSE, TRUE),
('payment_info', 'Text', 'critical', 1.0, 'payment', '完整支付信息', FALSE, TRUE),
('credit_card', 'String', 'critical', 1.0, 'payment', '信用卡号码', FALSE, TRUE),
('bank_account', 'String', 'critical', 1.0, 'payment', '银行账户', FALSE, TRUE),
('payment_method', 'String', 'low', 0.3, 'payment', '支付方式类型', FALSE, TRUE),
('item_list', 'Text', 'low', 0.2, 'business', '订单商品清单(JSON)', FALSE, TRUE),
('item_name', 'String', 'low', 0.2, 'business', '主要商品名称', FALSE, TRUE),
('item_price', 'Decimal', 'low', 0.3, 'business', '商品价格', FALSE, TRUE),
('quantity', 'Integer', 'low', 0.2, 'business', '商品数量', FALSE, TRUE),
('total_amount', 'Decimal', 'medium', 0.5, 'business', '订单总金额', FALSE, TRUE),
('tax_amount', 'Decimal', 'low', 0.4, 'business', '税额', FALSE, TRUE),
('shipping_cost', 'Decimal', 'low', 0.3, 'business', '运费', FALSE, TRUE),
('discount', 'Decimal', 'low', 0.3, 'business', '折扣', FALSE, TRUE),
('status', 'String', 'low', 0.2, 'system', '订单状态', TRUE, TRUE),
('created_at', 'DateTime', 'low', 0.1, 'system', '订单创建时间', TRUE, TRUE);

-- 插入角色字段权限 (admin - 可以访问所有字段)
INSERT IGNORE INTO role_field_permissions (role_id, field_id, can_view, can_decrypt)
SELECT r.id, f.id, TRUE, TRUE
FROM roles r, order_fields f 
WHERE r.name = 'admin';

-- seller角色权限 (可查看基本商业信息，不能查看敏感支付和身份信息)
INSERT IGNORE INTO role_field_permissions (role_id, field_id, can_view, can_decrypt)
SELECT r.id, f.id, TRUE, FALSE
FROM roles r, order_fields f 
WHERE r.name = 'seller' 
AND f.field_name IN ('order_id', 'user_id', 'name', 'phone', 'shipping_address', 'city', 'state', 'country', 'payment_method', 'item_list', 'item_name', 'item_price', 'quantity', 'total_amount', 'tax_amount', 'shipping_cost', 'discount', 'status', 'created_at');

-- payment角色权限 (只能查看支付相关信息)
INSERT IGNORE INTO role_field_permissions (role_id, field_id, can_view, can_decrypt)
SELECT r.id, f.id, TRUE, TRUE
FROM roles r, order_fields f 
WHERE r.name = 'payment' 
AND f.field_name IN ('order_id', 'user_id', 'payment_info', 'credit_card', 'bank_account', 'payment_method', 'total_amount', 'tax_amount', 'status', 'created_at');

-- logistics角色权限 (只能查看配送相关信息)
INSERT IGNORE INTO role_field_permissions (role_id, field_id, can_view, can_decrypt)
SELECT r.id, f.id, TRUE, FALSE
FROM roles r, order_fields f 
WHERE r.name = 'logistics' 
AND f.field_name IN ('order_id', 'user_id', 'name', 'phone', 'address', 'shipping_address', 'zip_code', 'city', 'state', 'country', 'item_list', 'item_name', 'quantity', 'shipping_cost', 'status', 'created_at');

-- auditor角色权限 (可查看审计所需的关键信息)
INSERT IGNORE INTO role_field_permissions (role_id, field_id, can_view, can_decrypt)
SELECT r.id, f.id, TRUE, FALSE
FROM roles r, order_fields f 
WHERE r.name = 'auditor' 
AND f.field_name IN ('order_id', 'user_id', 'name', 'payment_method', 'total_amount', 'tax_amount', 'status', 'created_at');

-- platform角色权限 (可查看大部分信息，除了最敏感的支付详情)
INSERT IGNORE INTO role_field_permissions (role_id, field_id, can_view, can_decrypt)
SELECT r.id, f.id, TRUE, FALSE
FROM roles r, order_fields f 
WHERE r.name = 'platform' 
AND f.field_name IN ('order_id', 'user_id', 'name', 'phone', 'email', 'address', 'shipping_address', 'billing_address', 'zip_code', 'city', 'state', 'country', 'payment_method', 'item_list', 'item_name', 'item_price', 'quantity', 'total_amount', 'tax_amount', 'shipping_cost', 'discount', 'status', 'created_at');

-- 插入演示用户 (密码都是 123456 的bcrypt哈希值)
INSERT IGNORE INTO users (username, email, password_hash, full_name, department, role_id) 
SELECT 'admin', 'admin@dvss.com', '$2b$12$K7gNU3sAFUvj.nIMKIBaXO7kB9PK.r6w4zR4Y8H.j7oZ8K.L5P8QC', '系统管理员', 'IT', r.id
FROM roles r WHERE r.name = 'admin';

INSERT IGNORE INTO users (username, email, password_hash, full_name, department, role_id) 
SELECT 'seller', 'seller@dvss.com', '$2b$12$K7gNU3sAFUvj.nIMKIBaXO7kB9PK.r6w4zR4Y8H.j7oZ8K.L5P8QC', '卖家演示账号', 'Sales', r.id
FROM roles r WHERE r.name = 'seller';

INSERT IGNORE INTO users (username, email, password_hash, full_name, department, role_id) 
SELECT 'payment', 'payment@dvss.com', '$2b$12$K7gNU3sAFUvj.nIMKIBaXO7kB9PK.r6w4zR4Y8H.j7oZ8K.L5P8QC', '支付服务商演示账号', 'Payment', r.id
FROM roles r WHERE r.name = 'payment';

INSERT IGNORE INTO users (username, email, password_hash, full_name, department, role_id) 
SELECT 'logistics', 'logistics@dvss.com', '$2b$12$K7gNU3sAFUvj.nIMKIBaXO7kB9PK.r6w4zR4Y8H.j7oZ8K.L5P8QC', '物流演示账号', 'Logistics', r.id
FROM roles r WHERE r.name = 'logistics';

INSERT IGNORE INTO users (username, email, password_hash, full_name, department, role_id) 
SELECT 'auditor', 'auditor@dvss.com', '$2b$12$K7gNU3sAFUvj.nIMKIBaXO7kB9PK.r6w4zR4Y8H.j7oZ8K.L5P8QC', '审计员演示账号', 'Audit', r.id
FROM roles r WHERE r.name = 'auditor';

INSERT IGNORE INTO users (username, email, password_hash, full_name, department, role_id) 
SELECT 'platform', 'platform@dvss.com', '$2b$12$K7gNU3sAFUvj.nIMKIBaXO7kB9PK.r6w4zR4Y8H.j7oZ8K.L5P8QC', '平台管理员演示账号', 'Platform', r.id
FROM roles r WHERE r.name = 'platform';

-- 插入演示订单数据 (包含各种敏感字段用于测试权限)
INSERT IGNORE INTO original_orders (
    order_id, user_id, name, phone, email,
    address, shipping_address, billing_address, zip_code, city, state, country,
    payment_info, credit_card, bank_account, payment_method,
    item_list, item_name, item_price, quantity,
    total_amount, tax_amount, shipping_cost, discount, sensitivity_score, status
) VALUES 
(
    'ORD001', 'user_001', '张三', '13800138001', 'zhangsan@example.com',
    '北京市朝阳区建国路88号SOHO现代城A座1001', '北京市朝阳区建国路88号SOHO现代城A座1001', '北京市朝阳区建国路88号SOHO现代城A座1001', '100020', '北京', '北京', '中国',
    '{"method":"credit_card","last4":"1234","bank":"招商银行"}', '6225881234567890', '6225881234567890', 'credit_card',
    '[{"name":"iPhone 14","price":5999,"qty":1},{"name":"保护壳","price":99,"qty":2}]', 'iPhone 14', 5999.00, 1,
    6197.00, 617.00, 100.00, 0.00, 0.85, 'completed'
),
(
    'ORD002', 'user_002', '李四', '13900139002', 'lisi@example.com',
    '上海市浦东新区陆家嘴环路1000号恒生银行大厦20F', '上海市浦东新区陆家嘴环路1000号恒生银行大厦20F', '上海市浦东新区陆家嘴环路1000号恒生银行大厦20F', '200120', '上海', '上海', '中国',
    '{"method":"alipay","account":"li****@alipay.com"}', NULL, '6228481234567891', 'alipay',
    '[{"name":"小米13","price":3999,"qty":1},{"name":"充电器","price":199,"qty":1}]', '小米13', 3999.00, 1,
    4198.00, 199.00, 80.00, 50.00, 0.72, 'completed'
),
(
    'ORD003', 'user_003', '王五', '13700137003', 'wangwu@example.com',
    '广州市天河区珠江新城花城大道123号', '广州市天河区珠江新城花城大道123号', '广州市天河区珠江新城花城大道123号', '510623', '广州', '广东', '中国',
    '{"method":"wechat_pay","openid":"wx_abc123"}', NULL, '6217001234567892', 'wechat_pay',
    '[{"name":"MacBook Air","price":8999,"qty":1},{"name":"鼠标","price":299,"qty":1}]', 'MacBook Air', 8999.00, 1,
    9298.00, 929.80, 150.00, 200.00, 0.90, 'processing'
),
(
    'ORD004', 'user_004', '赵六', '13600136004', 'zhaoliu@example.com',
    '成都市武侯区天府大道中段1号', '成都市武侯区天府大道中段1号', '成都市武侯区天府大道中段1号', '610041', '成都', '四川', '中国',
    '{"method":"bank_transfer","bank":"工商银行","account":"622202****1234"}', NULL, '6222021234567893', 'bank_transfer', 
    '[{"name":"耳机","price":599,"qty":1},{"name":"数据线","price":59,"qty":3}]', '耳机', 599.00, 1,
    776.00, 76.00, 50.00, 30.00, 0.65, 'shipped'
),
(
    'ORD005', 'user_005', '钱七', '13500135005', 'qianqi@example.com',
    '深圳市南山区科技园南区深南大道9966号威盛科技大厦', '深圳市南山区科技园南区深南大道9966号威盛科技大厦', '深圳市南山区科技园南区深南大道9966号威盛科技大厦', '518057', '深圳', '广东', '中国',
    '{"method":"credit_card","last4":"5678","bank":"平安银行"}', '6230581234567894', '6230581234567894', 'credit_card',
    '[{"name":"华为MatePad","price":2499,"qty":1},{"name":"键盘","price":399,"qty":1}]', '华为MatePad', 2499.00, 1,
    2898.00, 289.80, 60.00, 0.00, 0.78, 'pending'
);

-- 演示数据插入完成
SELECT 'DVSS演示数据初始化完成！' AS message;
SELECT 'Admin账号: admin/123456' AS admin_info;
SELECT 'Seller账号: seller/123456' AS seller_info;
SELECT 'Payment账号: payment/123456' AS payment_info;
SELECT 'Logistics账号: logistics/123456' AS logistics_info;
SELECT 'Auditor账号: auditor/123456' AS auditor_info;
SELECT 'Platform账号: platform/123456' AS platform_info;
