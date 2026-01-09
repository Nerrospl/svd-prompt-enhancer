"""
═══════════════════════════════════════════════════════════════════════════════
PLIK 2: ui/tabs/enhance_tab.py (KOMPLETNY - ZASTĄP CAŁY PLIK)
WERSJA: 2.1 – Z PEŁNYMI SLIDERAMI I COMBO BOXY

Data: 2026-01-08
Status: ✅ GOTOWY DO WKLEJENIA
═══════════════════════════════════════════════════════════════════════════════

INSTRUKCJA:
1. Otwórz: /mnt/dane/svd-prompt-enhancer/ui/tabs/enhance_tab.py
2. Zaznacz wszystko: Ctrl+A
3. Usuń: Delete
4. Wklej CAŁY kod poniżej
5. Zapisz: Ctrl+O, Enter, Ctrl+X
6. Weryfikacja: python3 -m py_compile ui/tabs/enhance_tab.py

═══════════════════════════════════════════════════════════════════════════════
"""

import logging
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QSlider, QFileDialog, QProgressBar, QComboBox, QMessageBox, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSlot
from workers.enhancement_worker import EnhancementWorker
from workers.image_analysis_worker import ImageAnalysisWorker

logger = logging.getLogger(__name__)


class EnhanceTab(QWidget):
    """Główny tab do wzbogacania promptów"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.image_analysis = None
        self.enhancement_worker = None
        self.image_worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """Zabuduj UI"""
        
        main_layout = QVBoxLayout()
        
        # Dwa sub-taby
        mode_tabs = QTabWidget()
        
        direct_widget = self._build_direct_tab()
        mode_tabs.addTab(direct_widget, "⚡ Bezpośrednie")
        
        with_image_widget = self._build_with_image_tab()
        mode_tabs.addTab(with_image_widget, "🖼️ Z obrazem")
        
        main_layout.addWidget(mode_tabs)
        self.setLayout(main_layout)
    
    # ─────────────────────────────────────────────────────────────────────
    # TAB 1: BEZPOŚREDNIE
    # ─────────────────────────────────────────────────────────────────────
    
    def _build_direct_tab(self) -> QWidget:
        """Buduj UI dla bezpośredniego wzbogacania"""
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        info = QLabel(
            "🔧 Wzbogacz polskie prompty bezpośrednio bez załadowania obrazu.\n"
            "System automatycznie rozwijać będzie szczegóły i detale.\n"
            "WAŻNE: Ustaw pełną długość (300-500 słów) i wysoki poziom detali!"
        )
        info.setStyleSheet("color: #FF9800; font-size: 11px; margin: 10px 0; font-weight: bold;")
        layout.addWidget(info)
        
        # PROMPT INPUT
        layout.addWidget(QLabel("📝 Wpisz prompt w języku POLSKIM:"))
        
        self.direct_prompt_input = QTextEdit()
        self.direct_prompt_input.setPlaceholderText(
            "np. 'piękna, blond włosa kobieta spaceruje po plaży, "
            "przezroczyste białe ubranko, zmysłowe detale'"
        )
        self.direct_prompt_input.setMinimumHeight(80)
        layout.addWidget(self.direct_prompt_input)
        
        # USTAWIENIA - RZĄD 1
        settings_layout1 = QHBoxLayout()
        
        settings_layout1.addWidget(QLabel("Język:"))
        self.direct_language = QComboBox()
        self.direct_language.addItems(["🇵🇱 Polski", "🇬🇧 English"])
        self.direct_language.setMaximumWidth(150)
        settings_layout1.addWidget(self.direct_language)
        
        settings_layout1.addSpacing(20)
        
        settings_layout1.addWidget(QLabel("Kreatywność:"))
        self.direct_creativity = QSlider(Qt.Horizontal)
        self.direct_creativity.setMinimum(0)
        self.direct_creativity.setMaximum(100)
        self.direct_creativity.setValue(80)
        self.direct_creativity.setMaximumWidth(150)
        self.direct_creativity.sliderMoved.connect(self._on_direct_creativity_changed)
        settings_layout1.addWidget(self.direct_creativity)
        
        self.direct_creativity_label = QLabel("0.80")
        self.direct_creativity_label.setMaximumWidth(50)
        settings_layout1.addWidget(self.direct_creativity_label)
        
        settings_layout1.addStretch()
        layout.addLayout(settings_layout1)
        
        # USTAWIENIA - RZĄD 2
        settings_layout2 = QHBoxLayout()
        
        settings_layout2.addWidget(QLabel("📏 Długość odpowiedzi:"))
        self.direct_word_count = QSlider(Qt.Horizontal)
        self.direct_word_count.setMinimum(50)
        self.direct_word_count.setMaximum(500)
        self.direct_word_count.setValue(350)
        self.direct_word_count.setSingleStep(50)
        self.direct_word_count.setMaximumWidth(150)
        self.direct_word_count.sliderMoved.connect(self._on_direct_word_count_changed)
        settings_layout2.addWidget(self.direct_word_count)
        
        self.direct_word_count_label = QLabel("350 słów")
        self.direct_word_count_label.setMaximumWidth(80)
        settings_layout2.addWidget(self.direct_word_count_label)
        
        settings_layout2.addSpacing(20)
        
        settings_layout2.addWidget(QLabel("📊 Poziom detali:"))
        self.direct_detail_level = QComboBox()
        self.direct_detail_level.addItems(["🟢 Niski", "🟡 Średni", "🔴 Wysoki"])
        self.direct_detail_level.setCurrentIndex(2)
        self.direct_detail_level.setMaximumWidth(140)
        settings_layout2.addWidget(self.direct_detail_level)
        
        settings_layout2.addStretch()
        layout.addLayout(settings_layout2)
        
        # USTAWIENIA - RZĄD 3
        settings_layout3 = QHBoxLayout()
        
        settings_layout3.addWidget(QLabel("🎨 Styl opisu:"))
        self.direct_style = QComboBox()
        self.direct_style.addItems(["🎬 Kinematograficzny", "🎨 Artystyczny", "⚙️ Techniczny"])
        self.direct_style.setCurrentIndex(0)
        self.direct_style.setMaximumWidth(200)
        settings_layout3.addWidget(self.direct_style)
        
        settings_layout3.addStretch()
        layout.addLayout(settings_layout3)
        
        # PRZYCISKI
        action_layout = QHBoxLayout()
        
        self.direct_enhance_btn = QPushButton("✨ Wzbogać prompt (może potrwać 30-60 sek)")
        self.direct_enhance_btn.setStyleSheet(
            "background-color: #2196F3; color: white; font-weight: bold; padding: 10px;"
        )
        self.direct_enhance_btn.clicked.connect(self._on_direct_enhance)
        action_layout.addWidget(self.direct_enhance_btn)
        
        self.direct_clear_btn = QPushButton("🗑️ Wyczyść")
        self.direct_clear_btn.clicked.connect(self._on_direct_clear)
        action_layout.addWidget(self.direct_clear_btn)
        
        layout.addLayout(action_layout)
        
        # PROGRESS
        self.direct_progress = QProgressBar()
        self.direct_progress.setVisible(False)
        layout.addWidget(self.direct_progress)
        
        self.direct_status = QLabel("✅ Gotowy")
        self.direct_status.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")
        layout.addWidget(self.direct_status)
        
        # WYNIKI
        layout.addWidget(QLabel("📋 Wyniki wzbogacania (EN + PL):"))
        
        results_layout = QHBoxLayout()
        
        en_layout = QVBoxLayout()
        en_layout.addWidget(QLabel("🇬🇧 English:"))
        self.direct_result_en = QTextEdit()
        self.direct_result_en.setReadOnly(True)
        self.direct_result_en.setMinimumHeight(120)
        en_layout.addWidget(self.direct_result_en)
        results_layout.addLayout(en_layout)
        
        pl_layout = QVBoxLayout()
        pl_layout.addWidget(QLabel("🇵🇱 Polski:"))
        self.direct_result_pl = QTextEdit()
        self.direct_result_pl.setReadOnly(True)
        self.direct_result_pl.setMinimumHeight(120)
        pl_layout.addWidget(self.direct_result_pl)
        results_layout.addLayout(pl_layout)
        
        layout.addLayout(results_layout)
        
        # KOPIUJ
        copy_layout = QHBoxLayout()
        
        copy_en_btn = QPushButton("📋 Kopiuj EN")
        copy_en_btn.clicked.connect(self._copy_direct_en)
        copy_layout.addWidget(copy_en_btn)
        
        copy_pl_btn = QPushButton("📋 Kopiuj PL")
        copy_pl_btn.clicked.connect(self._copy_direct_pl)
        copy_layout.addWidget(copy_pl_btn)
        
        copy_layout.addStretch()
        layout.addLayout(copy_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    # ─────────────────────────────────────────────────────────────────────
    # TAB 2: Z OBRAZEM
    # ─────────────────────────────────────────────────────────────────────
    
    def _build_with_image_tab(self) -> QWidget:
        """Buduj UI dla wzbogacania z analizą obrazu"""
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        info = QLabel(
            "📸 Załaduj obraz i wzbogacz prompt w kontekście jego zawartości.\n"
            "System przeanalizuje obraz i dostosuje szczegóły do wizualnych elementów."
        )
        info.setStyleSheet("color: #FF9800; font-size: 11px; margin: 10px 0; font-weight: bold;")
        layout.addWidget(info)
        
        # WCZYTYWANIE OBRAZU
        layout.addWidget(QLabel("🖼️ Obraz:"))
        
        image_layout = QHBoxLayout()
        
        self.with_image_select_btn = QPushButton("📂 Wybierz obraz")
        self.with_image_select_btn.clicked.connect(self._on_with_image_select)
        image_layout.addWidget(self.with_image_select_btn)
        
        self.with_image_label = QLabel("Brak obrazu")
        self.with_image_label.setStyleSheet("color: #999;")
        image_layout.addWidget(self.with_image_label)
        
        image_layout.addStretch()
        layout.addLayout(image_layout)
        
        # PROMPT INPUT
        layout.addWidget(QLabel("📝 Wpisz krótki prompt:"))
        
        self.with_image_prompt_input = QTextEdit()
        self.with_image_prompt_input.setPlaceholderText(
            "np. 'kobieta' lub 'scena z naturą' – będzie rozwinięta na podstawie obrazu"
        )
        self.with_image_prompt_input.setMinimumHeight(80)
        layout.addWidget(self.with_image_prompt_input)
        
        # USTAWIENIA - RZĄD 1
        settings_layout1 = QHBoxLayout()
        
        settings_layout1.addWidget(QLabel("Język:"))
        self.with_image_language = QComboBox()
        self.with_image_language.addItems(["🇵🇱 Polski", "🇬🇧 English"])
        self.with_image_language.setMaximumWidth(150)
        settings_layout1.addWidget(self.with_image_language)
        
        settings_layout1.addSpacing(20)
        
        settings_layout1.addWidget(QLabel("Kreatywność:"))
        self.with_image_creativity = QSlider(Qt.Horizontal)
        self.with_image_creativity.setMinimum(0)
        self.with_image_creativity.setMaximum(100)
        self.with_image_creativity.setValue(80)
        self.with_image_creativity.setMaximumWidth(150)
        self.with_image_creativity.sliderMoved.connect(self._on_with_image_creativity_changed)
        settings_layout1.addWidget(self.with_image_creativity)
        
        self.with_image_creativity_label = QLabel("0.80")
        self.with_image_creativity_label.setMaximumWidth(50)
        settings_layout1.addWidget(self.with_image_creativity_label)
        
        settings_layout1.addStretch()
        layout.addLayout(settings_layout1)
        
        # USTAWIENIA - RZĄD 2
        settings_layout2 = QHBoxLayout()
        
        settings_layout2.addWidget(QLabel("📏 Długość:"))
        self.with_image_word_count = QSlider(Qt.Horizontal)
        self.with_image_word_count.setMinimum(50)
        self.with_image_word_count.setMaximum(500)
        self.with_image_word_count.setValue(350)
        self.with_image_word_count.setSingleStep(50)
        self.with_image_word_count.setMaximumWidth(150)
        self.with_image_word_count.sliderMoved.connect(self._on_with_image_word_count_changed)
        settings_layout2.addWidget(self.with_image_word_count)
        
        self.with_image_word_count_label = QLabel("350 słów")
        self.with_image_word_count_label.setMaximumWidth(80)
        settings_layout2.addWidget(self.with_image_word_count_label)
        
        settings_layout2.addSpacing(20)
        
        settings_layout2.addWidget(QLabel("📊 Detale:"))
        self.with_image_detail_level = QComboBox()
        self.with_image_detail_level.addItems(["🟢 Niski", "🟡 Średni", "🔴 Wysoki"])
        self.with_image_detail_level.setCurrentIndex(2)
        self.with_image_detail_level.setMaximumWidth(140)
        settings_layout2.addWidget(self.with_image_detail_level)
        
        settings_layout2.addStretch()
        layout.addLayout(settings_layout2)
        
        # USTAWIENIA - RZĄD 3
        settings_layout3 = QHBoxLayout()
        
        settings_layout3.addWidget(QLabel("🎨 Styl:"))
        self.with_image_style = QComboBox()
        self.with_image_style.addItems(["🎬 Kinematograficzny", "🎨 Artystyczny", "⚙️ Techniczny"])
        self.with_image_style.setCurrentIndex(0)
        self.with_image_style.setMaximumWidth(200)
        settings_layout3.addWidget(self.with_image_style)
        
        settings_layout3.addStretch()
        layout.addLayout(settings_layout3)
        
        # PRZYCISKI
        action_layout = QHBoxLayout()
        
        self.with_image_analyze_btn = QPushButton("🔍 Analizuj obraz")
        self.with_image_analyze_btn.setStyleSheet(
            "background-color: #FF9800; color: white; font-weight: bold; padding: 10px;"
        )
        self.with_image_analyze_btn.clicked.connect(self._on_with_image_analyze)
        action_layout.addWidget(self.with_image_analyze_btn)
        
        self.with_image_enhance_btn = QPushButton("✨ Wzbogać")
        self.with_image_enhance_btn.setStyleSheet(
            "background-color: #2196F3; color: white; font-weight: bold; padding: 10px;"
        )
        self.with_image_enhance_btn.clicked.connect(self._on_with_image_enhance)
        self.with_image_enhance_btn.setEnabled(False)
        action_layout.addWidget(self.with_image_enhance_btn)
        
        layout.addLayout(action_layout)
        
        # PROGRESS
        self.with_image_progress = QProgressBar()
        self.with_image_progress.setVisible(False)
        layout.addWidget(self.with_image_progress)
        
        self.with_image_status = QLabel("✅ Gotowy")
        self.with_image_status.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")
        layout.addWidget(self.with_image_status)
        
        # WYNIKI
        layout.addWidget(QLabel("📋 Wyniki:"))
        
        results_layout = QHBoxLayout()
        
        en_layout = QVBoxLayout()
        en_layout.addWidget(QLabel("🇬🇧 English:"))
        self.with_image_result_en = QTextEdit()
        self.with_image_result_en.setReadOnly(True)
        self.with_image_result_en.setMinimumHeight(120)
        en_layout.addWidget(self.with_image_result_en)
        results_layout.addLayout(en_layout)
        
        pl_layout = QVBoxLayout()
        pl_layout.addWidget(QLabel("🇵🇱 Polski:"))
        self.with_image_result_pl = QTextEdit()
        self.with_image_result_pl.setReadOnly(True)
        self.with_image_result_pl.setMinimumHeight(120)
        pl_layout.addWidget(self.with_image_result_pl)
        results_layout.addLayout(pl_layout)
        
        layout.addLayout(results_layout)
        
        # KOPIUJ
        copy_layout = QHBoxLayout()
        
        copy_en_btn = QPushButton("📋 Kopiuj EN")
        copy_en_btn.clicked.connect(self._copy_with_image_en)
        copy_layout.addWidget(copy_en_btn)
        
        copy_pl_btn = QPushButton("📋 Kopiuj PL")
        copy_pl_btn.clicked.connect(self._copy_with_image_pl)
        copy_layout.addWidget(copy_pl_btn)
        
        copy_layout.addStretch()
        layout.addLayout(copy_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    # ─────────────────────────────────────────────────────────────────────
    # SLOTY: BEZPOŚREDNIE
    # ─────────────────────────────────────────────────────────────────────
    
    @pyqtSlot()
    def _on_direct_enhance(self):
        """Uruchom wzbogacanie"""
        
        prompt = self.direct_prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Błąd", "Wpisz prompt!")
            return
        
        language = "pl" if "Polski" in self.direct_language.currentText() else "en"
        creativity = self.direct_creativity.value() / 100.0
        word_count = self.direct_word_count.value()
        
        detail_map = {"Niski": "low", "Średni": "medium", "Wysoki": "high"}
        detail_text = self.direct_detail_level.currentText()
        detail_level = detail_map.get(detail_text.split()[-1], "medium")
        
        style_map = {"Kinematograficzny": "cinematic", "Artystyczny": "artistic", "Techniczny": "technical"}
        style_text = self.direct_style.currentText()
        style = style_map.get(style_text.split()[-1], "cinematic")
        
        self.direct_enhance_btn.setEnabled(False)
        self.direct_progress.setVisible(True)
        self.direct_progress.setValue(0)
        self.direct_status.setText("🔄 Wzbogacanie... (ETAP 1: ekspansja, ETAP 2: generacja, ETAP 3: validacja)")
        
        self.enhancement_worker = EnhancementWorker(
            prompt=prompt,
            language=language,
            creativity=creativity,
            word_count=word_count,
            detail_level=detail_level,
            style=style
        )
        self.enhancement_worker.progress.connect(self._on_enhancement_progress)
        self.enhancement_worker.finished.connect(self._on_enhancement_finished)
        self.enhancement_worker.start()
    
    @pyqtSlot()
    def _on_direct_clear(self):
        """Wyczyść"""
        self.direct_prompt_input.clear()
        self.direct_result_en.clear()
        self.direct_result_pl.clear()
        self.direct_status.setText("✅ Gotowy")
    
    @pyqtSlot()
    def _on_direct_word_count_changed(self):
        val = self.direct_word_count.value()
        self.direct_word_count_label.setText(f"{val} słów")
    
    @pyqtSlot()
    def _on_direct_creativity_changed(self):
        val = self.direct_creativity.value() / 100.0
        self.direct_creativity_label.setText(f"{val:.2f}")
    
    @pyqtSlot()
    def _copy_direct_en(self):
        try:
            import pyperclip
            text = self.direct_result_en.toPlainText()
            if text:
                pyperclip.copy(text)
                QMessageBox.information(self, "OK", "Skopiowano EN!")
        except:
            QMessageBox.warning(self, "Błąd", "Nie udało się skopiować")
    
    @pyqtSlot()
    def _copy_direct_pl(self):
        try:
            import pyperclip
            text = self.direct_result_pl.toPlainText()
            if text:
                pyperclip.copy(text)
                QMessageBox.information(self, "OK", "Skopiowano PL!")
        except:
            QMessageBox.warning(self, "Błąd", "Nie udało się skopiować")
    
    # ─────────────────────────────────────────────────────────────────────
    # SLOTY: Z OBRAZEM
    # ─────────────────────────────────────────────────────────────────────
    
    @pyqtSlot()
    def _on_with_image_select(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz obraz",
            "",
            "Obrazy (*.jpg *.jpeg *.png *.bmp *.gif);;Wszystkie pliki (*)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.with_image_label.setText(Path(file_path).name)
            self.with_image_label.setStyleSheet("color: #4CAF50;")
            self.with_image_analyze_btn.setEnabled(True)
    
    @pyqtSlot()
    def _on_with_image_analyze(self):
        if not self.current_image_path:
            QMessageBox.warning(self, "Błąd", "Wybierz obraz!")
            return
        
        self.with_image_analyze_btn.setEnabled(False)
        self.with_image_progress.setVisible(True)
        self.with_image_progress.setValue(50)
        self.with_image_status.setText("🔄 Analiza...")
        
        self.image_worker = ImageAnalysisWorker(self.current_image_path)
        self.image_worker.progress.connect(self._on_image_analysis_progress)
        self.image_worker.finished.connect(self._on_image_analysis_finished)
        self.image_worker.start()
    
    @pyqtSlot()
    def _on_with_image_enhance(self):
        prompt = self.with_image_prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Błąd", "Wpisz prompt!")
            return
        
        language = "pl" if "Polski" in self.with_image_language.currentText() else "en"
        creativity = self.with_image_creativity.value() / 100.0
        word_count = self.with_image_word_count.value()
        
        detail_map = {"Niski": "low", "Średni": "medium", "Wysoki": "high"}
        detail_text = self.with_image_detail_level.currentText()
        detail_level = detail_map.get(detail_text.split()[-1], "medium")
        
        style_map = {"Kinematograficzny": "cinematic", "Artystyczny": "artistic", "Techniczny": "technical"}
        style_text = self.with_image_style.currentText()
        style = style_map.get(style_text.split()[-1], "cinematic")
        
        self.with_image_enhance_btn.setEnabled(False)
        self.with_image_progress.setVisible(True)
        self.with_image_progress.setValue(0)
        self.with_image_status.setText("🔄 Wzbogacanie...")
        
        self.enhancement_worker = EnhancementWorker(
            prompt=prompt,
            language=language,
            creativity=creativity,
            image_analysis=self.image_analysis,
            word_count=word_count,
            detail_level=detail_level,
            style=style
        )
        self.enhancement_worker.progress.connect(self._on_enhancement_progress)
        self.enhancement_worker.finished.connect(self._on_with_image_enhancement_finished)
        self.enhancement_worker.start()
    
    @pyqtSlot()
    def _on_with_image_word_count_changed(self):
        val = self.with_image_word_count.value()
        self.with_image_word_count_label.setText(f"{val} słów")
    
    @pyqtSlot()
    def _on_with_image_creativity_changed(self):
        val = self.with_image_creativity.value() / 100.0
        self.with_image_creativity_label.setText(f"{val:.2f}")
    
    @pyqtSlot()
    def _copy_with_image_en(self):
        try:
            import pyperclip
            text = self.with_image_result_en.toPlainText()
            if text:
                pyperclip.copy(text)
                QMessageBox.information(self, "OK", "Skopiowano EN!")
        except:
            QMessageBox.warning(self, "Błąd", "Nie udało się skopiować")
    
    @pyqtSlot()
    def _copy_with_image_pl(self):
        try:
            import pyperclip
            text = self.with_image_result_pl.toPlainText()
            if text:
                pyperclip.copy(text)
                QMessageBox.information(self, "OK", "Skopiowano PL!")
        except:
            QMessageBox.warning(self, "Błąd", "Nie udało się skopiować")
    
    # ─────────────────────────────────────────────────────────────────────
    # CALLBACKS
    # ─────────────────────────────────────────────────────────────────────
    
    @pyqtSlot(str)
    def _on_enhancement_progress(self, msg: str):
        self.direct_status.setText(msg)
        self.with_image_status.setText(msg)
        self.direct_progress.setValue(min(99, self.direct_progress.value() + 20))
        self.with_image_progress.setValue(min(99, self.with_image_progress.value() + 20))
    
    @pyqtSlot(bool, dict)
    def _on_enhancement_finished(self, success: bool, result: dict):
        self.direct_enhance_btn.setEnabled(True)
        self.direct_progress.setVisible(False)
        
        if success:
            self.direct_result_en.setText(result.get("prompt_en", ""))
            self.direct_result_pl.setText(result.get("prompt_pl", ""))
            en_words = len(result.get("prompt_en", "").split())
            pl_words = len(result.get("prompt_pl", "").split())
            self.direct_status.setText(
                f"✅ Gotowe! EN: {en_words} słów, PL: {pl_words} słów"
            )
        else:
            error = result.get("error", "Nieznany błąd")
            self.direct_status.setText(f"❌ Błąd: {error}")
            QMessageBox.critical(self, "Błąd", error)
    
    @pyqtSlot(bool, dict)
    def _on_with_image_enhancement_finished(self, success: bool, result: dict):
        self.with_image_enhance_btn.setEnabled(True)
        self.with_image_progress.setVisible(False)
        
        if success:
            self.with_image_result_en.setText(result.get("prompt_en", ""))
            self.with_image_result_pl.setText(result.get("prompt_pl", ""))
            en_words = len(result.get("prompt_en", "").split())
            pl_words = len(result.get("prompt_pl", "").split())
            self.with_image_status.setText(
                f"✅ Gotowe! EN: {en_words} słów, PL: {pl_words} słów"
            )
        else:
            error = result.get("error", "Nieznany błąd")
            self.with_image_status.setText(f"❌ Błąd: {error}")
            QMessageBox.critical(self, "Błąd", error)
    
    @pyqtSlot(str)
    def _on_image_analysis_progress(self, msg: str):
        self.with_image_status.setText(msg)
    
    @pyqtSlot(bool, dict)
    def _on_image_analysis_finished(self, success: bool, result: dict):
        self.with_image_analyze_btn.setEnabled(True)
        self.with_image_progress.setVisible(False)
        
        if success:
            self.image_analysis = result
            self.with_image_enhance_btn.setEnabled(True)
            w = result.get("width", "?")
            h = result.get("height", "?")
            self.with_image_status.setText(f"✅ Obraz przeanalizowany: {w}x{h}px")
        else:
            error = result.get("error", "Nieznany błąd")
            self.with_image_status.setText(f"❌ Błąd: {error}")
            QMessageBox.critical(self, "Błąd", error)
