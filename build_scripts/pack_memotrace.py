#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MemoTrace 主打包脚本
提供多种打包方式选择，自动处理依赖问题和兼容性问题
"""

import argparse
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

from build_scripts.build_cxfreeze import MemoTraceCxFreezePacker
from build_scripts.build_exe import MemoTracePacker
from build_scripts.build_nuitka import MemoTraceNuitkaPacker


class MemoTraceMainPacker:
    """MemoTrace主打包器"""

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.script_dir = Path(__file__).parent

    def show_welcome(self):
        """显示欢迎信息"""
        print("=" * 60)
        print("🚀 MemoTrace 专业打包工具")
        print("=" * 60)
        print()
        print("📋 功能：将 MemoTrace 微信聊天记录解析工具打包为独立的 .exe 文件")
        print("🎯 目标：生成可在本地运行的独立可执行文件，无需安装依赖")
        print("💡 特点：处理依赖问题、路径问题、兼容性问题")
        print()

    def check_system_requirements(self):
        """检查系统要求"""
        print("【系统检查】")
        print("-" * 30)

        if os.name == "nt":
            print("✅ 操作系统：Windows")
        else:
            print("⚠️  操作系统：非Windows系统（某些功能可能受限）")

        python_version = sys.version_info
        print(f"✅ Python版本：{python_version.major}.{python_version.minor}.{python_version.micro}")

        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python版本过低，需要 Python 3.8 及以上版本")
            return False

        main_script = self.root_dir / "example" / "3-exporter.py"
        if main_script.exists():
            print("✅ 项目文件：主脚本找到")
        else:
            print("❌ 项目文件：主脚本未找到")
            return False

        requirements_file = self.root_dir / "requirements.txt"
        if requirements_file.exists():
            print("✅ 依赖配置：requirements.txt 找到")
        else:
            print("❌ 依赖配置：requirements.txt 未找到")
            return False

        print("✅ 系统检查通过")
        print()
        return True

    def show_packing_options(self):
        """显示打包选项"""
        print("【打包方式选择】")
        print("-" * 30)
        print("1. PyInstaller 打包 (推荐)")
        print("   • 优点：成熟稳定，单文件输出，使用广泛")
        print("   • 缺点：文件较大，启动稍慢")
        print("   • 适合：大多数用户，首次打包")
        print()
        print("2. Nuitka 打包 (性能最佳)")
        print("   • 优点：编译型，启动快，内存占用少")
        print("   • 缺点：打包时间长，对某些模块支持有限")
        print("   • 适合：追求性能，频繁使用")
        print()
        print("3. cx_Freeze 打包 (兼容性最佳)")
        print("   • 优点：兼容性好，模块化结构，易于调试")
        print("   • 缺点：文件较多，体积相对较大")
        print("   • 适合：其他方式失败时的备选方案")
        print()
        print("4. 全部打包 (生成所有版本)")
        print("   • 生成三种版本，供用户选择最适合的")
        print("   • 需要较长时间，适合发布使用")
        print()
        print("0. 退出程序")
        print()

    def handle_dependency_issues(self, auto_confirm=False, non_interactive=False):
        """处理依赖问题，返回是否继续"""
        print("【依赖问题处理】")
        print("-" * 30)
        print("正在检查和处理常见依赖问题...")

        critical_deps = ["pywin32", "psutil", "pillow", "openpyxl"]
        missing_deps = [dep for dep in critical_deps if importlib.util.find_spec(dep) is None]

        if not missing_deps:
            print("✅ 依赖检查通过，未发现缺失依赖")
            print()
            return True

        print(f"⚠️  检测到缺失依赖: {', '.join(missing_deps)}")

        if non_interactive and not auto_confirm:
            print("❌ 非交互模式下未授权自动安装依赖，已终止")
            return False

        if auto_confirm:
            user_confirm = "y"
        elif non_interactive:
            user_confirm = "n"
        else:
            user_confirm = input("是否自动安装缺失依赖? (y/n): ").strip().lower()

        if user_confirm != "y":
            print("❌ 用户取消安装依赖，终止打包")
            return False

        try:
            cmd = [sys.executable, "-m", "pip", "install", *missing_deps]
            print(f"正在安装依赖: {' '.join(missing_deps)}")
            subprocess.run(cmd, check=True)
            print("✅ 依赖安装完成")
        except subprocess.CalledProcessError as exc:
            print(f"❌ 安装依赖失败: {exc}")
            return False

        print()
        return True

    def run_packer(self, choice):
        """根据选择运行打包器"""
        packer_map = {
            "1": (MemoTracePacker, "PyInstaller"),
            "2": (MemoTraceNuitkaPacker, "Nuitka"),
            "3": (MemoTraceCxFreezePacker, "cx_Freeze"),
        }

        packer_cls, name = packer_map.get(choice, (None, None))
        if not packer_cls:
            print("❌ 未知的打包方式")
            return False

        print(f"\n📦 正在使用 {name} 打包...")
        start_time = time.time()

        try:
            packer = packer_cls()
            success = packer.run_build()
        except Exception as exc:  # noqa: BLE001 - 提供用户可见错误信息
            print(f"❌ {name} 打包失败: {exc}")
            success = False

        end_time = time.time()
        elapsed = end_time - start_time

        if success:
            print(f"✅ {name} 打包完成，耗时 {elapsed:.1f} 秒")
        else:
            print(f"❌ {name} 打包未成功，耗时 {elapsed:.1f} 秒")

        return success

    def run_all_packers(self):
        """运行所有打包器"""
        print("\n🚀 开始全部打包流程...")
        print("=" * 50)

        packers = [
            ("1", "PyInstaller"),
            ("2", "Nuitka"),
            ("3", "cx_Freeze"),
        ]

        results = {}
        for packer_id, packer_name in packers:
            success = self.run_packer(packer_id)
            results[packer_name] = success
            time.sleep(2)

        print("\n" + "=" * 50)
        print("📊 打包结果总结:")
        print("-" * 30)
        for packer_name, status in results.items():
            status_text = "✅ 成功" if status else "❌ 失败"
            print(f"{packer_name:<12}: {status_text}")

        successful_count = sum(1 for status in results.values() if status)
        print(f"\n成功打包: {successful_count}/3 种方式")
        return successful_count > 0

    def show_troubleshooting(self):
        """显示问题排查指南"""
        print("\n【常见问题解决方案】")
        print("-" * 30)
        print("1. 权限问题:")
        print("   • 以管理员身份运行此脚本")
        print("   • 关闭杀毒软件实时保护")
        print("   • 将输出目录添加到杀毒软件白名单")
        print()
        print("2. 依赖问题:")
        print("   • 确保在正确的Python环境中运行")
        print("   • 手动安装缺失的依赖包")
        print("   • 使用虚拟环境避免依赖冲突")
        print()
        print("3. 路径问题:")
        print("   • 确保项目路径不包含中文或特殊字符")
        print("   • 使用较短的路径名")
        print("   • 避免路径中包含空格")
        print()
        print("4. 兼容性问题:")
        print("   • 尝试不同的打包方式")
        print("   • 检查Python版本兼容性")
        print("   • 更新相关依赖库到最新版本")
        print()

    def main(self, args=None):
        """主函数 / 支持非交互模式"""
        parser = argparse.ArgumentParser(description="MemoTrace 打包工具")
        parser.add_argument("--mode", "-m", choices=["1", "2", "3", "4"], help="指定打包方式: 1=PyInstaller 2=Nuitka 3=cx_Freeze 4=全部")
        parser.add_argument("--yes", "-y", action="store_true", help="自动确认依赖检查提示，适合CI/自动化")
        parser.add_argument("--no-input", action="store_true", help="完全非交互模式(出错直接退出)")
        parsed = parser.parse_args(args=args)

        self.show_welcome()

        if not self.check_system_requirements():
            print("❌ 系统检查失败，请解决上述问题后重试")
            if not parsed.no_input:
                input("按回车键退出...")
            sys.exit(1)

        if not self.handle_dependency_issues(auto_confirm=parsed.yes, non_interactive=parsed.no_input):
            if not parsed.no_input:
                input("按回车键退出...")
            sys.exit(1)

        if parsed.mode:
            if parsed.mode in ["1", "2", "3"]:
                ok = self.run_packer(parsed.mode)
            else:
                ok = self.run_all_packers()

            if not ok:
                print("❌ 打包失败")
                sys.exit(1)
            print("🎉 打包完成！")
            return

        while True:
            self.show_packing_options()
            try:
                choice = input("请选择打包方式 (0-4): ").strip()
                if choice == "0":
                    print("👋 感谢使用 MemoTrace 打包工具！")
                    break
                if choice in ["1", "2", "3"]:
                    success = self.run_packer(choice)
                    if success:
                        print("\n🎉 打包完成！请查看输出目录中的文件。")
                    else:
                        print("\n💡 提示：可以尝试其他打包方式，或查看问题排查指南。")
                        self.show_troubleshooting()
                elif choice == "4":
                    success = self.run_all_packers()
                    if success:
                        print("\n🎉 批量打包完成！请查看各个输出目录。")
                    else:
                        print("\n💡 所有打包方式都失败了，请查看问题排查指南。")
                        self.show_troubleshooting()
                else:
                    print("❌ 无效选择，请输入 0-4 之间的数字")
                    continue

                if choice != "0":
                    print("\n" + "=" * 50)
                    continue_choice = input("是否继续使用打包工具？(y/n): ").strip().lower()
                    if continue_choice != "y":
                        print("👋 感谢使用 MemoTrace 打包工具！")
                        break
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，感谢使用！")
                break
            except Exception as exc:  # noqa: BLE001 - 捕获并提示意外错误
                print(f"\n❌ 发生错误: {exc}")
                continue

        if not parsed.no_input:
            input("\n按回车键退出...")


if __name__ == "__main__":
    MemoTraceMainPacker().main()
