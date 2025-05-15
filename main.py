import os

from src.bert_model import CommaInsertionModel
from src.data_processor import get_texts
from src.evaluator import calculate_result, print_result
from src.mecab_utils import init_mecab
from tqdm import tqdm


def main():
    # データディレクトリの作成
    os.makedirs("data", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # MeCabの初期化
    mecab = init_mecab()

    # モデルの初期化
    model = CommaInsertionModel()

    # 学習データの読み込み
    train_data_path = "data/train.txt"
    test_data_path = "data/test.txt"

    print("学習データの読み込み中...")
    texts = get_texts(train_data_path)

    print("モデルの学習中...")
    finetuned_model = model.finetune(texts, mecab)

    print("テストデータの読み込み中...")
    texts = get_texts(test_data_path)

    print("読点挿入の評価中...")
    results = []
    for i in tqdm(range(len(texts))):
        text = texts[i - 1]
        removed_text = text.replace("、", "")
        output_text = model.insert_commas(removed_text, mecab)
        results.append(calculate_result(text, output_text))

    print("\n評価結果:")
    print_result(results)


if __name__ == "__main__":
    main()
