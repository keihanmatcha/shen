import json
import os

# --- 設定 ---
# 入力ファイル
VIDEO_FILE = 'archives/videos.json'              # 通常データ
EXTERNAL_FILE = 'archives/external_videos.json'  # 優先データ

# 出力ファイル
FINAL_FILE = 'songs/final_videos.json'  # マスターデータ（全件）
TEMP_FILE = 'songs/videos.json'         # 更新・新着データ（蓄積）

# 抽出対象のタグ
TARGET_TAGS = ["歌動画", "歌配信", "楽器配信・動画", "踊り動画", "踊り配信"]

def load_json(filepath):
    """JSONファイルを読み込む。なければ空リストを返す。"""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: {filepath} の読み込みに失敗しました ({e})")
        return []

def save_json(filepath, data):
    """JSONファイルに保存する。"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_and_merge_data():
    """
    2つのJSONファイルを読み込み、IDベースでマージする。
    external_videos.json のデータを優先（上書き）する。
    """
    videos_data = load_json(VIDEO_FILE)
    external_data = load_json(EXTERNAL_FILE)
    
    # IDをキーにしてマージ（externalで上書き）
    merged_map = {}
    for v in videos_data:
        if 'youtubeId' in v: merged_map[v['youtubeId']] = v
    for v in external_data:
        if 'youtubeId' in v: merged_map[v['youtubeId']] = v # 上書き
            
    return list(merged_map.values())

def is_target_video(video):
    """タグ判定ロジック"""
    tags = video.get('tags', [])
    return bool(set(tags) & set(TARGET_TAGS))

def main():
    # 1. 最新データの準備（マージ済み）
    all_videos = load_and_merge_data()
    if not all_videos:
        print("エラー: 動画データがありません。")
        return

    # 歌動画のみにフィルタリング
    current_target_videos = [v for v in all_videos if is_target_video(v)]
    
    # 高速検索用にIDをキーにしたマップを作成（今回の最新状態）
    current_map = {v['youtubeId']: v for v in current_target_videos}

    # 2. 前回のマスターデータ(final)を読み込み（比較用）
    old_final_list = load_json(FINAL_FILE)
    old_final_map = {v['youtubeId']: v for v in old_final_list}

    # 3. videos.json (更新通知用) を読み込み
    # 既存のリストを維持しつつ、今回変更があったものを上書き/追加する
    videos_json_list = load_json(TEMP_FILE)
    # IDをキーにしてマップ化（重複防止・更新用）
    videos_json_map = {v['youtubeId']: v for v in videos_json_list}

    # 4. 差分チェック & 更新反映
    updated_count = 0
    
    for vid, current_video in current_map.items():
        old_video = old_final_map.get(vid)
        
        # 判定ロジック:
        # (A) 新規追加: old_videoが存在しない
        # (B) 内容変更: old_videoと中身が一致しない
        if (old_video is None) or (current_video != old_video):
            # videos.json用のマップに最新情報をセット（Upsert）
            videos_json_map[vid] = current_video
            updated_count += 1
            
            status = "新規" if old_video is None else "変更"
            print(f"[{status}] {current_video.get('title', 'No Title')}")

    # 5. 保存処理

    # A. videos.json (更新・新着のみの蓄積リスト)
    # マップからリストに戻し、日付順にソート
    new_videos_list = list(videos_json_map.values())
    new_videos_list.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    save_json(TEMP_FILE, new_videos_list)
    print(f"Update: {TEMP_FILE} を更新しました (計 {len(new_videos_list)} 件, 今回の更新: {updated_count} 件)")
    
    # B. final_videos.json (全データマスター)
    # 今回の最新状態で完全に上書き
    current_list_sorted = list(current_map.values())
    current_list_sorted.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    save_json(FINAL_FILE, current_list_sorted)
    print(f"Update: {FINAL_FILE} を更新しました (計 {len(current_list_sorted)} 件)")

if __name__ == "__main__":
    main()
