#!/usr/bin/env python3
"""
Cursor Push Routes - 自动化Git推送流程
使用方法: python scripts/cursor_push.py "commit message"
"""

import subprocess
import sys
import os
from typing import Optional

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_status(message: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def print_success(message: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def run_command(command: str, check: bool = True) -> Optional[subprocess.CompletedProcess]:
    """执行shell命令"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"命令执行失败: {command}")
            print_error(f"错误信息: {e.stderr}")
        return None

def check_git_status():
    """检查Git状态"""
    print_status("检查当前Git状态...")
    result = run_command("git status --porcelain")
    if result and result.stdout.strip():
        print("有未提交的更改:")
        run_command("git status")
        return True
    else:
        print_warning("没有检测到需要提交的更改")
        return False

def add_and_commit(commit_message: str):
    """添加并提交更改"""
    print_status("添加所有更改到暂存区...")
    run_command("git add .")
    
    # 检查是否有暂存的更改
    result = run_command("git diff --cached --quiet", check=False)
    if result and result.returncode == 0:
        print_warning("没有检测到需要提交的更改")
        return False
    
    print_status("提交更改...")
    run_command(f'git commit -m "{commit_message}"')
    return True

def handle_remote_sync():
    """处理远程同步"""
    print_status("检查远程分支状态...")
    run_command("git fetch origin")
    
    # 检查是否落后于远程分支
    result = run_command("git rev-list --count HEAD..origin/main")
    if result:
        behind_count = int(result.stdout.strip())
        if behind_count > 0:
            print_warning(f"本地分支落后远程分支 {behind_count} 个提交，需要合并")
            
            print_status("尝试合并远程更改...")
            merge_result = run_command("git pull origin main --no-rebase", check=False)
            
            if merge_result and merge_result.returncode != 0:
                print_error("合并失败，存在冲突")
                print_status("请手动解决冲突，然后运行:")
                print("  git add .")
                print('  git commit -m "Merge remote changes and resolve conflicts"')
                print("  git push origin main")
                return False
            else:
                print_success("成功合并远程更改")
    
    return True

def push_to_remote():
    """推送到远程仓库"""
    print_status("推送到远程仓库...")
    result = run_command("git push origin main", check=False)
    
    if result and result.returncode == 0:
        print_success("成功推送到远程仓库!")
        
        # 显示最新提交信息
        print_status("最新提交信息:")
        run_command("git log --oneline -1")
        return True
    else:
        print_error("推送失败")
        return False

def main():
    # 检查参数
    if len(sys.argv) != 2:
        print_error("请提供提交信息")
        print(f"使用方法: python {sys.argv[0]} \"your commit message\"")
        sys.exit(1)
    
    commit_message = sys.argv[1]
    
    print_status("开始 Cursor Push 流程...")
    print_status(f"提交信息: {commit_message}")
    
    # 确保在正确的目录
    if not os.path.exists('.git'):
        print_error("当前目录不是Git仓库")
        sys.exit(1)
    
    try:
        # 1. 检查状态并提交
        if not check_git_status():
            sys.exit(0)
        
        if not add_and_commit(commit_message):
            sys.exit(0)
        
        # 2. 处理远程同步
        if not handle_remote_sync():
            sys.exit(1)
        
        # 3. 推送到远程
        if push_to_remote():
            print_success("Push 流程完成!")
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_error("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"发生未预期的错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 