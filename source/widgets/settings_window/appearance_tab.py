from modules.settings import (
    downloads_pages,
    get_default_downloads_page,
    get_default_library_page,
    get_default_tab,
    get_enable_download_notifications,
    get_enable_high_dpi_scaling,
    get_enable_new_builds_notifications,
    get_sync_library_and_downloads_pages,
    get_use_system_titlebar,
    library_pages,
    set_default_downloads_page,
    set_default_library_page,
    set_default_tab,
    set_enable_download_notifications,
    set_enable_high_dpi_scaling,
    set_enable_new_builds_notifications,
    set_make_error_notifications,
    set_sync_library_and_downloads_pages,
    set_use_system_titlebar,
    tabs,
)
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
)
from widgets.settings_form_widget import SettingsFormWidget

from .settings_group import SettingsGroup


class AppearanceTabWidget(SettingsFormWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Windows
        self.window_settings = SettingsGroup("Window related", parent=self)

        # Use System Title Bar
        self.UseSystemTitleBar = QCheckBox()
        self.UseSystemTitleBar.setText("Use System Title Bar")
        self.UseSystemTitleBar.setChecked(get_use_system_titlebar())
        self.UseSystemTitleBar.clicked.connect(self.toggle_system_titlebar)
        # High Dpi Scaling
        self.EnableHighDpiScalingCheckBox = QCheckBox()
        self.EnableHighDpiScalingCheckBox.setText("Enable High DPI Scaling")
        self.EnableHighDpiScalingCheckBox.clicked.connect(self.toggle_enable_high_dpi_scaling)
        self.EnableHighDpiScalingCheckBox.setChecked(get_enable_high_dpi_scaling())

        self.window_layout = QVBoxLayout()
        self.window_layout.addWidget(self.UseSystemTitleBar)
        self.window_layout.addWidget(self.EnableHighDpiScalingCheckBox)
        self.window_settings.setLayout(self.window_layout)

        # Notifications
        self.notification_settings = SettingsGroup("Notifications", parent=self)

        self.EnableNewBuildsNotifications = QCheckBox()
        self.EnableNewBuildsNotifications.setText("New Available Build")
        self.EnableNewBuildsNotifications.clicked.connect(self.toggle_enable_new_builds_notifications)
        self.EnableNewBuildsNotifications.setChecked(get_enable_new_builds_notifications())
        self.EnableDownloadNotifications = QCheckBox()
        self.EnableDownloadNotifications.setText("Finished Downloading")
        self.EnableDownloadNotifications.clicked.connect(self.toggle_enable_download_notifications)
        self.EnableDownloadNotifications.setChecked(get_enable_download_notifications())
        self.EnableErrorNotifications = QCheckBox()
        self.EnableErrorNotifications.setText("Errors")
        self.EnableErrorNotifications.clicked.connect(self.toggle_enable_download_notifications)
        self.EnableErrorNotifications.setChecked(get_enable_download_notifications())

        self.notification_layout = QVBoxLayout()
        self.notification_layout.addWidget(self.EnableNewBuildsNotifications)
        self.notification_layout.addWidget(self.EnableDownloadNotifications)
        self.notification_layout.addWidget(self.EnableErrorNotifications)
        self.notification_settings.setLayout(self.notification_layout)

        # Tabs
        self.tabs_settings = SettingsGroup("Tabs", parent=self)
        # Default Tab
        self.DefaultTabComboBox = QComboBox()
        self.DefaultTabComboBox.addItems(tabs.keys())
        self.DefaultTabComboBox.setCurrentIndex(get_default_tab())
        self.DefaultTabComboBox.activated[str].connect(self.change_default_tab)
        # Sync Library and Downloads pages
        self.SyncLibraryAndDownloadsPages = QCheckBox()
        self.SyncLibraryAndDownloadsPages.setText("Sync Library && Downloads Pages")
        self.SyncLibraryAndDownloadsPages.clicked.connect(self.toggle_sync_library_and_downloads_pages)
        self.SyncLibraryAndDownloadsPages.setChecked(get_sync_library_and_downloads_pages())
        # Default Library Page
        self.DefaultLibraryPageComboBox = QComboBox()
        self.DefaultLibraryPageComboBox.addItems(library_pages.keys())
        self.DefaultLibraryPageComboBox.setCurrentIndex(get_default_library_page())
        self.DefaultLibraryPageComboBox.activated[str].connect(self.change_default_library_page)
        # Default Downloads Page
        self.DefaultDownloadsPageComboBox = QComboBox()
        self.DefaultDownloadsPageComboBox.addItems(downloads_pages.keys())
        self.DefaultDownloadsPageComboBox.setCurrentIndex(get_default_downloads_page())
        self.DefaultDownloadsPageComboBox.activated[str].connect(self.change_default_downloads_page)

        self.tabs_layout = QFormLayout()
        self.tabs_layout.addRow(QLabel("Default Tab", self), self.DefaultTabComboBox)
        self.tabs_layout.addRow(self.SyncLibraryAndDownloadsPages)
        self.tabs_layout.addRow(QLabel("Default Library Page", self), self.DefaultLibraryPageComboBox)
        self.tabs_layout.addRow(QLabel("Default Downloads Page", self), self.DefaultDownloadsPageComboBox)
        self.tabs_settings.setLayout(self.tabs_layout)

        # Layout
        self.addRow(self.window_settings)
        self.addRow(self.notification_settings)
        self.addRow(self.tabs_settings)

    def toggle_system_titlebar(self, is_checked):
        set_use_system_titlebar(is_checked)
        self.parent.update_system_titlebar(is_checked)

    def toggle_enable_high_dpi_scaling(self, is_checked):
        set_enable_high_dpi_scaling(is_checked)

    def change_default_tab(self, tab):
        set_default_tab(tab)

    def toggle_sync_library_and_downloads_pages(self, is_checked):
        set_sync_library_and_downloads_pages(is_checked)
        self.parent.toggle_sync_library_and_downloads_pages(is_checked)

        if is_checked:
            index = self.DefaultLibraryPageComboBox.currentIndex()
            self.DefaultDownloadsPageComboBox.setCurrentIndex(index)
            text = self.DefaultLibraryPageComboBox.currentText()
            set_default_downloads_page(text)

    def change_default_library_page(self, page):
        set_default_library_page(page)

        if get_sync_library_and_downloads_pages():
            index = self.DefaultLibraryPageComboBox.currentIndex()
            self.DefaultDownloadsPageComboBox.setCurrentIndex(index)
            set_default_downloads_page(page)

    def change_default_downloads_page(self, page):
        set_default_downloads_page(page)

        if get_sync_library_and_downloads_pages():
            index = self.DefaultDownloadsPageComboBox.currentIndex()
            self.DefaultLibraryPageComboBox.setCurrentIndex(index)
            set_default_library_page(page)

    def toggle_enable_download_notifications(self, is_checked):
        set_enable_download_notifications(is_checked)

    def toggle_enable_new_builds_notifications(self, is_checked):
        set_enable_new_builds_notifications(is_checked)

    def toggle_enable_error_notifications(self, is_checked):
        set_make_error_notifications(is_checked)
