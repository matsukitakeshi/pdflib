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

class TkinterApp:
    """PDF周りGUIアプリケーションのクラス"""
    root = None
    file_label = None

    def __init__(self):
        """メインのWindowの立ち上げ"""
        self.root = tkinter.Tk()
        self.root.title(SCREEN_TITLE)
        self.root.geometry(f"{SCREEN_HEIGHT}x{SCREEN_WIDTH}")

        # ファイルアップロードボタンを作成
        pdf_upload_button = tkinter.Button(self.root, text="Open PDF", command=self.open_file_dialog)
        pdf_upload_button.pack(pady=DEFAULT_PADY)

        self.file_label = tkinter.Label(self.root, text="No file selected", wraplength=SCREEN_WIDTH - DEFAULT_PADY)
        self.file_label.pack(pady=DEFAULT_PADY)

        self.convert_image_tab()

        self.root.mainloop()

    def convert_image_tab(self):
        """画像化変換用のタブを作成"""
        # 出力ファイル名入力ボックス
        output_label = tkinter.Label(self.root, text="Output Filename (without extension):")
        output_label.pack(pady=DEFAULT_PADY // 2)

        self.output_entry = tkinter.Entry(self.root, width=30)
        self.output_entry.insert(0, "output")  # デフォルト値
        self.output_entry.pack(pady=DEFAULT_PADY // 2)

        # 拡張子選択ボタン、セレクトボックスで選択させる
        self.extension_var = tkinter.StringVar(value="PNG")
        extension_label = tkinter.Label(self.root, text="Select Image Format:")
        extension_label.pack(pady=DEFAULT_PADY // 2)
        self.extension_combobox = ttk.Combobox(
            self.root,
            textvariable=self.extension_var,
            values=["PNG", "JPEG"],
            state="readonly",
        )
        self.extension_combobox.pack(pady=DEFAULT_PADY // 2)

        # DPI選択スライダー
        dpi_label = tkinter.Label(self.root, text="Select DPI:")
        dpi_label.pack(pady=DEFAULT_PADY // 2)

        self.dpi_slider = tkinter.Scale(
            self.root,
            from_=150,
            to=400,
            orient="horizontal",
            resolution=10,
            label="DPI",
        )
        self.dpi_slider.set(DEFAULT_DPI)
        self.dpi_slider.pack(pady=DEFAULT_PADY)

        # 画像化ボタンを作成
        image_create_button = tkinter.Button(self.root, text="Convert to Images", command=self.convert_to_images)
        image_create_button.pack(pady=DEFAULT_PADY)

    def open_file_dialog(self):
        """ファイルのダイアログを開き、ファイル名を取得する"""
        file_name = filedialog.askopenfilename(
            title="Choose a PDF file",
            filetypes=[("PDF", "*.pdf")],
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
        if not hasattr(self, 'selected_pdf') or not self.selected_pdf:
            print("No PDF file selected!")
            return

        # 入力された情報を取得
        selected_dpi = self.dpi_slider.get()
        selected_extension = self.extension_var.get().lower()
        output_base_name = self.output_entry.get()

        if not output_base_name:
            print("Output filename is empty. Please enter a valid filename.")
            return

        print(f"Converting PDF with DPI: {selected_dpi}, Format: {selected_extension}, Base Name: {output_base_name}")

        # 出力フォルダを作成（存在しない場合）
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)

        try:
            pages = convert_from_path(self.selected_pdf, dpi=selected_dpi)
            for i, page in enumerate(pages):
                output_filename = f"{output_dir}/{output_base_name}_{i}.{selected_extension}"
                page.save(output_filename, selected_extension.upper())
                print(f"Saved: {output_filename}")
        except Exception as e:
            print(f"Error during conversion: {e}")

# アプリケーションの起動
if __name__ == "__main__":
    app = TkinterApp()
