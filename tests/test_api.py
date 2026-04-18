#!/usr/bin/env python3
"""
星鏈卡系統 - 快速測試腳本
用於測試 API 端點是否正常工作
"""

import asyncio
import json
from httpx import AsyncClient

# 配置
BASE_URL = "http://localhost:8000"  # 本地測試
# BASE_URL = "https://your-render-url.onrender.com"  # 生產環境

async def test_api():
    """測試 API 端點"""
    
    async with AsyncClient() as client:
        print("🧪 開始測試 API...")
        print("=" * 50)
        
        # 1. 測試健康檢查
        print("\n1️⃣ 健康檢查")
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"   狀態碼: {response.status_code}")
            print(f"   回應: {response.json()}")
        except Exception as e:
            print(f"   ❌ 錯誤: {e}")
        
        # 2. 測試根端點
        print("\n2️⃣ 根端點")
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"   狀態碼: {response.status_code}")
            print(f"   回應: {response.json()}")
        except Exception as e:
            print(f"   ❌ 錯誤: {e}")
        
        # 3. 測試用戶註冊
        print("\n3️⃣ 用戶註冊")
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "testpassword123"
                }
            )
            print(f"   狀態碼: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 註冊成功")
                print(f"   Token: {data['access_token'][:20]}...")
                token = data['access_token']
            else:
                print(f"   回應: {response.json()}")
                token = None
        except Exception as e:
            print(f"   ❌ 錯誤: {e}")
            token = None
        
        # 4. 測試商家註冊 (如果有 token)
        if token:
            print("\n4️⃣ 商家註冊")
            try:
                response = await client.post(
                    f"{BASE_URL}/api/v1/merchants/register",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "name": "測試商家",
                        "email": "merchant@test.com",
                        "phone": "0912345678",
                        "merchant_type": "type_a",
                        "address": "測試地址",
                        "description": "測試商家描述"
                    }
                )
                print(f"   狀態碼: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ 商家註冊成功")
                    merchant_data = response.json()
                    print(f"   商家 ID: {merchant_data['id']}")
                else:
                    print(f"   回應: {response.json()}")
            except Exception as e:
                print(f"   ❌ 錯誤: {e}")
        
        # 5. 測試系統狀態
        print("\n5️⃣ 系統狀態")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/teams/status")
            print(f"   狀態碼: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ 系統狀態:")
                data = response.json()
                print(f"   商家: {data['merchants']}")
                print(f"   卡片: {data['cards']}")
                print(f"   交易: {data['transactions']}")
                print(f"   用戶: {data['users']}")
        except Exception as e:
            print(f"   ❌ 錯誤: {e}")
        
        print("\n" + "=" * 50)
        print("✅ 測試完成！")

if __name__ == "__main__":
    asyncio.run(test_api())
