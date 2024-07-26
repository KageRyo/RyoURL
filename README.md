# RyoURL
RyoURL 是基於 Django 開發的短網址產生服務，使用者能夠創建短網址、查詢原始短網址及查看所有短網址。  
能夠搭配 [RyoUrl-frontend](https://github.com/KageRyo/RyoURL-frontend) 使用。  

## API
RyoURL 分別提供了一支 POST 及兩支 GET 的 API 可以使用，其 Schema 格式如下：
```python
orign_url    : str                 # 原網址
short_string : str                 # 為了短網址生成的字符串
short_url    : str                 # 短網址
create_date  : datetime.datetime   # 創建日期
```
### POST
- /api/short_url
    - 提供使用者創建新的短網址
    - 創建邏輯為隨機生成 6 位數的英數亂碼，並檢查是否已經存在於資料庫，若無則建立其與原網址的關聯
- /api/custom_url
    - 提供使用者自訂新的短網址
### GET
- /api/orign_url
    - 提供使用者以短網址查詢原網址
- /api/all_url
    - 提供查詢目前所有已被建立的短網址
### DELETE
- /api/short_url
    - 提供使用者刪除指定的短網址

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
此專案資料庫使用 Django 內建之 db.sqlite3，當然，您能依照需求更換成其他關聯性資料庫，包含但不限於：MySQL、PostgreSQL ......。

## 開源貢獻
歡迎對 RyoURL 做出任何形式的貢獻，您可以於 [Issues](https://github.com/KageRyo/RyoURL/issues) 提出問題或希望增加的功能，亦歡迎透過 [Pull Requests](https://github.com/KageRyo/RyoURL/pulls) 提交您的程式碼更動！

## LICENSE
此專案採用 [MIT License](License) 開源條款，
有任何問題也歡迎向我聯繫。  
電子信箱：[kageryo@coderyo.com](mailto:kageryo@coderyo.com) 。