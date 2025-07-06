/**
 * 日期时间工具函数
 */

/**
 * 格式化日期
 * @param {Date|string|number} date 日期
 * @param {string} format 格式字符串 默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return ''
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化相对时间
 * @param {Date|string|number} date 日期
 * @returns {string} 相对时间字符串
 */
export function formatRelativeTime(date) {
  if (!date) return ''
  
  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const week = 7 * day
  const month = 30 * day
  const year = 365 * day
  
  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    return `${Math.floor(diff / minute)}分钟前`
  } else if (diff < day) {
    return `${Math.floor(diff / hour)}小时前`
  } else if (diff < week) {
    return `${Math.floor(diff / day)}天前`
  } else if (diff < month) {
    return `${Math.floor(diff / week)}周前`
  } else if (diff < year) {
    return `${Math.floor(diff / month)}个月前`
  } else {
    return `${Math.floor(diff / year)}年前`
  }
}

/**
 * 获取日期范围
 * @param {string} type 类型：today, yesterday, week, month, year
 * @returns {Array} [开始日期, 结束日期]
 */
export function getDateRange(type) {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  
  switch (type) {
    case 'today':
      return [today, new Date(today.getTime() + 24 * 60 * 60 * 1000 - 1)]
    
    case 'yesterday':
      const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
      return [yesterday, new Date(yesterday.getTime() + 24 * 60 * 60 * 1000 - 1)]
    
    case 'week':
      const weekStart = new Date(today.getTime() - (today.getDay() || 7 - 1) * 24 * 60 * 60 * 1000)
      const weekEnd = new Date(weekStart.getTime() + 7 * 24 * 60 * 60 * 1000 - 1)
      return [weekStart, weekEnd]
    
    case 'month':
      const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
      const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999)
      return [monthStart, monthEnd]
    
    case 'year':
      const yearStart = new Date(now.getFullYear(), 0, 1)
      const yearEnd = new Date(now.getFullYear(), 11, 31, 23, 59, 59, 999)
      return [yearStart, yearEnd]
    
    default:
      return [today, new Date(today.getTime() + 24 * 60 * 60 * 1000 - 1)]
  }
}

/**
 * 判断是否为同一天
 * @param {Date|string|number} date1 日期1
 * @param {Date|string|number} date2 日期2
 * @returns {boolean} 是否为同一天
 */
export function isSameDay(date1, date2) {
  const d1 = new Date(date1)
  const d2 = new Date(date2)
  
  return d1.getFullYear() === d2.getFullYear() &&
         d1.getMonth() === d2.getMonth() &&
         d1.getDate() === d2.getDate()
}

/**
 * 获取两个日期之间的天数差
 * @param {Date|string|number} startDate 开始日期
 * @param {Date|string|number} endDate 结束日期
 * @returns {number} 天数差
 */
export function getDaysDiff(startDate, endDate) {
  const start = new Date(startDate)
  const end = new Date(endDate)
  
  const diffTime = Math.abs(end - start)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  return diffDays
}

/**
 * 添加天数
 * @param {Date|string|number} date 日期
 * @param {number} days 要添加的天数
 * @returns {Date} 新日期
 */
export function addDays(date, days) {
  const result = new Date(date)
  result.setDate(result.getDate() + days)
  return result
}

/**
 * 添加月份
 * @param {Date|string|number} date 日期
 * @param {number} months 要添加的月份
 * @returns {Date} 新日期
 */
export function addMonths(date, months) {
  const result = new Date(date)
  result.setMonth(result.getMonth() + months)
  return result
}

/**
 * 获取月份的第一天
 * @param {Date|string|number} date 日期
 * @returns {Date} 月份第一天
 */
export function getFirstDayOfMonth(date) {
  const d = new Date(date)
  return new Date(d.getFullYear(), d.getMonth(), 1)
}

/**
 * 获取月份的最后一天
 * @param {Date|string|number} date 日期
 * @returns {Date} 月份最后一天
 */
export function getLastDayOfMonth(date) {
  const d = new Date(date)
  return new Date(d.getFullYear(), d.getMonth() + 1, 0)
}

/**
 * 验证日期格式
 * @param {string} dateString 日期字符串
 * @param {string} format 格式
 * @returns {boolean} 是否有效
 */
export function isValidDate(dateString, format = 'YYYY-MM-DD') {
  if (!dateString) return false
  
  const date = new Date(dateString)
  return !isNaN(date.getTime())
}
