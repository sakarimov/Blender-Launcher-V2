import logging
from subprocess import Popen

from PyQt5.QtCore import QThread, pyqtSignal

logger = logging.getLogger()


class Observer(QThread):
    count_changed = pyqtSignal(int)
    append_proc = pyqtSignal(Popen)

    def __init__(self, parent):
        QThread.__init__(self)
        self.parent = parent
        self.processes: list[Popen] = []
        self.append_proc.connect(self.handle_append_proc)

    def run(self):
        old_proc_count = len(self.processes)
        while self.parent:
            for proc in self.processes:
                if proc.poll() is not None:
                    logger.debug(f"Process {proc.args} exited with code {proc.returncode}")
                    proc.terminate()
                    self.processes.remove(proc)

            if (p := len(self.processes)) != old_proc_count:
                self.count_changed.emit(p)
                old_proc_count = p
                if p == 0:
                    break

            QThread.sleep(1)

    def handle_append_proc(self, proc):
        self.processes.append(proc)
        self.count_changed.emit(len(self.processes))
