# RyoURL
RyoURL 是基於 Django 開發的短網址產生服務，使用者能夠創建短網址、查詢原始短網址及查看所有短網址。  
- 能夠搭配 [RyoUrl-frontend](https://github.com/KageRyo/RyoURL-frontend) 使用。  
- 能夠以 [RyoUrl-tesd](https://github.com/KageRyo/RyoURL-test) 進行單元測試。
  
## API
RyoURL 分別提供了一支 POST 及兩支 GET 的 API 可以使用，其 Schema 格式如下：
```python
orign_url    : HttpUrl          # 原網址
short_string : str              # 為了短網址生成的字符串
short_url    : HttpUrl          # 短網址
create_date  : datetime.datetime          # 創建日期
expire_date: Optional[datetime.datetime]  # 過期時間
visit_count: int                          # 瀏覽次數
```
### POST
- /api/register
    - 提供使用者註冊帳號
- /api/login
    - 提供使用者登入
- /api/logout
    - 提供使用者登出
- /api/short-url
    - 提供使用者創建新的短網址
    - 創建邏輯為隨機生成 6 位數的英數亂碼，並檢查是否已經存在於資料庫，若無則建立其與原網址的關聯
- /api/custom-url
    - 提供使用者自訂新的短網址
### GET
- /api/ (root)
    - 可提供用於測試與 API 的連線狀態使用
- /api/orign-url/{short_string}
    - 提供使用者以短網址查詢原網址
- /api/all-myurl
    - 提供查詢目前自己建立的短網址
- /api/all-url
    - 提供查詢目前所有已被建立的短網址
### DELETE
- /api/short-url/{short_string}
    - 提供使用者刪除指定的短網址
- /api/expire-url
    - 刪除過期的短網址
  
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