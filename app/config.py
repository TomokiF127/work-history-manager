"""
設定ファイル管理モジュール
"""
import os
import configparser
from pathlib import Path
from typing import Any, Optional

class Config:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Config._config is None:
            self.load_config()
    
    def load_config(self):
        """設定ファイルを読み込む"""
        config = configparser.ConfigParser()
        
        # デフォルト設定
        config['database'] = {
            'path': './data/skills.db',
            'echo': 'false'
        }
        config['app'] = {
            'name': '職務経歴管理ツール',
            'seed_initial_data': 'true'
        }
        config['export'] = {
            'default_directory': '',
            'csv_encoding': 'utf-8-sig'
        }
        config['ui'] = {
            'window_width': '1400',
            'window_height': '900',
            'project_name_width': '200',
            'role_width': '100',
            'period_width': '180',
            'scale_width': '150',
            'tech_list_height': '120'
        }
        
        # 設定ファイルのパスを検索（優先順位順）
        config_paths = [
            Path('./config.ini'),                    # カレントディレクトリ
            Path(__file__).parent.parent / 'config.ini',  # プロジェクトルート
            Path.home() / '.workhistory' / 'config.ini',  # ユーザーホーム
        ]
        
        # 設定ファイルが存在すれば読み込み
        for config_path in config_paths:
            if config_path.exists():
                try:
                    config.read(config_path, encoding='utf-8')
                    print(f"設定ファイルを読み込みました: {config_path}")
                    break
                except Exception as e:
                    print(f"設定ファイル読み込みエラー: {e}")
        
        Config._config = config
    
    def get(self, section: str, key: str, fallback: Optional[Any] = None) -> str:
        """設定値を取得"""
        try:
            return Config._config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if fallback is not None:
                return fallback
            raise
    
    def getint(self, section: str, key: str, fallback: Optional[int] = None) -> int:
        """整数値を取得"""
        try:
            return Config._config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            if fallback is not None:
                return fallback
            raise
    
    def getboolean(self, section: str, key: str, fallback: Optional[bool] = None) -> bool:
        """真偽値を取得"""
        try:
            return Config._config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            if fallback is not None:
                return fallback
            raise
    
    def get_database_path(self) -> str:
        """データベースパスを取得"""
        return self.get('database', 'path', './data/skills.db')
    
    def get_database_echo(self) -> bool:
        """SQLエコー設定を取得"""
        return self.getboolean('database', 'echo', False)
    
    def get_app_name(self) -> str:
        """アプリケーション名を取得"""
        return self.get('app', 'name', '職務経歴管理ツール')
    
    def should_seed_initial_data(self) -> bool:
        """初期データ投入フラグを取得"""
        return self.getboolean('app', 'seed_initial_data', True)
    
    def get_csv_encoding(self) -> str:
        """CSVエンコーディングを取得"""
        return self.get('export', 'csv_encoding', 'utf-8-sig')
    
    def get_window_size(self) -> tuple:
        """ウィンドウサイズを取得"""
        width = self.getint('ui', 'window_width', 1400)
        height = self.getint('ui', 'window_height', 900)
        return (width, height)

# シングルトンインスタンス
config = Config()