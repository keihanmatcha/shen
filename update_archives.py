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
GITHUB_REPO_NAME = "oukasui"
JSON_FILE_PATH = "archives/archive_videos.json"
MAX_PAGES_TO_FETCH = 100

CHANNELS = [
    {
        "id": "UCt5-0i4AVHXaWJrL8Wql3mw",
        "name": "緑仙"
    },
    {
        "id": "UChqQiUSyI-Q1j3k57_mAJHA",
        "name": "RainDrops",
        "fixed_tags": ["える", "ジョー・力一","鈴木勝","三枝明那","童田明治","RainDrops"]
    },
    {
        "id": "UCHRCp0CSacVnTVS2Z4x9xYg",
        "name": "七次元生徒会",
        "fixed_tags": ["叶", "樋口楓","三枝明那","レオス・ヴィンセント","周央サンゴ", "七次元生徒会"]
    }
]

# 管理対象のチャンネル名リスト
MANAGED_CHANNEL_NAMES = [ch["name"] for ch in CHANNELS]

# --- 2. 自動タグ付け用の辞書定義 ---
CATEGORY_LIST = [
    "ゲーム実況", "雑談", "歌配信", "歌動画", "踊り動画", "踊り配信",
    "記念配信", "殺陣", "お披露目配信", "3D", "企画", "大会", "対談",
    "ライブイベント", "楽器配信・動画", "プロモーション", "公式企画・番組",
    "動画系", "公式切り抜き", "手描き動画", "ぷちさんじ"
]

# 【追加】タイトルに含まれていたら強制的にカテゴリに追加するマッピング
FORCE_CATEGORY_MAP = {
    "踊ってみた": "踊り動画",
    "歌ってみた": "歌動画",
    "楽曲": "歌動画",
    "3D": "3D",
    "XFDムービー":"プロモーション",
    "特典":"プロモーション",
    "Cover": "歌動画",
    "踊ってみた": "踊り動画",
    "踊って": "踊り動画",
    "感想配信": "記念配信",
    "告知": "プロモーション",
    "ティーザー": "プロモーション",
    "ダンス動画": "踊り動画",
    "ダンス配信": "踊り配信",
    "ベース練習": "楽器配信・動画",
    "弾いて": "楽器配信・動画",
    "弾ける": "楽器配信・動画",
    "歌枠": "歌配信",
    "歌って": "歌動画",
    "歌ってみた": "歌動画",
    "COVER": "歌動画",
    "LIVE": "ライブイベント",
    "ライブ": "ライブイベント",
    "殺陣": "殺陣",
    "お披露目": "お披露目配信"
}

KEYWORD_GROUPS = {
    "MEMBERS": [
        "愛園愛美", "相羽ういは", "赤城ウェン", "赤羽葉子", "アクシア・クローネ", "朝日南アカネ", "飛鳥ひな", "遠北千南", "長尾姉上",
        "安土桃", "天ヶ瀬むゆ", "天宮こころ", "雨森小夜", "アルス・アルマル", "アンジュ・カトリーナ", "家長むぎ", "五十嵐梨花",
        "石神のぞみ", "出雲霞", "五木左京", "伊波ライ", "戌亥とこ", "イブラヒム", "宇佐美リト", "宇志海いちご", "卯月コウ",
        "海妹四葉", "エクス・アルビオ", "えま★おうがすと", "エリー・コニファー", "御伽原江良", "小野町春香", "オリバー・エバンス",
        "魁星", "甲斐田晴", "加賀美ハヤト", "蝸堂みかる", "綺沙良", "鏑木ろこ", "神田笑一", "北小路ヒスイ", "北見遊征", "雲母たまこ",
        "ギルザレンⅢ世", "グウェル・オス・ガール", "葛葉", "倉持めると", "黒井しば", "来栖夏芽", "郡道美玲", "弦月藤士郎", "剣持刀也",
        "梢桃音", "小清水透", "小柳ロウ", "佐伯イッテツ", "早乙女ベリー", "榊ネス", "酒寄颯馬", "桜凛月", "笹木咲", "椎名唯華", "シェリン・バーガンディ",
        "栞葉るり", "司賀りこ", "四季凪アキラ", "獅子堂あかり", "静凛", "シスター・クレア", "渋谷ハジメ", "篠宮ゆの", "城瀬いすみ", "ジョー・力一","鈴原るる",
        "白雪巴", "周央サンゴ", "健屋花那", "鈴鹿詩子", "皇れお", "鈴木勝", "鈴原るる", "鈴谷アキ", "瀬戸美夜子", "セラフ・ダズルガーデン",
        "ソフィア・ヴァレンタイン", "空星きらめ", "鷹宮リオン", "立伝都々", "珠乃井ナナ", "月ノ美兎", "でびでび・でびる", "東堂コハク",
        "十河ののは", "ドーラ", "轟京子", "名伽尾アズマ", "渚トラウト","長尾景", "七瀬すず菜", "奈羅花", "成瀬鳴", "西園チグサ", "ニュイ・ソシエール",
        "猫屋敷美紅", "葉加瀬冬雪", "花畑チャイカ", "早瀬走", "葉山舞鈴", "春崎エアル", "花籠つばさ", "樋口楓", "一橋綾人", "緋八マナ",
        "壱百満天原サロメ", "風楽奏斗", "伏見ガク", "フミ", "文野環", "フレン・E・ルスタリオ", "不破湊", "ベルモンド・バンデラス",
        "星川サラ", "星導ショウ", "先斗寧", "本間ひまわり", "舞元啓介", "魔界ノりりむ", "ましろ爻", "町田ちま", "魔使マオ", "黛灰",
        "ミラン・ケストレル", "叢雲カゲツ", "メリッサ・キンレンカ", "森中花咲", "矢車りね", "夜牛詩乃", "社築", "山神カルタ", "勇気ちひろ",
        "夕陽リリ", "雪城眞尋", "夢月ロア", "夢追翔", "夜見れな", "ラトナ・プティ", "リゼ・ヘルエスタ","竜胆尊", "ルイス・キャミー",
        "ルンルン", "レイン・パターソン", "レヴィ・エリファ", "レオス・ヴィンセント", "ローレン・イロアス", "渡会雲雀", "童田明治",
        # EN / ID / KR
        "Amicia Michella", "Xia-Ekavira", "Zea-Cornelia", "Taka Radjiman", "Derem Kado", "Nara Haramaung", "Hana Macchia",
        "Mika Melatika", "Miyu Ottavia", "Layla Astroemeria", "Riksa Dhirendra", "Reza Avanluna", "아키라 레이（明楽 レイ）",
        "이로하（イ・ロハ）", "오지유（オ・ジユ）", "가온（ガオン）", "신유야（シン・ユヤ）", "세피나（セフィナ）", "소나기（ソ・ナギ）",
        "나세라（ナ・セラ）", "하윤（ハ・ユン）", "반하다（バン・ハダ）", "민수하（ミン・スゥーハ）", "양나리（ヤン・ナリ）", "Ike Eveland",
        "Aia Amare", "Yugo Asuma", "Vezalius Bandage", "Uki Violeta", "Enna Alouette", "Elira Pendora", "Endou Reimu", "Fulgur Ovid",
        "Kyoran Meloco", "Kaelix Debonair", "Sonny Brisko", "Selen Tatsuki", "Torahime Kotoka", "Petra Gurin", "Pomu Rainpuff",
        "Maria Marionette", "Millie Parfait", "Shu Yamino", "Luca Kaneshiro", "Ren Zotto", "星弥", "Noor",
        # 外部・声優・その他
        "歌衣メイカ", "渋谷ハル", "熊谷タクマ", "かなえ先生", "天開司", 
        "百花繚乱", "ぽんぽこ", "ピーナッツくん", "ばあちゃる", "英リサ",
        "兎麹まり", "一ノ瀬うるは", "神威きゅぴ", "橘ひなの", "八雲ぺに", "ゴモリー", "多井隆晴", "松本吉弘", "前野智昭", "土田玲央",
        "平川大輔", "龍惺ろたん"
    ],
    "UNITS": [
        "七次元生徒会", "アニソンカラオケ同好会", "Alri", "いちから中央銀行", "いのるぱんだ", "ウィシェン", "エビ仙", "ERRors",
        "解散GIG", "cresc.", "こじらせハラスメント", "SEEDs1期生", "チームヘラクレス",
        "しかばねぱんだ", "私立だいさんじ学園", "西弦緑渡", "にじさんじ乙女ゲーム製作委員会",
        "にじさんじカゲプロ", "にじさんじレジスタンス", "にじさんじ恋愛相談室", "にじ飯調査隊",
        "SitR名古屋", "にじロック", "ねないこ", "Vtuberロック革命","保健室組","保健室同盟","よるみどり",
        "猟友会","RainDrops","le jouet","レッドガーネット","ワールドアトラス", "2年4組"
    ],
    "GAMES": [
        "アイドルマスター SideM", "あつまれどうぶつの森", "Apex Legends", "A Little to the Left", "BUCK SHOT ROULETTE", "ARK",
        "ARK:Survival Ascended", "ARK:Survival Evolved", "ARK-アイランドマップ", "ARK-ラグナロクマップ", "ときめきメモリアル", "AmongUs",
        "ARK-エクスティンクションマップ", "ARK-クリスタルアイルズマップ", "ASTRONEER", "Blazing Sails", "ドラえもんのどら焼き屋さん物語",
        "Cooking Simulator", "Dead by Daylight", "eFootball ウイニングイレブン", "ウマ娘　プリティダービー", "Ring Fit Adventure",
        "おえかきの森", "Fall Guys", "Getting Over It", "Gartic Phones", "Get To Work", "Golf It!", "Inverted Angel",
        "Fast Food Simulator", "Human: Fall Flat", "Left 4 Dead 2", "maimai", "Nintendo Switch Sports", "PADDLE PADDLE PADDLE",
        "Operation: Tango", "Overcooked!2", "Overwatch", "Overwatch2", "Papers, Please", "PEAK", "Portal2","一致するまで終われまテン!!",
        "PowerWash Simulator", "PUBG", "slither.io/wormax.io", "Stray", "BLEACH", "ラブラブスクールデイズ", "Unpacking",
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
        "Poppy Playtime", "Keep Talking and Nobody Explodes", "Protein for Muscle", "R.E.P.O.", "青鬼", "RTA", "例外配達",
        "その他ホラーゲーム", "カードゲーム", "その他ゲーム", "Five Nights at Freddy's", "Getting Over It", "V最協", "V祭協"
    ],
    "PROGRAMS": [
        "SYMPHONIA Day1", "LOCK ON FLEEK", "にじ鯖夏祭り", "VTuberエンジョイカジュアル交流戦",
        "ベース","緑仙1st Ryushen", "緑仙2nd 緑一色", "CDJ2425",
        "CDJ2526", "にじロック", "V祭協", "NIJIROCK NEXTBEAT", "くろのわーるがなんかやる",
        "にじさんじ Anniversary Festival 2021 前夜祭", "ゲームる？ゲームる！", "だいさんじ甲子園", "にじさんじ甲子園",
        "にじワイテ人狼RPG", "格付けマリカ", "にじさんじイカ祭り", "にじさんじスマブラ杯", "神域甲子園", "ながおちぐ甲子園",
        "マリカにじさんじ杯", "にじスプラDREAMDEATHMATCH", "にじスプラ大会", "ミリしらスト６チャレンジ", "FIFA",
        "にじさんじイヤホンガンガンゲーム", "みどりとお話するだけ", "緑仙の音楽ダイアログ", "NIJIMelodyTime",
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
    "楽曲": "歌動画",
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
    "談義": "対談",
    "XFDムービー":"プロモーション",
    "特典":"プロモーション",
    "Cover": "歌動画",
    "踊ってみた": "踊り動画",
    "踊って": "踊り動画",
    "感想配信": "記念配信",
    "告知": "プロモーション",
    "ティーザー": "プロモーション",
    "ダンス動画": "踊り動画",
    "ダンス配信": "踊り配信",
    "ベース練習": "楽器配信・動画",
    "弾いて": "楽器配信・動画",
    "弾ける": "楽器配信・動画",
    "ポケカ": "Pokémon Trading Card Game Pocket",
    "パワプロ": "パワフルプロ野球",
    "にじさんじマリカ杯": "マリカにじさんじ杯",
    "プロセカ": "プロジェクトセカイ カラフルステージ！ feat. 初音ミク",
    "ヒューマンフォールフラット": "Human: Fall Flat",
    "レイドロ": "RainDrops",
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
    "OW": "Overwatch",
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
    "@GilzarenIII": "ギルザレンIII世", "@KenmochiToya": "剣持刀也", "@Kanae": "叶", "@ShiinaYuika": "椎名唯華", "@Dola": "ドーラ",
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
    "@KanaeVCriminologist": "かなえ先生", "@Peanutskun": "ピーナッツくん", "@pokopea": "ぽんぽこ", "@_Ubiba": "ばあちゃる",
    "@lisahanabusa": "英リサ", "@TOMARI_MARI": "兎麹まり", "@uruhaichinose": "一ノ瀬うるは", "@KaminariQpi": "神威きゅぴ",
    "@hinanotachiba7": "橘ひなの", "@八雲ぺに": "八雲ぺに", "@takachan0317": "多井隆晴", "@zunmaruch": "村上淳",
    "@SuzukiTaro_CH": "鈴木たろう", "@sibukawa": "渋川難波", "@Matsumotogumi": "松本吉弘", "@RyuseiRotan": "龍惺ろたん",
    "@tenkaitsukasa": "天開司", "@sakinomoco": "咲乃もこ", "@Izumi_Yunohara": "柚原いづみ", "@OmaruPolka": "尾丸ポルカ",
    "@TakaneLui": "鷹嶺ルイ", "@MoriCalliope": "森カリオペ", "@Inaba_Haneru": "因幡はねる"
}
"七次元生徒会", "アニソンカラオケ同好会", "Alri", "いちから中央銀行", "いのるぱんだ", "ウィシェン", "エビ仙", "ERRors",
        "解散GIG", "cresc.", "こじらせハラスメント", "SEEDs1期生", "チームヘラクレス",
        "しかばねぱんだ", "私立だいさんじ学園", "西弦緑渡", "にじさんじ乙女ゲーム製作委員会",
        "にじさんじカゲプロ", "にじさんじレジスタンス", "にじさんじ恋愛相談室", "にじ飯調査隊",
        "SitR名古屋", "にじロック", "ねないこ", "Vtuberロック革命","保健室組","保健室同盟","よるみどり",
        "猟友会","RainDrops","le jouet","レッドガーネット","ワールドアトラス", "2年4組"
UNIT_GROUP_MAP = {
    "七次元生徒会": ["叶", "樋口楓","三枝明那","レオス・ヴィンセント","周央サンゴ"],
    "RainDrops": ["える", "ジョー・力一","鈴木勝","三枝明那","童田明治","RainDrops"]
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
    "西弦緑渡": ["弦月藤士郎", "西園チグサ", "渡会雲雀"],
    "私立だいさんじ学園": ["花畑チャイカ", "剣持刀也", "鷹宮リオン"],
    "にじさんじカゲプロ": ["樋口楓","町田ちま","戌亥とこ","リゼ・ヘルエスタ","三枝明那","葉加瀬冬雪","星川サラ","ましろ爻","弦月藤士郎","西園チグサ","レイン・パターソン","渡会雲雀"],
    "アニソンカラオケ同好会": [ 早瀬走", "オリバー・エバンス","社築"],
    "にじさんじ乙女ゲーム製作委員会": ["葉加瀬冬雪", "ニュイ・ソシエール", "奈羅花"],
    "Alri": ["アンジュ・カトリーナ"],
    "ねないこ": ["鈴谷アキ"],
    "しかばねぱんだ": ["赤羽葉子"],
    "解散GIG": ["笹木咲", "椎名唯華","赤羽葉子"],
    "cresc.": ["シスター・クレア", "ドーラ"],
    "ERRors": ["える", "夕陽リリ"],
    "にじ飯調査隊":["伏見ガク","長尾景"]
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
# --- 3. タグ判定関数 (リスト形式へ変更) ---
# パフォーマンス最適化: ループ外で小文字化マップを作成
HANDLE_MAP_LOWER = {k.lower(): v for k, v in HANDLE_TO_NAME_MAP.items()}

def analyze_video_tags(title, description, fixed_tags, channel_name="", is_short=False):
    detected_categories = set()  # セットで重複排除
    detected_keywords = set()
    
    title_lower = str(title).lower()
    description_lower = str(description).lower() if description else ""

    # 1. カテゴリ判定（該当するものをすべて追加）
    for cat in CATEGORY_LIST:
        if cat in title:
            detected_categories.add(cat)

    # 2. キーワード判定
    for group_name, keyword_list in KEYWORD_GROUPS.items():
        for keyword in keyword_list:
            if keyword.lower() in title_lower:
                detected_keywords.add(keyword)

    # 3. 特別判定処理
    if re.search(r'【[^】]*える[^】]*】', title):
        detected_keywords.add("える")
    if re.search(r'【[^】]*叶[^】]*】', title):
        detected_keywords.add("叶")

    # 【変更点】FORCE_CATEGORY_MAPを使った強制カテゴリ追加
    # タイトルに "踊ってみた" があれば "踊り動画" をカテゴリリストに追加（複数可）
    for phrase, forced_cat in FORCE_CATEGORY_MAP.items():
        if phrase in title:
            detected_categories.add(forced_cat)

    # 4. 表記ゆれ・略称から正式タグを追加
    for slang, formal_tag in TAG_CONVERSION_MAP.items():
        if slang.lower() in title_lower:
            detected_keywords.add(formal_tag)

    # 5. ハンドルネーム(@xxxx)の検出
    found_handles = re.findall(r'(@[\w\.\-]+)', description_lower)
    for handle in found_handles:
        h_lower = handle.lower()
        if h_lower in HANDLE_MAP_LOWER:
            detected_keywords.add(HANDLE_MAP_LOWER[h_lower])

    # 6. ユニットとメンバーの相互補完
    for unit_name, members in UNIT_GROUP_MAP.items():
        if unit_name in detected_keywords:
            for member in members:
                detected_keywords.add(member)
        if set(members).issubset(detected_keywords):
            detected_keywords.add(unit_name)

    # 7. 固定タグ
    if fixed_tags:
        for tag in fixed_tags:
            detected_keywords.add(tag)

    # 8. カテゴリの自動修正 (キーワードからカテゴリを逆算)
    # リストが空ならキーワードから探す
    if not detected_categories:
        for kw in detected_keywords:
            if kw in CATEGORY_LIST:
                detected_categories.add(kw)
                break

    # 9. ゲーム実況判定
    has_game_keyword = False
    games_set = set(KEYWORD_GROUPS["GAMES"])
    if not detected_keywords.isdisjoint(games_set):
        has_game_keyword = True
    
    if has_game_keyword:
        if not detected_categories:
            detected_categories.add("ゲーム実況")
        else:
            if "ゲーム実況" not in detected_categories:
                detected_categories.add("ゲーム実況")
            
    # 【変更点】10. 公式切り抜き判定
    # 条件: ショート動画 かつ タイトルまたはチャンネル名に「長尾景」が含まれる
    if is_short and ("長尾景" in channel_name or "長尾景" in title):
        # 除外したいカテゴリ（これらが含まれていたら「公式切り抜き」は足さない）
        exclude_categories = {"踊り動画", "歌動画", "楽器配信・動画", "歌配信", "踊り配信"}
        
        # 積集合をとって、除外カテゴリが1つも含まれていない場合のみ追加
        if not detected_categories.intersection(exclude_categories):
            detected_categories.add("公式切り抜き")

    # 最終的に空なら「未分類」を入れる
    if not detected_categories:
        detected_categories.add("未分類")

    # リストに変換してソート
    return sorted(list(detected_categories)), sorted(list(detected_keywords))

# --- 4. YouTube API ---
def get_duration_seconds(duration_str):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    return h * 3600 + m * 60 + s

def get_uploads_playlist_id(youtube, channel_id):
    try:
        resp = youtube.channels().list(part='contentDetails', id=channel_id).execute()
        return resp['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    except Exception as e:
        print(f"❌ Error getting playlist ID: {e}")
        return None

def fetch_videos_from_playlist(youtube, playlist_id, channel_name, fixed_tags):
    videos = []
    next_page_token = None
    page_count = 0
    
    print(f"🔍 {channel_name} の動画を取得開始...")
    
    while page_count < MAX_PAGES_TO_FETCH:
        try:
            request = youtube.playlistItems().list(
                part='snippet,contentDetails', playlistId=playlist_id,
                maxResults=50, pageToken=next_page_token
            )
            response = request.execute()
            items = response.get('items', [])
            if not items: break
            
            video_ids = [item['contentDetails']['videoId'] for item in items]
            
            vid_response = youtube.videos().list(
                part='contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            durations = {}
            for v in vid_response.get('items', []):
                durations[v['id']] = v['contentDetails']['duration']

            for item in items:
                snippet = item['snippet']
                if not snippet.get('publishedAt'): continue
                
                try:
                    dt = datetime.strptime(snippet['publishedAt'][:10], '%Y-%m-%d')
                    published_date = dt.strftime('%Y-%m-%d')
                except ValueError:
                    published_date = "2000-01-01"

                video_id = item['contentDetails']['videoId']
                
                duration_str = durations.get(video_id, "PT0S")
                seconds = get_duration_seconds(duration_str)
                is_short = (0 < seconds <= 60)
                
                # categories (list) を取得
                categories, keywords = analyze_video_tags(
                    snippet['title'], 
                    snippet.get('description', ''), 
                    fixed_tags, 
                    channel_name=channel_name, 
                    is_short=is_short
                )
                
                videos.append({
                    "youtubeId": video_id,
                    "title": snippet['title'],
                    "channel": channel_name,
                    "date": published_date,
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
                    "category": categories, 
                    "keywords": keywords,
                    "songs": []
                })
                
            next_page_token = response.get('nextPageToken')
            page_count += 1
            print(f"  - Page {page_count}: {len(videos)} videos fetched so far.")
            
            if not next_page_token: break
            
        except Exception as e:
            print(f"⚠️ Fetch Error on page {page_count}: {e}")
            break
            
    print(f"✅ {channel_name}: 合計 {len(videos)} 件取得成功")
    return videos

# --- 5. GitHub更新処理 (リスト対応版) ---
def update_github_json(new_videos):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    contents_url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/{JSON_FILE_PATH}"

    response = requests.get(contents_url, headers=headers)
    existing_videos = []
    existing_sha = None

    if response.status_code == 200:
        content_info = response.json()
        existing_content = content_info['content']
        existing_sha = content_info['sha']
        try:
            decoded_content = base64.b64decode(existing_content).decode('utf-8-sig')
            existing_videos = json.loads(decoded_content)
        except Exception:
            print("⚠️ 予期せぬエラーによりファイルを初期化します。")
            existing_videos = []
    else:
        print(f"ℹ️ ファイルが見つかりません。新規作成します。")
        existing_videos = []

    preserved_videos = [v for v in existing_videos if v.get('channel') not in MANAGED_CHANNEL_NAMES]
    managed_map = {v['youtubeId']: v for v in existing_videos if v.get('channel') in MANAGED_CHANNEL_NAMES}
    
    updated_count = 0
    added_count = 0

    for new_video in new_videos:
        vid_id = new_video['youtubeId']
        
        if vid_id in managed_map:
            existing_record = managed_map[vid_id]
            is_changed = False
            
            if 'songs' not in existing_record: existing_record['songs'] = []
            
            # カテゴリの比較（リスト同士の比較）
            old_cat = existing_record.get('category')
            # 古いデータが文字列だった場合の互換処理（比較用）
            if isinstance(old_cat, str):
                old_cat = [old_cat] if old_cat != "未分類" else []
                # 既存データ側もリスト形式に更新しておく
                existing_record['category'] = new_video['category']
                is_changed = True
            elif isinstance(old_cat, list):
                if sorted(old_cat) != sorted(new_video['category']):
                    existing_record['category'] = new_video['category']
                    is_changed = True
            else:
                 # categoryキーが無い場合など
                existing_record['category'] = new_video['category']
                is_changed = True

            current_kws = set(existing_record.get('keywords', []))
            new_kws = set(new_video['keywords'])
            
            if current_kws != new_kws:
                existing_record['keywords'] = list(new_kws)
                is_changed = True
            
            if is_changed: updated_count += 1
            managed_map[vid_id] = existing_record
        else:
            managed_map[vid_id] = new_video
            added_count += 1

    final_videos_list = preserved_videos + list(managed_map.values())
    final_videos_list.sort(key=lambda x: x.get('date', '1900-01-01'), reverse=True)

    print(f"📦 コミット準備: 新規{added_count}件, 更新{updated_count}件, 総数{len(final_videos_list)}件")
    
    new_content_bytes = json.dumps(final_videos_list, indent=2, ensure_ascii=False).encode('utf-8')
    new_content_base64 = base64.b64encode(new_content_bytes).decode('utf-8')

    commit_data = {
        "message": f"ARCHIVE_BOT: Repair & Update (Add {added_count}, Update {updated_count})",
        "content": new_content_base64,
        "sha": existing_sha
    }

    put_res = requests.put(contents_url, headers=headers, json=commit_data)
    if put_res.status_code in [200, 201]:
        print(f"🚀 GitHubコミット完了！")
    else:
        print(f"❌ コミット失敗: {put_res.status_code}")
        print(put_res.text)

# --- 6. メイン処理 ---
def main():
    print("--- 長尾景＆VΔLZ アーカイブ全件更新スクリプト開始 ---")
    if not YOUTUBE_API_KEY or not GITHUB_TOKEN:
        print("❌ エラー: 環境変数 (YOUTUBE_API_KEY, GITHUB_TOKEN) が設定されていません")
        return

    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    fetched_videos = []
    
    for ch in CHANNELS:
        playlist_id = get_uploads_playlist_id(youtube, ch['id'])
        if playlist_id:
            fixed_tags = ch.get('fixed_tags', [])
            videos = fetch_videos_from_playlist(youtube, playlist_id, ch['name'], fixed_tags)
            fetched_videos.extend(videos)

    if fetched_videos:
        update_github_json(fetched_videos)
    else:
        print("⚠️ 動画が1件も取得できませんでした。")

if __name__ == "__main__":
    main()








