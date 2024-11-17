import os
import tkinter as tk
from tkinter import filedialog, ttk

import pikepdf
from pdf2image import convert_from_path
from PIL import ImageTk

SCREEN_HEIGHT = 1300
SCREEN_WIDTH = 1000
SCREEN_TITLE = "PDF Converter Tool"
DEFAULT_PADY = 20
DEFAULT_DPI = 150
DEFAULT_OUTPUT_DIR = "./output"
THUMBNAIL_SIZE = (150, 150)
THUMBNAIL_GRID_COLUMNS = 5


class TkinterApp:
    """PDF周りGUIアプリケーションのクラス"""

    def __init__(self):
        """メインのWindowの立ち上げ"""
        self.root = tk.Tk()
        self.root.title(SCREEN_TITLE)
        self.root.geometry(f"{SCREEN_HEIGHT}x{SCREEN_WIDTH}")

        self.selected_pdf = None
        self.selected_pdf_for_merge = None  # マージ用の2番目のPDF
        self.selected_pages = []
        self.thumbnails = []
        self.highlighted_buttons = []
        self.init_ui()

        self.root.mainloop()

    def init_ui(self):
        """UIの初期化"""
        self.create_pdf_upload_button()
        self.create_notebook()

    def create_notebook(self):
        """ノートブック（タブ）を作成"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # タブ（画像変換タブ、PDF分割タブ、PDFマージタブ）を作成
        self.create_convert_tab()
        self.create_split_tab()
        self.create_merge_tab()  # 新しいPDFマージタブを追加

    def create_pdf_upload_button(self):
        """PDFアップロードボタンを作成"""
        self.pdf_upload_button = tk.Button(
            self.root, text="Open PDF", command=self.open_file_dialog
        )
        self.pdf_upload_button.pack(pady=DEFAULT_PADY)

        self.file_label = tk.Label(
            self.root, text="No file selected", wraplength=SCREEN_WIDTH - DEFAULT_PADY
        )
        self.file_label.pack(pady=DEFAULT_PADY)

    def create_convert_tab(self):
        """画像変換タブを作成"""
        convert_tab = ttk.Frame(self.notebook)
        self.notebook.add(convert_tab, text="Convert PDF to Images")

        self.create_output_filename_input(convert_tab)
        self.create_image_format_selector(convert_tab)
        self.create_dpi_slider(convert_tab)
        self.create_convert_button(convert_tab)

    def create_split_tab(self):
        """PDF分割タブを作成"""
        split_tab = ttk.Frame(self.notebook)
        self.notebook.add(split_tab, text="Split PDF into Pages")

        self.create_output_filename_input(split_tab)
        self.create_split_button(split_tab)
        self.create_thumbnail_area(split_tab)

    def create_merge_tab(self):
        """PDFマージタブを作成"""
        merge_tab = ttk.Frame(self.notebook)
        self.notebook.add(merge_tab, text="Merge PDFs")

        self.create_merge_button(merge_tab)
        self.create_merge_pdf_upload_button(merge_tab)

    def create_merge_pdf_upload_button(self, parent):
        """PDFファイルをもう一度アップロードするボタンを作成"""
        self.pdf_upload_for_merge_button = tk.Button(
            parent, text="Open Second PDF for Merge", command=self.open_file_dialog_for_merge
        )
        self.pdf_upload_for_merge_button.pack(pady=DEFAULT_PADY)

        self.file_label_for_merge = tk.Label(
            parent, text="No second PDF selected", wraplength=SCREEN_WIDTH - DEFAULT_PADY
        )
        self.file_label_for_merge.pack(pady=DEFAULT_PADY)

    def create_merge_button(self, parent):
        """PDFマージボタンを作成"""
        merge_button = tk.Button(
            parent, text="Merge PDFs", command=self.merge_pdfs
        )
        merge_button.pack(pady=DEFAULT_PADY)

    def create_output_filename_input(self, parent):
        """出力ファイル名入力フィールドを作成"""
        output_label = tk.Label(parent, text="Output Filename :")
        output_label.pack(pady=DEFAULT_PADY // 2)

        self.output_entry = tk.Entry(parent, width=30)
        self.output_entry.insert(0, "output")
        self.output_entry.pack(pady=DEFAULT_PADY // 2)

    def create_image_format_selector(self, parent):
        """画像形式選択セレクトボックスを作成"""
        self.extension_var = tk.StringVar(value="PNG")
        extension_label = tk.Label(parent, text="Select Image Format:")
        extension_label.pack(pady=DEFAULT_PADY // 2)

        self.extension_combobox = ttk.Combobox(
            parent,
            textvariable=self.extension_var,
            values=["PNG", "JPEG"],
            state="readonly",
        )
        self.extension_combobox.pack(pady=DEFAULT_PADY // 2)

    def create_dpi_slider(self, parent):
        """DPI選択スライダーを作成"""
        dpi_label = tk.Label(parent, text="Select DPI:")
        dpi_label.pack(pady=DEFAULT_PADY // 2)

        self.dpi_slider = tk.Scale(
            parent, from_=150, to=400, orient="horizontal", resolution=10
        )
        self.dpi_slider.set(DEFAULT_DPI)
        self.dpi_slider.pack(pady=DEFAULT_PADY)

    def create_convert_button(self, parent):
        """画像化ボタンを作成"""
        image_create_button = tk.Button(
            parent, text="Convert to Images", command=self.convert_to_images
        )
        image_create_button.pack(pady=DEFAULT_PADY)

    def create_split_button(self, parent):
        """PDF分割ボタンを作成"""
        split_button = tk.Button(
            parent, text="Split PDF into Pages", command=self.split_pdf
        )
        split_button.pack(pady=DEFAULT_PADY)

    def create_thumbnail_area(self, parent):
        """サムネイル表示エリアを作成"""
        self.thumbnail_frame = tk.Frame(parent)
        self.thumbnail_frame.pack(pady=DEFAULT_PADY, fill="both", expand=True)

        # キャンバスとスクロールバーの作成
        self.canvas = tk.Canvas(self.thumbnail_frame)
        self.scrollbar = tk.Scrollbar(
            self.thumbnail_frame, orient="vertical", command=self.canvas.yview
        )
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # サムネイル表示用フレームをキャンバス内に配置
        self.thumbnail_canvas_frame = tk.Frame(self.canvas)
        self.canvas.create_window(
            (0, 0), window=self.thumbnail_canvas_frame, anchor="nw"
        )

        # サムネイルをスクロール可能にする
        self.thumbnail_canvas_frame.bind(
            "<Configure>",
            lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all")),
        )

    def open_file_dialog(self):
        """ファイルダイアログを開き、選択されたPDFファイルを設定"""
        file_name = filedialog.askopenfilename(
            title="Choose a PDF file", filetypes=[("PDF", "*.pdf")]
        )
        if file_name:
            print(f"選択されたPDFファイル: {file_name}")
            self.file_label.config(text=file_name)
            self.selected_pdf = file_name
            self.load_pdf_thumbnails(file_name)

    def open_file_dialog_for_merge(self):
        """マージ用の2番目のPDFファイルダイアログ"""
        file_name = filedialog.askopenfilename(
            title="Choose a Second PDF for Merge", filetypes=[("PDF", "*.pdf")]
        )
        if file_name:
            print(f"選択された2番目のPDFファイル: {file_name}")
            self.file_label_for_merge.config(text=file_name)
            self.selected_pdf_for_merge = file_name
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

        print(
            f"以下の条件で画像変換が完了しました。 DPI: {selected_dpi}, 拡張子: {selected_extension}, ファイル名: {output_base_name}"
        )

        # 出力フォルダ作成
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

        try:
            pages = convert_from_path(self.selected_pdf, dpi=selected_dpi)
            for i, page in enumerate(pages):
                output_filename = os.path.join(
                    DEFAULT_OUTPUT_DIR, f"{output_base_name}_{i}.{selected_extension}"
                )
                page.save(output_filename, selected_extension.upper())
                print(f"Saved: {output_filename}")
        except Exception as e:
            print(f"エラーが発生しました。: {e}")

    def merge_pdfs(self):
        """2つのPDFをマージする"""
        if not self.selected_pdf or not self.selected_pdf_for_merge:
            print("2つのPDFが選択されていません。")
            return

        output_base_name = self.output_entry.get()

        if not output_base_name:
            print("出力ファイル名が入力されていません。")
            return

        try:
            pdf1 = pikepdf.open(self.selected_pdf)
            pdf2 = pikepdf.open(self.selected_pdf_for_merge)

            # 新しいPDFを作成し、両方のPDFを追加
            merged_pdf = pikepdf.Pdf.new()
            merged_pdf.pages.extend(pdf1.pages)
            merged_pdf.pages.extend(pdf2.pages)

            # 出力ファイル名を決定
            output_filename = os.path.join(
                DEFAULT_OUTPUT_DIR, f"{output_base_name}_merged.pdf"
            )

            # マージしたPDFを保存
            merged_pdf.save(output_filename)
            print(f"マージされたPDFが保存されました: {output_filename}")

        except Exception as e:
            print(f"PDFのマージ中にエラーが発生しました: {e}")

    def load_pdf_thumbnails(self, pdf_path):
        """PDFのサムネイルを生成して表示する"""
        self.thumbnails.clear()

        pages = convert_from_path(pdf_path, dpi=DEFAULT_DPI)

        # サムネイル画像を表示
        for i, page in enumerate(pages):
            thumbnail = page.resize(THUMBNAIL_SIZE)  # サイズを調整
            self.thumbnails.append(thumbnail)

            # 画像をTkinterで表示可能な形式に変換
            thumbnail_tk = ImageTk.PhotoImage(thumbnail)

            # サムネイルボタンを作成
            thumbnail_button = tk.Button(
                self.thumbnail_canvas_frame, image=thumbnail_tk
            )
            thumbnail_button.image = thumbnail_tk  # 参照を保持して画像がガーベジコレクションされないようにする

            # ボタンにコマンドを設定
            thumbnail_button.config(
                command=lambda i=i, button=thumbnail_button: self.select_page(i, button)
            )

            # サムネイルボタンを表示
            thumbnail_button.grid(
                row=i // THUMBNAIL_GRID_COLUMNS,
                column=i % THUMBNAIL_GRID_COLUMNS,
                padx=5,
                pady=5,
            )

    def select_page(self, page_index, thumbnail_button):
        """ページを選択する処理"""
        if page_index in self.selected_pages:
            self.selected_pages.remove(page_index)
            print(f"ページ {page_index + 1} を解除しました")
            self.remove_highlight(thumbnail_button)
        else:
            self.selected_pages.append(page_index)
            print(f"ページ {page_index + 1} を選択しました")
            self.add_highlight(thumbnail_button)

    def split_pdf(self):
        """選択したページでPDFを結合する"""
        if not self.selected_pdf or not self.selected_pages:
            print("PDFが選択されていません、または分割ページが選ばれていません。")
            return

        output_base_name = self.output_entry.get()

        if not output_base_name:
            print("出力ファイル名が入力されていません。")
            return

        # 選択されたページを昇順にソート
        self.selected_pages.sort()
        print(f"選択されたページ {self.selected_pages} でPDFを結合中...")

        try:
            pdf = pikepdf.open(self.selected_pdf)

            # 新しいPDFを作成
            new_pdf = pikepdf.Pdf.new()

            # 選択されたページを新しいPDFに追加
            for page_num in self.selected_pages:
                new_pdf.pages.append(pdf.pages[page_num])

            # 出力ファイル名を決定
            output_filename = os.path.join(
                DEFAULT_OUTPUT_DIR, f"{output_base_name}.pdf"
            )

            # 新しいPDFを保存
            new_pdf.save(output_filename)

            print(f"結合されたPDFが保存されました: {output_filename}")

            # ページ選択を初期化
            self.selected_pages.clear()

            # サムネイルのハイライトをリセット
            for button in self.highlighted_buttons:
                button.config(highlightbackground=None, highlightthickness=0)
            self.highlighted_buttons.clear()

        except Exception as e:
            print(f"PDFの結合中にエラーが発生しました: {e}")

    def add_highlight(self, button):
        """選択したサムネイルに赤い枠を追加"""
        if button not in self.highlighted_buttons:
            button.config(highlightbackground="red", highlightthickness=3)
            self.highlighted_buttons.append(button)

    def remove_highlight(self, button):
        """選択したサムネイルから赤い枠を取り除く"""
        if button in self.highlighted_buttons:
            button.config(highlightbackground=None, highlightthickness=0)
            self.highlighted_buttons.remove(button)


# アプリケーションの起動
if __name__ == "__main__":
    app = TkinterApp()
