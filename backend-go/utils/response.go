package utils

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// APIResponse 标准API响应结构
type APIResponse struct {
	Success   bool        `json:"success"`
	Message   string      `json:"message"`
	Data      interface{} `json:"data,omitempty"`
	Error     string      `json:"error,omitempty"`
	Code      int         `json:"code"`
	Timestamp string      `json:"timestamp"`
}

// PaginatedResponse 分页响应结构
type PaginatedResponse struct {
	Success   bool        `json:"success"`
	Message   string      `json:"message"`
	Data      interface{} `json:"data"`
	Total     int64       `json:"total"`
	Page      int         `json:"page"`
	PageSize  int         `json:"page_size"`
	Timestamp string      `json:"timestamp"`
}

// SuccessResponse 成功响应
func SuccessResponse(c *gin.Context, message string, data interface{}) {
	c.JSON(http.StatusOK, APIResponse{
		Success:   true,
		Message:   message,
		Data:      data,
		Code:      http.StatusOK,
		Timestamp: time.Now().Format(time.RFC3339),
	})
}

// ErrorResponse 错误响应
func ErrorResponse(c *gin.Context, code int, message string, err error) {
	errorMsg := ""
	if err != nil {
		errorMsg = err.Error()
	}
	
	c.JSON(code, APIResponse{
		Success:   false,
		Message:   message,
		Error:     errorMsg,
		Code:      code,
		Timestamp: time.Now().Format(time.RFC3339),
	})
}

// PaginatedSuccessResponse 分页成功响应
func PaginatedSuccessResponse(c *gin.Context, message string, data interface{}, total int64, page, pageSize int) {
	c.JSON(http.StatusOK, PaginatedResponse{
		Success:   true,
		Message:   message,
		Data:      data,
		Total:     total,
		Page:      page,
		PageSize:  pageSize,
		Timestamp: time.Now().Format(time.RFC3339),
	})
}

// ValidationErrorResponse 验证错误响应
func ValidationErrorResponse(c *gin.Context, message string, validationErrors interface{}) {
	c.JSON(http.StatusBadRequest, APIResponse{
		Success:   false,
		Message:   message,
		Data:      validationErrors,
		Code:      http.StatusBadRequest,
		Timestamp: time.Now().Format(time.RFC3339),
	})
}

// UnauthorizedResponse 未授权响应
func UnauthorizedResponse(c *gin.Context, message string) {
	c.JSON(http.StatusUnauthorized, APIResponse{
		Success:   false,
		Message:   message,
		Code:      http.StatusUnauthorized,
		Timestamp: time.Now().Format(time.RFC3339),
	})
}

// ForbiddenResponse 禁止访问响应
func ForbiddenResponse(c *gin.Context, message string) {
	c.JSON(http.StatusForbidden, APIResponse{
		Success:   false,
		Message:   message,
		Code:      http.StatusForbidden,
		Timestamp: time.Now().Format(time.RFC3339),
	})
}

// NotFoundResponse 未找到响应
func NotFoundResponse(c *gin.Context, message string) {
	c.JSON(http.StatusNotFound, APIResponse{
		Success:   false,
		Message:   message,
		Code:      http.StatusNotFound,
		Timestamp: time.Now().Format(time.RFC3339),
	})
}

// InternalServerErrorResponse 服务器内部错误响应
func InternalServerErrorResponse(c *gin.Context, message string, err error) {
	ErrorResponse(c, http.StatusInternalServerError, message, err)
}
		Message: message,
		Data:    nil,
		Success: false,
	})
}

// ServerError 服务器错误
func ServerError(c *gin.Context, message string) {
	c.JSON(http.StatusInternalServerError, Response{
		Code:    500,
		Message: message,
		Data:    nil,
		Success: false,
	})
}

// NotFound 未找到
func NotFound(c *gin.Context, message string) {
	c.JSON(http.StatusNotFound, Response{
		Code:    404,
		Message: message,
		Data:    nil,
		Success: false,
	})
}
