import MeCab


def init_mecab():
    """MeCabの初期化"""
    mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    return mecab


def bunsetsu_wakachi(text, mecab):
    """文節分割を行う関数"""
    mecab_result = mecab.parse(text).splitlines()
    mecab_result = mecab_result[:-1]  # 最後の1行は不要な行なので除く
    break_pos = [
        "名詞",
        "動詞",
        "接頭詞",
        "副詞",
        "感動詞",
        "形容詞",
        "形容動詞",
        "連体詞",
    ]  # 文節の切れ目を検出するための品詞リスト
    wakachi = [""]  # 分かち書きのリスト
    prev_pos_detail = []
    afterPrepos = False  # 接頭詞の直後かどうかのフラグ
    afterSahenNoun = False  # サ変接続名詞の直後かどうかのフラグ
    nextNoBreak = False

    for v in mecab_result:
        if "\t" not in v:
            continue
        surface = v.split("\t")[0]  # 表層系
        pos = v.split("\t")[1].split(",")  # 品詞など
        pos_detail = ",".join(pos[1:4])  # 品詞細分類

        # この単語が文節の切れ目とならないかどうかの判定
        noBreak = False
        if nextNoBreak:
            noBreak = True

        nextNoBreak = False
        noBreak = noBreak or (pos[0] not in break_pos)
        noBreak = noBreak or ("数" in prev_pos_detail and "数" in pos_detail)
        noBreak = noBreak or "接尾" in pos_detail
        noBreak = noBreak or (pos[0] == "動詞" and "サ変接続" in pos_detail)
        noBreak = noBreak or "非自立" in pos_detail
        noBreak = noBreak or afterPrepos
        noBreak = noBreak or (
            afterSahenNoun and pos[0] == "動詞" and pos[4] == "サ変・スル"
        )

        if surface.endswith("-"):
            noBreak = True
            nextNoBreak = True

        if not noBreak:
            wakachi.append("")  # 要素を増やす（つまり次の文節に行く）

        if not nextNoBreak:  # '-' 以外は加える
            wakachi[-1] += (
                surface  # 要素は増やさず最後のやつに加える（まだ文節であるとして繋げる）
            )

        afterPrepos = pos[0] == "接頭詞"
        afterSahenNoun = "サ変接続" in pos_detail
        prev_pos_detail = pos_detail

    if wakachi[0] == "":
        wakachi = wakachi[1:]  # 最初が空文字のとき削除する
    return wakachi
