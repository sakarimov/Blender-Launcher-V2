import os

from modules.settings import (
    get_launch_minimized_to_tray,
    get_launch_when_system_starts,
    get_library_folder,
    get_platform,
    get_show_tray_icon,
    get_worker_thread_count,
    set_launch_minimized_to_tray,
    set_launch_when_system_starts,
    set_library_folder,
    set_show_tray_icon,
    set_worker_thread_count,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QLineEdit, QPushButton, QSpinBox, QWidget
from widgets.settings_form_widget import SettingsFormWidget
from windows.dialog_window import DialogWindow
from windows.file_dialog_window import FileDialogWindow


class GeneralTabWidget(SettingsFormWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # Library Folder
        self.LibraryFolderLineEdit = QLineEdit()
        self.LibraryFolderLineEdit.setText(str(get_library_folder()))
        self.LibraryFolderLineEdit.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.LibraryFolderLineEdit.setReadOnly(True)
        self.LibraryFolderLineEdit.setCursorPosition(0)
        self.SetLibraryFolderButton = QPushButton(self.parent.icons.folder, "")
        self.SetLibraryFolderButton.clicked.connect(self.set_library_folder)

        self.LibraryFolderWidget = QWidget()
        self.LibraryFolderLayout = QHBoxLayout(self.LibraryFolderWidget)
        self.LibraryFolderLayout.setContentsMargins(6, 0, 6, 0)
        self.LibraryFolderLayout.setSpacing(0)

        self.LibraryFolderLayout.addWidget(self.LibraryFolderLineEdit)
        self.LibraryFolderLayout.addWidget(self.SetLibraryFolderButton)

        # Launch When System Starts
        self.LaunchWhenSystemStartsCheckBox = QCheckBox()
        self.LaunchWhenSystemStartsCheckBox.setChecked(get_launch_when_system_starts())
        self.LaunchWhenSystemStartsCheckBox.clicked.connect(self.toggle_launch_when_system_starts)

        # Launch Minimized To Tray
        self.LaunchMinimizedToTrayCheckBox = QCheckBox()
        self.LaunchMinimizedToTrayCheckBox.setChecked(get_launch_minimized_to_tray())
        self.LaunchMinimizedToTrayCheckBox.clicked.connect(self.toggle_launch_minimized_to_tray)

        # Show Tray Icon
        self.ShowTrayIconCheckBox = QCheckBox()
        self.ShowTrayIconCheckBox.setChecked(get_show_tray_icon())
        self.ShowTrayIconCheckBox.clicked.connect(self.toggle_show_tray_icon)

        # Worker thread count

        self.WorkerThreadCount = QSpinBox()

        self.WorkerThreadCount.setToolTip(
            "Determines how many IO operations can be done at once, ex. Downloading, deleting, and extracting files"
        )
        self.WorkerThreadCount.editingFinished.connect(self.set_worker_thread_count)
        self.WorkerThreadCount.setMinimum(1)
        self.WorkerThreadCount.setValue(get_worker_thread_count())

        # Warn if thread count exceeds cpu count
        cpu_count = os.cpu_count()
        if cpu_count is not None:

            def warn_values_above_cpu(v: int):
                if v > cpu_count:
                    self.WorkerThreadCount.setSuffix(f" (warning: value above {cpu_count} (cpu count) !!)")
                else:
                    self.WorkerThreadCount.setSuffix(None)

            self.WorkerThreadCount.valueChanged.connect(warn_values_above_cpu)

        # Layout
        self._addRow("Library Folder", self.LibraryFolderWidget, new_line=True)

        if get_platform() == "Windows":
            self._addRow("Launch When System Starts", self.LaunchWhenSystemStartsCheckBox)

        self._addRow("Show Tray Icon", self.ShowTrayIconCheckBox)
        self.LaunchMinimizedToTrayRow = self._addRow("Launch Minimized To Tray", self.LaunchMinimizedToTrayCheckBox)
        self.LaunchMinimizedToTrayRow.setEnabled(get_show_tray_icon())

        self._addRow("Worker Thread Count", self.WorkerThreadCount)

    def set_library_folder(self):
        library_folder = str(get_library_folder())
        new_library_folder = FileDialogWindow().get_directory(self, "Select Library Folder", library_folder)

        if new_library_folder and (library_folder != new_library_folder):
            if set_library_folder(new_library_folder) is True:
                self.LibraryFolderLineEdit.setText(new_library_folder)
                self.parent.draw_library(clear=True)
            else:
                self.dlg = DialogWindow(
                    parent=self.parent,
                    title="Warning",
                    text="Selected folder doesn't have write permissions!",
                    accept_text="Retry",
                    cancel_text=None,
                )
                self.dlg.accepted.connect(self.set_library_folder)

    def toggle_launch_when_system_starts(self, is_checked):
        set_launch_when_system_starts(is_checked)

    def toggle_launch_minimized_to_tray(self, is_checked):
        set_launch_minimized_to_tray(is_checked)

    def toggle_show_tray_icon(self, is_checked):
        set_show_tray_icon(is_checked)
        self.LaunchMinimizedToTrayRow.setEnabled(is_checked)
        self.parent.tray_icon.setVisible(is_checked)

    def set_worker_thread_count(self):
        set_worker_thread_count(self.WorkerThreadCount.value())