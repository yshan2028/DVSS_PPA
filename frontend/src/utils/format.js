/**
 * 格式化工具函数
 */

/**
 * 格式化文件大小
 * @param {number} bytes 字节数
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 格式化数字
 * @param {number} num 数字
 * @param {number} decimals 小数位数
 * @returns {string} 格式化后的数字
 */
export function formatNumber(num, decimals = 2) {
  if (num === null || num === undefined) return '-'
  return Number(num).toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

/**
 * 格式化百分比
 * @param {number} value 数值
 * @param {number} total 总数
 * @param {number} decimals 小数位数
 * @returns {string} 格式化后的百分比
 */
export function formatPercentage(value, total, decimals = 1) {
  if (!total || total === 0) return '0%'
  const percentage = (value / total) * 100
  return percentage.toFixed(decimals) + '%'
}

/**
 * 格式化货币
 * @param {number} amount 金额
 * @param {string} currency 货币符号
 * @returns {string} 格式化后的货币
 */
export function formatCurrency(amount, currency = '¥') {
  if (amount === null || amount === undefined) return '-'
  return currency + Number(amount).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

/**
 * 格式化手机号
 * @param {string} phone 手机号
 * @returns {string} 格式化后的手机号
 */
export function formatPhone(phone) {
  if (!phone) return '-'
  const phoneStr = phone.toString()
  if (phoneStr.length === 11) {
    return phoneStr.replace(/(\d{3})(\d{4})(\d{4})/, '$1****$3')
  }
  return phone
}

/**
 * 格式化邮箱
 * @param {string} email 邮箱
 * @returns {string} 格式化后的邮箱
 */
export function formatEmail(email) {
  if (!email) return '-'
  const [username, domain] = email.split('@')
  if (username.length <= 2) {
    return email
  }
  const hiddenUsername = username.charAt(0) + '*'.repeat(username.length - 2) + username.charAt(username.length - 1)
  return hiddenUsername + '@' + domain
}

/**
 * 格式化银行卡号
 * @param {string} cardNumber 银行卡号
 * @returns {string} 格式化后的银行卡号
 */
export function formatBankCard(cardNumber) {
  if (!cardNumber) return '-'
  const cardStr = cardNumber.toString()
  if (cardStr.length >= 8) {
    return cardStr.substring(0, 4) + ' **** **** ' + cardStr.substring(cardStr.length - 4)
  }
  return cardNumber
}

/**
 * 格式化身份证号
 * @param {string} idCard 身份证号
 * @returns {string} 格式化后的身份证号
 */
export function formatIdCard(idCard) {
  if (!idCard) return '-'
  const idStr = idCard.toString()
  if (idStr.length === 18) {
    return idStr.substring(0, 4) + '**********' + idStr.substring(14)
  }
  return idCard
}

/**
 * 格式化状态
 * @param {string|number} status 状态值
 * @param {Object} statusMap 状态映射
 * @returns {string} 格式化后的状态
 */
export function formatStatus(status, statusMap = {}) {
  return statusMap[status] || status || '-'
}

/**
 * 截断文本
 * @param {string} text 文本
 * @param {number} length 最大长度
 * @param {string} suffix 后缀
 * @returns {string} 截断后的文本
 */
export function truncateText(text, length = 50, suffix = '...') {
  if (!text) return '-'
  if (text.length <= length) return text
  return text.substring(0, length) + suffix
}
