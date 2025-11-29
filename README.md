# 项目目录
autotest/  
├── config/ —> 配置目录  
│   └── airtest_config.py —> airtest配置ST值设置  
│   └── android_config.py —> Android App测试设置  
│   └── windows_app_config.py —> Windows应用测试配置  
│   └── api_test_plan.py —> 接口测试计划  
│   └── android_test_plan.py —> Android App测试计划  
├── core/ —> 测试工具库  
│   └── windows_client.py —> Windows应用测试工具类  
│   └── http_client.py —> 接口测试工具类  
│   └── api_test_executor.py —> 接口测试执行器  
│   └── android_client.py —> Android App测试工具类  
│   └── android_test_executor.py —> Android App测试执行器  
├── platform/ —> 测试平台——flask框架  
│   ├── mock/  —>mock server包  
│       └── order_service.py —> order相关接口实现  
│       └── user_service.py —> user相关接口实现  
│   ├── services/  —>自动化测试平台后端逻辑实现包  
│       └── platform.py —> 自动化测试平台后端实现逻辑  
│   ├── static/  —> 测试平台静态文件css与js存放目录  
│   ├── templates/  —> 测试平台html页面存放目录  
│   ├── routes.py/  —> 测试平台路由文件  
│   └── app.py —> 测试平台启动入口  
├── reports/ —> 报告日志目录  
│   ├── logs/  —>日志目录  
│   ├── screenshots/  —>测试失败后截图目录  
├── resources/ —> 资源库  
│   ├── image/ —> 存放应用不同模块操作按钮的截图目录  
│   │    ├── calculator_button/ —> windows系统计算器按钮截图目录  
│   │    ├── calculator_assert/ —> 计算器测试断言截图目录  
├── tests_data/ —> 测试数据  
├── tests/ —> 测试入口  
│   ├── Android/  —>Android App测试入口  
│       └── conftest.py —> Android App测试相关的夹具配置  
│       └── test_entrance.py —> Android App测试入口  
│   ├── API/  —>API测试入口  
│       └── conftest.py —> API测试相关的夹具配置  
│       └── test_entrance.py —> API测试入口  
│   ├── UI/  —>UI测试入口  
│       └── conftest.py —> UI测试相关的夹具配置  
│       └── test_calculator_demo.py —> 测试计算器的一个示例  
├── utils/ —> 工具函数  
│   └── file_utils.py  
│   └── kill_process.py  
│   └── logger.py  
│   └── path_util.py  
└── conftest.py  
└── Dockerfile —> 项目容器  
└── docker-compose.yml —> 项目容器配置  
└── pytest.ini  
└── requirements.txt  

# 说明
    
## 1、不使用测试平台
### 1）tests_data目录下级目录名为测试计划名,下级目录内容为该测试计划下的测试用例.
### 2) 测试计划变动时需要维护test_entrance.py文件

## 2、pytest快捷执行命令
### 1）运行所有单接口测试
    pytest test_entrance.py -v
### 2）执行标记为 smoke 的用例
    pytest -m smoke
### 3）运行特定测试用例
    pytest test_entrance.py::TestExecute::test_execute_all_fun_cases
    pytest test_entrance.py::test_execute_smoke_cases
### 4）运行上次失败的测试
    pytest --lf
    pytest --last-failed
### 5）使用通配符匹配文件名
    pytest test_*.py
    pytest *login*.py
### 6）常用参数组合
    # 快速运行并立即在失败时停止
    pytest -x
    
    # 运行并显示详细输出
    pytest -v
    
    # 运行并显示打印语句
    pytest -s
    
    # 运行并在第一个失败后停止
    pytest -x --tb=short

## 2、ui自动化
    在运行calculator ui自动化报”import win32api ImportError: DLL load failed: 找不到指定的程序。“，请安装：
    https://aka.ms/vs/17/release/vc_redist.x64.exe

