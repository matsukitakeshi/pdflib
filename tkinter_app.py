import tkinter
from tkinter import filedialog
from tkinter import ttk
from pdf2image import convert_from_path
import os

SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 400
SCREEN_TITLE = "Software Title"

DEFAULT_PADY = 20
DEFAULT_DPI = 150
DEFAULT_OUTPUT_DIR = "./output"


class TkinterApp:
    """PDF周りGUIアプリケーションのクラス

    tkinter内で日本語を使用すると文字化けするので英語で記載している
    """

    def __init__(self):
        """メインのWindowの立ち上げ"""
        self.root = tkinter.Tk()
        self.root.title(SCREEN_TITLE)
        self.root.geometry(f"{SCREEN_HEIGHT}x{SCREEN_WIDTH}")

        self.selected_pdf = None
        self.init_ui()

        self.root.mainloop()

    def init_ui(self):
        """UIの初期化"""
        # PDFアップロードボタン
        self.create_pdf_upload_button()

        # 出力ファイル名入力フィールド
        self.create_output_filename_input()

        # 画像形式選択
        self.create_image_format_selector()

        # DPI選択スライダー
        self.create_dpi_slider()

        # 画像変換ボタン
        self.create_convert_button()

    def create_pdf_upload_button(self):
        """PDFアップロードボタンを作成"""
        pdf_upload_button = tkinter.Button(self.root, text="Open PDF", command=self.open_file_dialog)
        pdf_upload_button.pack(pady=DEFAULT_PADY)

        self.file_label = tkinter.Label(self.root, text="No file selected", wraplength=SCREEN_WIDTH - DEFAULT_PADY)
        self.file_label.pack(pady=DEFAULT_PADY)

    def create_output_filename_input(self):
        """出力ファイル名入力フィールドを作成"""
        output_label = tkinter.Label(self.root, text="Output Filename :")
        output_label.pack(pady=DEFAULT_PADY // 2)

        self.output_entry = tkinter.Entry(self.root, width=30)
        self.output_entry.insert(0, "output")
        self.output_entry.pack(pady=DEFAULT_PADY // 2)

    def create_image_format_selector(self):
        """画像形式選択セレクトボックスを作成"""
        self.extension_var = tkinter.StringVar(value="PNG")
        extension_label = tkinter.Label(self.root, text="Select Image Format:")
        extension_label.pack(pady=DEFAULT_PADY // 2)

        self.extension_combobox = ttk.Combobox(self.root, textvariable=self.extension_var, values=["PNG", "JPEG"], state="readonly")
        self.extension_combobox.pack(pady=DEFAULT_PADY // 2)

    def create_dpi_slider(self):
        """DPI選択スライダーを作成"""
        dpi_label = tkinter.Label(self.root, text="Select DPI:")
        dpi_label.pack(pady=DEFAULT_PADY // 2)

        self.dpi_slider = tkinter.Scale(self.root, from_=150, to=400, orient="horizontal", resolution=10, label="DPI")
        self.dpi_slider.set(DEFAULT_DPI)
        self.dpi_slider.pack(pady=DEFAULT_PADY)

    def create_convert_button(self):
        """画像化ボタンを作成"""
        image_create_button = tkinter.Button(self.root, text="Convert to Images", command=self.convert_to_images)
        image_create_button.pack(pady=DEFAULT_PADY)

    def open_file_dialog(self):
        """ファイルダイアログを開き、選択されたPDFファイルを設定"""
        file_name = filedialog.askopenfilename(
            title="Choose a PDF file", filetypes=[("PDF", "*.pdf")]
        )
        if file_name:
            print(f"選択されたPDFファイル: {file_name}")
            self.file_label.config(text=file_name)
            self.selected_pdf = file_name
        else:
            print("ファイルが選択されませんでした。")
            self.selected_pdf = None

    def convert_to_images(self):
        """PDFファイルを画像に変換する"""
        if not self.selected_pdf:
            print("PDFが選択されていません。")
            return

        selected_dpi = self.dpi_slider.get()
        selected_extension = self.extension_var.get().lower()
        output_base_name = self.output_entry.get()

        if not output_base_name:
            print("出力ファイル名が入力されていません。")
            return

        print(f"以下の条件で画像変換が完了しました。 DPI: {selected_dpi}, 拡張子: {selected_extension}, ファイル名: {output_base_name}")

        # 出力フォルダ作成
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

        try:
            pages = convert_from_path(self.selected_pdf, dpi=selected_dpi)
            for i, page in enumerate(pages):
                output_filename = os.path.join(DEFAULT_OUTPUT_DIR, f"{output_base_name}_{i}.{selected_extension}")
                page.save(output_filename, selected_extension.upper())
                print(f"Saved: {output_filename}")
        except Exception as e:
            print(f"エラーが発生しました。: {e}")


# アプリケーションの起動
if __name__ == "__main__":
    app = TkinterApp()
