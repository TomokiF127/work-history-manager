# 職務経歴管理ツール

PySide6とSQLAlchemyを使用した職務経歴管理デスクトップアプリケーション。プロジェクトと技術経験を管理し、重複なしで経験月数を集計します。

## 機能

### 主要機能
- **プロジェクト管理**: 案件情報（名称、期間、役割、業務内容など）の登録・編集
- **技術管理**: OS、言語、フレームワーク、ツール、クラウド、DBの使用技術を管理
- **経験月数集計**: 技術ごとの経験月数を重複なしで自動集計
- **マスタ管理**: 技術・役割・作業のマスタデータをCRUD操作で管理
- **エクスポート**: CSV/Markdown形式で統計データを出力

### 特徴
- **重複なし集計**: 並行プロジェクトでの技術使用期間の重複を自動除外
- **技術使用期間の自動生成**: プロジェクト期間から技術使用期間を自動生成
- **現場管理**: プロジェクト内の複数現場（engagement）を管理
- **柔軟なフィルタリング**: 期間、技術、役割、フリーテキストでの検索

## システム要件

- Python 3.11以上
- macOS / Windows / Linux
- 画面解像度: 1400x900以上推奨

## 設定ファイル

### 初期設定

1. `config.ini.sample` を `config.ini` にコピー:
```bash
cp config.ini.sample config.ini
```

2. 必要に応じて `config.ini` を編集

### 設定項目

| セクション | キー | 説明 | デフォルト値 |
|-----------|------|------|------------|
| database | path | DBファイルの場所 | ./data/skills.db |
| database | echo | SQL文の表示 | false |
| app | name | アプリ名 | 職務経歴管理ツール |
| app | seed_initial_data | 初期データ投入 | true |
| export | csv_encoding | CSV文字コード | utf-8-sig |
| ui | window_width | ウィンドウ幅 | 1400 |
| ui | window_height | ウィンドウ高さ | 900 |

### 設定ファイルの優先順位

1. `./config.ini` （カレントディレクトリ）
2. `[プロジェクトルート]/config.ini`
3. `~/.workhistory/config.ini` （ユーザーホーム）

設定ファイルが無い場合はデフォルト値が使用されます。

## インストール

### 1. リポジトリのクローン（またはファイルを配置）
```bash
cd ~/Develop
mkdir workhistory
cd workhistory
# ここにappフォルダとその他ファイルを配置
```

### 2. Python仮想環境の作成
```bash
python3 -m venv venv
```

### 3. 仮想環境の有効化

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

## 起動方法

### 🖱️ クリック起動（推奨）

**macOS:**
- `起動.command` ファイルをダブルクリック

**Windows:**
- `起動.bat` ファイルをダブルクリック

### 📱 単一実行ファイル作成

**macOSアプリケーション(.app)を作成:**
```bash
./create_app_bundle.sh
```
→ `dist/職務経歴管理ツール.app` が作成されます

**単一実行ファイルを作成:**
```bash
./build_executable.sh
```
→ `dist/職務経歴管理ツール` が作成されます

### ⌨️ コマンドライン起動

**macOS:**
```bash
cd ~/Develop/workhistory
source venv/bin/activate
python app/main.py
```

**Windows:**
```bash
cd C:\Users\YourName\Develop\workhistory
venv\Scripts\activate
python app\main.py
```

初回起動時に`./data/skills.db`が自動作成され、初期マスタデータが投入されます。

## 使い方

### 1. プロジェクト管理
1. 「プロジェクト管理」タブを開く
2. 「新規」ボタンでプロジェクトを追加
3. プロジェクト情報を入力:
   - プロジェクト名、業務内容、詳細
   - 期間（開始日・終了日）
   - 役割、作業担当を選択
   - 使用技術を複数選択
4. 「技術使用期間をプロジェクト期間で自動生成」をクリック
5. 「保存」ボタンで保存

### 2. 技術使用期間の編集
1. プロジェクトを選択
2. 「技術使用期間編集」ボタンをクリック
3. 各技術の使用期間を個別に調整可能
4. 「プロジェクト期間で自動生成」で一括生成も可能

### 3. 現場（Engagement）管理
1. プロジェクトの「現場」タブを開く
2. 「現場追加」で現場期間を追加
3. 各現場で役割や規模の上書き設定が可能
4. 「選択現場で技術期間を自動生成」で現場期間に基づく技術使用期間を生成

### 4. マスタ管理
1. 「マスタ管理」タブを開く
2. 各カテゴリ（OS、言語、フレームワークなど）のタブを選択
3. 追加・編集・削除でマスタデータを管理

### 5. 経験年数統計
1. 「経験年数統計」タブを開く
2. 期間フィルタで集計範囲を指定（任意）
3. 各技術カテゴリのタブで経験月数を確認
4. CSVまたはMarkdownでエクスポート

### 6. データエクスポート
- 個別カテゴリ: 各タブの「CSVエクスポート」「Markdownエクスポート」ボタン
- 全カテゴリ一括: 「全カテゴリ一括エクスポート」ボタン

## ディレクトリ構成
```
workhistory/
├── app/
│   ├── main.py              # エントリポイント
│   ├── models/              # データベースモデル
│   │   ├── base.py
│   │   ├── project.py
│   │   ├── master.py
│   │   ├── relations.py
│   │   ├── engagement.py
│   │   └── tech_usage.py
│   ├── services/            # ビジネスロジック
│   │   ├── db.py
│   │   ├── repository.py
│   │   ├── stats.py
│   │   ├── export.py
│   │   └── seed.py
│   ├── ui/                  # GUI
│   │   ├── main_window.py
│   │   ├── projects_view.py
│   │   ├── masters_view.py
│   │   └── stats_view.py
│   └── data/                # SQLiteデータベース（自動生成）
│       └── skills.db
├── requirements.txt
└── README.md
```

## データベース仕様

### SQLite設定
- WALモード有効
- 外部キー制約有効
- 同期モード: NORMAL

### 主要テーブル
- `projects`: プロジェクト情報
- `engagements`: 現場期間
- `tech_usages`: 技術使用期間明細
- `oses`, `languages`, `frameworks`, `tools`, `clouds`, `dbs`: 技術マスタ
- `roles`, `tasks`: 役割・作業マスタ
- `project_*`: プロジェクトと技術の多対多関連

## 集計ロジック

### 重複なし月数計算
1. 各技術の全使用期間を月単位（YYYY-MM）に展開
2. 重複する月を集合演算でユニーク化
3. ユニークな月数をカウント

例: プロジェクトA（2023-01〜2023-06）とプロジェクトB（2023-04〜2023-08）で同じ技術を使用
→ 実質経験月数: 8ヶ月（2023-01〜2023-08）

## 単一実行ファイル化（オプション）

PyInstallerを使用して単一実行ファイルを作成:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "WorkHistory" \
  --add-data "app/data:data" \
  --hidden-import="sqlalchemy.sql.default_comparator" \
  app/main.py
```

## トラブルシューティング

### Qt関連のエラー
```bash
export QT_QPA_PLATFORM=offscreen  # ヘッドレス環境の場合
```

### データベースエラー
- `./data/skills.db`を削除して再起動すると初期化されます

### 文字化け
- CSV出力はBOM付きUTF-8で保存されます
- Excelで開く際は「データ」→「テキストから」でインポート

## ライセンス

**このプロジェクトはライセンスフリーです。**

- 商用・非商用問わず自由にご利用いただけます
- 改変・再配布も自由に行えます
- クレジット表記は任意です（していただけると嬉しいです）

## 貢献について

### バグ報告・機能要望
- [Issues](https://github.com/TomokiF127/work-history-manager/issues)でご報告ください
- バグの場合は再現手順も含めてください

### 変更提案
- [Pull Request](https://github.com/TomokiF127/work-history-manager/pulls)でご提案ください
- 大きな変更の場合は事前にIssueで相談していただけると助かります

### 独自カスタマイズ
- **大幅なカスタマイズを行う場合はフォークを推奨します**
- フォーク後は自由に改変してお使いください
- 有用な機能は本リポジトリへのPRも歓迎です

## 作成者

TomokiF127

---

**License-Free Software** - Feel free to use, modify, and distribute.