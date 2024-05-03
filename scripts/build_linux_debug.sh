cd..
PYTHONOPTIMIZE=2 pyinstaller \
--hidden-import "pynput.keyboard._xorg" \
--hidden-import "pynput.mouse._xorg" \
--hidden-import "python-xlib" \
--clean \
--noconsole \
--noupx \
--onefile \
--debug=all \
--name="Blender Launcher" \
--add-binary="source/resources/certificates/custom.pem:files" \
--distpath="./dist/debug" \
source/main.py
