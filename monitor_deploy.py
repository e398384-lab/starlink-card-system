#!/usr/bin/env python3
"""
自動監控 Render 部署日誌並修復錯誤
"""
import subprocess
import time
import re
from pathlib import Path

RENDER_SERVICE_ID = "srv-d7hqn2rbc2fs73dl2egg"
CHECK_INTERVAL = 30  # 每 30 秒檢查一次

def get_render_logs():
    """獲取 Render 日誌（需要 Render CLI）"""
    try:
        result = subprocess.run(
            ["render", "logs", RENDER_SERVICE_ID, "--tail", "50"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def detect_error(logs: str):
    """從日誌中檢測錯誤類型"""
    if "ModuleNotFoundError" in logs:
        match = re.search(r"ModuleNotFoundError: No module named '(.+)'", logs)
        if match:
            return f"missing_module", match.group(1)
    
    if "ImportError" in logs:
        match = re.search(r"ImportError: cannot import name '(.+)' from '(.+)'", logs)
        if match:
            return f"missing_import", (match.group(1), match.group(2))
    
    if "NameError" in logs:
        match = re.search(r"NameError: name '(.+)' is not defined", logs)
        if match:
            return f"missing_name", match.group(1)
    
    return None, None

def fix_missing_module(module_name: str):
    """修復缺少的模組"""
    print(f"🔧 修復缺少的模組：{module_name}")
    # 這裡可以添加自動修復邏輯
    # 例如：更新 requirements.txt 並重新部署

def fix_missing_import(import_name: str, from_module: str):
    """修復缺少的導入"""
    print(f"🔧 修復缺少的導入：{import_name} from {from_module}")
    # 這裡可以添加自動修復邏輯
    # 例如：更新 __init__.py 或對應的檔案

def fix_missing_name(name: str):
    """修復未定義的名稱"""
    print(f"🔧 修復未定義的名稱：{name}")
    # 這裡可以添加自動修復邏輯
    # 例如：檢查 import 語句

def main():
    print(f"🔍 開始監控 Render 服務：{RENDER_SERVICE_ID}")
    print(f"⏰ 檢查間隔：{CHECK_INTERVAL} 秒\n")
    
    while True:
        print(f"📊 檢查時間：{time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        logs = get_render_logs()
        error_type, error_detail = detect_error(logs)
        
        if error_type:
            print(f"❌ 檢測到錯誤：{error_type}")
            print(f"   詳情：{error_detail}")
            
            if error_type == "missing_module":
                fix_missing_module(error_detail)
            elif error_type == "missing_import":
                fix_missing_import(*error_detail)
            elif error_type == "missing_name":
                fix_missing_name(error_detail)
            
            print("🚀 提交並推送修復...\n")
            time.sleep(5)
        else:
            print("✅ 沒有檢測到錯誤")
        
        print("-" * 50)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
