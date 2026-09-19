import json
import os
import re
from datetime import date


def normalize_title(title):
    """タイトル表記の揺れを修正（前後の空白除去、全角括弧→半角括弧）"""
    if not title:
        return ""
    title = title.strip()
    title = title.replace("（L）", "(L)").replace("（H）", "(H)")
    return title


def parse_txt_files_to_json(input_dir, output_json_filepath):
    # 読み込むターゲットファイルの定義
    files = {
        ("☆12", "AC"): os.path.join(input_dir, "12 AC.txt"),
        ("☆12", "INF"): os.path.join(input_dir, "12 INF.txt"),
        ("☆11", "AC"): os.path.join(input_dir, "11 AC.txt"),
        ("☆11", "INF"): os.path.join(input_dir, "11 INF.txt"),
    }

    # 楽曲データの保持用 dict: (title, bemaniDifficulty) -> data
    records = {}

    for (bemani_diff, mode), filepath in files.items():
        if not os.path.exists(filepath):
            print(f"警告: ファイルが見つかりません: {filepath}")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            current_rank = None

            for line in f:
                line = line.strip("\ufeff\r\n")
                if not line or "片手難易度表" in line:
                    continue

                # タブ区切りで分割
                cells = [c.strip() for c in line.split("\t")]

                # ①〜⑩などの難易度ランクヘッダー判定
                if (
                    len(cells) == 1
                    and cells[0]
                    and re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩1-9]$", cells[0])
                ):
                    current_rank = cells[0]
                    continue

                # 各セル（曲名）を処理
                for cell in cells:
                    title = normalize_title(cell)

                    # 空文字、全角スペース、またはランク番号自体の場合はスキップ
                    if (
                        not title
                        or title == " "
                        or re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩1-9]$", title)
                    ):
                        if re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩1-9]$", title):
                            current_rank = title
                        continue

                    key = (title, bemani_diff)
                    if key not in records:
                        records[key] = {
                            "title": title,
                            "bemaniDifficulty": bemani_diff,
                            "acDifficulty": None,
                            "infDifficulty": None,
                        }

                    if mode == "AC":
                        records[key]["acDifficulty"] = current_rank
                    else:
                        records[key]["infDifficulty"] = current_rank

    # 集計およびリストの構築
    songs = []
    ac_count = 0
    inf_count = 0
    both_count = 0
    ac_only_count = 0
    inf_only_count = 0

    for item in records.values():
        has_ac = item["acDifficulty"] is not None
        has_inf = item["infDifficulty"] is not None

        if has_ac:
            ac_count += 1
        if has_inf:
            inf_count += 1

        if has_ac and has_inf:
            both_count += 1
        elif has_ac:
            ac_only_count += 1
        elif has_inf:
            inf_only_count += 1

        songs.append(
            {
                "title": item["title"],
                "bemaniDifficulty": item["bemaniDifficulty"],
                "ac": has_ac,
                "acDifficulty": item["acDifficulty"],
                "inf": has_inf,
                "infDifficulty": item["infDifficulty"],
            }
        )

    # メタデータと結果の作成
    result = {
        "meta": {
            "source_dir": input_dir,
            "source_note": "txt形式の難易度表（AC版/INF版および☆11/☆12）から正規化",
            "generated": date.today().isoformat(),
            "record_count": len(songs),
            "ac_count": ac_count,
            "inf_count": inf_count,
            "both_count": both_count,
            "ac_only_count": ac_only_count,
            "inf_only_count": inf_only_count,
        },
        "songs": songs,
    }

    # JSON出力
    with open(output_json_filepath, mode="w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"変換完了: {len(songs)} 件の楽曲データを統合出力しました。")


if __name__ == "__main__":
    input_folder = "./元ネタ"
    json_file = "difficulty-data_normalized.json"
    parse_txt_files_to_json(input_folder, json_file)