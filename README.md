# pdflib

## 出来ること

- PDF 画像変換
  - 対象拡張子：png, jpeg
- PDF 分割機能
- PDF マージ機能

## 実行方法

```
git clone {当レポジトリ}
./pdflib/dist/main
```

## 環境構築

- Ubuntu python3.12 の場合

```
pip3.12 install pikepdf
pip3.12 install pytk
pip3.12 install pdf2image

sudo apt update
sudo apt install python3.12-tk
sudo apt install poppler-utils
```

```
python3.12 main.py
```
