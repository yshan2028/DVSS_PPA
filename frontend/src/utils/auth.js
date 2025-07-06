/**
 * 认证工具函数
 */

const TOKEN_KEY = 'dvss_access_token'
const REFRESH_TOKEN_KEY = 'dvss_refresh_token'
const USER_INFO_KEY = 'dvss_user_info'

/**
 * 获取访问令牌
 */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * 设置访问令牌
 */
export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

/**
 * 删除访问令牌
 */
export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

/**
 * 获取刷新令牌
 */
export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

/**
 * 设置刷新令牌
 */
export function setRefreshToken(token) {
  localStorage.setItem(REFRESH_TOKEN_KEY, token)
}

/**
 * 删除刷新令牌
 */
export function removeRefreshToken() {
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

/**
 * 获取用户信息
 */
export function getUserInfo() {
  const userInfo = localStorage.getItem(USER_INFO_KEY)
  return userInfo ? JSON.parse(userInfo) : null
}

/**
 * 设置用户信息
 */
export function setUserInfo(userInfo) {
  localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo))
}

/**
 * 删除用户信息
 */
export function removeUserInfo() {
  localStorage.removeItem(USER_INFO_KEY)
}

/**
 * 清除所有认证信息
 */
export function clearAuth() {
  removeToken()
  removeRefreshToken()
  removeUserInfo()
}

/**
 * 检查是否已登录
 */
export function isLoggedIn() {
  return !!getToken()
}

/**
 * 检查是否有特定权限
 */
export function hasPermission(permission) {
  const userInfo = getUserInfo()
  if (!userInfo || !userInfo.permissions) {
    return false
  }
  return userInfo.permissions.includes(permission)
}

/**
 * 检查是否有特定角色
 */
export function hasRole(role) {
  const userInfo = getUserInfo()
  if (!userInfo || !userInfo.role) {
    return false
  }
  return userInfo.role === role || (Array.isArray(userInfo.role) && userInfo.role.includes(role))
}
