# 项目目录
autotest/  
├── config/ —> 配置目录  
│   └── android_config.py —> Android App测试设置  
│   └── windows_app_config.py —> Windows应用测试配置  
│   └── api_test_plan.py —> 接口测试计划  
│   └── android_test_plan.py —> Android App测试计划  
│   └── windows_test_plan.py —> Windows App测试计划  
├── core/ —> 测试工具库  
│   └── airtest_client.py —> airtest测试工具类  
│   └── airtest_executor.py —> airtest测试工具测试执行器  
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
│   ├── image/ —> 图片资源目录  
│   │    ├── android_app/ —> android app按钮截图及断言截图目录  
│   │    ├── windows_app/ —> windows app按钮截图及断言截图目录
├── tests/ —> 测试入口  
│   ├── Android/  —>Android App测试入口  
│       └── conftest.py —> Android App测试相关的夹具配置  
│       └── test_entrance.py —> Android App测试入口  
│   ├── API/  —>API测试入口  
│       └── conftest.py —> API测试相关的夹具配置  
│       └── test_entrance.py —> API测试入口  
│   ├── Windows/  —>Windows App测试入口 
│       └── conftest.py —> Windows App测试相关的夹具配置  
│       └── test_windows_app_entrance.py —> Windows App测试入口  
├── tests_data/ —> 测试用例集数据  
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

## 3、airtest测试工具使用相关
### 1）[测试用例编写](https://github.com/FengZiQ/autotest/blob/main/docs/tests_data_for_Windows.json)
    
### 2）测试windows app注意点
    程序报”import win32api ImportError: DLL load failed: 找不到指定的程序。“，请安装：
    https://aka.ms/vs/17/release/vc_redist.x64.exe

