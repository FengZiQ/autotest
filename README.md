# 项目目录
autotest/
├── config/ —> 配置目录  
│   └── airtest_config.py —> airtest配置ST值设置  
│   └── app_config.py —> 测试应用相关配置  
│   └── api_test_plan.py —> 接口测试计划  
├── core/ —> 测试工具库  
│   └── windows_app_test.py —> Windows应用测试工具类  
│   └── http_client.py —> 接口测试工具类  
│   └── api_test_executor.py —> 接口测试执行器  
├── platform/ —> 测试平台  
│   ├── mock/  —>mock接口返回脚本目录
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
│   ├── API/  —>API测试入口  
│       └── test_entrance.py —> API测试入口  
│   ├── UI/  —>UI测试入口  
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
    
## 1、接口测试
### 1）接口测试用例数据示例在tests_data/user_center/*.json文件中
### 2）接口测试计划在config/api_test_plan.py文件中配置

## 3、pytest快捷执行命令
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

# 为何用pytest
## 一、简洁至上 (Convention over Configuration):

    自动发现： 不需要继承特定类。任何 test_*.py 文件或 *_test.py 文件中，以 test_ 开头的函数或 Test 开头的类中以 test_ 开头的方法，都会被自动识别为测试用例。
    
    原生断言： 使用 Python 内置的 assert 语句进行断言。pytest 会智能地重写 assert 语句，在失败时提供极其详细和可读性高的上下文信息（显示变量值、表达式比较等），这是相比 unittest 的巨大优势。
    
## 二、强大的 Fixture 系统： 这是 pytest 的杀手锏。
    
    超越 setUp/tearDown： Fixture 提供了更灵活、模块化和可重用的方式来设置测试环境（setup）和清理（teardown）。它们本质上就是一些被 @pytest.fixture 装饰的函数。
    
    作用域控制： Fixture 可以定义不同的作用域：
    
    function (默认)：每个测试函数运行一次。
    
    class：每个测试类运行一次（该类中的所有测试方法共享）。
    
    module：每个测试模块（文件）运行一次。
    
    package：每个测试包（目录）运行一次。
    
    session：整个测试会话（运行一次 pytest 命令）只运行一次。非常适合启动/关闭全局资源（如数据库连接池、Web 服务器）。
    
    依赖注入： 测试函数通过将 Fixture 名称作为参数来请求它。pytest 自动解析依赖关系并按需创建/注入 Fixture 实例。这使得测试代码更清晰，依赖关系更明确。
    
    模块化和重用： Fixture 可以放在单独的 conftest.py 文件中，供该目录及其所有子目录下的测试使用。极大提高了代码复用率。
    
    工厂模式： Fixture 可以返回一个生成器函数 (yield) 或使用 request.addfinalizer 来精确控制 teardown 逻辑（yield 之前的代码是 setup，之后的代码是 teardown）。
    
    参数化 Fixture： Fixture 本身也可以被参数化，为依赖它的测试提供不同的数据源。

## 三、优雅的参数化测试：
    
    @pytest.mark.parametrize： 这是 pytest 处理参数化测试的主要方式。它允许你为一个测试函数或方法定义多组输入参数和预期输出。
    
    清晰展示： 在测试报告中，每组参数都会作为一个独立的测试用例项显示，清晰地标识出是哪组参数导致了失败。
    
    灵活组合： 可以在函数、类、模块级别应用参数化标记，甚至可以组合多个 parametrize 标记（产生笛卡尔积）。

## 四、丰富的插件生态： pytest 的核心设计是可扩展的。

    海量插件： 有数百个官方和社区维护的插件，覆盖几乎所有测试需求：
    
    报告： pytest-html (生成 HTML 报告), pytest-allure-adaptor/allure-pytest (生成 Allure 报告), pytest-xdist (分布式/并行测试)
    
    覆盖率： pytest-cov (集成 coverage.py)
    
    Mock： pytest-mock (提供更简洁的 mocker Fixture, 封装 unittest.mock)
    
    特定领域： pytest-django, pytest-flask (Web 框架支持), pytest-selenium (Web UI 自动化), pytest-bdd (行为驱动开发), pytest-asyncio (异步支持), pytest-datadir (测试数据管理), pytest-timeout (测试超时控制) 等等。
    
    易于安装和使用： pip install pytest-<plugin-name> 即可。

## 五、灵活的标记系统：

    @pytest.mark.<markername>： 允许你给测试函数/类打上自定义标签。
    
    用途广泛：
    
    选择性运行： pytest -m slow 只运行标记为 @pytest.mark.slow 的测试。
    
    跳过： @pytest.mark.skip(reason="...") / @pytest.mark.skipif(condition, reason="...")
    
    预期失败： @pytest.mark.xfail(condition, reason="...", strict=True/False)
    
    参数化： @pytest.mark.parametrize 本身也是一种标记。
    
    自定义行为： 插件可以利用标记实现特定功能（如 pytest-selenium 的 @pytest.mark.selenium）。
    
    注册标记： 在 pytest.ini 或 conftest.py 中注册标记以避免拼写错误警告：markers = slow: marks tests as slow (deselect with '-m "not slow"')

## 六、优秀的失败报告：

    丰富的上下文： assert 失败时展示局部变量值、函数参数、调用栈上下文。
    
    输出捕获： 自动捕获测试过程中的 stdout/stderr，并在测试失败时显示。也可用 caplog Fixture 捕获日志。
    
    回溯优化： 默认隐藏 pytest 和标准库的内部调用栈，聚焦于用户代码。
    
    --showlocals / -l： 命令行选项，在失败时显示所有局部变量。
    
    --pdb： 测试失败时自动进入 Python 调试器 (pdb)。
    
    --lf / --last-failed： 只重新运行上次失败的测试。
    
    --ff / --failed-first： 先运行上次失败的测试，再运行其他的。