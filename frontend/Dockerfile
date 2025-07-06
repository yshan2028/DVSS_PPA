# 多阶段构建 - 构建阶段
FROM node:18-alpine as build-stage

WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码 (排除 node_modules)
COPY . .

# 清理可能存在的 node_modules 并重新安装依赖
RUN rm -rf node_modules && npm ci

# 构建生产版本
RUN npm run build

# 生产阶段
FROM nginx:alpine as production-stage

# 安装 curl 用于健康检查
RUN apk add --no-cache curl

# 复制构建文件到 nginx
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
