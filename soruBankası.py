import sys
import sqlite3
import os 
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QTextEdit, QRadioButton, QButtonGroup, QMessageBox,
                             QAction, QMenu, QSizePolicy, QHeaderView, QStackedWidget, QSpacerItem)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt5.QtGui import (QPainter, QFont, QTextDocument, QTextCharFormat,
                         QTextCursor, QColor, QBrush, QPalette, QPixmap, QIcon)
from PyQt5.QtCore import Qt, QUrl, QSize, QDate

NAVY_PRIMARY = "#0A2240"
NAVY_ACCENT = "#1A3873"  
RED_PRIMARY = "#C00000"   
RED_ACCENT = "#E04040"    
WHITE_PRIMARY = "#FFFFFF"
OFF_WHITE_BG = "#F4F6F8" 
TEXT_ON_DARK_BG = "#FFFFFF"
TEXT_ON_LIGHT_BG = "#212121" 
TEXT_NAVY_HEADER = NAVY_PRIMARY
BORDER_COLOR = "#B0BEC5" 

DB_NAME = 'soru_bankasi.db'

def init_db():
    print("DEBUG: init_db çağrıldı.")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sorular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soru_metni TEXT NOT NULL,
            secenek1 TEXT,
            secenek2 TEXT,
            secenek3 TEXT,
            secenek4 TEXT,
            secenek5 TEXT,
            dogru_secenek_index INTEGER,
            kategori TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"DEBUG: init_db tamamlandı. Veritabanı dosyası ({DB_NAME}) şu dizinde olmalı veya oluşturulmuş olmalı: {os.getcwd()}")


def add_question_to_db(soru_metni, secenekler, dogru_secenek_index, kategori="Genel"):
    print(f"DEBUG: add_question_to_db: Soru='{soru_metni[:20]}...'")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        current_secenekler = list(secenekler)
        while len(current_secenekler) < 5:
            current_secenekler.append("")
        cursor.execute('''
            INSERT INTO sorular (soru_metni, secenek1, secenek2, secenek3, secenek4, secenek5, dogru_secenek_index, kategori)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (soru_metni, current_secenekler[0], current_secenekler[1], current_secenekler[2], current_secenekler[3], current_secenekler[4], dogru_secenek_index, kategori))
        conn.commit()
        print("DEBUG: Soru veritabanına eklendi.")
        return True
    except sqlite3.Error as e:
        print(f"DEBUG: add_question_to_db - Veritabanı hatası: {e}")
        return False
    finally:
        conn.close()

def get_all_questions():
    print("DEBUG: get_all_questions çağrıldı.")
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, soru_metni, secenek1, secenek2, secenek3, secenek4, secenek5, dogru_secenek_index, kategori FROM sorular ORDER BY id")
        sorular = cursor.fetchall()
        print(f"DEBUG: Veritabanından {len(sorular)} adet soru çekildi.")
        return sorular
    except sqlite3.Error as e:
        print(f"DEBUG: get_all_questions içinde veritabanı hatası: {e}")
        return []
    finally:
        if conn:
            conn.close()


class WelcomeWidget(QWidget):
    def __init__(self, add_question_callback, view_questions_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("WelcomeWidget")
        self.setAutoFillBackground(True)

        self.add_question_action = add_question_callback
        self.view_questions_action = view_questions_callback

        try:
            font_family = "Segoe UI"
            QFont(font_family)
        except:
            font_family = "Arial"

        title_font = QFont(font_family, 44, QFont.Bold)
        tagline_font = QFont(font_family, 15)
        button_font = QFont(font_family, 14, QFont.Bold)

        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(QColor(OFF_WHITE_BG)))
        self.setPalette(palette)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(70, 50, 70, 50)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)

        main_layout.addStretch(2)

        self.title_label = QLabel("Mini Soru Bankası")
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"color: {TEXT_NAVY_HEADER}; margin-bottom: 5px;")
        main_layout.addWidget(self.title_label)

        self.tagline_label = QLabel("Sorularınızı oluşturun, düzenleyin ve sınavlara hazırlanın.")
        self.tagline_label.setFont(tagline_font)
        self.tagline_label.setAlignment(Qt.AlignCenter)
        self.tagline_label.setStyleSheet(f"color: {NAVY_ACCENT}; margin-bottom: 35px;")
        self.tagline_label.setWordWrap(True)
        main_layout.addWidget(self.tagline_label)

        main_layout.addStretch(1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(25)
        buttons_layout.setAlignment(Qt.AlignCenter)

        self.add_button = QPushButton(" Yeni Soru Oluştur")
        self.add_button.setFont(button_font)
        self.add_button.setMinimumHeight(55)
        self.add_button.setMinimumWidth(240)
        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED_PRIMARY};
                color: {TEXT_ON_DARK_BG};
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: {RED_ACCENT}; }}
            QPushButton:pressed {{ background-color: {RED_PRIMARY}; }}
        """)
        self.add_button.clicked.connect(self.add_question_action)
        buttons_layout.addWidget(self.add_button)

        self.view_button = QPushButton(" Soru Listesini Aç")
        self.view_button.setFont(button_font)
        self.view_button.setMinimumHeight(55)
        self.view_button.setMinimumWidth(240)
        self.view_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {NAVY_PRIMARY};
                color: {TEXT_ON_DARK_BG};
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: {NAVY_ACCENT}; }}
            QPushButton:pressed {{ background-color: {NAVY_PRIMARY}; }}
        """)
        self.view_button.clicked.connect(self.view_questions_action)
        buttons_layout.addWidget(self.view_button)

        main_layout.addLayout(buttons_layout)
        main_layout.addStretch(3)

class AddQuestionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Soru Ekle")
        self.setMinimumWidth(550)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {WHITE_PRIMARY}; }}
            QLabel {{
                font-size: 14px;
                color: {TEXT_NAVY_HEADER};
                margin-bottom: 2px;
            }}
            QTextEdit, QLineEdit {{
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 7px;
                font-size: 14px;
                background-color: {WHITE_PRIMARY};
                color: {TEXT_ON_LIGHT_BG};
            }}
            QTextEdit:focus, QLineEdit:focus {{
                border: 1.5px solid {NAVY_PRIMARY};
            }}
            QRadioButton {{ font-size: 13px; color: {TEXT_ON_LIGHT_BG}; }}
            QRadioButton::indicator::unchecked {{
                border: 1px solid {NAVY_ACCENT};
                border-radius: 7px; background-color: {WHITE_PRIMARY};
            }}
            QRadioButton::indicator::checked {{
                border: 1px solid {NAVY_PRIMARY};
                border-radius: 7px; background-color: {NAVY_PRIMARY};
            }}
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.soru_label = QLabel("SORU METNİ:")
        self.soru_label.setStyleSheet(f"font-weight: bold; margin-top: 5px; color: {TEXT_NAVY_HEADER};")
        self.soru_input = QTextEdit()
        self.soru_input.setPlaceholderText("Sorunuzu buraya detaylı bir şekilde yazınız...")
        self.soru_input.setFixedHeight(100)
        self.layout.addWidget(self.soru_label)
        self.layout.addWidget(self.soru_input)

        self.dogru_sik_label = QLabel("SEÇENEKLER VE DOĞRU YANIT:")
        self.dogru_sik_label.setStyleSheet(f"font-weight: bold; margin-top: 10px; color: {TEXT_NAVY_HEADER};")
        self.layout.addWidget(self.dogru_sik_label)

        self.secenek_inputs = []
        self.radio_buttons = []
        self.radio_group = QButtonGroup(self)

        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)
        for i in range(5):
            h_layout = QHBoxLayout()
            h_layout.setSpacing(8)
            label = QLabel(f"{chr(65+i)}:")
            label.setFixedWidth(30)
            label.setStyleSheet(f"font-weight: normal; color: {NAVY_ACCENT};")

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Seçenek {chr(65+i)}")
            self.secenek_inputs.append(line_edit)

            radio_button = QRadioButton("Doğru Şık")
            self.radio_buttons.append(radio_button)
            self.radio_group.addButton(radio_button, i)

            h_layout.addWidget(label)
            h_layout.addWidget(line_edit)
            h_layout.addWidget(radio_button)
            h_layout.setStretchFactor(line_edit, 1)
            options_layout.addLayout(h_layout)
        self.layout.addLayout(options_layout)

        self.kategori_label = QLabel("KATEGORİ (Opsiyonel):")
        self.kategori_label.setStyleSheet(f"font-weight: bold; margin-top:10px; color: {TEXT_NAVY_HEADER};")
        self.kategori_input = QLineEdit("Genel")
        self.kategori_input.setPlaceholderText("Örn: Tarih, Matematik...")
        self.layout.addWidget(self.kategori_label)
        self.layout.addWidget(self.kategori_input)

        self.add_button_q = QPushButton("SORUYU KAYDET")
        self.add_button_q.setFixedHeight(40)
        self.add_button_q.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED_PRIMARY}; color: {TEXT_ON_DARK_BG};
                padding: 10px; font-weight: bold; font-size: 14px;
                border-radius: 5px; border: none;
            }}
            QPushButton:hover {{ background-color: {RED_ACCENT}; }}
            QPushButton:pressed {{ background-color: {RED_PRIMARY}; }}
        """)
        self.add_button_q.clicked.connect(self.add_question_dialog_save)

        button_box_layout = QHBoxLayout()
        button_box_layout.addStretch()
        button_box_layout.addWidget(self.add_button_q)
        self.layout.addLayout(button_box_layout)

    def add_question_dialog_save(self):
        soru_metni = self.soru_input.toPlainText().strip()
        secenekler = [inp.text().strip() for inp in self.secenek_inputs]
        kategori = self.kategori_input.text().strip() or "Genel"
        dogru_secenek_index = self.radio_group.checkedId()

        if not soru_metni: QMessageBox.warning(self, "Eksik Bilgi", "Soru metni boş olamaz."); return
        filled_options_count = sum(1 for s in secenekler if s)
        if dogru_secenek_index != -1 and filled_options_count < 1:
             QMessageBox.warning(self, "Eksik Bilgi", "Lütfen en az bir yanıt seçeneği girin (doğru şık dahil)."); return
        if sum(1 for s in secenekler if s) == 0: QMessageBox.warning(self, "Eksik Bilgi", "Lütfen en az bir yanıt seçeneği girin."); return
        if dogru_secenek_index == -1: QMessageBox.warning(self, "Eksik Bilgi", "Lütfen doğru şıkkı işaretleyin."); return
        if not secenekler[dogru_secenek_index]: QMessageBox.warning(self, "Eksik Bilgi", f"İşaretlediğiniz {chr(65+dogru_secenek_index)}. yanıt boş olamaz."); return

        if add_question_to_db(soru_metni, secenekler, dogru_secenek_index, kategori):
            QMessageBox.information(self, "Başarılı", "Soru başarıyla eklendi.")
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", "Soru eklenirken bir veritabanı hatası oluştu.")

class ViewPrintQuestionsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {WHITE_PRIMARY};")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(8)
        self.table_widget.setHorizontalHeaderLabels([
            "ID", "Soru Metni", "A", "B", "C", "D", "E", "Cevap Şıkkı"
        ])
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setShowGrid(True)
        self.table_widget.setAlternatingRowColors(True)

        self.table_widget.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #E0E0E0; font-size: 13px;
                border: 1px solid {BORDER_COLOR}; border-radius: 4px;
                alternate-background-color: {OFF_WHITE_BG};
                background-color: {WHITE_PRIMARY}; color: {TEXT_ON_LIGHT_BG};
            }}
            QHeaderView::section {{
                background-color: {NAVY_PRIMARY}; color: {TEXT_ON_DARK_BG};
                padding: 7px; font-weight: bold; font-size: 13px;
                border-top: 0px; border-bottom: 1px solid {NAVY_ACCENT};
                border-right: 1px solid {NAVY_ACCENT}; border-left: 0px;
            }}
            QHeaderView::section:first {{ border-left: 1px solid {NAVY_ACCENT}; }}
            QTableWidget::item {{ padding: 6px; border-bottom: 1px solid #F0F0F0; }}
            QTableWidget::item:selected {{
                background-color: {NAVY_ACCENT}; color: {TEXT_ON_DARK_BG};
            }}
        """)

        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(2, 7):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
            self.table_widget.setColumnWidth(i, 90)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.table_widget.setSortingEnabled(True)
        self.layout.addWidget(self.table_widget)

        self.bottom_controls_layout = QHBoxLayout()
        self.load_button = QPushButton("Listeyi Yenile")
        self.load_button.setFixedHeight(35)
        self.load_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {NAVY_PRIMARY}; color: {TEXT_ON_DARK_BG};
                padding: 8px 15px; font-weight: bold; font-size: 13px;
                border-radius: 4px; border: none;
            }}
            QPushButton:hover {{ background-color: {NAVY_ACCENT}; }}
            QPushButton:pressed {{ background-color: {NAVY_PRIMARY}; }}
        """)
        self.load_button.clicked.connect(self.load_questions)
        self.bottom_controls_layout.addStretch(1)
        self.bottom_controls_layout.addWidget(self.load_button)
        self.layout.addLayout(self.bottom_controls_layout)

    def load_questions(self):
        questions = get_all_questions()
        self.table_widget.setSortingEnabled(False)
        self.table_widget.setRowCount(0)
        self.table_widget.setRowCount(len(questions))
        for row_idx, row_data in enumerate(questions):
            try:
                id_item = QTableWidgetItem(); id_item.setData(Qt.DisplayRole, row_data[0])
                self.table_widget.setItem(row_idx, 0, id_item)
                self.table_widget.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))
                for i in range(5): self.table_widget.setItem(row_idx, 2 + i, QTableWidgetItem(str(row_data[2+i])))
                correct_option_char = "N/A"; dogru_idx = row_data[7]
                if dogru_idx is not None and 0 <= dogru_idx < 5:
                    if row_data[2+dogru_idx]: correct_option_char = chr(65 + dogru_idx)
                    else: correct_option_char = f"{chr(65 + dogru_idx)} (Boş)"
                self.table_widget.setItem(row_idx, 7, QTableWidgetItem(str(correct_option_char)))
            except Exception as e: print(f"DEBUG: HATA - Satır {row_idx} (ID: {row_data[0]}) yüklenirken: {e}")
        self.table_widget.setSortingEnabled(True)

    def _prepare_document_for_printing(self):
        document = QTextDocument()
        cursor = QTextCursor(document)
        try: base_font_family = "Segoe UI"; QFont(base_font_family)
        except: base_font_family = "Arial"

        title_format = QTextCharFormat(); title_font = QFont(base_font_family, 16, QFont.Bold)
        title_format.setFont(title_font); title_format.setForeground(QBrush(QColor(NAVY_PRIMARY)))
        cursor.insertText("Mini Soru Bankası - Soru Listesi\n\n", title_format)

        question_font_bold = QFont(base_font_family, 12, QFont.Bold)
        question_font_normal = QFont(base_font_family, 12)
        option_font = QFont(base_font_family, 10)
        option_font_bold_correct = QFont(base_font_family, 10, QFont.Bold)
        category_font = QFont(base_font_family, 9, QFont.Normal, italic=True)

        questions_to_print = get_all_questions()
        if not questions_to_print:
            cursor.setFont(option_font); cursor.insertText("Yazdırılacak soru bulunmamaktadır."); return document

        for i, q_data in enumerate(questions_to_print):
            q_fmt_b = QTextCharFormat(); q_fmt_b.setFont(question_font_bold); q_fmt_b.setForeground(QBrush(QColor(TEXT_NAVY_HEADER)))
            cursor.insertText(f"Soru {i+1} (ID: {q_data[0]}): ", q_fmt_b)
            q_fmt_n = QTextCharFormat(); q_fmt_n.setFont(question_font_normal); q_fmt_n.setForeground(QBrush(QColor(TEXT_ON_LIGHT_BG)))
            cursor.insertText(f"{q_data[1]}\n", q_fmt_n)
            correct_option_index = q_data[7]
            for j in range(5):
                option_text = q_data[2+j]
                if option_text or (j == correct_option_index and correct_option_index is not None):
                    opt_char_format = QTextCharFormat()
                    prefix = "    "; option_label = f"{chr(65+j)})"
                    current_option_text = option_text if option_text else "[BOŞ]"
                    opt_char_format.setForeground(QBrush(QColor(TEXT_ON_LIGHT_BG)))
                    if j == correct_option_index:
                        opt_char_format.setFont(option_font_bold_correct)
                        opt_char_format.setForeground(QBrush(QColor(RED_PRIMARY))) # Correct answer in Red
                        prefix = "  * "
                    else: opt_char_format.setFont(option_font)
                    cursor.insertText(f"{prefix}{option_label} {current_option_text}\n", opt_char_format)
            if q_data[8] and q_data[8].lower() != "genel":
                cat_fmt = QTextCharFormat(); cat_fmt.setFont(category_font); cat_fmt.setForeground(QBrush(QColor(NAVY_ACCENT)))
                cursor.insertText(f"    Kategori: {q_data[8]}\n", cat_fmt)
            cursor.insertBlock()
        return document

    def print_questions(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QDialog.Accepted:
            document = self._prepare_document_for_printing()
            document.print_(printer)
            QMessageBox.information(self, "Yazdırma", "Sorular yazdırıldı.")

    def print_preview(self):
        printer = QPrinter(QPrinter.HighResolution)
        preview_dialog = QPrintPreviewDialog(printer, self)
        preview_dialog.paintRequested.connect(self._handle_paint_request)
        preview_dialog.setWindowState(Qt.WindowMaximized)
        preview_dialog.exec_()

    def _handle_paint_request(self, printer):
        document = self._prepare_document_for_printing()
        document.print_(printer)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Soru Bankası")
        self.setGeometry(100, 100, 1024, 768)

        self.central_w = QWidget()
        self.central_w.setStyleSheet(f"background-color: {OFF_WHITE_BG};")
        self.setCentralWidget(self.central_w)
        self.main_layout = QVBoxLayout(self.central_w)
        self.main_layout.setContentsMargins(0,0,0,0)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        self.welcome_screen = WelcomeWidget(
            add_question_callback=self.show_add_question_dialog,
            view_questions_callback=self.show_question_view_and_load_data
        )
        self.view_print_screen = ViewPrintQuestionsWidget(self)

        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.view_print_screen)

        self.setup_menu()
        self.show_welcome_screen()

    def setup_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {NAVY_PRIMARY}; color: {TEXT_ON_DARK_BG};
                font-size: 13px; padding: 5px 0px;
                border-bottom: 1px solid {NAVY_ACCENT};
            }}
            QMenuBar::item {{
                background-color: transparent; padding: 8px 15px;
                margin: 0px 1px; border-radius: 3px;
            }}
            QMenuBar::item:selected {{ background-color: {RED_PRIMARY}; color: {TEXT_ON_DARK_BG}; }}
            QMenuBar::item:pressed {{ background-color: {RED_ACCENT}; }}
            QMenu {{
                background-color: {WHITE_PRIMARY}; color: {TEXT_NAVY_HEADER};
                border: 1px solid {NAVY_ACCENT}; padding: 6px; font-size: 13px;
            }}
            QMenu::item {{ padding: 8px 25px; margin: 1px 0px; border-radius: 3px; }}
            QMenu::item:selected {{ background-color: {RED_ACCENT}; color: {TEXT_ON_DARK_BG}; }}
            QMenu::separator {{ height: 1px; background: {NAVY_ACCENT}; margin: 6px 5px; }}
        """)

        self.home_action = QAction("Ana Sayfa", self)
        self.home_action.triggered.connect(self.show_welcome_screen)
        menubar.addAction(self.home_action)

        print_menu = menubar.addMenu("Yazdırma")
        self.print_action = QAction("Tüm Soruları Yazdır", self)
        self.print_action.triggered.connect(self.direct_print_questions)
        print_menu.addAction(self.print_action)
        self.preview_action = QAction("Baskı Önizleme", self)
        self.preview_action.triggered.connect(self.direct_preview_questions)
        print_menu.addAction(self.preview_action)

        system_menu = menubar.addMenu("Sistem")
        self.exit_action = QAction("Çıkış", self)
        self.exit_action.triggered.connect(self.close)
        system_menu.addAction(self.exit_action)

    def show_welcome_screen(self):
        self.stacked_widget.setCurrentWidget(self.welcome_screen)

    def show_add_question_dialog(self):
        dialog = AddQuestionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            if self.stacked_widget.currentWidget() == self.view_print_screen:
                self.view_print_screen.load_questions()

    def show_question_view_and_load_data(self):
        self.stacked_widget.setCurrentWidget(self.view_print_screen)
        self.view_print_screen.load_questions()

    def direct_print_questions(self):
        if self.stacked_widget.currentWidget() != self.view_print_screen:
            self.show_question_view_and_load_data(); QApplication.processEvents()
        if not self.view_print_screen.table_widget.rowCount() and not get_all_questions():
            QMessageBox.information(self, "Yazdırma", "Yazdırılacak soru bulunmamaktadır."); return
        self.view_print_screen.print_questions()

    def direct_preview_questions(self):
        if self.stacked_widget.currentWidget() != self.view_print_screen:
            self.show_question_view_and_load_data(); QApplication.processEvents()
        if not self.view_print_screen.table_widget.rowCount() and not get_all_questions():
            QMessageBox.information(self, "Baskı Önizleme", "Önizlenecek soru bulunmamaktadır."); return
        self.view_print_screen.print_preview()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    print(f"Script'in çalıştığı dizin (CWD): {os.getcwd()}")
    init_db()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())