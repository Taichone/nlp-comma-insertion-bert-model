# 日本語読点挿入モデル

BERTを使用して日本語テキストに読点を自動挿入するモデルです。

## セットアップ

1. MeCabのインストール:
```bash
brew install mecab mecab-ipadic
```

2. Pythonパッケージのインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

1. 学習データとテストデータを用意し、`data`ディレクトリに配置します。

2. モデルの学習と評価を実行:
```bash
python main.py
```

## プロジェクト構造

- `src/mecab_utils.py`: MeCabを使用した文節分割のユーティリティ
- `src/bert_model.py`: BERTモデルの定義と学習
- `src/data_processor.py`: データの前処理と後処理
- `src/evaluator.py`: モデルの評価機能
- `main.py`: メインスクリプト 