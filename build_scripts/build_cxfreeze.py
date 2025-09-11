#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MemoTrace cx_Freeze打包脚本
使用cx_Freeze将MemoTrace打包为独立的.exe文件
cx_Freeze在某些情况下兼容性更好

作者：软件打包专家
版本：1.0
日期：2024-12-19
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from memotrace_version import __version__, __app_name__
from build_scripts.common_build_util import ensure_icon, create_version_file


class MemoTraceCxFreezePacker:
    """MemoTrace cx_Freeze打包器"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.build_dir = self.root_dir / "build_cx_freeze"
        self.dist_dir = self.root_dir / "dist_cx_freeze"
        self.main_script = self.root_dir / "example" / "3-exporter.py"
        
    def check_environment(self):
        """检查打包环境"""
        print("【步骤1】检查环境配置...")
        
        # 检查Python版本
        python_version = sys.version_info
        print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            raise Exception("需要Python 3.8及以上版本")
            
        # 检查是否在Windows环境
        if os.name != 'nt':
            print("⚠️ 警告: 当前不在Windows环境，某些Windows特定功能可能无法正常工作")
        
        # 检查主脚本
        if not self.main_script.exists():
            raise Exception(f"主脚本不存在: {self.main_script}")
            
        print("✅ 环境检查完成")
        
    def install_dependencies(self):
        """安装依赖"""
        print("\n【步骤2】安装依赖库...")
        
        # 升级pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # 安装cx_Freeze
        subprocess.run([sys.executable, "-m", "pip", "install", "cx_Freeze"], check=True)
        
        # 安装项目依赖
        requirements_file = self.root_dir / "requirements.txt"
        if requirements_file.exists():
            print("安装项目依赖...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], check=True)
        
        print("✅ 依赖安装完成")
        
    def prepare_build_dirs(self):
        """准备构建目录"""
        print("\n【步骤3】准备构建目录...")
        
        # 清理旧的构建目录
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            
        # 创建新目录
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ 构建目录准备完成")
        
    def create_setup_file(self):
        """创建cx_Freeze setup文件"""
        print("\n【步骤4】创建cx_Freeze配置文件...")
        
    icon_path = ensure_icon(self.root_dir)
    version_file = create_version_file(self.root_dir)
    setup_content = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable
from pathlib import Path

# 项目根目录
root_dir = Path(r"{self.root_dir}")

# 包含的文件和目录
include_files = [
    (str(root_dir / "exporter" / "resources"), "exporter/resources"),
    (str(root_dir / "exporter" / "ffmpeg.exe"), "exporter/ffmpeg.exe"),
    (str(root_dir / "wxManager" / "decrypt" / "version_list.json"), "wxManager/decrypt/version_list.json"),
]

# 添加emoji表情包目录（如果存在）
emoji_dir = root_dir / "exporter" / "resources" / "emoji"
if emoji_dir.exists():
    include_files.append((str(emoji_dir), "exporter/resources/emoji"))

# 包含的包
packages = [
    "multiprocessing",
    "PIL",
    "win32api",
    "win32con",
    "win32gui", 
    "win32process",
    "win32file",
    "pywintypes",
    "psutil",
    "yara",
    "pymem",
    "lxml",
    "bs4",
    "openpyxl",
    "cryptography",
    "Crypto",
    "requests",
    "dateparser",
    "xmltodict",
    "aiofiles",
    "typing_extensions",
    "json",
    "sqlite3",
    "xml",
    "html",
    "urllib",
    "http",
    "email",
    "encodings",
]

# 排除的模块
excludes = [
    "tkinter",
    "unittest",
    "test",
    "distutils",
]

# 构建选项
build_exe_options = {{
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "build_exe": str(Path(r"{self.dist_dir}") / "MemoTrace"),
    "optimize": 2,
    "include_msvcrt": True,
}}

# 可执行文件配置
executables = [
    Executable(
        r"{self.main_script}",
        base="Win32GUI" if sys.platform == "win32" else None,  # 隐藏控制台窗口
        target_name="MemoTrace.exe",
        icon=r"{icon_path}",
    )
]

setup(
    name="{__app_name__}",
    version="{__version__}",
    description="微信聊天记录解析和导出工具",
    options={{"build_exe": build_exe_options}},
    executables=executables
)
'''
        
        setup_file = self.build_dir / "setup_cx_freeze.py"
        with open(setup_file, "w", encoding="utf-8") as f:
            f.write(setup_content)
            
        self.setup_file = setup_file
        print(f"✅ Setup文件已创建: {setup_file}")
        
    def build_executable(self):
        """构建可执行文件"""
        print("\n【步骤5】开始使用cx_Freeze打包...")
        
        # 切换到构建目录
        original_cwd = os.getcwd()
        os.chdir(self.build_dir)
        
        try:
            # 运行cx_Freeze
            cmd = [sys.executable, str(self.setup_file), "build"]
            
            print(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode != 0:
                print(f"❌ cx_Freeze打包失败:")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                raise Exception("cx_Freeze打包失败")
                
            print("✅ cx_Freeze打包完成")
            
        finally:
            os.chdir(original_cwd)
            
    def create_launcher_script(self):
        """创建启动脚本"""
        print("\n【步骤6】创建启动脚本...")
        
        launcher_content = '''@echo off
chcp 65001 > nul
title MemoTrace - 微信聊天记录解析工具 (cx_Freeze版本)

echo ========================================
echo   MemoTrace 启动器 (cx_Freeze版本)
echo ========================================
echo.

cd /d "%~dp0MemoTrace"

REM 检查文件是否存在
if not exist "MemoTrace.exe" (
    echo ❌ 错误：MemoTrace.exe 未找到！
    echo 请确保在正确的目录中运行此脚本。
    pause
    exit /b 1
)

echo 🚀 正在启动 MemoTrace (cx_Freeze版本)...
echo 📝 cx_Freeze版本具有良好的兼容性
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
'''
        
        launcher_file = self.dist_dir / "启动MemoTrace_CxFreeze.bat"
        with open(launcher_file, "w", encoding="gbk") as f:  # 使用GBK编码兼容Windows
            f.write(launcher_content)
            
        print(f"✅ 启动脚本已创建: {launcher_file}")
        
    def create_readme(self):
        """创建使用说明"""
        print("\n【步骤7】创建使用说明...")
        
        readme_content = '''# MemoTrace 使用说明 (cx_Freeze版本)

## 简介
此版本使用cx_Freeze打包工具生成，具有以下特点：
- 良好的跨平台兼容性
- 模块化的文件结构
- 相对较小的启动开销
- 对Python标准库的良好支持

## 运行要求
- Windows 10/11 系统
- 已安装微信客户端
- 具有管理员权限（用于访问微信数据库）

## 使用步骤

### 1. 启动程序
- 双击 `启动MemoTrace_CxFreeze.bat` 或进入MemoTrace文件夹运行 `MemoTrace.exe`
- 如果出现闪退，请右键选择"以管理员身份运行"

### 2. 文件结构特点
cx_Freeze生成的是一个文件夹结构，包含：
- MemoTrace.exe：主程序
- 各种.dll文件：运行库
- lib/：Python库文件
- 资源文件夹：程序需要的数据文件

### 3. 兼容性优势
- 对Windows系统API调用更稳定
- 对不同Python版本兼容性更好
- 模块化结构便于问题排查

## 打包工具对比

### cx_Freeze
- 优点：兼容性好，模块化结构，问题易排查
- 缺点：文件较多，体积相对较大

### PyInstaller
- 优点：单文件输出，使用广泛
- 缺点：可能存在兼容性问题

### Nuitka
- 优点：性能最好，启动最快
- 缺点：打包时间长，对某些模块支持有限

## 推荐使用场景
- 其他打包方式失败时的备选方案
- 需要良好兼容性的场合
- 需要调试和排查问题时

## 常见问题
与其他版本相同，详见主版本的使用说明.md文件

## 技术支持
如遇问题，请查看项目主页：https://github.com/shixiaogaoya/MemoTrace

## 免责声明
- 本工具仅供学习研究使用
- 请遵守相关法律法规
- 不得用于非法用途
'''
        
        readme_file = self.dist_dir / "使用说明_CxFreeze.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)
            
        print(f"✅ 使用说明已创建: {readme_file}")
        
    def package_complete(self):
        """打包完成后的处理"""
        print("\n【步骤8】完成打包...")
        
        exe_file = self.dist_dir / "MemoTrace" / "MemoTrace.exe"
        if exe_file.exists():
            file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
            
            # 计算整个文件夹大小
            folder_size = sum(f.stat().st_size for f in (self.dist_dir / "MemoTrace").rglob('*') if f.is_file()) / (1024 * 1024)
            
            print(f"✅ cx_Freeze打包成功！")
            print(f"📦 可执行文件: {exe_file}")
            print(f"📏 可执行文件大小: {file_size:.1f} MB")
            print(f"📁 整个程序大小: {folder_size:.1f} MB")
            print(f"📁 输出目录: {self.dist_dir}")
            print(f"🔧 特点: 模块化结构，兼容性良好")
        else:
            raise Exception("打包失败：未找到生成的exe文件")
            
    def run_build(self):
        """执行完整的打包流程"""
        try:
            print("🚀 开始MemoTrace cx_Freeze打包流程...")
            print("=" * 50)
            
            self.check_environment()
            self.install_dependencies()  
            self.prepare_build_dirs()
            self.create_setup_file()
            self.build_executable()
            self.create_launcher_script()
            self.create_readme()
            self.package_complete()
            
            print("\n" + "=" * 50)
            print("🎉 MemoTrace cx_Freeze打包完成！")
            print(f"📁 输出目录: {self.dist_dir}")
            print("📖 使用方法: 查看 '使用说明_CxFreeze.md' 文件")
            print("🚀 快速启动: 双击 '启动MemoTrace_CxFreeze.bat'")
            print("🔧 优势: 此版本兼容性最好，适合作为备选方案")
            
        except Exception as e:
            print(f"\n❌ 打包过程中出现错误: {str(e)}")
            print("请检查错误信息并重试，或尝试其他打包方式")
            return False
            
        return True


if __name__ == "__main__":
    packer = MemoTraceCxFreezePacker()
    success = packer.run_build()
    
    if not success:
        input("\n按回车键退出...")
        sys.exit(1)
    else:
        input("\n打包完成，按回车键退出...")