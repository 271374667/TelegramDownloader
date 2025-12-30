[English](README.md) | [中文](README_CN.md)

# TDL-GUI - Telegram 下载器图形界面

为 [TDL (Telegram Downloader)](https://github.com/iyear/tdl) 打造的现代化、用户友好的图形界面，让 Telegram 文件下载变得更加简单。

## 功能特性

### 核心功能
- **直观的图形界面** - 基于 PySide6 构建的易用标签页界面
- **自动剪贴板监控** - 自动检测并添加剪贴板中的 Telegram 链接
- **批处理配置** - 生成 Windows 批处理文件执行 TDL 下载
- **会话管理** - 配置 TDL 会话设置（命名空间、线程数、速率限制）
- **下载配置** - 全面的下载选项与预览功能

### 高级特性
- **悬浮快捷面板** - 始终置顶的快速操作面板（Ctrl+Shift+F）
- **系统托盘集成** - 最小化到托盘，后台剪贴板监控
- **智能链接识别** - 支持多种 Telegram 链接格式
- **桌面通知** - Windows 吐司通知提示新链接检测
- **Telegram Desktop 登录** - 使用现有 Telegram Desktop 会话快速登录

### 支持的链接格式
- `https://t.me/channel/123`
- `https://t.me/c/1234567890/123`
- `https://t.me/channel/123/456`（消息范围）
- `https://t.me/channel/123?comment=456`（评论）
- `https://t.me/channel/123?thread=456`（论坛主题）

## 系统要求

- **操作系统**：Windows 10/11（64位）
- **Python**：3.11 或更高版本
- **TDL**：tdl.exe 必须放置在 `bin/` 目录
- **Telegram**：已安装 Telegram Desktop（用于初次登录）

## 安装步骤

### 1. 克隆仓库
```bash
git clone https://github.com/yourusername/TDL-GUI.git
cd TDL-GUI
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

必需的包：
- PySide6 >= 6.5.0（GUI 框架）
- winotify >= 1.1.0（Windows 通知）

### 3. 配置 TDL 可执行文件
下载 [tdl.exe](https://github.com/iyear/tdl/releases) 并放置到 `bin/` 目录：
```
TDL-GUI/
├── bin/
│   └── tdl.exe          # 将 TDL 可执行文件放在这里
├── src/
├── run.py
└── requirements.txt
```

### 4. 运行程序
```bash
python run.py
```

## 快速入门

### 初始设置

#### 1. 首次启动 - Telegram 登录
首次运行时，TDL-GUI 会检查登录状态：

1. 如果未登录，会弹出登录对话框
2. 点击 **浏览** 选择您的 Telegram Desktop 目录
   - 默认位置：`C:\Users\您的用户名\AppData\Roaming\Telegram Desktop`
3. 点击 **打开登录终端**
4. 在终端窗口中：
   - 使用方向键选择您的账户
   - 按 Enter 确认
   - **重要**：当询问 "Logout from official client?" 时 → 按 **N**（否）
5. 等待 "Login successful" 消息
6. 返回 GUI 并点击 **验证登录**

#### 2. 会话配置（可选）
导航到 **会话配置** 标签页进行自定义：
- **命名空间**：TDL 数据目录（默认：`.tdl`）
- **线程数**：并发下载线程（1-32）
- **速率限制**：下载速度限制（例如：`1M`、`500K`）
- **代理**：SOCKS5 代理设置

### 基本工作流程

#### 方法 1：剪贴板监控（推荐）
1. 在下载配置标签页中启用 **剪贴板监控** 复选框
2. 复制任何 Telegram 链接（Ctrl+C）
3. 链接自动出现在 URL 列表中
4. 配置下载选项
5. 点击 **生成批处理文件** 或使用悬浮面板的 **运行** 按钮

#### 方法 2：手动输入链接
1. 导航到 **下载配置** 标签页
2. 在 URL 列表中粘贴链接（每行一个或逗号分隔）
3. 点击 **添加链接**
4. 配置下载选项
5. 点击 **生成批处理文件**

### 下载配置选项

#### 链接管理
- **添加链接**：手动添加 Telegram 链接
- **清空**：清除列表中的所有链接
- **剪贴板监控**：自动检测新链接

#### 文件选择
- **下载所有文件**：下载链接中的所有媒体
- **按扩展名选择**：筛选特定文件类型（例如：`.pdf`、`.mp4`）
- **按正则表达式选择**：高级模式匹配

#### 下载设置
- **跳过相同文件**：跳过已下载的文件
- **覆盖文件**：覆盖现有文件
- **Takeout 模式**：使用 Telegram takeout 进行大量下载

#### 输出配置
- **下载目录**：目标文件夹
- **子文件夹模板**：按频道/日期组织（例如：`{{ .DialogID }}`）
- **自定义文件名**：重命名下载的文件（例如：`{{ .FileName }}`）

## 高级功能

### 悬浮快捷面板
- **访问方式**：Ctrl+Shift+F 或系统托盘菜单
- **功能**：
  - 显示当前链接数量
  - 快捷按钮：清空、生成 BAT、运行
  - 始终置顶显示
  - 可拖动到屏幕任意位置

### 系统托盘
右键单击托盘图标访问：
- 显示/隐藏主窗口
- 切换悬浮面板
- 切换剪贴板监控
- 查看当前链接数
- 退出应用程序

### 键盘快捷键
- `Ctrl+Shift+F` - 切换悬浮面板

## 配置文件

TDL 在以下位置创建配置：
- **会话数据**：`%USERPROFILE%\.tdl\data\`
- **配置文件**：`%USERPROFILE%\.tdl\config.yaml`

## 故障排除

### 登录问题

**问题**："登录验证失败"
- **解决方案**：确保终端登录成功完成
- 检查会话数据是否存在于 `%USERPROFILE%\.tdl\data\`
- 尝试手动登录：`bin\tdl.exe login -d "C:\Telegram Desktop 路径"`

### 找不到 TDL

**问题**："bin 目录中找不到 tdl.exe"
- **解决方案**：从 [发布页面](https://github.com/iyear/tdl/releases) 下载 tdl.exe
- 放置到 `bin/` 目录
- 确保文件名为 `tdl.exe`

### 剪贴板监控不工作

**问题**：链接未自动检测
- **解决方案**：
  - 检查 "剪贴板监控" 是否已启用
  - URL 必须是有效的 Telegram 链接格式
  - 确保链接不在列表中

### 下载失败

**问题**：批处理文件执行失败
- **解决方案**：
  - 验证 TDL 登录状态
  - 检查 URL 有效性
  - 确保下载目录可访问
  - 查看批处理终端中的错误消息

### 权限错误

**问题**：无法写入文件
- **解决方案**：
  - 以管理员身份运行
  - 检查下载目录权限
  - 临时禁用杀毒软件（可能阻止 tdl.exe）

## 常见问题

**问：TDL-GUI 安全吗？**
答：是的，它是官方 TDL 工具的 GUI 封装。所有下载操作都由 TDL 执行。

**问：会退出 Telegram Desktop 登录吗？**
答：不会，登录时提示时按 **N** 保持 Telegram Desktop 登录状态。

**问：可以下载私有频道吗？**
答：可以，只要您的 Telegram 账户有访问权限。

**问：支持 Linux/macOS 吗？**
答：目前仅支持 Windows。底层 TDL 支持其他平台，但此 GUI 是 Windows 专用的。

**问：如何更新 TDL？**
答：从 [发布页面](https://github.com/iyear/tdl/releases) 下载最新的 tdl.exe 并替换 `bin/` 目录中的文件。

## 许可证

本项目为开源项目。请查看许可证文件了解详情。

## 致谢

- **TDL**：[iyear/tdl](https://github.com/iyear/tdl) - Telegram Downloader CLI
- **PySide6**：Qt for Python GUI 框架
- **winotify**：Windows 10/11 吐司通知

## 支持

相关问题：
- **TDL-GUI**：在此仓库中提交 issue
- **TDL 核心**：访问 [TDL 仓库](https://github.com/iyear/tdl)

---

**注意**：这是 TDL 的非官方 GUI 客户端。与 Telegram 或 TDL 项目无关联。
