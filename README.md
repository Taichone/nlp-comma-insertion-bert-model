# Comma Insertion BERT Model
大規模言語モデル BERT をベースとして、日本語テキストに読点を自動挿入する言語モデルです。
作者の過去の文章を学習させておくことで、作者の読点位置の傾向を踏まえた出力にカスタマイズ可能です。

## プロジェクト構造

- `src/mecab_utils.py`: MeCabを使用した文節分割のユーティリティ
- `src/bert_model.py`: BERTモデルの定義と学習
- `src/data_processor.py`: データの前処理と後処理
- `src/evaluator.py`: モデルの評価機能
- `main.py`: メインスクリプト 
