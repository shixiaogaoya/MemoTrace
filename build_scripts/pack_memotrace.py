#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MemoTrace 主打包脚本
提供多种打包方式选择，自动处理依赖问题和兼容性问题

作者：软件打包专家
版本：1.0
日期：2024-12-19
"""

import os
import sys
import subprocess
import time
from pathlib import Path


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
        
        # 检查操作系统
        if os.name == 'nt':
            print("✅ 操作系统：Windows")
        else:
            print("⚠️  操作系统：非Windows系统（某些功能可能受限）")
            
        # 检查Python版本
        python_version = sys.version_info
        print(f"✅ Python版本：{python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python版本过低，需要 Python 3.8 及以上版本")
            return False
            
        # 检查项目文件
        main_script = self.root_dir / "example" / "3-exporter.py"
        if main_script.exists():
            print("✅ 项目文件：主脚本找到")
        else:
            print("❌ 项目文件：主脚本未找到")
            return False
            
        # 检查依赖文件
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
        
    def handle_dependency_issues(self):
        """处理依赖问题"""
        print("【依赖问题处理】")
        print("-" * 30)
        
        print("正在检查和处理常见依赖问题...")
        
        try:
            # 检查关键依赖
            critical_deps = ['pywin32', 'psutil', 'pillow', 'openpyxl']
            missing_deps = []
            
            for dep in critical_deps:
                try:
                    __import__(dep.replace('-', '_').lower())
                    print(f"✅ {dep}: 已安装")
                except ImportError:
                    print(f"❌ {dep}: 未安装")
                    missing_deps.append(dep)
                    
            if missing_deps:
                print(f"\\n发现缺失依赖: {', '.join(missing_deps)}")
                print("建议先安装项目依赖：pip install -r requirements.txt")
                
                choice = input("\\n是否继续打包？(y/n): ").strip().lower()
                if choice != 'y':
                    return False
                    
            print("✅ 依赖检查完成")
            return True
            
        except Exception as e:
            print(f"⚠️  依赖检查过程中出现问题: {e}")
            print("建议手动安装依赖后重试")
            return True  # 不阻止继续进行
            
    def run_packer(self, packer_type):
        """运行指定的打包器"""
        script_map = {
            '1': 'build_exe.py',
            '2': 'build_nuitka.py', 
            '3': 'build_cxfreeze.py'
        }
        
        if packer_type not in script_map:
            print("❌ 无效的打包方式")
            return False
            
        script_name = script_map[packer_type]
        script_path = self.script_dir / script_name
        
        if not script_path.exists():
            print(f"❌ 打包脚本未找到: {script_path}")
            return False
            
        print(f"\\n🚀 开始执行 {script_name}...")
        print("=" * 50)
        
        try:
            # 运行打包脚本
            result = subprocess.run([sys.executable, str(script_path)], 
                                  cwd=str(self.root_dir),
                                  capture_output=False)
            
            if result.returncode == 0:
                print("\\n✅ 打包完成！")
                return True
            else:
                print(f"\\n❌ 打包失败，退出码: {result.returncode}")
                return False
                
        except Exception as e:
            print(f"\\n❌ 运行打包脚本时出错: {e}")
            return False
            
    def run_all_packers(self):
        """运行所有打包器"""
        print("\\n🚀 开始全部打包流程...")
        print("=" * 50)
        
        packers = [
            ('1', 'PyInstaller'),
            ('2', 'Nuitka'), 
            ('3', 'cx_Freeze')
        ]
        
        results = {}
        
        for packer_id, packer_name in packers:
            print(f"\\n📦 正在使用 {packer_name} 打包...")
            start_time = time.time()
            
            success = self.run_packer(packer_id)
            end_time = time.time()
            
            results[packer_name] = {
                'success': success,
                'time': end_time - start_time
            }
            
            if success:
                print(f"✅ {packer_name} 打包成功，耗时: {end_time - start_time:.1f}秒")
            else:
                print(f"❌ {packer_name} 打包失败")
                
            # 稍作停顿
            time.sleep(2)
            
        # 显示总结
        print("\\n" + "=" * 50)
        print("📊 打包结果总结:")
        print("-" * 30)
        
        for packer_name, result in results.items():
            status = "✅ 成功" if result['success'] else "❌ 失败"
            time_str = f"{result['time']:.1f}秒" if result['success'] else "N/A"
            print(f"{packer_name:<12}: {status:<6} (耗时: {time_str})")
            
        successful_count = sum(1 for r in results.values() if r['success'])
        print(f"\\n成功打包: {successful_count}/3 种方式")
        
        return successful_count > 0
        
    def show_troubleshooting(self):
        """显示问题排查指南"""
        print("\\n【常见问题解决方案】")
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
        
    def main(self):
        """主函数"""
        self.show_welcome()
        
        # 系统检查
        if not self.check_system_requirements():
            print("❌ 系统检查失败，请解决上述问题后重试")
            input("按回车键退出...")
            return
            
        # 依赖处理
        if not self.handle_dependency_issues():
            print("❌ 用户选择退出")
            return
            
        while True:
            self.show_packing_options()
            
            try:
                choice = input("请选择打包方式 (0-4): ").strip()
                
                if choice == '0':
                    print("👋 感谢使用 MemoTrace 打包工具！")
                    break
                elif choice in ['1', '2', '3']:
                    success = self.run_packer(choice)
                    if success:
                        print("\\n🎉 打包完成！请查看输出目录中的文件。")
                    else:
                        print("\\n💡 提示：可以尝试其他打包方式，或查看问题排查指南。")
                        self.show_troubleshooting()
                elif choice == '4':
                    success = self.run_all_packers()
                    if success:
                        print("\\n🎉 批量打包完成！请查看各个输出目录。")
                    else:
                        print("\\n💡 所有打包方式都失败了，请查看问题排查指南。")
                        self.show_troubleshooting()
                else:
                    print("❌ 无效选择，请输入 0-4 之间的数字")
                    
            except KeyboardInterrupt:
                print("\\n\\n👋 用户中断，感谢使用！")
                break
            except Exception as e:
                print(f"\\n❌ 发生错误: {e}")
                continue
                
            # 询问是否继续
            if choice != '0':
                print("\\n" + "=" * 50)
                continue_choice = input("是否继续使用打包工具？(y/n): ").strip().lower()
                if continue_choice != 'y':
                    print("👋 感谢使用 MemoTrace 打包工具！")
                    break
                    
        input("\\n按回车键退出...")


if __name__ == "__main__":
    packer = MemoTraceMainPacker()
    packer.main()