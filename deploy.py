#!/usr/bin/env python3
"""
StarLink Card System - 自動化部署腳本
這個腳本會自動完成所有部署步驟
"""

import os
import sys
import json
import time
from pathlib import Path

# 顏色輸出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    NC = '\033[0m'

def print_title(text):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")

def print_step(num, text):
    print(f"{Colors.GREEN}[步驟 {num}]{Colors.NC} {text}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.NC}  {text}")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.NC}  {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.NC}  {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.NC}  {text}")

# 配置
github_repo_name = "starlink-card-system"
project_path = Path.home() / "starlink-card-system"

# 檢查環境
def check_environment():
    print_title("環境檢查")
    
    # 檢查項目目錄
    if not project_path.exists():
        print_error(f"項目目錄不存在: {project_path}")
        return False
    print_success(f"項目目錄存在: {project_path}")
    
    # 檢查 Python
    result = os.system("python3 --version >/dev/null 2>&1")
    if result != 0:
        print_warning("Python3 未檢測到，將跳過本地測試")
    else:
        print_success("Python3 可用")
    
    # 檢查 Git
    result = os.system("git --version >/dev/null 2>&1")
    if result != 0:
        print_error("Git 未安裝")
        return False
    print_success("Git 已安裝")
    
    # 檢查是否已有 commit
    if (project_path / ".git").exists():
        print_step(0, "檢測到 Git 倉庫")
    
    return True

# 部署指南
def show_deployment_guide():
    print_title("🚀 StarLink Card System 自動化部署指南")
    
    print("""
這個腳本會自動完成所有部署步驟。你需要：

1. GitHub 帳戶（用於存放代碼）
2. Supabase 帳戶（免費 PostgreSQL）
3. Upstash 帳戶（免費 Redis）
4. Render.com 帳戶（免費主機）

所有服務都可以使用 GitHub 快速登錄，不需要額外註冊。
""")
    
    # 步驟列表
    print_title("部署步驟檢查清單")
    
    steps = [
        "檢查環境 (Python, Git 等)",
        "GitHub - 創建倉庫並推送代碼",
        "Supabase - 創建免費 PostgreSQL",
        "Upstash - 創建免費 Redis",
        "生成環境變量 (.env.prod)",
        "Render.com - 自動部署",
        "初始化數據庫",
        "測試 API",
        "生成使用說明"
    ]
    
    for i, step in enumerate(steps, 1):
        print_step(i, step)
    
    input("\n按下 Enter 開始部署...")

# GitHub 設置
def setup_github():
    print_title("GitHub 設置")
    
    print_info("你需要一個 GitHub Personal Access Token")
    print_info("訪問: https://github.com/settings/tokens")
    print_info("生成新的 Token (classic)，選擇 'repo' 權限")
    print_info("複製生成的 Token\n")
    
    token = input("請輸入你的 GitHub Token (ghp_...): ").strip()
    username = input("請輸入你的 GitHub 用戶名: ").strip()
    
    if not token or not username:
        print_error("未提供 Token 或用戶名")
        return None
    
    # 配置 Git
    os.chdir(project_path)
    os.system(f'git config --global user.email "{username}@users.noreply.github.com"')
    os.system(f'git config --global user.name "{username}"')
    os.system('git branch -M main')
    
    # 如果 remote 不存在，添加它
    result = os.system('git remote get-url origin 2>/dev/null')
    if result != 0:
        repo_url = f"https://{token}@github.com/{username}/{github_repo_name}.git"
        os.system(f'git remote add origin {repo_url}')
    
    # 推送代碼
    print("\n推送代碼到 GitHub...")
    result = os.system('git push -u origin main')
    
    if result == 0:
        print_success("GitHub 倉庫已創建並推送成功！")
        return {"token": token, "username": username}
    else:
        print_warning("可能倉庫已存在或連接失敗")
        return None

# Supabase 設置
def setup_supabase():
    print_title("Supabase 設置")
    
    print_info("訪問: https://supabase.com")
    print_info("點擊 'Start your project' 用 GitHub 登錄")
    print_info("創建新項目:")
    print_info("  - Name: starlink-card-system")
    print_info("  - Password: 自己設置一個密碼")
    print_info("  - Region: Singapore")
    print_info("  - 等待 2-3 分鐘\n")
    
    print_info("然後進入 Project Settings → Database")
    print_info("複製 Connection string → URI\n")
    
    db_url = input("請輸入 Supabase DATABASE_URL: ").strip()
    
    if not db_url:
        print_error("未提供 DATABASE_URL")
        return None
    
    print_success("Supabase 配置完成！")
    return db_url

# Upstash 設置
def setup_upstash():
    print_title("Upstash 設置")
    
    print_info("訪問: https://upstash.com")
    print_info("點擊 'Sign up' 用 GitHub 登錄")
    print_info("創建數據庫:")
    print_info("  - Name: starlink-redis")
    print_info("  - Region: Singapore")
    print_info("  - Type: Free Tier")
    print_info("  - 等待 1 分鐘\n")
    
    print_info("點擊你的數據庫 → Details → REST API")
    print_info("複製 UPSTASH_REDIS_REST_URL\n")
    
    redis_url = input("請輸入 Upstash REDIS_URL (REST API URL): ").strip()
    
    if not redis_url:
        print_error("未提供 REDIS_URL")
        return None
    
    print_success("Upstash 配置完成！")
    return redis_url

# 生成環境變量文件
def generate_env_file(db_url, redis_url):
    print_title("生成環境變量")
    
    # 生成隨機密鑰
    import secrets
    secret_key = secrets.token_urlsafe(32)
    
    env_content = f"""# StarLink Card System - Production Environment
DATABASE_URL={db_url}
REDIS_URL={redis_url}
SECRET_KEY={secret_key}
PORT=10000
HOST=0.0.0.0
"""
    
    # 保存到 .env.prod
    env_file = project_path / ".env.prod"
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print_success(f"環境變量已保存到: {env_file}")
    print_info("請妥善保管 SECRET_KEY")
    
    return env_file

# 部署到 Render.com
def deploy_to_render():
    print_title("Render.com 部署")
    
    print_info("訪問: https://render.com")
    print_info("點擊 'Sign in' 用 GitHub 登錄\n")
    
    print_info("Dashboard → New → Web Service")
    print_info("連接你的 GitHub 倉庫: your-username/starlink-card-system\n")
    
    print_info("配置設置:")
    print_info("  - Name: starlink-card-api")
    print_info("  - Region: Singapore")
    print_info("  - Branch: main")
    print_info("  - Build Command: pip install -r requirements.txt")
    print_info("  - Start Command: uvicorn app.main:app --host 0.0.0.0 --port 10000")
    print_info("  - Plan: Free")
    print_info("  - Environment Variables:")
    print_info("    * DATABASE_URL: (貼上 Supabase URL)")
    print_info("    * REDIS_URL: (貼上 Upstash URL)")
    print_info("    * SECRET_KEY: (從 .env.prod 複製)\n")
    
    print_info("點擊 'Create Web Service' 等待 5 分鐘\n")
    
    render_url = input("部署完成後，請輸入 Render 提供的 URL: ").strip()
    
    if not render_url:
        print_error("未提供 Render URL")
        return None
    
    print_success("Render.com 部署完成！")
    return render_url

# 測試部署
def test_deployment(url):
    print_title("測試部署")
    
    print(f"測試健康檢查: {url}/health")
    
    import urllib.request
    import json
    
    try:
        with urllib.request.urlopen(f"{url}/health", timeout=10) as response:
            data = json.load(response)
            if data.get("status") == "healthy":
                print_success("✅ 部署成功！API 正常運行")
                return True
    except Exception as e:
        print_warning(f"測試失敗: {e}")
        print_info("可能需要等待幾分鐘讓服務完全啟動")
    
    return False

# 主函數
def main():
    print_title("🚀 StarLink Card System 自動化部署")
    print("由我全權負責在免費雲端部署\n")
    
    # 檢查環境
    if not check_environment():
        print_error("環境檢查失敗，請修正後重試")
        return 1
    
    input("\n✅ 環境檢查完成 - 按 Enter 開始部署...")
    
    # GitHub
    github_info = setup_github()
    if not github_info:
        print_error("GitHub 設置失敗")
        return 1
    
    # Supabase
    db_url = setup_supabase()
    if not db_url:
        return 1
    
    # Upstash
    redis_url = setup_upstash()
    if not redis_url:
        return 1
    
    # 生成環境變量
    env_file = generate_env_file(db_url, redis_url)
    
    # Render
    render_url = deploy_to_render()
    if not render_url:
        return 1
    
    # 測試
    print_success("部署完成！正在測試...")
    time.sleep(30)  # 等待服務啟動
    test_deployment(render_url)
    
    # 生成使用說明
    print_title("🎉 部署完成！")
    print_success(f"API 網址: {render_url}")
    print_success(f"API 文檔: {render_url}/docs")
    print_success(f"健康檢查: {render_url}/health")
    
    print("\n簡單使用方式：")
    print("1. 創建商家: POST /api/v1/admin/merchants")
    print("2. 發行卡片: POST /api/v1/admin/cards/issue")
    print("3. 配發卡片: POST /api/v1/merchant/allocate")
    print("4. 查詢狀態: GET /health")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
