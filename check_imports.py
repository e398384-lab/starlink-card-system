#!/usr/bin/env python3
"""
自動檢查並修復 FastAPI 路由檔案的導入問題
"""
import re
import sys
from pathlib import Path

BASE_PATH = Path(__file__).parent / "starlink-card-system"

ROUTER_FILES = [
    "app/routers/auth.py",
    "app/routers/merchants.py",
    "app/routers/cards.py",
    "app/routers/teams.py"
]

def check_and_fix_imports(file_path: str):
    """檢查並修復檔案中的導入問題"""
    full_path = BASE_PATH / file_path
    
    if not full_path.exists():
        print(f"❌ 檔案不存在: {file_path}")
        return False
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    # 提取當前的導入
    model_import_match = re.search(r'from app\.models import (.+)', content, re.MULTILINE)
    if not model_import_match:
        print(f"⚠️  {file_path}: 沒有找到 app.models 導入")
        return True
    
    current_imports = [m.strip() for m in model_import_match.group(1).split(',')]
    
    # 檢查需要使用的模型
    all_models = ['User', 'Merchant', 'StarLinkCard', 'Transaction', 'TeamsMessage', 
                  'CardStateEnum', 'TransactionTypeEnum', 'MerchantType', 'MerchantStatus']
    
    used_models = []
    for model in all_models:
        if re.search(rf'\b{model}\b', content):
            used_models.append(model)
    
    missing = [m for m in used_models if m not in current_imports]
    
    if not missing:
        print(f"✅ {file_path}: 導入完整")
        return True
    
    # 修復導入
    new_imports = sorted(set(current_imports + missing))
    new_import_line = f"from app.models import {', '.join(new_imports)}"
    
    old_import_line = f"from app.models import {', '.join(current_imports)}"
    
    # 替換
    new_content = content.replace(old_import_line, new_import_line)
    
    with open(full_path, 'w') as f:
        f.write(new_content)
    
    print(f"🔧 {file_path}: 已添加缺失的導入: {missing}")
    return True

def main():
    print("🔍 開始檢查路由檔案的導入問題...\n")
    
    all_ok = True
    for file_path in ROUTER_FILES:
        if not check_and_fix_imports(file_path):
            all_ok = False
    
    if all_ok:
        print("\n✅ 所有檔案檢查完成，沒有問題！")
        return 0
    else:
        print("\n❌ 部分檔案有問題，請手動檢查")
        return 1

if __name__ == "__main__":
    sys.exit(main())
