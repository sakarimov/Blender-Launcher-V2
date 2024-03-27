from __future__ import annotations

import gettext
import json
import logging
import multiprocessing
import os
import sys
from argparse import ArgumentParser
from operator import attrgetter
from pathlib import Path

import modules._resources_rc
from modules import argument_parsing as ap
from modules._platform import _popen, get_cwd, get_launcher_name, get_platform, is_frozen
from modules.build_info import parse_blender_ver, read_build_info
from modules.settings import get_favorite_path, get_settings, get_worker_thread_count
from modules.version_matcher import VersionMatcher, VersionSearch
from PyQt5.QtWidgets import QApplication
from semver import Version
from threads.library_drawer import DrawLibraryTask
from windows.dialog_window import DialogWindow

version = "2.0.24"

_ = gettext.gettext

# Setup logging config
_format = "[%(asctime)s:%(levelname)s] %(message)s"
logging.basicConfig(
    format=_format,
    handlers=[logging.FileHandler(get_cwd() / "Blender Launcher.log"), logging.StreamHandler(stream=sys.stdout)],
)
logger = logging.getLogger(__name__)


# Setup exception handling
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error(f"{get_platform()} - Blender Launcher {version}", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def add_help(parser: ArgumentParser):
    parser.add_argument(
        parser.prefix_chars + "h",
        parser.prefix_chars * 2 + "help",
        action="store_true",
        help="show this help message and exit",
    )


def main():
    parser = ArgumentParser(description=f"Blender Launcher V2 ({version})", add_help=False)
    add_help(parser)

    subparsers = parser.add_subparsers(dest="command")

    update_parser = subparsers.add_parser("update", help="Update the application to a new version.", add_help=False)
    add_help(update_parser)
    update_parser.add_argument("version", help="Version to update to.", nargs="?")

    parser.add_argument("-debug", help="Enable debug logging.", action="store_true")
    parser.add_argument("-set-library-folder", help="Set library folder", type=Path)
    parser.add_argument(
        "--offline",
        "-offline",
        help="Run the application offline. (Disables scraper threads and update checks)",
        action="store_true",
    )
    parser.add_argument(
        "--instanced",
        "-instanced",
        help="Do not check for existing instance.",
        action="store_true",
    )

    launch_parser = subparsers.add_parser("launch", description="Launch a specific version of blender.")
    launch_parser.add_argument("-f", "--file", type=Path, help="Path to a specific .blend file to launch.")
    launch_parser.add_argument(
        "-v",
        "--version",
        type=str,
        help="The blender version to launch. if none is specified, a version will be estimated",
    )

    args, argv = parser.parse_known_args()
    if argv:
        msg = _("unrecognized arguments: ") + " ".join(argv)
        ap.error(parser, msg)

    # Custom help is necessary for frozen Windows builds
    if args.help:
        ap.show_help(parser, update_parser, args)
        sys.exit(0)

    if args.debug:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    # Create an instance of application and set its core properties
    app = QApplication([])
    app.setStyle("Fusion")
    app.setApplicationVersion(version)

    set_lib_folder: Path | None = args.set_library_folder
    if set_lib_folder is not None:
        start_set_library_folder(app, str(set_lib_folder))

    if args.command == "update":
        start_update(app, args.instanced, args.version)

    elif args.command == "launch":
        start_launch(app, args.file, args.version)

    if not args.instanced:
        check_for_instance()

    from windows.main_window import BlenderLauncher

    app.setQuitOnLastWindowClosed(False)

    BlenderLauncher(app=app, version=version, offline=args.offline)
    sys.exit(app.exec())


def start_set_library_folder(app: QApplication, lib_folder: str):
    from modules.settings import set_library_folder

    if set_library_folder(str(lib_folder)):
        logging.info(f"Library folder set to {lib_folder!s}")
    else:
        logging.error("Failed to set library folder")
        dlg = DialogWindow(
            title="Warning",
            text="Passed path is not a valid folder or<br>it doesn't have write permissions!",
            accept_text="Quit",
            cancel_text=None,
            app=app,
        )
        dlg.show()
        sys.exit(app.exec())


def start_update(app: QApplication, is_instanced: bool, tag: str | None):
    import shutil

    from windows.update_window import BlenderLauncherUpdater

    if is_instanced or not is_frozen():
        BlenderLauncherUpdater(app=app, version=version, release_tag=tag)
        sys.exit(app.exec())
    else:
        # Copy the launcher to the updater position
        bl_exe, blu_exe = get_launcher_name()
        cwd = get_cwd()
        source = cwd / bl_exe
        dist = cwd / blu_exe
        shutil.copy(source, dist)

        # Run the updater with the instanced flag
        if get_platform() == "Windows":
            _popen([blu_exe, "--instanced", "update"])
        elif get_platform() == "Linux":
            os.chmod(blu_exe, 0o744)
            _popen(f'nohup "{blu_exe}" --instanced update')
        sys.exit(0)


def start_launch(app: QApplication, file: Path | None, version: str | None):
    # TODO: Move the majority of this to another file
    from pprint import pprint

    from blender_asset_tracer import blendfile
    from blender_asset_tracer.blendfile import magic_compression
    from blender_asset_tracer.blendfile.header import BlendFileHeader

    print("Reading builds...")
    # Get all builds
    builds = [build_path for valid, build_path in DrawLibraryTask().get_builds() if valid]
    with multiprocessing.Pool(get_worker_thread_count()) as p:
        blinfos = p.map(read_build_info, builds)
    versions = {}
    links = {}
    for blinfo in blinfos:
        versions[blinfo.semversion] = blinfo
        links[blinfo.link] = blinfo

    # get selectors
    selectors = {
        VersionSearch.from_str(s): VersionSearch.from_str(search)
        for s, search in json.loads(get_settings().value("build-selectors", defaultValue="{}", type=str)).items()
    }
    print(selectors)
    matcher = VersionMatcher(tuple(versions))

    pprint(versions)
    print("Selecting best build candidate...")
    if file is None and version is None:
        fav_path = get_favorite_path()
        if fav_path and fav_path in links:
            blinfo = links[fav_path]
            print("Fav exists, selected: ")
            pprint(blinfo)
        else:
            raise ValueError("No path was specified, and no favorite build exists")

    if file is None and version is not None:  # Launch the specified build version
        ...

    if file is not None and version is None:  # get the build version from the file
        # TODO: create a stripped down version of blender_asset_tracer to just the header
        fileobj = magic_compression.open(file, "rb", blendfile.FILE_BUFFER_SIZE).fileobj
        header = BlendFileHeader(fileobj, file)
        _ver = header.version
        print(_ver)
        if _ver // 100 == 2:  # major == 2
            # there are a few versions with quadruple digits but those aren't detectable i think
            ver = Version(*divmod(_ver, 100), 0)
        else:
            major, mp = divmod(_ver, 100)
            minor, patch = divmod(mp, 10)
            ver = Version(major, minor, patch)
        print(ver)

        query = VersionSearch(ver.major, ver.minor, ver.patch)
        print(selectors)
        exit()
        match = matcher.match(query)
        if not match:  # No match was made; check selectors
            query = selectors.get(ver)
            if query is None: # Create window to make a selector
                print("Create a selector...")
                ...
            else:
                match = matcher.match(query)
                print(match)
        # print(match)

    sys.exit()


def check_for_instance():
    from PyQt5.QtCore import QByteArray
    from PyQt5.QtNetwork import QLocalSocket

    socket = QLocalSocket()
    socket.connectToServer("blender-launcher-server")
    is_running = socket.waitForConnected()
    if is_running:
        socket.write(QByteArray(version.encode()))
        socket.waitForBytesWritten()
        socket.close()
        sys.exit()


if __name__ == "__main__":
    main()
