# ToolBox

ToolBox 是一个用 PySide6 写的桌面工具箱项目，把一批常用小工具放在同一个 GUI 里。

一句话：
如果你平时会写很多零碎脚本，这个项目就是把它们“模块化 + 可视化”的一次整理。

## 目前包含的内容

从代码结构看，当前工具箱包含这些方向：

- 文件分类工具
- 代码清理/资源处理类工具
- 文本/翻译相关工具
- 若干实验模块（部分为历史代码）

## 目录结构

- `top/dwgx/Client.py`：主程序入口
- `top/dwgx/Manager/`：模块与配置管理
- `top/dwgx/Modules/`：具体功能模块
- `top/resource/`：图标、背景、资源文件
- `programtool/`：独立脚本工具集合
- `requirements`：依赖列表

## 运行环境

- Python 3.10+
- Windows（优先）

## 快速启动

```bash
git clone https://github.com/dwgx/ToolBox.git
cd ToolBox
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements
python top/dwgx/Client.py
```

## 已知情况

- 仓库里存在部分 `__pycache__` 历史文件
- 个别模块属于实验性质，不保证长期维护

## 建议

- 先把你常用模块保留，其余模块按需精简
- 再按模块拆包，后续维护会更轻松

## 免责声明

请仅在合法、合规和授权的场景下使用本项目。
