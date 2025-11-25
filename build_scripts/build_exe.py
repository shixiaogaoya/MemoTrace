#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MemoTrace 本地打包脚本
使用PyInstaller将MemoTrace打包为独立的.exe文件

作者：软件打包专家
版本：1.0
日期：2024-12-19
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from textwrap import dedent

from memotrace_version import __version__, __app_name__
from build_scripts.common_build_util import ensure_icon, create_version_file


class MemoTracePacker:
    """MemoTrace打包器"""

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.build_dir = self.root_dir / "build_output"
        self.dist_dir = self.root_dir / "dist_local"
        self.main_script = self.root_dir / "example" / "3-exporter.py"

    def check_environment(self):
        """检查打包环境"""
        print("【步骤1】检查环境配置...")

        python_version = sys.version_info
        print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")

        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            raise Exception("需要Python 3.8及以上版本")

        if os.name != "nt":
            print("⚠️ 警告: 当前不在Windows环境，某些Windows特定功能可能无法正常工作")

        if not self.main_script.exists():
            raise Exception(f"主脚本不存在: {self.main_script}")

        print("✅ 环境检查完成")

    def install_dependencies(self):
        """安装依赖"""
        print("\n【步骤2】安装依赖库...")

        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=5.0"], check=True)

        requirements_file = self.root_dir / "requirements.txt"
        if requirements_file.exists():
            print("安装项目依赖...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], check=True)

        print("✅ 依赖安装完成")

    def prepare_build_dirs(self):
        """准备构建目录"""
        print("\n【步骤3】准备构建目录...")

        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)

        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.dist_dir.mkdir(parents=True, exist_ok=True)

        print("✅ 构建目录准备完成")

    def create_spec_file(self):
        """创建PyInstaller spec文件"""
        print("\n【步骤4】创建PyInstaller配置文件...")

        icon_path = ensure_icon(self.root_dir)
        version_file = create_version_file(self.root_dir)

        spec_content = dedent(
            f"""# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# 项目根目录
root_dir = Path(r"{self.root_dir}")

# 数据文件和资源文件
datas = [
    (str(root_dir / "exporter" / "resources"), "exporter/resources"),
    (str(root_dir / "exporter" / "ffmpeg.exe"), "exporter"),
    (str(root_dir / "wxManager" / "decrypt" / "version_list.json"), "wxManager/decrypt"),
]

# 隐藏导入
hiddenimports = [
    'multiprocessing',
    'PIL._tkinter_finder',
    'win32api',
    'win32con',
    'win32gui',
    'win32process',
    'win32file',
    'pywintypes',
    'psutil',
    'yara',
    'pymem',
    'lxml',
    'bs4',
    'openpyxl',
    'cryptography',
    'Crypto',
    'requests',
    'dateparser',
    'xmltodict',
    'aiofiles',
    'typing_extensions',
]

# 二进制文件
binaries = []

# 添加emoji表情包目录（如果存在）
emoji_dir = root_dir / "exporter" / "resources" / "emoji"
if emoji_dir.exists():
    datas.append((str(emoji_dir), "exporter/resources/emoji"))

# 创建分析对象
a = Analysis(
    [r"{self.main_script}"],
    pathex=[str(root_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 创建PYZ对象
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建EXE对象
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{__app_name__}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 隐藏控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r"{icon_path}",
    version_file=r"{version_file}",
)
"""
        )

        spec_file = self.build_dir / "MemoTrace.spec"
        with open(spec_file, "w", encoding="utf-8") as file:
            file.write(spec_content)

        self.spec_file = spec_file
        print(f"✅ Spec文件已创建: {spec_file}")

    def build_executable(self):
        """构建可执行文件"""
        print("\n【步骤5】开始打包...")

        original_cwd = os.getcwd()
        os.chdir(self.root_dir)

        try:
            cmd = [
                "pyinstaller",
                "--clean",
                "--distpath",
                str(self.dist_dir),
                "--workpath",
                str(self.build_dir / "work"),
                str(self.spec_file),
            ]

            print(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

            if result.returncode != 0:
                print("❌ 打包失败:")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                raise Exception("PyInstaller打包失败")

            print("✅ 打包完成")
        finally:
            os.chdir(original_cwd)

    def create_launcher_script(self):
        """创建启动脚本"""
        print("\n【步骤6】创建启动脚本...")

        launcher_content = dedent(
            """@echo off
chcp 65001 > nul
title MemoTrace - 微信聊天记录解析工具

echo ========================================
echo        MemoTrace 启动器
echo ========================================
echo.

REM 检查文件是否存在
if not exist "MemoTrace.exe" (
    echo ❌ 错误：MemoTrace.exe 未找到！
    echo 请确保在正确的目录中运行此脚本。
    pause
    exit /b 1
)

echo 🚀 正在启动 MemoTrace...
echo.

REM 尝试以管理员权限运行
MemoTrace.exe

if %ERRORLEVEL% neq 0 (
    echo.
    echo ⚠️  如果出现权限问题，请：
    echo 1. 右键点击此脚本，选择"以管理员身份运行"
    echo 2. 或者右键点击 MemoTrace.exe，选择"以管理员身份运行"
    echo 3. 如果杀毒软件提示威胁，请选择"允许"或"信任"
    echo.
    pause
)
"""
        )

        launcher_file = self.dist_dir / "启动MemoTrace.bat"
        with open(launcher_file, "w", encoding="gbk") as file:  # 使用GBK编码兼容Windows
            file.write(launcher_content)

        print(f"✅ 启动脚本已创建: {launcher_file}")

    def create_readme(self):
        """创建使用说明"""
        print("\n【步骤7】创建使用说明...")

        readme_content = dedent(
            """# MemoTrace 使用说明

## 简介
MemoTrace 是一个微信聊天记录解析和导出工具，支持将微信聊天数据导出为多种格式。

## 运行要求
- Windows 10/11 系统
- 已安装微信客户端
- 具有管理员权限（用于访问微信数据库）

## 使用步骤

### 1. 启动程序
- 双击 `启动MemoTrace.bat` 或直接运行 `MemoTrace.exe`
- 如果出现闪退，请右键选择"以管理员身份运行"

### 2. 使用流程
1. 首先运行数据解析，生成数据库文件夹
2. 查看联系人列表，获取要导出的联系人信息
3. 配置导出参数（格式、时间范围等）
4. 执行导出操作

### 3. 输出文件
- 解析后的数据库：`./wxid_xxx/db_storage`（微信4.0）或 `./wxid_xxx/Msg`（微信3.x）
- 导出的聊天记录：`./data/` 目录下

## 支持的导出格式
- HTML：完整的聊天界面，支持图片、表情、文件等
- TXT：纯文本格式
- DOCX：Word文档格式
- XLSX：Excel表格格式
- Markdown：Markdown文档格式

## 常见问题

### 程序闪退
1. 右键程序，选择"以管理员身份运行"
2. 重启微信客户端
3. 重启电脑
4. 检查杀毒软件是否误报，添加到白名单

### 权限问题
- 确保以管理员身份运行
- 关闭微信客户端后再运行程序
- 检查用户账户控制(UAC)设置

### 杀毒软件误报
- 将程序添加到杀毒软件白名单
- 临时关闭实时保护
- 下载时选择"保留"或"信任"

### 找不到微信数据
- 确保微信已登录
- 检查微信版本是否支持（支持3.x和4.0版本）
- 尝试重新登录微信

## 技术支持
如遇问题，请查看项目主页：https://github.com/shixiaogaoya/MemoTrace

## 免责声明
- 本工具仅供学习研究使用
- 请遵守相关法律法规
- 不得用于非法用途
"""
        )

        readme_file = self.dist_dir / "使用说明.md"
        with open(readme_file, "w", encoding="utf-8") as file:
            file.write(readme_content)

        print(f"✅ 使用说明已创建: {readme_file}")

    def package_complete(self):
        """打包完成后的处理"""
        print("\n【步骤8】完成打包...")

        exe_file = self.dist_dir / "MemoTrace.exe"
        if exe_file.exists():
            file_size = exe_file.stat().st_size / (1024 * 1024)
            print("✅ 打包成功！")
            print(f"📦 可执行文件: {exe_file}")
            print(f"📏 文件大小: {file_size:.1f} MB")
            print(f"📁 输出目录: {self.dist_dir}")
        else:
            raise Exception("打包失败：未找到生成的exe文件")

    def run_build(self):
        """执行完整的打包流程"""
        try:
            print("🚀 开始MemoTrace打包流程...")
            print("=" * 50)

            self.check_environment()
            self.install_dependencies()
            self.prepare_build_dirs()
            self.create_spec_file()
            self.build_executable()
            self.create_launcher_script()
            self.create_readme()
            self.package_complete()

            print("\n" + "=" * 50)
            print("🎉 MemoTrace打包完成！")
            print(f"📁 输出目录: {self.dist_dir}")
            print("📖 使用方法: 查看 '使用说明.md' 文件")
            print("🚀 快速启动: 双击 '启动MemoTrace.bat'")

        except Exception as exc:
            print(f"\n❌ 打包过程中出现错误: {exc}")
            print("请检查错误信息并重试")
            return False

        return True


if __name__ == "__main__":
    packer = MemoTracePacker()
    success = packer.run_build()

    if not success:
        input("\n按回车键退出...")
        sys.exit(1)
    else:
        input("\n打包完成，按回车键退出...")
