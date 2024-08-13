# RyoURL

RyoURL 是基於 Django 開發的短網址產生服務，使用者能夠創建短網址、查詢原始短網址及查看所有短網址。  
- 能夠搭配 [RyoUrl-frontend](https://github.com/KageRyo/RyoURL-frontend) 使用。  
- 能夠以 [RyoUrl-test](https://github.com/KageRyo/RyoURL-test) 進行單元測試。

## API

RyoURL 提供了多種 API 端點，分為以下幾個類別：

### 短網址相關

#### 基本短網址功能 (/api/short-url/)

- **POST /short**
  - 提供使用者創建新的隨機短網址
  - 創建邏輯為隨機生成 6 位數的英數亂碼，並檢查是否已經存在於資料庫，若無則建立其與原網址的關聯
- **GET /origin/{short_string}**
  - 提供使用者以短網址查詢原網址

#### 需要認證的短網址功能 (/api/auth-short-url/)

- **POST /custom**
  - 提供使用者自訂新的短網址 (需要登入)
- **GET /all-my**
  - 提供查詢目前自己建立的所有短網址 (需要登入)
- **DELETE /url/{short_string}**
  - 提供使用者刪除指定的短網址 (需要登入)

### 認證相關 (/api/auth/)

- **POST /register**
  - 提供使用者註冊帳號
- **POST /login**
  - 提供使用者登入

### 用戶相關 (/api/user/)

- **GET /info**
  - 獲取用戶資訊 (需要登入)
- **POST /refresh-token**
  - 更新 TOKEN 權杖 (需要登入)

### 管理員功能 (/api/admin/)

- **GET /all-urls**
  - 獲取所有 URL (需要管理員權限)
- **DELETE /expire-urls**
  - 刪除過期 URL (需要管理員權限)
- **GET /users**
  - 獲取所有用戶 (需要管理員權限)
- **PUT /user/{username}**
  - 更新用戶類型 (需要管理員權限)
- **DELETE /user/{username}**
  - 刪除用戶 (需要管理員權限)
  
## 權限管理

- 管理員 [2]
    - 擁有完整權限
- 一般使用者 [1]
    - 產生隨機短網址
    - 產生自訂短網址
    - 以短網址查詢原網址
    - 查看自己產生的所有短網址
    - 刪除自己產生的短網址
- 未登入的使用者 [0]
    - 產生隨機短網址
    - 以短網址查詢原網址

## 如何在本地架設 RyoURL 環境

1. 您必須先將此專案 Clone 到您的環境
    ```bash
    git clone https://github.com/KageRyo/RyoURL.git
    ```
2. 接著安裝所需要的函式庫
    ```bash
    pip install -r requirements.txt
    ```
3. 在 RyoURL Django 專案資料夾內建立 `.env` 設定環境變數，範例如下：
    ```bash
    DEBUG = 'True or False'
    SECRET_KEY = 'Your Django Secret Key'
    SENTRY_CLIENT_DSN = 'Your Sentry Key'
    ```
4. 執行此 Django 應用程式
    ```bash
    python manage.py runserver
    ```

## 資料庫

此專案資料庫使用 PostgreSQL。當然，您能依照需求更換成其他關聯性資料庫，包含但不限於：MySQL、sqlite3 ......等，別忘了到 `settings.py` 中進行修改。

## 開源貢獻

歡迎對 RyoURL 做出任何形式的貢獻，您可以於 [Issues](https://github.com/KageRyo/RyoURL/issues) 提出問題或希望增加的功能，亦歡迎透過 [Pull Requests](https://github.com/KageRyo/RyoURL/pulls) 提交您的程式碼更動！

## LICENSE

此專案採用 [MIT License](License) 開源條款，
有任何問題也歡迎向我聯繫。  
電子信箱：[kageryo@coderyo.com](mailto:kageryo@coderyo.com) 。