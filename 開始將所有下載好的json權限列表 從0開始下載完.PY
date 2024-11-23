import os
import hmac
import hashlib
import urllib.parse
import base64
import time
import random
import requests
import json

# 配置參數
consumer_key = "wPGJ2oHKUheyP6B7zg2olF9aVkOvA0HW"
consumer_secret = "GMNmyqSSOjCBSDN4IwiqmE4h6jb3Q6bsFBmDs8h4hqEcQzeGfxqPnB7jIMv18AxBiYQhCCAJBSi77GfK5cAaKNuM05MrxXZMWGayzfm5VwdLpZ3zLJlsg6JLqOiVmCzpp6iLFdsCqzfBqJiXcw0yC1PvbwaTEIExjnx4vzLmuQRS"
token = "7pTn6l22uFZh3fGx1yXoH6"  
token_secret = "Ycq2gFlR9YyyBYe9F0VmDl8gWvjGyZ2jqmPk9quO5Z2QnWE2Q8Z4S3SG5ZTwzj7CysMYk7Disc5Ddu8XpCV0A" 
user_id = "5Z29EGlHoYnWchaGW2TRV6"
url = "https://tonofura-web-r.deepone-online.com/deep-one/api/story/getResource"
method = "POST"

# 獲取當前目錄下的所有 .json 文件名稱
json_files = [f for f in os.listdir('.') if f.endswith('.json')]

# 從文件名中提取 ID（去掉 .json 後綴）
story_ids = [os.path.splitext(f)[0] for f in json_files]

# 對每個 storyId 執行請求
for story_id in story_ids:
    # 動態生成請求的時間戳和隨機 nonce
    timestamp = str(int(time.time()))  # 當前的時間戳
    nonce = str(random.randint(1000000000000000, 9999999999999999))  # 隨機生成 nonce

    # 請求參數
    params = {
        "oauth_token": token,
        "xoauth_requestor_id": user_id,
        "oauth_consumer_key": consumer_key,
        "oauth_signature_method": "HMAC-SHA256",
        "oauth_nonce": nonce,
        "oauth_timestamp": timestamp,
    }

    # 按照字典順序對參數進行排序並進行URL編碼
    sorted_params = sorted(params.items())
    encoded_params = urllib.parse.urlencode(sorted_params)

    # 簽名基礎字串（這裡需要確保 URL 和參數都被正確編碼）
    base_string = f"{method.upper()}&{urllib.parse.quote(url, safe='')}"
    encoded_params_str = urllib.parse.urlencode(sorted_params)
    base_string += f"&{urllib.parse.quote(encoded_params_str, safe='')}"

    # 需要加密的 key，這是用來生成簽名的秘密部分
    key = f"{urllib.parse.quote(consumer_secret)}&{urllib.parse.quote(token_secret)}"

    # 使用 HMAC-SHA256 算法進行簽名
    signature = hmac.new(key.encode(), base_string.encode(), hashlib.sha256).digest()

    # 將簽名結果轉換為 Base64 編碼
    oauth_signature = base64.b64encode(signature).decode()

    # 組合完整的 authorization 標頭
    authorization_header = (
        f'OAuth realm="Users", '
        f'oauth_token="{token}", '
        f'xoauth_requestor_id="{user_id}", '
        f'oauth_consumer_key="{consumer_key}", '
        f'oauth_signature_method="HMAC-SHA256", '
        f'oauth_nonce="{nonce}", '
        f'oauth_timestamp="{timestamp}", '
        f'oauth_signature="{oauth_signature}"'
    )

    # 構建 headers
    headers = {
        "accept": "application/json;charset=UTF-8",
        "accept-language": "zh-TW,zh;q=0.9,ja-JP;q=0.8,ja;q=0.7,yue-CN;q=0.6,yue;q=0.5,en-US;q=0.4,en;q=0.3",
        "authorization": authorization_header,
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "x-deep-one-app-version": "{\"masterVersion\":\"1.234.0\",\"webVersion\":\"1.234.0\",\"apkHotUpdateVersion\":\"1.234.0\"}"
    }

    # 動態生成請求的 body
    body = json.dumps({"storyIds": str(story_id), "adult": 1})

    # 發送 POST 請求
    response = requests.post(url, headers=headers, data=body)

    # 打印返回的結果
    if response.status_code == 200:
        print(f"Request for storyId {story_id} succeeded!")
        try:
            response_json = response.json()
            file_name = f"{story_id}_response.json"
            with open(file_name, 'w', encoding='utf-8') as json_file:
                json.dump(response_json, json_file, ensure_ascii=False, indent=4)
            print(f"Response saved to {file_name}")
        except ValueError:
            print(f"Failed to parse the response as JSON for storyId {story_id}.")
    else:
        print(f"Request for storyId {story_id} failed with status code {response.status_code}")
        print(response.text)
