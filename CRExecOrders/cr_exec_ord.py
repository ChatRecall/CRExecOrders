import subprocess
import sys

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                               QStatusBar, QMessageBox, QComboBox, QPushButton,QHBoxLayout, QLineEdit, QSpinBox)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QDate
from pathlib import Path

import logging

logging.basicConfig(
    level=logging.INFO,
    format = '%(name)s - %(levelname)s - %(message)s (line: %(lineno)d)',
    handlers=[
        logging.StreamHandler(),  # Log to console
        # logging.FileHandler('app.log')  # Log to file
    ]
)

logger = logging.getLogger(__name__)

from WrapSideSix.layouts.grid_layout import WSGridLayoutHandler, WSGridRecord, WSGridPosition
from WrapSideSix.toolbars.toolbar_icon import WSToolbarIcon, DropdownItem
from WrapSideSix.widgets.list_widget import WSListSelectionWidget, WSSortOrder
from WrapConfig import INIHandler, RuntimeConfig
from WrapCapExecOrders import (ExecutiveOrderManager, ExecutiveOrderDownloader)

from dialog_about import AboutDialog
from dialog_settings import SettingsDialog

import WrapSideSix.icons.icons_mat_des
WrapSideSix.icons.icons_mat_des.qInitResources()

class CRExecOrder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatRecall Executive Order Downloader")
        self.setMinimumWidth(800)

        # Set executive order manager
        self.manager = ExecutiveOrderManager()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.status_bar = QStatusBar()

        self.download_grid_layout_handler = WSGridLayoutHandler()
        self.filter_grid_layout_handler = WSGridLayoutHandler()
        self.list_grid_layout_handler = WSGridLayoutHandler()
        self.main_grid_layout_handler = WSGridLayoutHandler()

        self.toolbar = WSToolbarIcon('toolbar')

        # Create Widgets
        current_year = QDate.currentDate().year()

        self.download_year_end_combobox = QSpinBox()
        self.download_year_begin_combobox = QSpinBox()
        self.download_year_begin_combobox.setRange(1937, current_year)
        self.download_year_end_combobox.setRange(1937, current_year)
        self.download_year_begin_combobox.setValue(current_year)
        self.download_year_end_combobox.setValue(current_year)

        self.keyword_search = QLineEdit()
        self.president_search = QComboBox()

        self.not_downloaded_list = WSListSelectionWidget(multi_select=True)
        self.downloaded_list = WSListSelectionWidget(multi_select=False)

        self.download_library_button = QPushButton("Download List")
        icon_select = QIcon(":/icons/mat_des/download_24dp.png")  # Path to your icon file
        self.download_library_button.setIcon(icon_select)

        self.download_selected_button = QPushButton("Selected", self)
        icon_select = QIcon(":/icons/mat_des/download_24dp.png")  # Path to your icon file
        self.download_selected_button.setIcon(icon_select)

        self.download_all_button = QPushButton("All")
        icon_all = QIcon(":/icons/mat_des/select_all_24dp.png")
        self.download_all_button.setIcon(icon_all)

        self.select_none_button = QPushButton("Clear Selection")
        icon_none = QIcon(":/icons/mat_des/clear_all_24dp.png")
        self.select_none_button.setIcon(icon_none)

        # # Radio buttons
        # # Create radio buttons
        # self.all_button = QRadioButton("All")
        # self.downloaded_button = QRadioButton("Downloaded")
        # self.not_downloaded_button = QRadioButton("Not Downloaded")
        #
        # # Set the default selection (optional)
        # self.all_button.setChecked(True)
        #
        # # Create a button group to ensure only one button can be selected at a time
        # self.button_group = QButtonGroup(self)
        # self.button_group.addButton(self.all_button)
        # self.button_group.addButton(self.downloaded_button)
        # self.button_group.addButton(self.not_downloaded_button)
        #
        # # Create layout and add the radio buttons
        # self.radio_layout = QHBoxLayout()
        # self.radio_layout.addWidget(self.all_button)
        # self.radio_layout.addWidget(self.downloaded_button)
        # self.radio_layout.addWidget(self.not_downloaded_button)
        #
        # self.radio_widget = QWidget()
        # self.radio_widget.setLayout(self.radio_layout)

        # Dialogs
        self.dialog_about = AboutDialog(self)
        self.dialog_settings = SettingsDialog(self)

        self.run_time = RuntimeConfig()
        # program_dir = self.run_time.program_dir
        # self.library_path = program_dir / "Executive_Order_library"
        self.library_path = None
        self.eo_data_dir = None
        self.ini_handler = None
        self.update_default_attributes()

        self.init_ui()
        self.init_toolbar()
        self.init_status_bar()
        self.connect_signals()

        if not self.eo_data_dir:
            self.show_settings()

        if not self.library_path:
            self.library_path = f"{self.eo_data_dir}/Executive_Order_library"
        else:
            raise ValueError("eo_data_dir must be set before use")

        self.downloader = ExecutiveOrderDownloader(doc_dir=self.eo_data_dir, manager=self.manager)
        self.manager.load_from_file(self.library_path)
        self.populate_not_downloaded_listing()
        self.populate_downloaded_listing()


    # init helper methods
    def init_ui(self):
        download_grid_widgets = [
            WSGridRecord(widget=QLabel("Years to download (1937 to current):"),
                         position=WSGridPosition(row=0, column=0),
                         col_span=3, alignment=Qt.AlignmentFlag.AlignLeft),

            WSGridRecord(widget=QLabel("Beg year:"),
                         position=WSGridPosition(row=1, column=0),
                         col_stretch=0, alignment=Qt.AlignmentFlag.AlignLeft),
            WSGridRecord(widget=self.download_year_begin_combobox,
                         position=WSGridPosition(row=2, column=0),
                         col_stretch=0, alignment=Qt.AlignmentFlag.AlignLeft),

            WSGridRecord(widget=QLabel("End year:"),
                         position=WSGridPosition(row=1, column=1),
                         col_stretch=0, alignment=Qt.AlignmentFlag.AlignLeft),
            WSGridRecord(widget=self.download_year_end_combobox,
                         position=WSGridPosition(row=2, column=1),
                         col_stretch=0, alignment=Qt.AlignmentFlag.AlignLeft),

            WSGridRecord(widget=self.download_library_button,
                         position=WSGridPosition(row=1, column=2),
                         row_span=2, alignment=Qt.AlignmentFlag.AlignLeft)
        ]
        self.download_grid_layout_handler.add_widget_records(download_grid_widgets)

        filter_grid_widgets =[
            WSGridRecord(widget=QLabel("Keyword"),
                         position=WSGridPosition(row=0, column=0),
                         col_stretch=0
                         ), # alignment=Qt.AlignmentFlag.AlignLeft
            WSGridRecord(widget=self.keyword_search,
                         position=WSGridPosition(row=0, column=1)),

            # WSGridRecord(widget=QLabel("President"),
            #              position=WSGridPosition(row=1, column=0),
            #              col_stretch=0),
            # WSGridRecord(widget=self.president_search,
            #              position=WSGridPosition(row=1, column=1))

        ]
        self.filter_grid_layout_handler.add_widget_records(filter_grid_widgets)

        button_box = QHBoxLayout()
        button_box.addWidget(self.download_selected_button)
        button_box.addWidget(self.download_all_button)
        button_box.addWidget(self.select_none_button)
        button_box_widget = QWidget()  # Create a QWidget first
        button_box_widget.setLayout(button_box)  # Set the layout separately


        list_grid_widgets = [
            WSGridRecord(widget=QLabel("Not Downloaded"),
                         position=WSGridPosition(row=0, column=0),
                         col_stretch=1),
            WSGridRecord(widget=self.not_downloaded_list,
                         position=WSGridPosition(row=1, column=0),
                         col_stretch=1),

            WSGridRecord(widget=QLabel("Downloaded"),
                         position=WSGridPosition(row=0, column=1),
                         col_stretch=2),
            WSGridRecord(widget=self.downloaded_list,
                         position=WSGridPosition(row=1, column=1),
                         col_stretch=2),

            WSGridRecord(widget=button_box_widget,
                         position=WSGridPosition(row=2, column=0),
                         alignment=Qt.AlignmentFlag.AlignCenter)

        ]

        self.list_grid_layout_handler.add_widget_records(list_grid_widgets)

        main_grid_widgets = [
            WSGridRecord(widget=self.download_grid_layout_handler.as_widget(),
                         position=WSGridPosition(row=0, column=0),
                         col_span=1, col_stretch=1), # , alignment=Qt.AlignmentFlag.AlignJustify

            WSGridRecord(widget=self.filter_grid_layout_handler.as_widget(),
                         position=WSGridPosition(row=0, column=1),
                         col_span=1, col_stretch=3),

            WSGridRecord(widget=QLabel(""),
                         position=WSGridPosition(row=1, column=0),
                         col_span=2),

            WSGridRecord(widget=self.list_grid_layout_handler.as_widget(),
                         position=WSGridPosition(row=2, column=0),
                         col_span=2)
        ]

        self.main_grid_layout_handler.add_widget_records(main_grid_widgets)

        self.setCentralWidget(self.main_grid_layout_handler.as_widget())

    def init_menu(self):
        pass

    def init_toolbar(self):
        self.addToolBar(self.toolbar)
        self.toolbar.clear_toolbar()

        self.toolbar.add_action_to_toolbar(
            "filter",
            "Filter",
            "Toggle Filter",
            self.filter_action,
            ":/icons/mat_des/filter_alt_24dp.png")

        self.toolbar.add_action_to_toolbar(
            "settings",
            "Settings",
            "Settings",
            self.show_settings,
            ":/icons/mat_des/settings_24dp.png")

        dropdown_with_icons = [
            DropdownItem("Help", self.show_not_implemented_dialog),
            DropdownItem("About", self.show_about),
        ]

        self.toolbar.update_dropdown_menu(
            name="Open",  # or any unique name
            icon=":/icons/mat_des/question_mark_24dp.png",
            dropdown_definitions=dropdown_with_icons
        )

        self.toolbar.add_action_to_toolbar(
            "close",
            "Close",
            "Close Program",
            self.close,
            ":/icons/mat_des/exit_to_app_24dp.png")

    def init_status_bar(self):
        self.setStatusBar(self.status_bar)
        self.update_status_bar()

    def update_default_attributes(self):
        self.ini_handler = INIHandler(self.run_time.ini_file_name)
        # Re-initiated so self.ini_handler.reload() not needed
        self.eo_data_dir = self.ini_handler.read_value('CRExecOrder', 'exec_ord_directory') or self.eo_data_dir

    def connect_signals(self):
        self.download_year_begin_combobox.valueChanged.connect(self.update_end_year)
        self.download_year_end_combobox.valueChanged.connect(self.update_begin_year)

        self.download_library_button.clicked.connect(self.process_button_action)

        self.downloaded_list.doubleClicked.connect(self.open_selected_eo)

        self.download_selected_button.clicked.connect(self.download_library_list_selected)

        self.download_all_button.clicked.connect(self.download_library_list_all)
        self.select_none_button.clicked.connect(self.select_none_not_downloaded)

    # Status bar methods
    def update_status_bar(self, message="Welcome to ChatRecall Executive Orders", duration=5000):
        self.statusBar().showMessage(message, duration)

    def clear_status_bar(self):
        self.statusBar().clearMessage()

    # Validation methods
    # Define slot to enforce logical order
    def update_begin_year(self, value):
        if value < self.download_year_begin_combobox.value():
            self.download_year_begin_combobox.setValue(value)

    def update_end_year(self, value):
        if value > self.download_year_end_combobox.value():
            self.download_year_end_combobox.setValue(value)

    # Evaluate button actions
    def process_button_action(self):
        logger.debug("Start downloading library entries")
        start_year = self.download_year_begin_combobox.value()
        end_year = self.download_year_end_combobox.value()

        if start_year == end_year:
            self.manager.fetch_executive_orders(start_year)  # Single year
        else:
            self.manager.fetch_executive_orders(f"{start_year}-{end_year}")

        self.manager.save_to_file(file_name=self.library_path)
        logger.debug("Done downloading library entries")
        self.populate_not_downloaded_listing()

    def populate_not_downloaded_listing(self):
        library_titles_prelim = self.manager.get_not_downloaded_documents()
        library_titles = self.manager.get_display_titles(library_titles_prelim)
        self.not_downloaded_list.populate_list(
            [(doc_id, display_title) for doc_id, display_title in library_titles.items()]
        )

    def populate_downloaded_listing(self):
        library_titles_prelim = self.manager.get_downloaded_documents()
        library_titles = self.manager.get_display_titles(library_titles_prelim)
        # results = {
        #     doc: details
        #     for doc, details in self.manager.get_display_titles().items()
        # }
        # print(results)
        self.downloaded_list.populate_list(
            [(doc_id, display_title) for doc_id, display_title in library_titles.items()],
            sort_mode=WSSortOrder.DESCENDING
        )

    def download_library_list_selected(self):
        """Get selected items' doc_ids (keys)"""
        selected_items = self.not_downloaded_list.get_all_selected_items()

        # Extract only the IDs from each tuple and store them in a list
        selected_keys = [item_id for item_id, _ in selected_items]
        # This is equivalent to:
        # selected_keys = []
        # for item in selected_items:
        #     item_id = item[0]  # Get the first value of the tuple (the ID)
        #     selected_keys.append(item_id)

        total_files = len(selected_keys)
        if total_files == 0:
            self.update_status_bar("No items selected for download.")
            return

        self.update_status_bar(f"Downloading {total_files} files...")
        QApplication.processEvents()

        self.downloader.download_from_list([doc.strip() for doc in selected_keys], self.library_path)
        self.populate_not_downloaded_listing()
        self.populate_downloaded_listing()
        self.manager.save_to_file(file_name=self.library_path)

    def download_library_list_all(self):
        self.select_all_not_downloaded()
        self.download_library_list_selected()

    def open_selected_eo(self, doc_id, doc_name):
        """Opens the selected executive order's PDF file."""
        logger.debug(f"Received in open_selected_eo -> doc_id={doc_id} (type: {type(doc_id)}), doc_name={doc_name}")

        if not doc_id or doc_id == "0":
            logger.error(f"Error: No document number found in the selected item (doc_id={doc_id}).")
            return

        file_name = self.manager.get_file_name(doc_id)
        logger.debug(f"Lookup result -> doc_id={doc_id}, file_name={file_name}")

        if file_name == "Unknown":
            logger.error(f"Error: No file name found for document {doc_id}")
            return

        pdf_path = Path(self.eo_data_dir) / file_name

        try:
            pdf_path = pdf_path.resolve(strict=True)  # Works on all OS
        except FileNotFoundError:
            logger.error(f"Error: File not found - {pdf_path}")
            return

        # ✅ Step 4: Print the full path (for debugging)
        logger.debug(f"Opening file: {pdf_path}")

        # ✅ Step 5: Open the file using the system's default viewer
        try:
            if sys.platform == "win32":
                subprocess.run(["start", "", str(pdf_path)], shell=True)
            elif sys.platform == "darwin":
                subprocess.run(["open", pdf_path], check=True)  # macOS
            else:
                subprocess.run(["xdg-open", pdf_path], check=True)  # Linux
        except Exception as e:
            logger.error(f"Error opening PDF: {e}")

    def select_all_not_downloaded(self):
        for i in range(self.not_downloaded_list.count()):
            self.not_downloaded_list.item(i).setSelected(True)

    def select_none_not_downloaded(self):
        self.not_downloaded_list.clearSelection()

    # Filter actions
    def filter_action(self):
        keyword = self.keyword_search.text().lower()
        results = {
            doc: details
            for doc, details in self.manager.get_display_titles().items()
            if keyword in details.lower()
        }
        logger.debug(f"Filter results: {results}")
        self.downloaded_list.populate_list(list(results.items()),
            sort_mode=WSSortOrder.DESCENDING)

    # Dialogs
    def show_about(self):
        self.dialog_about.show()

    def show_settings(self):
        logger.debug("showing dialog")
        if self.dialog_settings.exec():
            logger.info("after if")
            self.update_default_attributes()
            logger.info("after update")


    # Other widget actions

    # Helper methods

    def show_not_implemented_dialog(self):
        QMessageBox.information(self, "Not Implemented", "This feature is not yet implemented.", QMessageBox.StandardButton.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CRExecOrder()  # project_dir="/home/dave/Desktop/"
    window.show()
    sys.exit(app.exec())
