############################################################
# 构建阶段（Stage 1）：使用 Node 镜像安装依赖并打包前端代码
############################################################
FROM node:20-alpine AS build

# 设置工作目录
WORKDIR /app

# 仅复制依赖清单文件，利用 Docker 层级缓存
COPY package*.json ./

# 安装项目依赖（npm ci = 干净安装，速度更快）
RUN npm ci

# 复制其余源代码（确保 .dockerignore 已排除 node_modules 等）
COPY . .

# 生产环境构建
RUN npm run build

############################################################
# 运行阶段（Stage 2）：使用轻量级 Nginx 镜像托管静态文件
############################################################
FROM nginx:alpine

# 安装 curl 用于健康检查
RUN apk add --no-cache curl

# 拷贝自定义 Nginx 配置，覆盖默认配置
COPY nginx.conf /etc/nginx/nginx.conf

# 将前端构建产物复制到 Nginx 默认静态目录
COPY --from=build /app/dist/ /usr/share/nginx/html/

# 暴露服务端口
EXPOSE 80

# 健康检查：访问 Nginx 中已固定返回 200 的 /health 路由
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# 以“前景模式”启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
