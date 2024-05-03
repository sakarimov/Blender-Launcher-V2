cd..
ls

if exist __pycache__ rd /S /Q __pycache__
if exist build rd /S /Q build
if exist "dist/release" rd /S /Q "dist/release"
if exist "Blender Launcher.spec" del /Q "Blender Launcher.spec"

python -OO -m PyInstaller ^
--hidden-import "pynput.keyboard._win32" ^
--hidden-import "pynput.mouse._win32" ^
--clean ^
--noconsole ^
--noupx ^
--onefile ^
--windowed ^
--icon="source\resources\icons\bl\bl.ico" ^
--name="Blender Launcher" ^
--version-file="version.txt" ^
--add-binary="source\resources\icons\winblender.ico;files" ^
--add-binary="source\resources\certificates\custom.pem;files" ^
--distpath="./dist/release" ^
source\main.py
