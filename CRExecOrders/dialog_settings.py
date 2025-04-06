#  dialog_settings.py

from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QDir

import logging

# Logger Configuration
logger = logging.getLogger(__name__)

from WrapSideSix.layouts.grid_layout import (WSGridRecord, WSGridLayoutHandler, WSGridPosition)
from WrapSideSix.io.ws_io import WSGuiIO
from WrapSideSix.widgets.line_edit_widget import WSLineButtonDirectory
from WrapConfig import INIHandler, RuntimeConfig

import WrapSideSix.icons.icons_mat_des
WrapSideSix.icons.icons_mat_des.qInitResources()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.run_time = RuntimeConfig()
        self.ini_handler = INIHandler(self.run_time.ini_file_name)
        self.settings_io = None

        # self.eo_data_dir = WSLineButton(button_icon=":/icons/mat_des/folder_24dp.png", button_action=self.select_exec_ord_directory)
        self.eo_data_dir = WSLineButtonDirectory()

        self.project_dir = QDir.homePath()


        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save |
                                           QDialogButtonBox.StandardButton.Cancel)
        self.layout = QVBoxLayout()

        self.init_ui()
        self.connect_signals()
        self.set_fields()

    def init_ui(self):
        grid_layout_handler = WSGridLayoutHandler()

        main_grid_widgets = [
            WSGridRecord(widget=QLabel("Required fields"), position=WSGridPosition(row=0, column=0), alignment=Qt.AlignmentFlag.AlignLeft),
            WSGridRecord(widget=QLabel("Executive Order Directory"), position=WSGridPosition(row=6, column=0)),
            WSGridRecord(widget=self.eo_data_dir, position=WSGridPosition(row=6, column=1)),
            WSGridRecord(widget=self.button_box, position=WSGridPosition(row=10, column=0), col_span=2),
            ]

        grid_layout_handler.add_widget_records(main_grid_widgets)
        self.layout.addWidget(grid_layout_handler.as_widget())
        self.setLayout(self.layout)

    def connect_signals(self):
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    # def select_exec_ord_directory(self):
    #     # Get the path from the line edit
    #     current_path = self.eo_data_dir.text().strip()
    #
    #     # Use it if it's a valid directory, otherwise use the home directory
    #     start_dir = current_path if Path(current_path).is_dir() else str(Path.home())
    #
    #     folder_path = QFileDialog.getExistingDirectory(
    #         self,
    #         "Select a folder",
    #         start_dir  # Starting directory, leave empty for default
    #     )
    #     if folder_path:
    #         logger.debug(f"Selected folder: {folder_path}")
    #         self.eo_data_dir.setText(folder_path)
    #
    #         # directory = folder_path  # Change this to your target directory
    #         # files = [f.name for f in Path(directory).iterdir() if f.is_file()]


    def set_fields(self):
        try:
            eo_data_dir = self.ini_handler.read_value('CRExecOrder', 'exec_ord_directory') or self.project_dir

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read settings: {e}")
            return

        # Populate fields
        self.eo_data_dir.setText(eo_data_dir)

        widget_mapping = {
            'exec_ord_directory': self.eo_data_dir,
        }
        dialog_values = {
            'exec_ord_directory': eo_data_dir,
        }
        self.settings_io = WSGuiIO(widget_mapping, dialog_values)
        self.settings_io.set_gui()

    def get_fields(self):
        try:
            updated_settings = self.settings_io.get_gui()
            # Retrieve the model name from the combo box's item data.
            self.ini_handler.create_or_update_option('CRExecOrder', 'exec_ord_directory', updated_settings['exec_ord_directory'])

            self.ini_handler.save_changes()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
            return False

    def accept(self):
        if self.get_fields():  # Save the fields if valid
            super().accept()  # Only accept the dialog if saving succeeded
        else:
            QMessageBox.critical(self, "Error", "Failed to save settings.")


if __name__ == "__main__":
    app = QApplication([])
    dialog = SettingsDialog()
    if dialog.exec():
        print(dialog.get_fields())
    else:
        print("Dialog canceled")
