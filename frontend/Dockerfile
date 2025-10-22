# 构建阶段
FROM node:18-alpine as build-stage

WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制项目文件
COPY . .

# 构建生产版本
RUN npm run build

# 生产阶段 - 使用轻量级服务器
FROM node:18-alpine as production-stage

WORKDIR /app

# 全局安装serve
RUN npm install -g serve

# 从构建阶段复制构建产物
COPY --from=build-stage /app/dist /app/dist

# 暴露端口
EXPOSE 8082

# 启动serve服务
CMD ["serve", "-s", "dist", "-l", "8082"]
