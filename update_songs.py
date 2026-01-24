import json
import os

# --- 設定 ---
VIDEO_FILE = 'archives/videos.json'
EXTERNAL_FILE = 'archives/external_videos.json'

FINAL_FILE = 'songs/final_videos.json'
TEMP_FILE = 'songs/videos.json'

# 抽出対象の動画タグ
TARGET_TAGS = ["歌動画", "歌配信", "楽器配信・動画", "踊り動画", "踊り配信"]

# ★ここが重要：緑仙が参加しているユニット・名義のリスト
# artistにこれらが含まれていれば「オリジナル」と判定します。
# また、この名前自体を「タグ」として自動追加します。
RYUSHEN_ARTISTS = [
    "Rain Drops",
    "cresc.",
    "ERRors",
    "ぱんだ立どじゃ高校",
    "にじさんじ",
    "解散GIG",
    "チームヘラクレス",
    "ヘラクレスメンバー",
    "le jouet",
    "七次元生徒会",
    "こじらせハラスメント",
    "緑仙 & ポルカドットスティングレイ",          # "緑仙 & 〇〇" のパターン用
    "緑仙"            # ソロ
]

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} が見つかりませんでした。")
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: {filepath} の読み込みに失敗しました ({e})")
        return []

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_and_merge_data():
    """videos.json と external_videos.json をマージ"""
    videos_data = load_json(VIDEO_FILE)
    external_data = load_json(EXTERNAL_FILE)
    
    # IDをキーにしてマージ（externalで上書き）
    merged_map = {}
    for v in videos_data:
        if 'youtubeId' in v: merged_map[v['youtubeId']] = v
    for v in external_data:
        if 'youtubeId' in v: merged_map[v['youtubeId']] = v
            
    return list(merged_map.values())

def is_target_video(video):
    """動画自体のタグ判定"""
    tags = video.get('tags', []) + video.get('category', [])
    return bool(set(tags) & set(TARGET_TAGS))

def generate_song_tags(song_artist):
    """
    アーティスト名から自動でタグ（オリジナル/カバー、ユニット名）を生成する関数
    """
    tags = []
    is_original = False
    
    # アーティスト名が空の場合は処理しない
    if not song_artist:
        return ["カバー"] # 不明な場合はとりあえずカバー扱い

    # ユニットリストと照合
    for unit in RYUSHEN_ARTISTS:
        if unit in song_artist:
            is_original = True
            
            # ユニット名自体もタグにする（"緑仙" や "緑仙&" は除外）
            if unit != "緑仙" and unit != "緑仙&":
                tags.append(unit)
            
            # "緑仙 & 〇〇" の場合、相手の名前もタグ化したいなら
            # ここで split などの処理を追加することも可能ですが、
            # 基本は artist 名全体が検索対象になるので必須ではありません。
            
            break

    if is_original:
        tags.append("オリジナル")
    else:
        tags.append("カバー")
        
    return tags

def main():
    # 1. データの読み込みとマージ
    all_videos = load_and_merge_data()
    if not all_videos:
        return

    # 2. 動画のフィルタリング
    current_target_videos = []
    for video in all_videos:
        if is_target_video(video):
            # --- ここで曲ごとのタグ付け処理を行う ---
            new_songs = []
            for song in video.get('songs', []):
                # 既存のタグを取得（手動でつけたタグがある場合用）
                existing_tags = song.get('tags', [])
                
                # 自動判定タグを生成
                auto_tags = generate_song_tags(song.get('artist', ''))
                
                # マージして重複排除
                final_song_tags = list(set(existing_tags + auto_tags))
                
                # ソングデータを更新
                song['tags'] = final_song_tags
                new_songs.append(song)
            
            video['songs'] = new_songs
            current_target_videos.append(video)

    # マップ作成（IDキー）
    current_map = {v['youtubeId']: v for v in current_target_videos}

    # 3. 前回のマスターデータ読み込み
    old_final_list = load_json(FINAL_FILE)
    old_final_map = {v['youtubeId']: v for v in old_final_list}

    # 4. videos.json 読み込み
    videos_json_list = load_json(TEMP_FILE)
    videos_json_map = {v['youtubeId']: v for v in videos_json_list}

    # 5. 差分検知 & videos.json 更新
    updated_count = 0
    for vid, current_video in current_map.items():
        old_video = old_final_map.get(vid)
        
        # 新規または変更があれば
        if (old_video is None) or (current_video != old_video):
            videos_json_map[vid] = current_video
            updated_count += 1

    # 6. 保存
    # A. 新着リスト
    new_videos_list = list(videos_json_map.values())
    new_videos_list.sort(key=lambda x: x.get('date', ''), reverse=True)
    save_json(TEMP_FILE, new_videos_list)
    print(f"Update: {TEMP_FILE} (計 {len(new_videos_list)} 件, 更新: {updated_count} 件)")
    
    # B. マスターリスト
    current_list_sorted = list(current_map.values())
    current_list_sorted.sort(key=lambda x: x.get('date', ''), reverse=True)
    save_json(FINAL_FILE, current_list_sorted)
    print(f"Update: {FINAL_FILE} (計 {len(current_list_sorted)} 件)")

if __name__ == "__main__":
    main()
