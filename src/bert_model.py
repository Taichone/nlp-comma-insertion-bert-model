import re

import torch
from torch.utils.data import Dataset
from tqdm import tqdm
from transformers import (
    BertForMaskedLM,
    BertJapaneseTokenizer,
    Trainer,
    TrainingArguments,
)


class JapaneseMLMDataset(Dataset):
    def __init__(self, encodings, labels, tokenizer, comma_id, none_token_id):
        self.encodings = encodings
        self.labels = labels
        self.tokenizer = tokenizer
        self.comma_id = comma_id
        self.none_token_id = none_token_id

    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
        label_ids = [-100] * len(item["input_ids"])
        mask_idx = torch.where(item["input_ids"] == self.tokenizer.mask_token_id)[0]
        label_ids[mask_idx] = self.comma_id if self.labels[idx] else self.none_token_id
        item["labels"] = torch.tensor(label_ids)
        return item

    def __len__(self):
        return len(self.labels)


class CommaInsertionModel:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.tokenizer = BertJapaneseTokenizer.from_pretrained(
            "cl-tohoku/bert-base-japanese-v3"
        )
        self.model = BertForMaskedLM.from_pretrained("cl-tohoku/bert-base-japanese-v3")
        self.model = self.model.to(device)

        # トークンIDの設定
        self.tokenizer.add_tokens(
            "[NONE]"
        )  # 特殊トークン [NONE] をトークナイザーに追加
        self.model.resize_token_embeddings(
            len(self.tokenizer)
        )  # モデルにも新しいトークンを追加
        self.none_token_id = self.tokenizer.convert_tokens_to_ids(
            "[NONE]"
        )  # トークンIDを取得
        self.comma_id = self.tokenizer.convert_tokens_to_ids("、")

    def finetune(self, texts, mecab):
        """モデルのファインチューニングを行う関数"""
        masked_texts = []
        labels = []
        for i in tqdm(range(len(texts))):
            original_text = texts[i - 1]
            masked_texts_and_is_commas = get_masked_texts_and_is_commas(
                original_text, mecab
            )
            if len(masked_texts_and_is_commas) == 2:
                masked_texts += masked_texts_and_is_commas[0]
                labels += masked_texts_and_is_commas[1]

        # データセットのトークナイズ
        encodings = self.tokenizer(
            masked_texts, padding=True, truncation=True, return_tensors="pt"
        )
        dataset = JapaneseMLMDataset(
            encodings, labels, self.tokenizer, self.comma_id, self.none_token_id
        )

        # トレーニングの設定
        training_args = TrainingArguments(
            output_dir="./results",
            num_train_epochs=3,
            per_device_train_batch_size=16,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir="./logs",
        )

        # トレーナーの初期化
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
        )

        # ファインチューニングの実行
        trainer.train()
        return self.model

    def insert_commas(self, text, mecab):
        """読点を挿入する関数"""
        masked_text = insert_masks_between_bunsetsu(text, mecab)

        while "[MASK]" in masked_text:
            # target_masked_text は、masked_text の最初の [MASK] だけを残したもの
            first_mask_index = masked_text.find("[MASK]")
            target_masked_text = masked_text[: first_mask_index + 6] + masked_text[
                first_mask_index + 6 :
            ].replace("[MASK]", "")

            input_ids = self.tokenizer.encode(target_masked_text, return_tensors="pt")
            input_ids = input_ids.to(self.device)
            with torch.no_grad():
                output = self.model(input_ids)
            predictions = output[0][0]

            input_tokens = self.tokenizer.convert_ids_to_tokens(input_ids[0])

            for i, prediction in enumerate(predictions):
                if input_ids[0][i] == self.tokenizer.mask_token_id:
                    comma_value = prediction[self.comma_id]
                    none_token_value = prediction[self.none_token_id]

                    if comma_value > none_token_value:
                        masked_text = masked_text.replace("[MASK]", "、", 1)
                    else:
                        masked_text = masked_text.replace("[MASK]", "", 1)

        punctuated_text = masked_text
        punctuated_text = re.sub("#|\[CLS]|\[SEP]", "", punctuated_text)
        return punctuated_text
