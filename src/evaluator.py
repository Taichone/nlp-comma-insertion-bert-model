def get_comma_indexes(text):
    """テキストに含まれる読点のインデックスのリストを返す関数"""
    comma_indexes = []
    for i in range(len(text)):
        if text[i] == "、":
            comma_indexes.append(i)
    return comma_indexes


def calculate_result(original_text, output_text):
    """モデルの出力を評価する関数"""
    # 読点のインデックスのリストを取得
    original_indexes = get_comma_indexes(original_text)
    output_indexes = get_comma_indexes(output_text)
    saigen = 0  # 再現できている読点の数
    num_original_indexes = len(original_indexes)
    num_output_indexes = len(output_indexes)

    # 原文または出力文のどちらかの読点数がゼロなら saigen == 0 なので終わる
    if num_original_indexes == 0 or num_output_indexes == 0:
        return [
            original_text,
            output_text,
            num_original_indexes,
            num_output_indexes,
            saigen,
        ]

    # 再現数のカウント
    output_i = 0
    index_diff = 0

    for i in range(num_original_indexes):
        original_index = original_indexes[i] + index_diff
        output_index = output_indexes[output_i]

        if original_index == output_index:
            # output_index で再現できている場合
            saigen += 1
            if output_i + 1 < num_output_indexes:
                output_i += 1
            else:
                break

        elif original_index > output_index:
            # 原文の読点までに、余分に挿入した読点がある場合
            while original_indexes[i] + index_diff > output_indexes[output_i]:
                if output_i + 1 < num_output_indexes:
                    output_i += 1
                    index_diff += 1
                else:
                    break
            if original_indexes[i] + index_diff == output_indexes[output_i]:
                # output_index で再現できている場合
                saigen += 1
                if output_i + 1 < num_output_indexes:
                    output_i += 1
                else:
                    break
            else:
                # i番目の読点は再現できていないことが確定
                index_diff -= 1
                continue

        else:
            # i番目の読点は再現できていないことが確定
            index_diff -= 1
            continue

    return [
        original_text,
        output_text,
        num_original_indexes,
        num_output_indexes,
        saigen,
    ]


def print_result(results):
    """評価結果を表示する関数"""
    num_all_saigen = 0
    num_all_original_commas = 0
    num_all_output_commas = 0

    for result in results:
        num_saigen = result[4]
        num_original_commas = result[2]
        num_output_commas = result[3]

        # 統計に追加
        num_all_saigen += num_saigen
        num_all_original_commas += num_original_commas
        num_all_output_commas += num_output_commas

    # 指標を計算
    precision = 0
    if num_all_output_commas > 0:
        precision = num_all_saigen / num_all_output_commas  # 適合率
    recall = 0
    if num_all_original_commas > 0:
        recall = num_all_saigen / num_all_original_commas  # 再現率
    f_value = 0
    if (precision + recall) > 0:
        f_value = 2 * precision * recall / (precision + recall)  # F値

    if num_all_original_commas != 0 and num_all_output_commas != 0:
        print(f"再現率: {recall: .3f}, 適合率: {precision: .3f}, F値： {f_value: .3f}")
    else:
        print(f"再現率: 0, 適合率: 0, F値： {f_value: .3f}")
