import html
import os
import json
import base64
import re
from datetime import datetime
from googleapiclient.discovery import build
import requests
import sys

# --- 1. 設定値 ---
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO_OWNER = "keihanmatcha"
GITHUB_REPO_NAME = "shen"
JSON_FILE_PATH = "archives/archive_videos.json"
MAX_PAGES_TO_FETCH = 5
FINAL_JSON_PATH = "archives/external_videos.json"

OWNER_NAME="緑仙"

CHANNELS = [
    {
        "id": "UCt5-0i4AVHXaWJrL8Wql3mw",
        "name": "緑仙"
    },
    {
        "id": "UChqQiUSyI-Q1j3k57_mAJHA",
        "name": "Rain Drops",
        "fixed_tags": ["える", "ジョー・力一","鈴木勝","三枝明那","童田明治","Rain Drops"]
    },
    {
        "id": "UCHRCp0CSacVnTVS2Z4x9xYg",
        "name": "七次元生徒会",
        "fixed_tags": ["叶", "樋口楓","三枝明那","レオス・ヴィンセント","周央サンゴ", "七次元生徒会"]
    }
]
MANUAL_VIDEO_IDS = [
]
EXTRA_PLAYLISTS = [
    # 手動追加用
    {
        "id": "PLBp6ycTto5Go5QZhTJCULksxsE4ZP3gXM",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["踊り動画"]   # 自動で付けたいタグ
    },
    {
        "id": "PLBp6ycTto5GqDp-0RniUkfHG1rLQobf2N",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["雑談"]   # 自動で付けたいタグ
    },
    {
        "id": "PLBp6ycTto5GpkDrrQbA2-odoeK4eR05WA",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["歌動画"]   # 自動で付けたいタグ
    },
    {
        "id": "PLBp6ycTto5GqM1eX6hCv0w3wMOMAEowT7",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["企画"]   # 自動で付けたいタグ
    },
    {
        "id": "PLBp6ycTto5GrgYKpoKFjR9i5V0Z4RCDZq",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["プロモーション"]   # 自動で付けたいタグ
    },
    {
        "id": "PLBp6ycTto5GrO1_g6oZYiLYJtfWaffjhr",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["歌配信"]   # 自動で付けたいタグ
    },
    {
        "id": "PLBp6ycTto5GoqrXTuXOFOvDibqScSxHBP",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["公式切り抜き"]   # 自動で付けたいタグ
    },
     # 緑仙　限定公開　公式プレイリスト
    # 緑仙　限定公開
    {
        "id": "PL2tNRe-9n6lZ995VG1GUkYf72CpKktd66",      # ここに再生リストIDを入れる
        "name": "緑仙",  
        "fixed_tags": ["限定公開","雑談"]   # 自動で付けたいタグ
    },
    {
        "id": "PL2tNRe-9n6lZ-M4iepguywhKTMpuVz1bQ",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["限定公開","雑談"]   # 自動で付けたいタグ
    },
    {
        "id": "PL2tNRe-9n6lawsf6v4Gn9R0h8EHrI5fzQ",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["限定公開","雑談"]   # 自動で付けたいタグ
    },
    {
        "id": "PL2tNRe-9n6lZjxxLrZScGaaeKNWU7hSFm",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["限定公開","雑談"]   # 自動で付けたいタグ
    },
    {
        "id": "PL2tNRe-9n6lZrxVfOPXeDMgF2CTVoBzTS",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["限定公開","雑談"]   # 自動で付けたいタグ
    },
    {
        "id": "PL2tNRe-9n6lb85F7ZJjGsHV_XeAY0nhFK",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["限定公開","雑談"]   # 自動で付けたいタグ
    },
    {
        "id": "PL2tNRe-9n6lZUcoSgvqkqaeU6T5t_hv-W",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["限定公開","雑談"]   # 自動で付けたいタグ
    },
    {
        "id": "PL2tNRe-9n6lYCvsOsBGsu_886CGRKkrul",      # ここに再生リストIDを入れる
        # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["限定公開","雑談"]   # 自動で付けたいタグ
    },
    # 緑仙　企画　公式プレイリスト
    {
        "id": "PL2tNRe-9n6lb6v2JjGQVjKVzU3-wcVAIz",      # ここに再生リストIDを入れる
        "fixed_tags": ["企画"]   # 自動で付けたいタグ
    },
    # 緑仙　歌配信　公式プレイリスト
    {
        "id": "PL2tNRe-9n6lYPvqVv2dLhQfO4MpimYjWW",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌配信"]   # 自動で付けたいタグ
    },
    # 緑仙　みどりとおはなしするだけ　公式プレイリスト
    {
        "id": "PL2tNRe-9n6lasIWq0_M2hu9-4Qb3ExXxc",      # ここに再生リストIDを入れる
        "name": "緑仙",                      # サイト上の「チャンネル名」として表示したい名前
        "fixed_tags": ["みどりとおはなしするだけ","雑談"]   # 自動で付けたいタグ
    },
     # 緑仙　お悩み相談&質問コーナー　公式プレイリスト
    {
        "id": "PL2tNRe-9n6lZgAkmjPYzLFzhre1EUQspQ",      # ここに再生リストIDを入れる
        "fixed_tags": ["お悩み相談&質問コーナー"]   # 自動で付けたいタグ
    },
    # 緑仙　ライブイベント　公式プレイリスト
    {
        "id": "PL2tNRe-9n6lZgMABzB_DEwf4t7V2E0nV8",      # ここに再生リストIDを入れる
        "fixed_tags": ["ライブイベント"]   # 自動で付けたいタグ
    },
    # 緑仙　緑仙の独りアソビ　公式プレイリスト
    {
        "id": "PL2tNRe-9n6lYvwDkdus_57eW1vSsbOLAW",      # ここに再生リストIDを入れる
        "fixed_tags": ["ゲーム実況","緑仙の独りアソビ"]   # 自動で付けたいタグ
    },
    # 緑仙　ゲーム実況　公式プレイリスト
    {
        "id": "PL2tNRe-9n6lZIafvEeZQEVbXLvyaZnDhM",      # ここに再生リストIDを入れる
        "fixed_tags": ["ゲーム実況"]   # 自動で付けたいタグ
    },
    # 緑仙　麻雀　公式プレイリスト
    {
        "id": "PL2tNRe-9n6lZY_PMgLEnzjPVTWUyTsdtV",      # ここに再生リストIDを入れる
        "fixed_tags": ["ゲーム実況","麻雀"]   # 自動で付けたいタグ
    },
    # 緑仙　マインクラフト　公式プレイリスト
    {
        "id": "PL2tNRe-9n6laDXKZxMI8qAU1f96p2mbyr",      # ここに再生リストIDを入れる
        "fixed_tags": ["ゲーム実況","マインクラフト"]   # 自動で付けたいタグ
    },
    # Rain Drops　公式プレイリスト
    {
        "id": "PLJJYjHjj3LYOUSivmmPc42q9p7776Pig3",      # ここに再生リストIDを入れる
        "fixed_tags": ["Rain Drops","える", "ジョー・力一","鈴木勝","三枝明那","童田明治"]   # 自動で付けたいタグ
    },
    # Rain Drops　オリジナル曲　公式プレイリスト
    {
        "id": "PLJJYjHjj3LYPcuTYj4pDerAE4FIXgLbyP",      # ここに再生リストIDを入れる
        "fixed_tags": ["Rain Drops","える", "ジョー・力一","鈴木勝","三枝明那","童田明治","歌動画","オリジナル曲"]   # 自動で付けたいタグ
    },
    # Rain Drops　リリース　公式プレイリスト
    {
        "id": "OLAK5uy_lDmp3Ak0wRHOL5BuQQIjV8WLza-Pqttlw",      # ここに再生リストIDを入れる
        "fixed_tags": ["Rain Drops","える", "ジョー・力一","鈴木勝","三枝明那","童田明治","歌動画","オリジナル曲","リリース","Rain Drops-リフレインズ"]   # 自動で付けたいタグ
    },
    {
        "id": "OLAK5uy_nGXxvlcQf-fJVf7v3tSJJSH77qyAES5Fk",      # ここに再生リストIDを入れる
        "fixed_tags": ["Rain Drops","える", "ジョー・力一","鈴木勝","三枝明那","童田明治","歌動画","オリジナル曲","リリース","Rain Drops-バイオグラフィ"]   # 自動で付けたいタグ
    },
    {
        "id": "OLAK5uy_lw1gyDY1_uE4ZRcHT2_OpgcLPYk_puEZA",      # ここに再生リストIDを入れる
        "fixed_tags": ["Rain Drops","える", "ジョー・力一","鈴木勝","三枝明那","童田明治","歌動画","オリジナル曲","リリース","Rain Drops-シナスタジア"]   # 自動で付けたいタグ
    },
    {
        "id": "OLAK5uy_mhpwJagwfrzhK3PWdewk_I9mDPBR3Lzow",      # ここに再生リストIDを入れる
        "fixed_tags": ["Rain Drops","える", "ジョー・力一","鈴木勝","三枝明那","童田明治","歌動画","オリジナル曲","リリース","Rain Drops-オントロジー"]   # 自動で付けたいタグ
    },
    {
        "id": "OLAK5uy_kFOGn0GpCIeOZQNm_OAbUm0MLlF76ZXEI",      # ここに再生リストIDを入れる
        "fixed_tags": ["Rain Drops","える", "ジョー・力一","鈴木勝","三枝明那","童田明治","歌動画","オリジナル曲","リリース","Rain Drops-アコースティックライブ『開花宣言』2021.03.31"]   # 自動で付けたいタグ
    },
    {
        "id": "OLAK5uy_l1MQdlsI7yQpwJYjd0sVTnlm5FJalsUek",      # ここに再生リストIDを入れる
        "fixed_tags": ["Rain Drops","える", "ジョー・力一","鈴木勝","三枝明那","童田明治","歌動画","オリジナル曲","リリース","Rain Drops-バイオグラフィ"]   # 自動で付けたいタグ
    },
    # 七次元生徒会　生徒会、使わせていただきます！　公式プレイリスト
    {
        "id": "PL3m9klpxyzPfuO9z1BVf8GTeX0bT2WXal",      # ここに再生リストIDを入れる
        "fixed_tags": ["生徒会、使わせていただきます！","企画","七次元生徒会","叶", "樋口楓","三枝明那","レオス・ヴィンセント","周央サンゴ"]   # 自動で付けたいタグ
    },
    {
        "id": "PL3m9klpxyzPdKWYNPXC3EhR8IazmzbxBk",      # ここに再生リストIDを入れる
        "fixed_tags": ["#24時限生徒会","七次元生徒会","叶", "樋口楓","三枝明那","レオス・ヴィンセント","周央サンゴ"]   # 自動で付けたいタグ
    },
    {
        "id": "PL3m9klpxyzPcH4CfG55TLu5KNCOuBOklv",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌動画","七次元生徒会","叶", "樋口楓","三枝明那","レオス・ヴィンセント","周央サンゴ"]   # 自動で付けたいタグ
    },
    # 七次元生徒会　リリース　公式プレイリスト
    {
        "id": "OLAK5uy_lo_PN7esxBBGMFXA8otiQB434doFbnt4Q",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌動画","七次元生徒会","叶", "樋口楓","三枝明那","レオス・ヴィンセント","周央サンゴ","オリジナル曲","リリース"]   # 自動で付けたいタグ
    },
    {
        "id": "OLAK5uy_n8lP-ooZpd9CC6elPM0GHPqdpfW4yRSF0",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌動画","七次元生徒会","叶", "樋口楓","三枝明那","レオス・ヴィンセント","周央サンゴ","オリジナル曲","リリース"]   # 自動で付けたいタグ
    },
    {
        "id": "OLAK5uy_lEq4Cb1mjxdZynIOSZbFX2wRto-qf5wTE",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌動画","七次元生徒会","叶", "樋口楓","三枝明那","レオス・ヴィンセント","周央サンゴ","オリジナル曲","リリース"]   # 自動で付けたいタグ
    },
    # 緑仙　リリース　公式プレイリスト
    {
        "id": "OLAK5uy_mR46w9gg9UKnxf0CZ-T7y7IBOirZP0CWs",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌動画","オリジナル曲","緑仙-It'sLie"]   # 自動で付けたいタグ
    },
    {
        "id": "OLAK5uy_lWfTV7Z7sI-yUBpuKOr1k80rLn4ziUNmM",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌動画","オリジナル曲","緑仙-パラグラム"]   # 自動で付けたいタグ
    },
    {
        "id": "OLAK5uy_n77u21cEJlnPW5_ysaE8IQfnyDhYpI9HQ",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌動画","オリジナル曲","緑仙-ゴチソウサマノススメ"]   # 自動で付けたいタグ
    },
    {
        "id": "OLAK5uy_kBFEKoBsjc4uluEefCQldv84Qkfka9Nno",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌動画","オリジナル曲","緑仙-イタダキマスノススメ"]   # 自動で付けたいタグ
    },
    {
        "id": "OLAK5uy_lK3vYQuMzo3A6i4TXjim4gU6Mk-bNml3k",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌動画","オリジナル曲","緑仙-最初の晩餐"]   # 自動で付けたいタグ
    },
    # 緑仙　歌動画　公式プレイリスト
    {
        "id": "PL2tNRe-9n6layYbKKj92KCO6KVjKivLsi",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌動画","カバー曲"]   # 自動で付けたいタグ
    },
    {
        "id": "PL2tNRe-9n6lbkKpeS1eH2F1GvPLIWgl82",      # ここに再生リストIDを入れる
        "fixed_tags": ["歌動画","オリジナル曲"]   # 自動で付けたいタグ
    },
    # SEEDs24　公式プレイリスト
    {
        "id": "PL5su7mgHJJj9GcxKEp2Wqx9T0B_yGdfLh",      # ここに再生リストIDを入れる
        "fixed_tags": ["SEEDs1期生","企画","#SEEDs24","SEEDs"]   # 自動で付けたいタグ
    },
    # こじらせハラスメント　公式プレイリスト
    {
        "id": "OLAK5uy_mlSNfpk3-Eg-8vFXobzB1gmaf5iV_TQlk",      # ここに再生リストIDを入れる
        "fixed_tags": ["こじらせハラスメント","弦月藤士郎", "相羽ういは","歌動画","リリース","オリジナル曲","こじらせハラスメント-さよならハラスメント"]   # 自動で付けたいタグ
    },
    {
        "id": "PLUDVjoVRQVQeIRJnXirhmDm2pVppfb9MC",      # ここに再生リストIDを入れる
        "fixed_tags": ["こじらせハラスメント","弦月藤士郎", "相羽ういは","歌動画","リリース","オリジナル曲","こじらせハラスメント-さよならハラスメント"]   # 自動で付けたいタグ
    }
]
# 管理対象のチャンネル名リスト
MANAGED_CHANNEL_NAMES = [ch["name"] for ch in CHANNELS]

# --- 2. 自動タグ付け用の辞書定義 ---
CATEGORY_LIST = [
    "ゲーム実況", "雑談", "歌配信", "歌動画", "踊り動画", "踊り配信",
    "記念配信", "少林寺拳法", "お披露目配信", "3D", "企画", "大会", "対談",
    "ライブイベント", "楽器配信・動画", "プロモーション", "公式企画・番組",
    "動画系", "公式切り抜き", "手描き動画", "ぷちさんじ"
]

# 【追加】タイトルに含まれていたら強制的にカテゴリに追加するマッピング
FORCE_CATEGORY_MAP = {
    "踊ってみた": "踊り動画",
    "歌ってみた": "歌動画",
    "楽曲": "歌動画",
    "3D": "3D",
    "3d": "3D",
    "万人": "記念配信",
    "爆誕": "記念配信",
    "生誕祭": "記念配信",
    "周年": "記念配信",
    "誕生日": "記念配信",
    "誕生祭": "記念配信",
    "新衣装": "お披露目配信",
    "新衣装": "お披露目配信",
    "XFDムービー":"プロモーション",
    "特典":"プロモーション",
    "Cover": "歌動画",
    "アイマス": "アイドルマスター",
    "ラブライブ": "ラブライブ!",
    "踊ってみた": "踊り動画",
    "踊って": "踊り動画",
    "感想配信": "記念配信",
    "告知": "プロモーション",
    "ティーザー": "プロモーション",
    "PR": "プロモーション",
    "ダンス動画": "踊り動画",
    "ダンス配信": "踊り配信",
    "ギター": "楽器配信・動画",
    "弾いて": "楽器配信・動画",
    "弾ける": "楽器配信・動画",
    "カラオケ": "歌配信",
    "歌枠": "歌配信",
    "Music Video": "歌動画",
    "MV": "歌動画",
    "歌ってみた": "歌動画",
    "COVER": "歌動画",
    "音楽ライブ": "歌配信",
    "公演": "ライブイベント",
    "3DLIVE": "ライブイベント",
    "ツアー": "ライブイベント",
    "フェス": "ライブイベント",
    "イベント": "ライブイベント",
    "ライブ": "ライブイベント",
    "少林寺": "少林寺拳法",
    "お披露目": "お披露目配信"
}

KEYWORD_GROUPS = {
    "MEMBERS": [
        # --- あ行 ---
        "愛園愛美", "相羽ういは", "赤城ウェン", "赤羽葉子", "明楽レイ", "アクシア・クローネ", "朝日南アカネ",
        "飛鳥ひな", "東堂コハク", "アミシア・ミチェラ", "雨森小夜", "アルス・アルマル", "アンジュ・カトリーナ",
        "安土桃", "家長むぎ", "五十嵐梨花", "伊波ライ", "イ・オン", "イ・シウ", "イ・ロハ",
        "壱百満天原サロメ", "イブラヒム", "出雲霞", "一橋綾人", "五木左京", "戌亥とこ", "宇佐美リト",
        "宇志海いちご", "卯月コウ", "海妹四葉", "エクス・アルビオ", "えま★おうがすと", "エトナ・クリムソン",
        "エリー・コニファー", "える", "遠北千南", "オ・ジユ", "御伽原江良", "小野町春香", "オリバー・エバンス",
        
        # --- か行 ---
        "甲斐田晴", "海夜叉神", "魁星", "加賀美ハヤト", "カエン", "蝸堂みかる", "ガオン", "風楽奏斗",
        "春崎エアル", "霞", "片眼鏡", "葛葉", "語部紡", "叶", "鏑木ろこ", "神田笑一", "北小路ヒスイ",
        "北見遊征", "ギルザレンIII世", "久遠千歳", "九里詠太", "黒井しば", "雲母たまこ", "倉持めると",
        "グウェル・オス・ガール", "郡道美玲", "剣持刀也", "弦月藤士郎", "小清水透", "梢桃音", "小柳ロウ",
        "コ・ヤミ",
        
        # --- さ行 ---
        "佐伯イッテツ", "早乙女ベリー", "榊ネス", "酒寄颯馬", "桜凛月", "笹木咲", "シスカ・レオンタイン",
        "椎名唯華", "シェリン・バーガンディ", "栞葉るり", "シスター・クレア", "四季凪アキラ", "司賀りこ",
        "獅子堂あかり", "静凛", "渋谷ハジメ", "嶋野", "篠宮ゆの", "城瀬いすみ", "ジョー・力一",
        "白砂あやね", "白雪巴", "シン・ギル", "シン・ユヤ", "周央サンゴ", "鈴木勝", "鈴鹿詩子",
        "鈴原るる", "鈴谷アキ", "瀬戸美夜子", "セフィナ", "セラフ・ダズルガーデン", "先斗寧",
        "ソ・ナギ", "ソフィア・ヴァレンタイン", "ソン・ミア", "十河ののは",
        
        # --- た行 ---
        "鷹宮リオン", "立伝都々", "千凛あゆむ", "珠乃井ナナ", "タカ・ラジマン", "月ノ美兎", "月見しずく",
        "塚原大地", "チェ・アラ", "童田明治", "ドーラ", "轟京子",
        
        # --- な行 ---
        "渚トラウト", "名伽尾アズマ", "七瀬すず菜", "奈羅花", "鳴門こがね", "ナ・セラ", "成瀬鳴","長尾景",
        "ナギサ・アルシニア", "西園チグサ", "ニュイ・ソシエール", "猫屋敷美紅", "ヌン・ボラ",
        
        # --- は行 ---
        "長尾景", "長尾姉上", "ハクレン", "ハ・ユン", "博衣こより", "花籠つばさ", "花畑チャイカ",
        "早瀬走", "葉加瀬冬雪", "葉山舞鈴", "ハナ・マキア", "ハン・チホ", "バン・ハダ", "樋口楓",
        "日ノ隈らん", "緋八マナ", "伏見ガク", "フミ", "フレン・E・ルスタリオ", "不破湊", "文野環",
        "ボニフィエール・プラナジャ", "星川サラ", "星導ショウ", "本間ひまわり",
        
        # --- ま行 ---
        "舞元啓介", "魔界ノりりむ", "魔使マオ", "ましろ爻", "町田ちま", "水面まどか", "ミカ・メラティカ",
        "ミラン・ケストレル", "三枝明那", "ミン・スゥーハ", "ムン・ホジュン", "モアリン", "叢雲カゲツ",
        "物述有栖", "メリッサ・キンレンカ", "森中花咲",
        
        # --- や行 ---
        "矢車りね", "八朔ゆず", "山田龍一郎", "山神カルタ", "ヤン・ナリ", "勇気ちひろ", "夕陽リリ",
        "雪城眞尋", "雪汝", "ユ・ルリ", "夢月ロア", "夢追翔", "夜牛詩乃", "夜見れな",
        
        # --- ら・わ行 ---
        "ライ・ガリレイ", "ライラ・アルストロエメリア", "ラトナ・プティ", "リクサ・ディレンドラ", "リゼ・ヘルエスタ",
        "リュ・ハリ", "ルイス・キャミー", "ルンルン", "レイン・パターソン", "レヴィ・エリファ",
        "レオス・ヴィンセント", "レザ・アファンルナ", "レヨン", "ローレン・イロアス", "ローロー","竜胆尊", "渡会雲雀",
        
        # --- 記号・特殊・アルファベット ---
        "男虎", "皇れお", "神永タイガ", "御子神琴音", "ぷりん・らら・もーど", "ぽめろ・ぱんち",
        # EN / ID / KR
        "Amicia Michella", "Xia-Ekavira", "Zea-Cornelia", "Taka Radjiman", "Derem Kado", "Nara Haramaung", "Hana Macchia",
        "Mika Melatika", "Miyu Ottavia", "Layla Astroemeria", "Riksa Dhirendra", "Reza Avanluna", "아키라 레이（明楽 レイ）",
        "이로하（イ・ロハ）", "오지유（オ・ジユ）", "가온（ガオン）", "신유야（シン・ユヤ）", "세피나（セフィナ）", "소나기（ソ・ナギ）",
        "나세라（ナ・セラ）", "하윤（ハ・ユン）", "반하다（バン・ハダ）", "민수하（ミン・スゥーハ）", "양나리（ヤン・ナリ）", "Ike Eveland",
        "Aia Amare", "Yugo Asuma", "Vezalius Bandage", "Uki Violeta", "Enna Alouette", "Elira Pendora", "Endou Reimu", "Fulgur Ovid",
        "Kyoran Meloco", "Kaelix Debonair", "Sonny Brisko", "Selen Tatsuki", "Torahime Kotoka", "Petra Gurin", "Pomu Rainpuff",
        "Maria Marionette", "Millie Parfait", "Shu Yamino", "Luca Kaneshiro", "Ren Zotto", "星弥", "Noor",
        # 外部・声優・その他
        "歌衣メイカ", "渋谷ハル", "熊谷タクマ", "かなえ先生", "天開司","水槽","HIMEHINA","YuNi","ときのそら","音ノ乃のの",
        "空澄セラ","我部りえる","富士葵","松永依織","水無瀬","兎田ぺこら","緋月ゆい","花宮梨歌","花宮梨歌","Sena Kiryuin","佐藤ホームズ",
        "百花繚乱", "ぽんぽこ", "ピーナッツくん", "ばあちゃる", "英リサ","幸祜","コーサカ","MonsterZ MATE","Yaca","DJ WILDPARTY","りうら","律可","星街すいせい","宝鐘マリン","えるの",
        "兎麹まり", "一ノ瀬うるは", "神威きゅぴ", "橘ひなの", "八雲ぺに", "ゴモリー", "多井隆晴", "松本吉弘", "前野智昭", "土田玲央","ロボ子","悠佑","いれいす","癒月ちょこ","いくぜ!",
        "平川大輔","アンジョー","猫又おかゆ","アザミ","超学生","響木アオ","超学生","天音かなた", "龍惺ろたん","神楽めあ"
    ],
    "UNITS": [
        "七次元生徒会", "アニソンカラオケ同好会", "Alri", "いちから中央銀行", "いのるぱんだ", "ウィシェン", "エビ仙", "ERRors",
        "解散GIG", "cresc.", "こじらせハラスメント", "SEEDs1期生", "チームヘラクレス",
        "しかばねぱんだ", "私立だいさんじ学園", "西弦緑渡", "にじさんじ乙女ゲーム製作委員会",
        "にじさんじカゲプロ", "にじさんじレジスタンス", "にじさんじ恋愛相談室", "にじ飯調査隊",
        "SitR名古屋", "にじロック", "ねないこ", "Vtuberロック革命","保健室組","保健室同盟","よるみどり",
        "猟友会","Rain Drops","le jouet","レッドガーネット","ワールドアトラス", "2年4組"
    ],
    "GAMES": [
        "アイドルマスター SideM", "あつまれどうぶつの森", "Apex Legends", "A Little to the Left", "BUCK SHOT ROULETTE", "ARK","レゴシティアンダーカバー",
        "ARK:Survival Ascended", "ARK:Survival Evolved", "ARK-アイランドマップ", "ARK-ラグナロクマップ", "ときめきメモリアル", "AmongUs",
        "ARK-エクスティンクションマップ", "ARK-クリスタルアイルズマップ", "ASTRONEER", "Blazing Sails", "ドラえもんのどら焼き屋さん物語",
        "Cooking Simulator", "Dead by Daylight", "eFootball ウイニングイレブン", "ウマ娘　プリティダービー", "Ring Fit Adventure",
        "おえかきの森", "Fall Guys", "Getting Over It", "Gartic Phones", "Get To Work", "Golf It!", "Inverted Angel",
        "Fast Food Simulator", "Human: Fall Flat", "Left 4 Dead 2", "maimai", "Nintendo Switch Sports", "PADDLE PADDLE PADDLE",
        "Operation: Tango", "Overcooked!2", "Overwatch", "Overwatch2", "Papers, Please", "PEAK", "Portal2","一致するまで終われまテン!!",
        "PowerWash Simulator", "PUBG", "slither.io/wormax.io", "Stray","ラブラブスクールデイズ", "Unpacking",
        "断罪室", "Ultimate Chicken Horse", "UNDERTALE", "Unrailed!", "GeoGuessr", "ito(イト)", "エアホッケー",
        "オバケイドロ!", "くそいサイト", "コードネーム", "にじさんじ共通テスト", "恋愛相談", "Raft", "遊戯王", "閉店事件",
        "グランド・セフト・オートV", "クロノ・トリガー", "原神", "幻塔", "ゴッドフィールド", "7days to die",
        "逆凸", "ゆびをふる", "シャドウバース", "雀魂", "白猫GOLF", "スイカゲーム", "ストリートファイター6",
        "スーパーモンキーボール バナナランブル", "やわらかあたま塾", "ゴブリン・ノーム・ホーン", "カービィのエアライダー",
        "マイクラ肝試し", "ゲームモーション研究会", "同時視聴", "凸待ち", "Splatoon", "Splatoon2", "Splatoon3", "ワンス・アポン・ア・塊魂",
        "おにぎり屋さんシミュレーター", "全国一般人常識チェック", "世界のアソビ大全51", "VALORANT", "Untitled Goose Game",
        "ゼルダの伝説 ブレス オブ ザ ワイルド", "太鼓の達人", "ツイステッドワンダーランド", "逆水寒", "夜間警備", "PotionPermit",
        "開店コンビニ日記", "牧場物語", "大乱闘スマッシュブラザーズSPECIAL", "テトリス99", "ダンガンロンパ", "Amanda the Adventurer",
        "刀剣乱舞", "Detroit Become Human", "大乱闘スマッシュブラザーズ", "ツイステッドワンダーランド", "塊塊アンコール",
        "ドキドキ文芸部", "ネコトモ", "バイオハザード ヴィレッジ", "パワフルプロ野球", "ロックマンエグゼ", "Q REMASTERED",
        "パワプロ", "プロセカ", "プロジェクトセカイ カラフルステージ！ feat. 初音ミク", "ポーカーチェイス", "Gang Beasts",
        "ポケットモンスター", "ポケットモンスター-金・銀", "ポケットモンスター-ユナイト", "GTA", "There Is No Game", "FOOD DELIVERY SERVICE",
        "Pokémon Trading Card Game Pocket", "ポケットモンスター-ファイアレッド・リーフグリーン", "大乱闘スマッシュブラザーズ",
        "ポケットモンスター-ルビー・サファイア", "ポケットモンスター-ブリリアントダイヤモンド・シャイニングパール", "BIOHAZARD VILLAGE",
        "ポケットモンスター-スカーレットバイオレット", "ポケットモンスター-ソード・シールド", "アリーナ・オブ・ヴァラー", "BATTLEFIELD V",
        "Pokémon LEGENDS アルセウス", "マインクラフト", "マリオシリーズ", "スーパーマリオブラザーズ", "深夜放送", "キーボードパズル",
        "スーパーマリオメーカー2", "マリオカート8DX", "マリオカートワールド", "マリオパーティ", "漢字でGO!", "PC Building Simulator",
        "その他マリオシリーズ", "みんなで空気読み。", "メイド イン ワリオ", "桃太郎電鉄", "モンスターストライク", "つぐのひ　忌み夜の喰霊品店",
        "モンスターハンター：ワールド", "星のカービィシリーズ", "リズム天国", "レイトン教授と不思議な町", "崩壊：スターレイル", "Knockout City",
        "一致するまで終われまテン!!", "任天堂", "パチスロ", "ホラーゲーム", "Chilla's Art", "PACIFY", "Twelve Minutes", "トロッコ問題",
        "Poppy Playtime", "Keep Talking and Nobody Explodes", "Protein for Muscle", "R.E.P.O.", "青鬼", "RTA", "例外配達","MTGアリーナ",
        "その他ホラーゲーム", "カードゲーム", "その他ゲーム", "Five Nights at Freddy's", "Getting Over It", "V最協", "V祭協"
    ],
    "PROGRAMS": [
        "SYMPHONIA Day1",
        "SYMPHONIA Day2", "LOCK ON FLEEK", "にじ鯖夏祭り", "VTuberエンジョイカジュアル交流戦",
        "ベース", "歳の差バラエティ(?)", "VΔLZ1st 一唱入魂", "VΔLZ2nd 三華の樂", "にじ漢歌祭り",
        "にじメンメドレー", "VTuber最協決定戦", "V祭協", "VTuberのあそびば", "くろのわーるがなんかやる",
        "Talking in English Collab", "ゲームる？ゲームる！", "だいさんじ甲子園", "にじさんじ甲子園",
        "にじワイテ人狼RPG", "格付けマリカ", "にじさんじイカ祭り", "にじさんじスマブラ杯", "神域甲子園", "ながおちぐ甲子園",
        "マリカにじさんじ杯", "にじスプラDREAMDEATHMATCH", "にじスプラ大会", "ミリしらスト６チャレンジ", "FIFA",
        "にじさんじイヤホンガンガンゲーム", "おながましろの心霊対談", "ケイナガオの楽屋裏", "NIJIMelodyTime",
        "Nagao's Kitchen", "初心者講座", "たい変", "にじフェス", "視聴者参加型", "にじさんじ麻雀杯",
        "にじさんじのTOYBOX！", "にじさんじのハッピーアワー!!", "にじさんじのB級バラエティ(仮)",
        "桜魔大戦譚", "にじさんじ大運動会", "にじさんじMIX UP!!", "にじさんじユニット歌謡祭2022", "目隠しポケモン",
        "にじさんじ歌謡祭2024", "にじマイクラ占領戦", "全肯定長尾景", "にじクイ", "木10！ろふまお塾", "KZHCUP", "にじさんじVALORANTカスタム",
        "ヤシロ&ササキのレバガチャダイパン", "レバガチャダイパン杯", "にじプロセカ大会", "カラフェス", "にじエペ祭", "神域リーグ", "にじさんじ遊戯王マスターデュエル",
        "ギター","緑仙1st Ryushen", "緑仙2nd 緑一色", "CDJ2425",
        "CDJ2526", "にじロック", "V祭協", "NIJIROCK NEXTBEAT", "くろのわーるがなんかやる",
        "にじさんじ Anniversary Festival 2021 前夜祭", "ゲームる？ゲームる！", "だいさんじ甲子園", "にじさんじ甲子園",
        "にじワイテ人狼RPG", "格付けマリカ", "にじさんじイカ祭り", "にじさんじスマブラ杯", "神域甲子園",
        "マリカにじさんじ杯", "にじスプラDREAMDEATHMATCH", "にじスプラ大会", "ミリしらスト６チャレンジ",
        "みどりとお話するだけ", "緑仙の音楽ダイアログ", "NIJIMelodyTime",
        "にじフェス", "視聴者参加型", "にじさんじ麻雀杯",
        "にじさんじのTOYBOX！", "にじさんじのハッピーアワー!!", "にじさんじのB級バラエティ(仮)",
        "にじさんじ大運動会", "にじさんじMIX UP!!", "にじさんじユニット歌謡祭2022", "目隠しポケモン",
        "にじさんじ歌謡祭2024", "にじマイクラ占領戦","にじクイ", "木10！ろふまお塾", "KZHCUP", "にじさんじVALORANTカスタム",
        "ヤシロ&ササキのレバガチャダイパン", "レバガチャダイパン杯", "にじプロセカ大会", "カラフェス", "にじエペ祭", "神域リーグ"
    ]
}

TAG_CONVERSION_MAP = {
    "マイクラ": "マインクラフト",
    "マリカ": "マリオカート8DX",
    "マリオカート8デラックス": "マリオカート8DX",
    "にじばろカスタム": "にじさんじVALORANTカスタム",
    "スプラ": "Splatoon",
    "Golf it": "Golf It!",
    "モンハンワイルズ": "モンスターハンターワイルズ",
    "スプラトゥーン": "Splatoon",
    "Pokemon LEGENDS アルセウス": "Pokémon LEGENDS アルセウス",
    "バイオハザードヴィレッジ": "BIOHAZARD VILLAGE",
    "スプラ2": "Splatoon2",
    "フードデリバリーサービス": "FOOD DELIVERY SERVICE",
    "VAROLANT": "VALORANT",
    "アリヴァラ": "アリーナ・オブ・ヴァラー",
    "スプラトゥーン2": "Splatoon2",
    "桃鉄": "桃太郎電鉄",
    "MTGA":"MTGアリーナ",
    "空気読み": "みんなで空気読み。",
    "アモアス": "AmongUs",
    "スプラ3": "Splatoon3",
    "スプラトゥーン3": "Splatoon3",
    "テトリス": "テトリス99",
    "切り抜き": "公式切り抜き",
    "リングフィットアドベンチャー": "Ring Fit Adventure",
    "お絵描きの森": "おえかきの森",
    "ライブ": "ライブ・イベント",
    "こじはら": "こじらせハラスメント",
    "SONG": "歌動画",
    "とうらぶ": "刀剣乱舞",
    "にじGTA": "にじさんじGTA",
    "オリジナル楽曲": "オリジナル曲",
    "Cover": "カバー曲",
    "カバー": "カバー曲",
    "カバー": "歌動画",
    "Special Live":"歌配信",
    "楽曲公開": "歌動画",
    "リリックビデオ": "歌動画",
    "こじハラ": "こじらせハラスメント",
    "にじスプラDREAM DEATHMATCH": "にじスプラDREAMDEATHMATCH",
    "V最協": "VTuber最協決定戦",
    "レバガチャ運動会": "レバガチャダイパン杯",
    "にじマイクラ占領戦": "にじマイクラ聖地占領戦",
    "あつ森": "あつまれどうぶつの森",
    "どうぶつの森": "あつまれどうぶつの森",
    "サイスタ": "アイドルマスター SideM GROWING STARS",
    "大乱闘スマッシュブラザーズSP": "大乱闘スマッシュブラザーズSPECIAL",
    "スマブラ": "大乱闘スマッシュブラザーズ",
    "ツイステ": "ツイステッドワンダーランド",
    "デトロイト": "Detroit Become Human",
    "剣盾": "ポケットモンスター-ソード・シールド",
    "L4D2": "Left 4 Dead 2",
    "スト6": "ストリートファイター6",
    "Power Wash Simulator": "PowerWash Simulator",
    "Apex": "Apex Legends",
    "APEX": "Apex Legends",
    "エペ": "Apex Legends",
    "ポケポケ": "Pokémon Trading Card Game Pocket",
    "にじイカ祭り": "にじさんじイカ祭り",
    "歌枠": "歌配信",
    "歌って": "歌動画",
    "歌ってみた": "歌動画",
    "COVER": "歌動画",
    "Music Video":"歌動画",
    "MV":"歌動画",
    "げんつき":"弦月藤士郎",
    "談義": "対談",
    "XFDムービー":"プロモーション",
    "特典":"プロモーション",
    "Cover": "歌動画",
    "踊ってみた": "踊り動画",
    "生演奏": "歌配信",
    "踊って": "踊り動画",
    "感想配信": "記念配信",
    "告知": "プロモーション",
    "ティーザー": "プロモーション",
    "ダンス動画": "踊り動画",
    "ダンス配信": "踊り配信",
    "ベース練習": "楽器配信・動画",
    "ギター": "楽器配信・動画",
    "弾いて": "楽器配信・動画",
    "弾ける": "楽器配信・動画",
    "SEEDs1期":"SEEDs1期生",
    "たねいち":"SEEDs1期生",
    "ポケカ": "Pokémon Trading Card Game Pocket",
    "パワプロ": "パワフルプロ野球",
    "にじさんじマリカ杯": "マリカにじさんじ杯",
    "プロセカ": "プロジェクトセカイ カラフルステージ！ feat. 初音ミク",
    "ヒューマンフォールフラット": "Human: Fall Flat",
    "レイドロ": "Rain Drops",
    "RainDrops": "Rain Drops",
    "社畜王子": "春崎エアル",
    "モンハンライズ": "モンスターハンターライズ",
    "ましろ": "ましろ爻",
    "えある": "春崎エアル",
    "エアル": "春崎エアル",
    "スプラトゥーン３": "Splatoon3",
    "スプラトゥーン２": "Splatoon2",
    "くれしぇ": "cresc.",
    "クレシェ": "cresc.",
    "Cresc": "cresc.",
    "OW2": "Overwatch2",
    "くれっしぇ":"cresc.",
    "クレッシェド":"cresc.",
    "SEEDs1期生":"SEEDs",
    "ポケモン銀": "ポケットモンスター-金・銀",
    "ポケモン金": "ポケットモンスター-金・銀",
    "ポケモンユナイト": "ポケットモンスター-ユナイト",
    "ポケモンSV": "ポケットモンスター-スカーレットバイオレット",
    "ポケモンサファイア": "ポケットモンスター-ルビー・サファイア",
    "ポケモンFRLG": "ポケットモンスター-ファイアレッド・リーフグリーン",
    "ポケモンBDSP": "ポケットモンスター-ブリリアントダイヤモンド・シャイニングパール"
}

HANDLE_TO_NAME_MAP = {
    "@KaidaHaru": "甲斐田晴", "@GenzukiTojiro": "弦月藤士郎", "@NagaoKei": "長尾景", "@Fumi": "フミ",
    "@HoshikawaSara": "星川サラ", "@YamagamiKaruta": "山神カルタ", "@TodoKohaku": "東堂コハク", "@OliverEvans": "オリバー・エバンス",
    "@HarusakiAir": "春崎エアル", "@NishizonoChigusa": "西園チグサ", "@LainPaterson": "レイン・パターソン",
    "@SeraphDazzlegarden": "セラフ・ダズルガーデン", "@ShibuyaHajime": "渋谷ハジメ", "@YuhiRiri": "夕陽リリ", "@Elu": "える",
    "@SukoyaKana": "健屋花那", "@GweluOsGar": "グウェル・オス・ガール", "@AkagiWen": "赤城ウェン", "@HoshirubeSho": "星導ショウ",
    "@SakakiNess": "榊ネス", "@FrenELustario": "フレン・E・ルスタリオ", "@PontoNei": "先斗寧", "@SasakiSaku": "笹木咲","@LuluSuzuhara":"鈴原るる",
    "@FuwaMinato": "不破湊", "@YukishiroMahiro": "雪城眞尋", "@OnomachiHaruka": "小野町春香", "@kuramochimerto": "倉持めると",
    "@SaegusaAkina": "三枝明那", "@MayuzumiKai": "黛灰", "@HonmaHimawari": "本間ひまわり", "@TakamiyaRion": "鷹宮リオン",
    "@KurusuNatsume": "来栖夏芽", "@Naraka": "奈羅花", "@WataraiHibari": "渡会雲雀","@HakaseFuyuki": "葉加瀬冬雪",
    "@KoshimizuToru": "小清水透", "@HanabatakeChaika": "花畑チャイカ", "@MaimotoKeisuke": "舞元啓介", "@KagamiHayato": "加賀美ハヤト",
    "@ShiorihaRuri": "栞葉るり", "@TsukinoMito": "月ノ美兎", "@YukiChihiro": "勇気ちひろ", "@HiguchiKaede": "樋口楓", "@FushimiGaku": "伏見ガク",
    "@GilzarenIII": "ギルザレンIII世", "@KenmochiToya": "剣持刀也", "@Kanae": "叶", "@ShiinaYuika": "椎名唯華", "@Dola": "ドーラ","@yukichihiro": "勇気ちひろ",
    "@TodorokiKyoko": "轟京子", "@SisterClaire": "シスター・クレア", "@YashiroKizuku": "社築", "@SuzukiMasaru": "鈴木勝",
    "@MachidaChima": "町田ちま", "@JoeRikiichi": "ジョー・力一", "@BelmondBanderas": "ベルモンド・バンデラス", "@YagurumaRine": "矢車りね",
    "@KuroiShiba": "黒井しば", "@WarabedaMeiji": "童田明治", "@InuiToko": "戌亥とこ", "@LeviElipha": "レヴィ・エリファ",
    "@YorumiRena": "夜見れな", "@ArsAlmal": "アルス・アルマル", "@AibaUiha": "相羽ういは", "@AmamiyaKokoro": "天宮こころ",
    "@ElieConifer": "エリー・コニファー", "@RatnaPetit": "ラトナ・プティ", "@HayaseSou": "早瀬走", "EmmaAugust": "えま★おうがすと",
    "@LuisCammy": "ルイス・キャミー", "@ShirayukiTomoe": "白雪巴", "@MashiroMeme": "ましろ爻", "@MelissaKinrenka": "メリッサ・キンレンカ",
    "@Ibrahim": "イブラヒム", "@KitakojiHisui": "北小路ヒスイ", "@AxiaCrone": "アクシア・クローネ", "@LaurenIroas": "ローレン・イロアス",
    "@LeosVincent": "レオス・ヴィンセント", "@UmiseYotsuha": "海妹四葉", "@HyakumantenbaraSalome": "壱百満天原サロメ",
    "@FurakuKanato": "風楽奏斗", "@ShikinagiAkira": "四季凪アキラ", "@ShishidoAkari": "獅子堂あかり", "@KaburagiRoco": "鏑木ろこ",
    "@IgarashiRika": "五十嵐梨花", "@IshigamiNozomi": "石神のぞみ", "@Sophia_Valentine": "ソフィア・ヴァレンタイン",
    "@SaikiIttetsu": "佐伯イッテツ", "@UsamiRito": "宇佐美リト", "@HibachiMana": "緋八マナ", "@MurakumoKagetsu": "叢雲カゲツ",
    "@KoyanagiRou": "小柳ロウ", "@InamiRai": "伊波ライ", "@kaisei": "魁星", "@KitamiYusei": "北見遊征", "@NagisaTrout": "渚トラウト",
    "@MilanKestrel": "ミラン・ケストレル", "@SakayoriSoma": "酒寄颯馬", "@NanaseSuzuna": "七瀬すず菜", "@HitotsubashiAyato": "一橋綾人",
    "@ItsukiSakyo": "五木左京", "@TogawaNonoha": "十河ののは", "@KozueMone": "梢桃音", "@LunLun_nijisanji": "ルンルン",
    "@ShiroseIsumi": "城瀬いすみ", "@KiraraTamako": "雲母たまこ", "@Saotomeberry": "早乙女ベリー", "@KadooMikaru": "蝸堂みかる",
    "@ShigaRiko": "司賀りこ", "@TachitsuteToto": "立伝都々", "@TamanoiNana": "珠乃井ナナ", "@ShinomiyaYuno": "篠宮ゆの",
    "@Kisara_nijisanji": "綺沙良", "@NekoyashikiMiku": "猫屋敷美紅", "@SumeragiReo": "皇れお", "@HanakagoTsubasa": "花籠つばさ",
    "@VALZ_ch": "VΔLZ", "@Suzuya_Aki": "鈴谷アキ", "@Moira": "モイラ", "@SuzukaUtako": "鈴鹿詩子", "@IenagaMugi": "家長むぎ",
    "@FuminoTamaki": "文野環", "@MorinakaKazaki": "森中花咲", "@AkabaneYouko": "赤羽葉子", "@MakainoRirimu": "魔界ノりりむ",
    "@AzuchiMomo": "安土桃", "@UzukiKou": "卯月コウ", "@AsukaHina": "飛鳥ひな", "@AmemoriSayo": "雨森小夜", "@NaruseMei": "成瀬鳴",
    "@SakuraRitsuki": "桜凛月", "@YumeoiKakeru": "夢追翔", "@YuzukiRoa": "夢月ロア", "@AngeKatrina": "アンジュ・カトリーナ",
    "@LizeHelesta": "リゼ・ヘルエスタ", "@ExAlbio": "エクス・アルビオ", "@NuiSociere": "ニュイ・ソシエール", "@HayamaMarin": "葉山舞鈴",
    "@Matsukaimao": "魔使マオ", "@SuoSango": "周央サンゴ", "@AsahinaAkane": "朝日南アカネ", "@AmagaseMuyu": "天ケ瀬むゆ",
    "@AmiciaMichella": "Amicia Michella", "@XiaEkavira": "Xia-Ekavira", "@ZEACornelia": "Zea-Cornelia", "@TakaRadjiman": "Taka Radjiman",
    "@DeremKado": "Derem Kado", "@NaraHaramaung": "Nara Haramaung", "@HanaMacchia": "Hana Macchia", "@MikaMelatika": "Mika Melatika",
    "@MiyuOttavia": "Miyu Ottavia", "@LaylaAstroemeria": "Layla Astroemeria", "@RiksaDhirendra": "Riksa Dhirendra",
    "@NagisaArcinia": "Nagisa Arcinia", "@EtnaCrimson": "Etna Crimson", "@Azura Cecillia": "Azura Cecillia", "@RaiGalilei": "Rai Galilei",
    "@RezaAvanluna": "Reza Avanluna", "@BonnivierPranaja": "Bonnivier Pranaja", "@SiskaLeontyne": "Siska Leontyne",
    "@HyonaElatiora": "Hyona Elatiora", "@AkiraRay": "아키라 레이（明楽 レイ）", "@LeeRoha": "이로하（イ・ロハ）", "@OhJiyu": "오지유（オ・ジユ）",
    "@RyuHari": "류하리（リュ・ハリ）", "@Gaon": "가온（ガオン）", "@yuya_shin": "신유야（シン・ユヤ）", "@Seffyna": "세피나（セフィナ）",
    "@SoNagi": "소나기（ソ・ナギ）", "@NaSera": "나세라（ナ・セラ）", "@haYun": "하윤（ハ・ユン）", "@BanHada": "반하다（バン・ハダ）",
    "@MinSuha": "민수하（ミン・スゥーハ）", "@YangNari": "양나리（ヤン・ナリ）", "@IkeEveland": "Ike Eveland", "@AiaAmare": "Aia Amare",
    "@AlbanKnox": "Alban Knox", "@AsterArcadia": "Aster Arcadia", "@ClaudeClawmark": "Claude Clawmark", "@YugoAsuma": "Yugo Asuma",
    "@YuQ.Wilson": "YuQ.Wilson", "@VezaliusBandage": "Vezalius Bandage", "@VantacrowBringer": "VantacrowBringer",
    "@VictoriaBrightshield": "Victoria Brightshield", "@UkiVioleta": "Uki Violeta", "@DoppioDropscythe": "Doppio Dropscythe",
    "@HexHaywire": "Hex Haywire", "@EnnaAlouette": "Enna Alouette", "@EliraPendora": "Elira Pendora", "@FinanaRyugu": "Finana Ryugu",
    "@Freodore_nijisanji": "Freodore", "@ReimuEndou": "Reimu Endou", "@FulgurOvid": "Fulgur Ovid", "@MelocoKyoran": "Meloco Kyoran",
    "@KyoKaneko": "Kyo Kaneko", "@KotokaTorahime": "Kotoka Torahime", "@KaelixDebonair": "Kaelix Debonair", "@KunaiNakasato": "Kunai Nakasato",
    "@KlaraCharmwood": "Klara Charmwood", "@SonnyBrisko": "Sonny Brisko", "@ScarleYonaguni": "ScarleYonaguni", "@SelenTatsuki": "Selen Tatsuki",
    "@Seible": "Seible_nijisanji", "@petragurin": "Petra Gurin", "@PomuRainpuff": "Pomu Rainpuff", "@Rosemi_Lovelock": "Rosemi Lovelock",
    "@MariaMarionette": "Maria Marionette", "@MystaRias": "Mysta Rias", "@MillieParfait": "Millie Parfait", "@ShuYamino": "Shu Yamino",
    "@Twisty Amanozako": "Twisty Amanozako", "@VoxAkuma": "Vox Akuma", "@VerVermillion": "Ver Vermillion", "@LucaKaneshiro": "Luca Kaneshiro",
    "@ZealGinjoka": "Zeal Ginjoka", "@RenZotto": "Ren Zotto", "@RyomaBarrenwort": "Ryoma Barrenwort", "@Hoshimi-virtualreal1845": "星弥",
    "@noornijisanjiin7271": "Noor", "@PIROPARU": "字ぴろぱる", "@shibuyaHAL": "渋谷ハル", "@UTAIMEIKA": "歌衣メイカ",
    "@KanaeVCriminologist": "かなえ先生", "@Peanutskun": "ピーナッツくん", "@pokopea": "ぽんぽこ", "@_Ubiba": "ばあちゃる","@伊東ライフ‬":"伊東ライフ",
    "@lisahanabusa": "英リサ", "@TOMARI_MARI": "兎麹まり", "@uruhaichinose": "一ノ瀬うるは", "@KaminariQpi": "神威きゅぴ","@monsterzmate":"MonsterZ MATE",
    "@hinanotachiba7": "橘ひなの", "@八雲ぺに": "八雲ぺに", "@takachan0317": "多井隆晴", "@zunmaruch": "村上淳","@satouholmes": "佐藤ホームズ",
    "@SuzukiTaro_CH": "鈴木たろう", "@sibukawa": "渋川難波", "@Matsumotogumi": "松本吉弘", "@RyuseiRotan": "龍惺ろたん",
    "@tenkaitsukasa": "天開司", "@sakinomoco": "咲乃もこ", "@Izumi_Yunohara": "柚原いづみ", "@OmaruPolka": "尾丸ポルカ",
    "@TakaneLui": "鷹嶺ルイ", "@MoriCalliope": "森カリオペ", "@Inaba_Haneru": "因幡はねる",
    "@結城さくな‬":"結城さくな","‪@ui_shig":"しぐれうい","‪@YukokuRoberu‬":"夕刻ロベル","@犬山たまき佃煮のりお":"犬山たまき",
    "@YanoKuromu":"夜乃くろむ","@shiranamiramune":"白波らむね","@KaguraMea":"神楽めあ"
}
UNIT_GROUP_MAP = {
    "七次元生徒会": ["叶", "樋口楓","三枝明那","レオス・ヴィンセント","周央サンゴ"],
    "Rain Drops": ["える", "ジョー・力一","鈴木勝","三枝明那","童田明治","Rain Drops"],
    "le jouet": ["夢追翔", "加賀美ハヤト"],
    "にじロック": ["夢追翔", "ジョー・力一","加賀美ハヤト","三枝明那","雨森小夜","轟京子"],
    "こじらせハラスメント": ["弦月藤士郎", "相羽ういは"],
    "Vtuberロック革命": ["不破湊", "戌亥とこ","加賀美ハヤト","樋口楓"],
    "猟友会":["伏見ガク", "叶", "本間ひまわり","夜見れな","魔使マオ", "奈羅花"],
    "アイス組": ["ギルザレンⅢ世", "童田明治"],
    "ウィシェン": ["相羽ういは"],
    "エビ仙": ["エクス・アルビオ"],
    "保健室同盟": ["黛灰", "健屋花那"],
    "保健室組": ["黛灰"],
    "MonsterZ MATE":["コーサカ","アンジョー"],
    "ワールドアトラス": ["海妹四葉","イブラヒム"],
    "西弦緑渡": ["弦月藤士郎", "西園チグサ", "渡会雲雀"],
    "私立だいさんじ学園": ["花畑チャイカ", "剣持刀也", "鷹宮リオン"],
    "にじさんじカゲプロ": ["樋口楓","町田ちま","戌亥とこ","リゼ・ヘルエスタ","三枝明那","葉加瀬冬雪","星川サラ","ましろ爻","弦月藤士郎","西園チグサ","レイン・パターソン","渡会雲雀"],
    "アニソンカラオケ同好会": ["早瀬走", "オリバー・エバンス","社築"],
    "にじさんじ乙女ゲーム製作委員会": ["葉加瀬冬雪", "ニュイ・ソシエール", "奈羅花"],
    "にじさんじ恋愛相談室": ["鷹宮リオン", "葉加瀬冬雪","星川サラ"],
    "Alri": ["アンジュ・カトリーナ"],
    "ねないこ": ["鈴谷アキ"],
    "よるみどり": ["夜見れな"],
    "ヨルミティ": ["椎名唯華","神田笑一", "鷹宮リオン", "郡道美玲", "葉山舞鈴", "夜見れな", "天宮こころ","シェリン・バーガンディ","ルイス・キャミー", "魔使マオ", "奈羅花"],
    "しかばねぱんだ": ["赤羽葉子"],
    "いのるぱんだ": ["シスター・クレア"],
    "みどねる": ["因幡はねる"],
    "解散GIG": ["笹木咲", "椎名唯華","赤羽葉子"],
    "にじさんじレジスタンス": ["笹木咲", "椎名唯華","赤羽葉子"],
    "cresc.": ["シスター・クレア", "ドーラ"],
    "ERRors": ["える", "夕陽リリ"],
    "にじ飯調査隊":["伏見ガク","長尾景"],
    "チームヘラクレス":["長尾景","龍惺ろたん","松本吉弘"],
    "SitR名古屋": ["長尾景", "葉加瀬冬雪", "渡会雲雀", "先斗寧", "小清水透"],
    "レッドガーネット": ["える","エリー・コニファー","綺沙良","多井隆晴"],
    "にじさんじラジオ体操部": [
        "月ノ美兎", "勇気ちひろ", "える", "樋口楓", "渋谷ハジメ", "伏見ガク", "ギルザレンIII世", "剣持刀也", "叶", "笹木咲", "椎名唯華", "ドーラ", "轟京子", "シスター・クレア", "花畑チャイカ", "社築", "鈴木勝", "緑仙", "鷹宮リオン", "舞元啓介", "でびでび・でびる", "桜凛月", "町田ちま", "ジョー・力一", "ベルモンド・バンデラス", "矢車りね", "黒井しば", "童田明治", "小野町春香", "戌亥とこ", "三枝明那", "雪城眞尋", "レヴィ・エリファ", "葉加瀬冬雪", "加賀美ハヤト", "夜見れな", "黛灰", "アルス・アルマル", "相羽ういは", "天宮こころ", "エリー・コニファー", "ラトナ・プティ", "早瀬走", "健屋花那", "フミ", "星川サラ", "えま★おうがすと", "ルイス・キャミー", "不破湊", "白雪巴", "グウェル・オス・ガール", "ましろ爻", "奈羅花", "来栖夏芽", "フレン・E・ルスタリオ", "メリッサ・キンレンカ", "イブラヒム", "弦月藤士郎", "甲斐田晴", "北小路ヒスイ", "西園チグサ", "アクシア・クローネ", "ローレン・イロアス", "レオス・ヴィンセント", "オリバー・エバンス", "レイン・パターソン", "海妹四葉", "壱百満天原サロメ", "風楽奏斗", "渡会雲雀", "四季凪アキラ", "セラフ・ダズルガーデン", "Taka Radjiman", "Zea-Cornelia", "Riksa Dhirendra", "Nara Haramaung", "Layla Alstroemeria", "Bonnivier Pranaja", "Derem Kado", "Xia-Ekavira", "Mika Melatika", "소나기（ソ・ナギ）", "양나리（ヤン・ナリ）", "하윤（ハ・ユン）", "오지유（オ・ジユ）", "세피나（セフィナ）", "나세라（ナ・セラ）", "小清水透", "獅子堂あかり", "鏑木ろこ", "五十嵐梨花", "石神のぞみ", "ソフィア・ヴァレンタイン", "倉持めると", "佐伯イッテツ", "赤城ウェン", "宇佐美リト", "緋八マナ", "星導ショウ", "叢雲カゲツ", "小柳ロウ", "伊波ライ", "Elira Pendora", "Pomu Rainpuff", "Petra Gurin", "Enna Alouette", "Reimu Endou", "Millie Parfait", "Luca Kaneshiro", "Shu Yamino", "Yugo Asuma", "Sonny Brisko", "Uki Violeta", "Aia Amare", "あばだんご"
    ],
    "2年4組": ["渋谷ハジメ", "宇志海いちご", "ドーラ", "出雲霞","神田笑一", "飛鳥ひな", "町田ちま", "遠北千南", "夢追翔", "童田明治"],
    "いちから中央銀行": ["鷹宮リオン", "ベルモンド・バンデラス", "雪城眞尋", "レヴィ・エリファ", "葉加瀬冬雪", "黛灰", "アルス・アルマル", "相羽ういは", "天宮こころ", "早瀬走", "フレン・E・ルスタリオ", "長尾景","弦月藤士郎"],
    "SEEDs1期生": ["ドーラ", "海夜叉神", "名伽尾アズマ", "出雲霞", "轟京子", "シスター・クレア", "花畑チャイカ","社築", "安土桃", "鈴木勝", "卯月コウ", "八朔ゆず"],
    "だいさんじ甲子園": ["長尾景", "グウェル・オス・ガール", "榊ネス"]
}
# 絵文字 / 記号 → ライバー名 変換辞書
LIVER_EMOJI_MAP = {
    # --- 4絵文字 ---
    "♥️♠️♦️♣️": "物述有栖",
    "♥♠♦♣": "物述有栖",

    # --- 3絵文字 ---
    "🥼🌱😺": "レオス・ヴィンセント",

    # --- 2絵文字（異字体セレクタ等のゆれ含む） ---
    "🎀💙": "勇気ちひろ",
    "🏰🌕️": "ギルザレンIII世",
    "🏰🌕": "ギルザレンIII世",
    "竜胆尊": "竜胆尊",
    "🍶⚜️": "竜胆尊",
    "🍶⚜": "竜胆尊",
    "🚪👿": "でびでび・でびる",
    "🎑💊": "月見しずく",
    "🐕🐾": "黒井しば",
    "🐺🍎": "童田明治",
    "📷💚": "瀬戸美夜子",
    "🏰🕛": "御伽原江良",
    "🌐💫": "雪城眞尋",
    "🍃🗻": "葉山舞鈴",
    "🎩🐤": "夜見れな",
    "💻💙": "黛灰",
    "🍮💎": "相羽ういは",
    "🐻💎": "ラトナ・プティ",
    "🏃‍♀️💨": "早瀬走",
    "💉💘": "健屋花那",
    "❤️🦋": "ルイス・キャミー",
    "❤🦋": "ルイス・キャミー",
    "💥衝突": "魔使マオ",
    "🥂✨": "不破湊",
    "👠⛓": "白雪巴",
    "👠⛓️": "白雪巴",
    "✖🍳": "奈羅花",
    "🐏🎵": "来栖夏芽",
    "🎻🛵": "弦月藤士郎",
    "🦖🎖": "朝日南アカネ",
    "🦖🎖️": "朝日南アカネ",
    "💞🦩": "周央サンゴ",
    "🐬🌱": "西園チグサ",
    "🗝💸": "ローレン・イロアス",
    "💯🦂": "壱百満天原サロメ",
    "🍝🍷": "風楽奏斗",
    "♦☕": "渡会雲雀",
    "♦️☕": "渡会雲雀",
    "🦉🎻": "セラフ・ダズルガーデン",
    "🦦✌️": "Miyu Ottavia",
    "🦦✌": "Miyu Ottavia",
    "😈💥": "Riksa Dhirendra",
    "🕰🌺": "Layla Alstroemeria",
    "🌋🍔": "Etna Crimson",
    "🔦🦁": "Siska Leontyne",
    "🐥🍭": "Nagisa Arcinia",
    "🌒☁": "Reza Avanluna",
    "🌒☁️": "Reza Avanluna",
    "🐾🏵": "Hyona Elatiora",
    "🐾🏵️": "Hyona Elatiora",
    "⚗️🎼": "Xia Ekavira",
    "⚗🎼": "Xia Ekavira",
    "👻📌": "Mika Melatika",
    "🎀🧸": "ユ・ルリ",
    "🌛🌱": "シン・ユヤ",
    "🦴🔔": "カエン",
    "🌑🦋": "ハン・チホ",
    "☁️🌫️": "ハクレン",
    "☁🌫": "ハクレン",
    "🌹💛": "チェ・アラ",
    "❄💜": "ヌン・ボラ",
    "❄️💜": "ヌン・ボラ",
    "💗🌕️": "セフィナ",
    "💗🌕": "セフィナ",
    "🐈‍⬛🔪": "コ・ヤミ",
    "🐈‍⬛🔪️": "コ・ヤミ",
    "🎮️🦭": "ハ・ユン",
    "🎮🦭": "ハ・ユン",
    "🌸🌙": "ナ・セラ",
    "🐱💫": "獅子堂あかり",
    "🍕🎢": "鏑木ろこ",
    "⚾🧡": "五十嵐梨花",
    "🐰🗞": "ソフィア・ヴァレンタイン",
    "🧸🌙": "倉持めると",
    "🍱🦖": "赤城ウェン",
    "🌩🦒": "宇佐美リト",
    "🌩️🦒": "宇佐美リト",
    "🐝🤣": "緋八マナ",
    "🐙🌟": "星導ショウ",
    "🥷🔫": "叢雲カゲツ",
    "👻🔪": "小柳ロウ",
    "🪓🎀": "立伝都々",
    "🚓🐾": "栞葉るり",
    "🦋⏳": "ミラン・ケストレル",
    "📿🍔": "北見遊征",
    "🔑🐍": "魁星",
    "🫖🌿": "榊ネス",
    "🍰🧁": "早乙女ベリー",
    "🐣📛": "雲母たまこ",
    "🐟🍴": "渚トラウト",
    "📚🗣": "一橋綾人",
    "📚🗣️": "一橋綾人",
    "💼📊": "五木左京",
    "♫🐌": "蝸堂みかる",
    "♫💮": "夜牛詩乃",
    "♫🦎": "十河ののは",
    "♫💐": "猫屋敷美紅",
    "👑🌸": "皇れお",
    "💍📘": "篠宮ゆの",
    "🏰🍬": "城瀬いすみ",
    "🧢🪽": "花籠つばさ",
    "🏖️🫶": "白砂あやね",
    "🏖🫶": "白砂あやね",
    "🪟🫶": "水面まどか",
    "👊🐯": "男虎",
    "🧰✂️": "九里詠太",
    "🧰✂": "九里詠太",
    "🫧🐬": "小々波いるか",
    "💜🗯️": "千凛あゆむ",
    "💜🗯": "千凛あゆむ",
    "🗡🐼": "塚原大地",
    "🦈✦": "Rei7",
    "🎮️🥇": "レヨン",
    "🎮🥇": "レヨン",
    "🍮💌": "ぷりん・らら・もーど",
    "🌠👊": "ぽめろ・ぱんち",
    "🐅🎻": "神永タイガ",
    "⛰️🎹": "山田龍一郎",
    "⛰🎹": "山田龍一郎",

    # --- 1絵文字 / 単一記号 ---
    "🐰": "月ノ美兎",
    "🗼": "える",
    "🍁": "樋口楓",
    "🥦": "静凛",
    "💜": "静凛",
    "🌱": "渋谷ハジメ",
    "🐈": "鈴谷アキ",
    "🎶": "鈴鹿詩子",
    "🍓": "宇志海いちご",
    "🌷": "家長むぎ",
    "🌇": "夕陽リリ",
    "🐟": "文野環",
    "✌️": "伏見ガク",
    "✌": "伏見ガク",
    "🦊": "伏見ガク",
    "⚔️": "剣持刀也",
    "⚔": "剣持刀也",
    "🌼": "森中花咲",
    "🐻": "森中花咲",
    "🔫": "叶",
    "💀": "赤羽葉子",
    "🎋": "笹木咲",
    "🍜": "闇夜乃モルル",
    "🌻": "本間ひまわり",
    "🍼": "魔界ノりりむ",
    "❄️": "雪汝",
    "❄": "雪汝",
    "👻": "椎名唯華",
    "🔥": "ドーラ",
    "⛩️": "海夜叉神",
    "⛩": "海夜叉神",
    "☀️": "名伽尾アズマ",
    "🦑": "出雲霞",
    "🐐": "轟京子",
    "🔔": "シスター・クレア",
    "🌵": "花畑チャイカ",
    "🖥️": "社築",
    "🖥": "社築",
    "🍑": "安土桃",
    "☪️": "鈴木勝",
    "☪": "鈴木勝",
    "🐼": "緑仙",
    "🌙": "卯月コウ",
    "🍊": "八朔ゆず",
    "🔪": "神田笑一",
    "🍅": "神田笑一",
    "🐤": "飛鳥ひな",
    "🍭": "春崎エアル",
    "☂️": "雨森小夜",
    "☔️": "雨森小夜",
    "☂": "雨森小夜",
    "☔": "雨森小夜",
    "🦅": "鷹宮リオン",
    "👨‍🌾": "舞元啓介",
    "🌸": "桜凛月",
    "🐹": "町田ちま",
    "🤡": "ジョー・力一",
    "🎈": "ジョー・力一",
    "🍬": "遠北千南",
    "🎙️": "成瀬鳴",
    "🎙": "成瀬鳴",
    "🥃": "ベルモンド・バンデラス",
    "🌽": "矢車りね",
    "🎤": "夢追翔",
    "🧠": "久遠千歳",
    "🐽": "郡道美玲",
    "🌖": "夢月ロア",
    "♨️": "小野町春香",
    "♨": "小野町春香",
    "🧂": "語部紡",
    "📘": "語部紡",
    "🍹": "戌亥とこ",
    "⚖️": "アンジュ・カトリーナ",
    "⚖": "アンジュ・カトリーナ",
    "👑": "リゼ・ヘルエスタ",
    "🌶️": "三枝明那",
    "🌶": "三枝明那",
    "💕": "愛園愛美",
    "🎨": "鈴原るる",
    "🛡️": "エクス・アルビオ",
    "🛡": "エクス・アルビオ",
    "🔲": "レヴィ・エリファ",
    "🎃": "ニュイ・ソシエール",
    "⚗️": "葉加瀬冬雪",
    "⚗": "葉加瀬冬雪",
    "🏢": "加賀美ハヤト",
    "📕": "アルス・アルマル",
    "🎐": "天宮こころ",
    "🌲": "エリー・コニファー",
    "🚴‍♀️": "早瀬走",
    "🧐": "シェリン・バーガンディ",
    "🔖": "フミ",
    "🌟": "星川サラ",
    "🎴": "山神カルタ",
    "★": "えま★おうがすと",
    "😎": "グウェル・オス・ガール",
    "🧷": "ましろ爻",
    "🎠": "フレン・E・ルスタリオ",
    "🐝": "メリッサ・キンレンカ",
    "💧": "イブラヒム",
    "☯️": "長尾景",
    "☯": "長尾景",
    "🌞": "甲斐田晴",
    "🌌": "空星きらめ",
    "🍯": "東堂コハク",
    "❇️": "北小路ヒスイ",
    "❇": "北小路ヒスイ",
    "🐈‍⬛": "アクシア・クローネ",
    "🍵": "オリバー・エバンス",
    "❤️‍🔥": "レイン・パターソン",
    "❤‍🔥": "レイン・パターソン",
    "💭": "天ヶ瀬むゆ",
    "🫐": "先斗寧",
    "🍀": "海妹四葉",
    "📄": "四季凪アキラ",
    "🥩": "Taka Radjiman",
    "🔶": "ZEA Cornelia",
    "☕": "Hana Macchia",
    "🚨": "Rai Galilei",
    "🐧": "Amicia Michella",
    "👽": "Azura Cecillia",
    "🐯": "Nara Haramaung",
    "🎣": "Bonnivier Pranaja",
    "🎁": "Derem Kado",
    "📶": "ウィフィ",
    "🌊": "ミン・スゥーハ",
    "👔": "ガオン",
    "🎵": "ローロー",
    "🌧": "ソ・ナギ",
    "🌧️": "ソ・ナギ",
    "🐾": "イ・シウ",
    "😸": "明楽レイ",
    "🚀": "イ・ロハ",
    "📌": "ヤン・ナリ",
    "👁‍🗨": "リュ・ハリ",
    "🌫️": "シン・ギル",
    "🌫": "シン・ギル",
    "⚜️": "オ・ジユ",
    "⚜": "オ・ジユ",
    "🍡": "ソン・ミア",
    "🏴‍☠️": "バン・ハダ",
    "🏴‍☠": "バン・ハダ",
    "🍰": "イ・オン",
    "🫧": "小清水透",
    "❤️‍🩹": "石神のぞみ",
    "❤‍🩹": "石神のぞみ",
    "🤝": "佐伯イッテツ",
    "💡": "伊波ライ",
    "📒": "司賀りこ",
    "🛼": "珠乃井ナナ",
    "🪞": "綺沙良",
    "🪷": "梢桃音",
    "🥨": "ルンルン",
    "🥗": "七瀬すず菜",
    "🍇": "酒寄颯馬",
    "🥢": "御子神琴音",

    # --- 予約語・全体歌唱 ---
    "全員": "全員"
}
# セトリパース時の除外単語
EXCLUDE_SETLIST_KEYWORDS = [
    "開始", "セトリ", "SETLIST", "本編", "待機", "挨拶",
    "MC", "トーク", "自己紹介", "感想", "告知", "お披露目",
    "OP", "ED", "スパチャ", "振り返り"
]
# キャッシュ辞書
GLOBAL_ARTIST_DB: Dict[str, str] = {}
HANDLE_MAP_LOWER = {k.lower(): v for k, v in HANDLE_TO_NAME_MAP.items()}

# --- 3. タグ判定関数 (リスト形式へ変更) ---
# パフォーマンス最適化: ループ外で小文字化マップを作成
HANDLE_MAP_LOWER = {k.lower(): v for k, v in HANDLE_TO_NAME_MAP.items()}

# ==============================================================================
# 2. タグ & メタデータ判定関数
# ==============================================================================

def analyze_video_tags(title, description, fixed_tags, channel_name="", is_short=False):
    detected_categories = set()
    detected_keywords = set()
    
    title_lower = str(title).lower()
    description_lower = str(description).lower() if description else ""

    # 1. タイトルからカテゴリを直接判定 (CATEGORY_LISTにある言葉)
    for cat in CATEGORY_LIST:
        if cat in title:
            detected_categories.add(cat)

    # 2. キーワード判定 (MEMBERS, UNITS, GAMES, PROGRAMS)
    for group_name, keyword_list in KEYWORD_GROUPS.items():
        for keyword in keyword_list:
            if keyword.lower() in title_lower:
                detected_keywords.add(keyword)

    # 3. 強制カテゴリ追加 (タイトルに特定のフレーズがあればカテゴリへ)
    for phrase, forced_cat in FORCE_CATEGORY_MAP.items():
        if phrase in title:
            detected_categories.add(forced_cat)

    # 4. 表記ゆれ・略称の変換 (マリカ → マリオカート8DX など)
    for slang, formal_tag in TAG_CONVERSION_MAP.items():
        if slang.lower() in title_lower:
            detected_keywords.add(formal_tag)

    # 5. 特殊判定 (【える】のような形式)
    if re.search(r'【[^】]*える[^】]*】', title):
        detected_keywords.add("える")
    if re.search(r'【[^】]*叶[^】]*】', title):
        detected_keywords.add("叶")

    # 6. 説明欄のハンドルネーム(@xxxx)からメンバー特定
    found_handles = re.findall(r'(@[\w\.\-]+)', description_lower)
    for handle in found_handles:
        h_lower = handle.lower()
        if h_lower in HANDLE_MAP_LOWER:
            detected_keywords.add(HANDLE_MAP_LOWER[h_lower])

    # 7. ユニットとメンバーの相互補完 (VΔLZがあれば甲斐田・弦月を追加)
    for unit_name, members in UNIT_GROUP_MAP.items():
        if unit_name in detected_keywords:
            for member in members:
                detected_keywords.add(member)
        # メンバーが全員揃っていたらユニット名も追加
        if set(members).issubset(detected_keywords):
            detected_keywords.add(unit_name)

    # 8. 固定タグ（チャンネル設定やプレイリスト設定）の反映
    if fixed_tags:
        for tag in fixed_tags:
            detected_keywords.add(tag)
            # もし固定タグがカテゴリリストにある言葉ならカテゴリにも入れる
            if tag in CATEGORY_LIST:
                detected_categories.add(tag)

    # 9. キーワードからカテゴリを推論
    # ゲーム名が含まれていれば「ゲーム実況」を追加
    games_set = set(KEYWORD_GROUPS["GAMES"])
    if not detected_keywords.isdisjoint(games_set):
        detected_categories.add("ゲーム実況")
        
    # 番組名が含まれていれば「公式企画・番組」を追加
    programs_set = set(KEYWORD_GROUPS["PROGRAMS"])
    if not detected_keywords.isdisjoint(programs_set):
        detected_categories.add("公式企画・番組")
        detected_categories.add("企画")

    # 10. 公式切り抜き判定 (ショート動画用)
    if is_short and ("長尾景" in channel_name or "長尾景" in title):
        exclude_cats = {"踊り動画", "歌動画", "楽器配信・動画", "歌配信", "踊り配信"}
        if not detected_categories.intersection(exclude_cats):
            detected_categories.add("公式切り抜き")

    # 11. 最終チェック
    if not detected_categories:
        detected_categories.add("未分類")

    return sorted(list(detected_categories)), sorted(list(detected_keywords))

# ==============================================================================
# 4. YouTube 巡回 & GitHub 連携
# ==============================================================================
# --- 4. YouTube API ---
def get_uploads_playlist_id(youtube, channel_id):
    try:
        resp = youtube.channels().list(part='contentDetails', id=channel_id).execute()
        return resp['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    except: return None
def timestamp_to_seconds(ts_str):
    parts = ts_str.split(':')
    if len(parts) == 2: return int(parts[0]) * 60 + int(parts[1])
    if len(parts) == 3: return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0

# ==============================================================================
# 3. 楽曲抽出 & セトリパース処理
# ==============================================================================
def extract_music_metadata(desc):
    auto_songs = []
    # 日本語・英語両方のパターンに対応
    song_m = re.search(r"(?:Song|曲|楽曲)\s*[:：\-]?\s*(.+)", desc, re.IGNORECASE)
    artist_m = re.search(r"(?:Artist|アーティスト)\s*[:：\-]?\s*(.+)", desc, re.IGNORECASE)
    
    if song_m:
        s_title = song_m.group(1).strip()
        s_artist = artist_m.group(1).strip() if artist_m else "Unknown Artist"
        # 配信元情報のノイズ除去
        s_artist = re.split(r'\(on behalf of', s_artist)[0].strip()
        auto_songs.append({"title": s_title, "artist": s_artist, "start": 0})
    return auto_songs
    
def parse_setlist_from_text(text, channel_owner=OWNER_NAME, fallback_members=None):
    if not text:
        return []
    text = html.unescape(text)

    r'(?:(?<=\s)|^|\b)(\d{1,2}:\d{1,2}:\d{2}|\d{1,2}:\d{2})(?!\d)'
    matches = list(re.finditer(ts_regex, text))
    if len(matches) < 3:
        return []

    raw_entries = []
    for i in range(len(matches)):
        ts_str = matches[i].group(1)
        start_idx = matches[i].end()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start_idx:end_idx].strip()
        raw_entries.append((ts_str, content))

    # 1. 登場ライバーの事前収集
    all_collab_livers = set()
    has_owner_symbol = False
    has_any_symbol = False

    for _, raw_text in raw_entries:
        line = raw_text.split('\n')[0]
        for mark in sorted(LIVER_EMOJI_MAP.keys(), key=len, reverse=True):
            liver_name = LIVER_EMOJI_MAP[mark]
            if mark in line and liver_name != "全員":
                has_any_symbol = True
                if liver_name == channel_owner:
                    has_owner_symbol = True
                else:
                    all_collab_livers.add(liver_name)

    if fallback_members:
        for m in fallback_members:
            if m != channel_owner and m in KEYWORD_GROUPS.get("MEMBERS", []):
                all_collab_livers.add(m)

    other_members = [m for m in all_collab_livers if m != channel_owner]

    # 2. 各曲の解析
    songs = []

    for ts_str, raw_text in raw_entries:
        clean_text = raw_text.split('\n')[0].strip()
        if not clean_text:
            continue

        clean_upper = clean_text.upper()
        if any(x in clean_upper for x in EXCLUDE_SETLIST_KEYWORDS):
            continue

        singers = []
        is_all = False

        if "全員" in clean_text:
            is_all = True
            clean_text = clean_text.replace("全員", "")

        for mark in sorted(LIVER_EMOJI_MAP.keys(), key=len, reverse=True):
            liver_name = LIVER_EMOJI_MAP[mark]
            if mark in clean_text:
                if liver_name == "全員":
                    is_all = True
                else:
                    singers.append(liver_name)
                clean_text = clean_text.replace(mark, "")

        singers = list(dict.fromkeys(singers))

        # 長尾景不参加の曲をスキップ（長尾の記号が全体で1度でも見つかった場合のみ適用）
        if has_any_symbol and has_owner_symbol:
            if not is_all and (channel_owner not in singers):
                continue

        # クレンジング
        clean_text = re.sub(r'^[:\s♪・\-\.\]】）)／/|｜￤~～]+', '', clean_text).strip()
        clean_text = re.sub(r'[\(（][\s,、️‍]*[\)）]', '', clean_text).strip()
        clean_text = re.sub(r'\s*[~～]+$', '', clean_text).strip()
        clean_text = re.sub(r'\s*[\(（]?http.*$', '', clean_text).strip()
        if not clean_text:
            continue

        # 曲名とアーティストの分離
        # まず「空白付きのスラッシュやハイフン」を優先
        priority_seps = [' / ', '／', ' - ', ' － ', '：', ' : ', '￤']
        matched_sep = None
        for sep in priority_seps:
            if sep in clean_text:
                matched_sep = sep
                break

        if matched_sep:
            parts = clean_text.split(matched_sep, 1)
            t, a = parts[0].strip(), parts[1].strip()
        else:
            # 空白なしの単独 '/' の場合、カッコの外側にある '/' だけで分割する
            # 例: 1925/冨田悠斗(とみー/T-POCKET) -> '1925' と '冨田悠斗(とみー/T-POCKET)'
            slash_pos = -1
            paren_depth = 0
            for idx, ch in enumerate(clean_text):
                if ch in "([（【「":
                    paren_depth += 1
                elif ch in ")]）】」":
                    paren_depth = max(0, paren_depth - 1)
                elif ch == '/' and paren_depth == 0:
                    slash_pos = idx
                    break
            
            if slash_pos != -1:
                t = clean_text[:slash_pos].strip()
                a = clean_text[slash_pos + 1:].strip()

        # トーク特有のスラッシュ誤判定を防止
        if any(c in t or c in a for c in ["？", "?", "！", "!", "w", "W", "草", "「", "」", "…", "俺","上手","思う","思って","思わ","よね","だろう","いいわ","だの","いいな","かな","布教"]):
            if not any(mark in raw_text for mark in ["♪", "♫"]):
                continue

        # with 〇〇 の付与
        if is_all:
            if other_members:
                t = f"{t} with {','.join(sorted(other_members))}"
        else:
            collab_partners = [s for s in singers if s != channel_owner]
            if collab_partners:
                t = f"{t} with {','.join(sorted(collab_partners))}"

        # 過去DBから自動補完
        if not a and GLOBAL_ARTIST_DB:
            pure_t = re.sub(r'\s+with\s+.*$', '', t).strip()
            if pure_t in GLOBAL_ARTIST_DB:
                a = GLOBAL_ARTIST_DB[pure_t]

        # 秒変換
        parts = list(map(int, ts_str.split(':')))
        if len(parts) == 3:
            sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            sec = parts[0] * 60 + parts[1]
        else:
            sec = 0

        songs.append({
            "title": t,
            "artist": a,
            "start": sec
        })

    # ★ ここから下は for ループの外（重複排除とソート）
    songs.sort(key=lambda x: x["start"])
    unique_songs = []
    seen_keys = set()
    for s in songs:
        dedup_key = (s["start"], s["title"])
        if dedup_key not in seen_keys:
            seen_keys.add(dedup_key)
            unique_songs.append(s)

    return unique_songs


def parse_cover_or_shorts(title, desc, is_short=False, video_id=None):
    """Shorts音源および歌ってみたの単曲メタデータ抽出"""
    if not desc:
        desc = ""

    # ========================================================
    # 1. 概要欄からカッコ形式の楽曲クレジットを抽出（最優先・高速）
    # ========================================================
    # パターン1: Dannie May「未完成婚姻論」
    m_bracket = re.search(r'([^\n「『\r]+?)\s*[「『]([^」』]+)[」』]', desc)
    if m_bracket:
        a_cand = re.sub(r'^(?:本家様?|Original|Music|Song|Vo|Cover|歌)[:：\s]*', '', m_bracket.group(1), flags=re.I).strip()
        t_cand = m_bracket.group(2).strip()
        # チャンネル紹介文やURL行を弾く
        if a_cand and t_cand and not any(x in a_cand for x in ["http", "@", "Twitter", "にじさんじ"]):
            return [{"title": t_cand, "artist": a_cand, "start": 0}]

    # パターン2: 「未完成婚姻論」/ Dannie May
    m_bracket_rev = re.search(r'[「『]([^」』]+)[」』]\s*[-－/／]\s*([^\n\r]+)', desc)
    if m_bracket_rev:
        t_cand = m_bracket_rev.group(1).strip()
        a_cand = re.sub(r'^(?:本家様?|Original|Music)[:：\s]*', '', m_bracket_rev.group(2), flags=re.I).strip()
        if t_cand and a_cand and not any(x in a_cand for x in ["http", "@", "Twitter", "にじさんじ"]):
            return [{"title": t_cand, "artist": a_cand, "start": 0}]

    # ========================================================
    # 2. 概要欄のキーワード（楽曲 / Music / 本家）から抽出
    # ========================================================
    if is_short:
        m = re.search(r'(?:楽曲|Music|音源)[:：\s]+(.*?)(?:\s*[-－/／]\s*)([^\n\r]+)', desc)
        if m:
            return [{"title": m.group(1).strip(), "artist": m.group(2).strip(), "start": 0}]

    meta_songs = extract_music_metadata(desc)
    if meta_songs and meta_songs[0]["artist"] and meta_songs[0]["artist"] != "Unknown Artist":
        return meta_songs

    # 本家行の探索
    for line in desc.split("\n"):
        if re.search(r'^(?:本家様?|Original|Music)[:：\s]+(.*)', line, re.I):
            val = re.sub(r'^(?:本家様?|Original|Music)[:：\s]+', '', line).strip()
            if any(x in val for x in ["http", "@", "Twitter", "にじさんじ"]):
                continue
            if " / " in val or "／" in val:
                parts = re.split(r'[/／]', val, 1)
                return [{"title": parts[0].strip(), "artist": parts[1].strip(), "start": 0}]
            elif val:
                return [{"title": re.sub(r'【.*?】|\[.*?\]', '', title).strip(), "artist": val, "start": 0}]

    # ========================================================
    # 3. タイトル形式 (曲名 / アーティスト)
    # ========================================================
    clean_title = re.sub(r'【(?:歌ってみた|COVER|Cover|歌|MV|オリジナルMV)】|\[(?:Cover|MV)\]', '', title, flags=re.I).strip()
    clean_title = re.sub(r'\/.*(?:にじさんじ|Ch).*$', '', clean_title).strip()

    pattern = r'^(.*?)(?:\s*[/／\-－]\s*)(.*?)(?:\s*[\(（].*covered.*[\)）]|\s*$)'
    m = re.search(pattern, clean_title, flags=re.I)
    if m:
        t, a = m.group(1).strip(), m.group(2).strip()
        if not a and t in GLOBAL_ARTIST_DB:
            a = GLOBAL_ARTIST_DB[t]
        return [{"title": t, "artist": a, "start": 0}]

    # ========================================================
    # 4. 概要欄に一切情報がない場合のみWebからShorts音源を取得
    # ========================================================
    if is_short and video_id:
        credit = fetch_youtube_music_credit(video_id)
        if credit and credit.get("title") and credit["title"] not in ["1.0", "1.0x", "登録", "再生"]:
            if not credit.get("artist") and credit["title"] in GLOBAL_ARTIST_DB:
                credit["artist"] = GLOBAL_ARTIST_DB[credit["title"]]
            return [credit]

    return []

def fetch_youtube_music_credit(video_id: str) -> Optional[dict]:
    """
    YouTube ShortsのHTML内から音源クレジット（曲名 · アーティスト名）を抽出する
    """
    try:
        url = f"https://www.youtube.com/shorts/{video_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
        }
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code != 200:
            return None

        html_text = res.text

        # 1. 「曲名 · アーティスト名」の中黒区切りパターン（最優先）
        # 例: {"content": "Will you marry me ? · Kiyoshi Ryujin Twenty Five"}
        m_credit = re.search(r'"content"\s*:\s*"([^"]+?)\s*[·・]\s*([^"]+?)"', html_text)
        if m_credit:
            title = m_credit.group(1).strip()
            artist = m_credit.group(2).strip()
            return {
                "title": title,
                "artist": artist,
                "start": 0
            }

        # 2. 中黒区切りがない場合のフォールバック（曲名のみ）
        m_label = re.search(r'"label"\s*:\s*"([^"]+?)"', html_text)
        if m_label:
            return {
                "title": m_label.group(1).strip(),
                "artist": "",
                "start": 0
            }

    except Exception as e:
        print(f"⚠️ [{video_id}] 音源抽出エラー: {e}")

    return None




def fetch_setlist_from_comments(youtube, video_id, fallback_members=None):
    """概要欄にセトリがない場合、コメント欄から取得"""
    best_songs = []
    
    try:
        # 1. 高評価・関連度順（上位30件を走査）
        res = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            order="relevance",
            maxResults=30,
            textFormat="plainText"
        ).execute()

        for item in res.get("items", []):
            text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            if re.search(r'\d{1,2}:\d{2}', text):
                songs = parse_setlist_from_text(text, fallback_members=fallback_members)
                if len(songs) > len(best_songs):
                    best_songs = songs

        # 充分な曲数が取れていれば早期リターン
        if len(best_songs) >= 3:
            return best_songs

        # 2. キーワード検索（「セトリ」「セットリスト」「タイムスタンプ」に対応）
        search_terms = ["セットリスト", "セトリ", "タイムスタンプ"]
        for term in search_terms:
            try:
                search_res = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    searchTerms=term,
                    maxResults=5,
                    textFormat="plainText"
                ).execute()

                for item in search_res.get("items", []):
                    text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                    if re.search(r'\d{1,2}:\d{2}', text):
                        songs = parse_setlist_from_text(text, fallback_members=fallback_members)
                        if len(songs) > len(best_songs):
                            best_songs = songs

                if len(best_songs) >= 3:
                    break
            except Exception:
                continue

        return best_songs

    except Exception as e:
        # コメント欄が無効化されている場合やAPIエラー時のログ出力
        print(f"⚠️ [{video_id}] コメント取得エラー: {e}")
        return best_songs

    
def get_duration_seconds(duration_str):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match: return 0
    h, m, s = [int(match.group(i) or 0) for i in range(1, 4)]
    return h * 3600 + m * 60 + s

def fetch_videos_from_playlist(youtube, playlist_id, channel_name, fixed_tags, auto_tags=None):
    videos = []
    next_page_token = None
    page_count = 0
    print(f"🔍 {channel_name} のプレイリストを取得中... (ID: {playlist_id})")
    
    while page_count < MAX_PAGES_TO_FETCH:
        try:
            res = youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            items = res.get('items', [])
            if not items:
                break
            
            v_ids = [it['contentDetails']['videoId'] for it in items]
            v_res = youtube.videos().list(part='contentDetails,snippet', id=','.join(v_ids)).execute()
            details = {v['id']: v for v in v_res.get('items', [])}

            for v_id in v_ids:
                if v_id not in details:
                    continue
                v_data = details[v_id]
                snip = v_data['snippet']
                desc = snip.get('description', '')
                sec = get_duration_seconds(v_data['contentDetails']['duration'])
                
                # ★ 1. 動画の本来の投稿者名（チャンネル名）を取得
                uploader_name = snip.get('channelTitle', channel_name)
                
                # ★ 2. is_short の安全な定義
                is_short = (0 < sec <= 60)
                
                # ★ 3. タグ判定 (本来の投稿者名 uploader_name を渡す)
                cat, kw = analyze_video_tags(snip['title'], desc, fixed_tags, channel_name=uploader_name, is_short=is_short)
                
                # ★ 4. カテゴリに応じた楽曲情報の自動補完
                auto_songs = []
                cat_set = set(cat)

                # 歌配信、または歌動画/踊り動画（長尺のカラオケ・ライブコラボなど）
                if "歌配信" in cat_set or cat_set.intersection({"歌動画", "踊り動画"}):
                    # 概要欄からセトリ抽出
                    auto_songs = parse_setlist_from_text(desc, fallback_members=kw)
                    
                    # 概要欄になく、5分以上の長尺動画ならコメント欄を探索
                    if not auto_songs and sec > 300:
                        print(f"💬 [{v_id}] 概要欄にセトリなし。コメント欄を探索中...")
                        auto_songs = fetch_setlist_from_comments(youtube, v_id, fallback_members=kw)
                        
                    # それでも取れず、単曲の歌動画・踊り動画なら公式メタデータまたはタイトルから抽出
                    if not auto_songs and not is_short:
                        auto_songs = extract_music_metadata(desc) or parse_cover_or_shorts(snip['title'], desc, is_short=False)
                        
                elif is_short:
                    # Shorts 音源の抽出
                    auto_songs = parse_cover_or_shorts(snip['title'], desc, is_short=True, video_id=v_id)

                # ★ 5. データの登録 ("channel" に uploader_name をセット)
                videos.append({
                    "youtubeId": v_id,
                    "title": snip['title'],
                    "channel": uploader_name,  # 投稿者名をセット
                    "date": snip['publishedAt'][:10],
                    "thumbnail": f"https://i.ytimg.com/vi/{v_id}/mqdefault.jpg",
                    "category": cat,
                    "keywords": kw,
                    "tags": auto_tags or [],
                    "songs": auto_songs
                })
            
            next_page_token = res.get('nextPageToken')
            if not next_page_token:
                break
            page_count += 1
            
        except Exception as e:
            # 404プレイリストやAPIエラー時も全体を止めずに安全に抜ける
            print(f"⚠️ {channel_name} (ID: {playlist_id}) 取得中にエラー: {e}")
            break
            
    return videos



def load_artist_db():
    """リポジトリ内の全曲情報（songs/videos.json, archives/*.json）からアーティストDBを構築"""
    global GLOBAL_ARTIST_DB
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    source_files = [
        "songs/videos.json",
        "archives/archive_videos.json",
        "archives/external_videos.json"
    ]

    all_data = []
    for rel_path in source_files:
        url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/{rel_path}"
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                raw_bytes = base64.b64decode(r.json()['content'])
                text = raw_bytes.decode('utf-8-sig').strip()
                if text:
                    all_data.extend(json.loads(text))
        except Exception:
            continue

    db = {}
    for item in all_data:
        for s in item.get("songs", []):
            title = s.get("title", "").strip()
            pure_title = re.sub(r'\s+with\s+.*$', '', title).strip()
            artist = s.get("artist", "").strip()
            if pure_title and artist and artist != "Unknown Artist" and pure_title not in db:
                db[pure_title] = artist

    GLOBAL_ARTIST_DB = db
    print(f"📚 アーティストDB初期化完了: {len(GLOBAL_ARTIST_DB)} 曲をキャッシュ")
    
def update_github_json(new_videos):
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/{JSON_FILE_PATH}"
    
    res = requests.get(url, headers=headers)
    existing_videos, existing_sha = [], None
    
    if res.status_code == 200:
        info = res.json()
        existing_sha = info['sha']
        try:
            # デコードした中身を一旦変数に入れる
            decoded = base64.b64decode(info['content']).decode('utf-8-sig').strip()
            # 中身が空でなければJSONとしてパース、空なら空リストにする
            existing_videos = json.loads(decoded) if decoded else []
        except json.JSONDecodeError:
            print("⚠️ 既存のJSONが壊れているか空のため、新規作成として処理します。")
            existing_videos = []

    managed_map = {v['youtubeId']: v for v in existing_videos if v.get('channel') in MANAGED_CHANNEL_NAMES}
    preserved = [v for v in existing_videos if v.get('channel') not in MANAGED_CHANNEL_NAMES]

    for nv in new_videos:
        vid = nv['youtubeId']
        if vid in managed_map:
            # 既存の songs/tags を保護
            if 'songs' in managed_map[vid] and managed_map[vid]['songs'] and not nv.get('songs'):
                nv['songs'] = managed_map[vid]['songs']
            if 'tags' in managed_map[vid] and managed_map[vid]['tags'] and not nv.get('tags'):
                nv['tags'] = managed_map[vid]['tags']
            managed_map[vid].update(nv)
        else:
            managed_map[vid] = nv

    final = sorted(preserved + list(managed_map.values()), key=lambda x: x.get('date', ''), reverse=True)
    
    # 書き出し
    json_text = json.dumps(final, indent=2, ensure_ascii=False)
    payload = {
        "message": "BOT: Update archive",
        "content": base64.b64encode(json_text.encode('utf-8')).decode('utf-8'),
        "sha": existing_sha
    }
    
    put_res = requests.put(url, headers=headers, json=payload)
    if put_res.status_code in [200, 201]:
        print("🚀 Archive updated successfully.")
    else:
        print(f"❌ Failed to update GitHub: {put_res.status_code}")
        print(put_res.text)

# ==============================================================================
# 5. エントリーポイント
# ==============================================================================
def main():
    if not YOUTUBE_API_KEY or not GITHUB_TOKEN: return
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    fetched_videos = []
    
    # 1. チャンネルの通常アップロード
    for ch in CHANNELS:
        pid = get_uploads_playlist_id(youtube, ch['id'])
        if pid: fetched_videos.extend(fetch_videos_from_playlist(youtube, pid, ch['name'], ch.get('fixed_tags', [])))

    # 2. 特殊プレイリスト (自動タグ付与あり)
    for pl in EXTRA_PLAYLISTS:
        try:
            # ★ pl.get('name', OWNER_NAME) にすることで、'name' キーが未定義でもエラーを回避
            pl_name = pl.get('name', OWNER_NAME)
            fetched_videos.extend(fetch_videos_from_playlist(
                youtube,
                pl['id'],
                pl_name,
                pl.get('fixed_tags', []),
                auto_tags=pl.get('auto_tags')
            ))
        except Exception as e:
            print(f"⚠️ プレイリストスキップ (ID: {pl.get('id')}): {e}")

    
    if fetched_videos:
        update_github_json(fetched_videos)

if __name__ == "__main__":
    main()


