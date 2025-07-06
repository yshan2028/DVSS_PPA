/**
 * 表单验证工具函数
 */

/**
 * 验证邮箱格式
 * @param {string} email 邮箱
 * @returns {boolean} 是否有效
 */
export function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

/**
 * 验证手机号格式
 * @param {string} phone 手机号
 * @returns {boolean} 是否有效
 */
export function validatePhone(phone) {
  const re = /^1[3-9]\d{9}$/
  return re.test(phone)
}

/**
 * 验证密码强度
 * @param {string} password 密码
 * @returns {Object} 验证结果
 */
export function validatePassword(password) {
  const result = {
    isValid: false,
    strength: 'weak',
    message: '',
    requirements: {
      length: false,
      lowercase: false,
      uppercase: false,
      number: false,
      special: false
    }
  }

  if (!password) {
    result.message = '密码不能为空'
    return result
  }

  // 检查长度
  result.requirements.length = password.length >= 8
  
  // 检查小写字母
  result.requirements.lowercase = /[a-z]/.test(password)
  
  // 检查大写字母
  result.requirements.uppercase = /[A-Z]/.test(password)
  
  // 检查数字
  result.requirements.number = /\d/.test(password)
  
  // 检查特殊字符
  result.requirements.special = /[!@#$%^&*(),.?":{}|<>]/.test(password)

  // 计算强度
  const metRequirements = Object.values(result.requirements).filter(Boolean).length
  
  if (metRequirements < 3) {
    result.strength = 'weak'
    result.message = '密码强度弱，建议包含大小写字母、数字和特殊字符'
  } else if (metRequirements < 4) {
    result.strength = 'medium'
    result.message = '密码强度中等'
  } else {
    result.strength = 'strong'
    result.message = '密码强度强'
    result.isValid = true
  }

  return result
}

/**
 * 验证用户名格式
 * @param {string} username 用户名
 * @returns {boolean} 是否有效
 */
export function validateUsername(username) {
  // 用户名只能包含字母、数字和下划线，长度3-20位
  const re = /^[a-zA-Z0-9_]{3,20}$/
  return re.test(username)
}

/**
 * 验证身份证号
 * @param {string} idCard 身份证号
 * @returns {boolean} 是否有效
 */
export function validateIdCard(idCard) {
  if (!idCard || idCard.length !== 18) return false
  
  const re = /^\d{17}[\dXx]$/
  if (!re.test(idCard)) return false
  
  // 校验位验证
  const factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
  const checkCodes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
  
  let sum = 0
  for (let i = 0; i < 17; i++) {
    sum += parseInt(idCard[i]) * factors[i]
  }
  
  const checkCode = checkCodes[sum % 11]
  return checkCode === idCard[17].toUpperCase()
}

/**
 * 验证银行卡号
 * @param {string} cardNumber 银行卡号
 * @returns {boolean} 是否有效
 */
export function validateBankCard(cardNumber) {
  if (!cardNumber) return false
  
  // 移除空格和连字符
  const cleanNumber = cardNumber.replace(/[\s-]/g, '')
  
  // 检查是否只包含数字
  if (!/^\d+$/.test(cleanNumber)) return false
  
  // 检查长度（通常为13-19位）
  if (cleanNumber.length < 13 || cleanNumber.length > 19) return false
  
  // Luhn算法验证
  let sum = 0
  let isEven = false
  
  for (let i = cleanNumber.length - 1; i >= 0; i--) {
    let digit = parseInt(cleanNumber[i])
    
    if (isEven) {
      digit *= 2
      if (digit > 9) {
        digit -= 9
      }
    }
    
    sum += digit
    isEven = !isEven
  }
  
  return sum % 10 === 0
}

/**
 * 验证URL格式
 * @param {string} url URL
 * @returns {boolean} 是否有效
 */
export function validateUrl(url) {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 验证IP地址
 * @param {string} ip IP地址
 * @returns {boolean} 是否有效
 */
export function validateIP(ip) {
  const re = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  return re.test(ip)
}

/**
 * 验证表单规则
 */
export const formRules = {
  // 必填验证
  required: {
    required: true,
    message: '此字段为必填项',
    trigger: 'blur'
  },
  
  // 邮箱验证
  email: {
    validator: (rule, value, callback) => {
      if (value && !validateEmail(value)) {
        callback(new Error('请输入有效的邮箱地址'))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  },
  
  // 手机号验证
  phone: {
    validator: (rule, value, callback) => {
      if (value && !validatePhone(value)) {
        callback(new Error('请输入有效的手机号'))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  },
  
  // 用户名验证
  username: {
    validator: (rule, value, callback) => {
      if (value && !validateUsername(value)) {
        callback(new Error('用户名只能包含字母、数字和下划线，长度3-20位'))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  },
  
  // 密码验证
  password: {
    validator: (rule, value, callback) => {
      if (value) {
        const result = validatePassword(value)
        if (!result.isValid) {
          callback(new Error(result.message))
        } else {
          callback()
        }
      } else {
        callback()
      }
    },
    trigger: 'blur'
  }
}
