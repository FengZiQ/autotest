# 使用说明

## 1. 构建和运行
### 运行所有测试：
    bash
    docker-compose up autotest-all

### 只运行API测试：
    bash
    docker-compose up autotest-api

### 只运行UI测试：
    bash
    docker-compose up autotest-ui


## 2. 直接使用Dockerfile
### 构建镜像：
    bash
    docker build -t automation-tests .
### 运行容器：
    bash
    docker run -v $(pwd)/reports:/app/reports -v $(pwd)/tests_data:/app/tests_data automation-tests

## 3. 自定义测试命令
### 如果您需要运行特定的测试命令，可以覆盖默认命令：
    bash
    docker run -v $(pwd)/reports:/app/reports automation-tests python -m pytest tests/API/ -v

## 4. 配置说明
    虚拟显示：使用Xvfb创建虚拟显示环境，这对于Airtest的UI自动化是必要的

### 卷挂载：

    reports：测试报告和日志
    tests_data：测试数据
    resources：UI测试需要的图片资源

### 环境变量：

    PYTHONPATH：确保Python可以找到项目模块
    DISPLAY：设置显示环境变量