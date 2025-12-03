# Water Intake Visualization App 💧

毎日の水分摂取量を可視化し、健康的な水分補給をサポートするWebアプリケーションです。

## 🌟 機能

1.  **目標の自動設定**: 身長、体重、年齢、性別から、1日に必要な水分量を自動計算します。
2.  **「置くだけ」自動計測**: 重量センサー（シミュレーション）からのデータを受け取り、摂取量を自動記録します。
3.  **ゲーム感覚の可視化**: 摂取量に応じて人型イラストの水位が上昇するアニメーションで、進捗を直感的に把握できます。
4.  **飲み忘れ防止通知**: 一定時間（デフォルト2時間）水分摂取がない場合、ブラウザ通知でお知らせします。

## 🛠️ 使用技術

-   **Backend**: Python, Flask, SQLAlchemy
-   **Frontend**: HTML, CSS, JavaScript
-   **Database**: SQLite

## 🚀 インストールと実行方法

### 前提条件

-   Python 3.x
-   Git

### 手順

1.  リポジトリをクローンします。
    ```bash
    git clone https://github.com/udtmhr/Water-intake-wab-App.git
    cd Water-intake-wab-App
    ```

2.  仮想環境を作成し、依存関係をインストールします。
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  アプリケーションを起動します。
    ```bash
    python app.py
    ```

4.  ブラウザで `http://127.0.0.1:5000` にアクセスします。

## 🧪 テスト方法

### センサーデータのシミュレーション

別のターミナルを開き、以下のスクリプトを実行することで、水分摂取（センサーデータ送信）をシミュレーションできます。

```bash
source venv/bin/activate
python test_sensor.py
```

または `curl` コマンドを使用することも可能です。

```bash
curl -X POST -H "Content-Type: application/json" -d '{"amount": 200}' http://127.0.0.1:5000/api/intake
```
