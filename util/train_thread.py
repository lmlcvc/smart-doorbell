from PyQt5.QtCore import QThread, pyqtSignal


class TrainThread(QThread):
    training_finished = pyqtSignal()

    def __init__(self, train_model):
        super().__init__()
        self.train_model = train_model

    def run(self):
        self.train_model.train()
        self.training_finished.emit()
        self.exit()