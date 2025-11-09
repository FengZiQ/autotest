# 使用说明

## 1. 构建和运行
    # 在项目根目录（autotest/）下执行
    
    # 构建并启动服务
    docker-compose up -d
    
    # 查看服务状态
    docker-compose ps
    
    # 查看日志
    docker-compose logs -f
    
    # 停止服务
    docker-compose down


## 2. 目录结构说明
启动后，容器内的目录结构将与宿主机保持同步：

容器内的 /app/reports 目录映射到宿主机的 ./reports

容器内的 /app/tests_data 目录映射到宿主机的 ./tests_data

## 3. 端口配置
### 如果您的测试平台使用其他端口，请修改 docker-compose.yml 中的端口映射：
    ports:
    - "宿主机端口:容器端口"

## 4. 镜像加速源配置
### 在 /etc/docker/daemon.json 中配置以下内容（需 root 权限）：
    {
      "registry-mirrors": [
        "https://docker.1ms.run",
        "https://docker-0.unsee.tech",
        "https://docker.m.daocloud.io",
        "https://docker.hlmirror.com"
      ],
      "max-concurrent-downloads": 10,
      "live-restore": true
    }