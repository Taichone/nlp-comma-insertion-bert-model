from .mecab_utils import bunsetsu_wakachi


def get_texts(data_path):
    """テキストファイルから文章を読み込む関数"""
    texts = []
    with open(data_path, encoding="utf-8") as file:
        for line in file:
            if 511 < len(line):
                while 511 < len(line):
                    first_256_chars = line[:256]  # 先頭から256文字を取得
                    last_period_index = first_256_chars.rfind(
                        "。"
                    )  # 取得した部分から最後の "。" までの位置を検索
                    # 最後の "。" までの部分を別の変数に代入
                    if last_period_index != -1:
                        extracted_part = first_256_chars[: last_period_index + 1]
                        texts.append(extracted_part)
                        line = line[
                            len(extracted_part) :
                        ]  # もとのtextから抽出した部分を除いた部分を更新
                    else:
                        print("先頭から256文字までに 。 がない")
                        break

            line = line.replace("\n", "")
            sentence_list = line.split("。")  # この時点で、"。" はなくなる
            sentences = []
            for s in sentence_list:
                if len(s) > 0:
                    sentences.append(s + "。")  # "。"　を復元する
            if 0 < len(sentences):
                texts += sentences

    return texts


def insert_masks_between_bunsetsu(text, mecab):
    """文節境界に[MASK]を挿入する関数"""
    bunsetsus = bunsetsu_wakachi(text, mecab)
    masked_text = ""
    for bunsetsu in bunsetsus:
        masked_text += bunsetsu
        if not bunsetsu.endswith("、"):
            masked_text += "[MASK]"
    masked_text = masked_text[:-6]  # 末尾の余分な '[MASK]' を削除
    return masked_text.strip()


def get_is_comma(original_text, masked_text):
    """元のテキストに読点があるかどうかを判定する関数"""
    result = ""
    i = j = 0
    while i < len(original_text) and j < len(masked_text):
        if masked_text[j] == "[":
            if original_text[i] == "、":
                return True
            else:
                return False
        elif (
            original_text[i] == "、"
        ):  # 文字列 A に読点があり、文字列 B に読点がない場合
            i += 1
        else:  # 両方の文字が一致する場合
            i += 1
            j += 1

    return False


def get_masked_texts_and_is_commas(original_text, mecab):
    """マスクされたテキストと読点の有無を取得する関数"""
    removed_text = original_text.replace("、", "")
    masked_text = insert_masks_between_bunsetsu(removed_text, mecab)

    masked_texts = []
    is_commas = []

    while "[MASK]" in masked_text:
        # target_masked_text は、masked_text の最初の [MASK] だけを残したもの
        first_mask_index = masked_text.find("[MASK]")
        target_masked_text = masked_text[: first_mask_index + 6] + masked_text[
            first_mask_index + 6 :
        ].replace("[MASK]", "")
        is_comma = get_is_comma(original_text, target_masked_text)

        masked_texts.append(target_masked_text)  # 追加
        is_commas.append(is_comma)  # 追加
        masked_text = masked_text.replace(
            "[MASK]", "", 1
        )  # 最初の [MASK] を消す（その [MASK] は完了）

    return [masked_texts, is_commas]
