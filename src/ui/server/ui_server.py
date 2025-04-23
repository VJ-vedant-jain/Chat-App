from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QSpinBox,
    QPushButton, QTextEdit, QLineEdit, QVBoxLayout, QHBoxLayout,
    QListWidget
)
from PyQt5.QtCore import Qt

class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chat Server")
        self.setGeometry(100, 100, 1500, 600)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)

        main_layout = QHBoxLayout()
        outer_layout.addLayout(main_layout)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        control_layout = QHBoxLayout()
        port_label = QLabel("Port:", self)
        control_layout.addWidget(port_label)

        self.port_input = QSpinBox(self)
        self.port_input.setRange(1024, 65535)
        self.port_input.setValue(9090)
        control_layout.addWidget(self.port_input)

        self.start_button = QPushButton("Start Server", self)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Server", self)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        self.status_label = QLabel("Status: Not Running", self)
        self.status_label.setStyleSheet("QLabel { color: red; }")
        control_layout.addWidget(self.status_label)

        left_layout.addLayout(control_layout)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        left_layout.addWidget(self.log_display)

        main_layout.addWidget(left_panel, 2)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        labels_layout = QHBoxLayout()
        users_label = QLabel("Connected Users", self)
        users_label.setAlignment(Qt.AlignCenter)
        chat_label = QLabel("Chat Log", self)
        chat_label.setAlignment(Qt.AlignCenter)

        labels_layout.addWidget(users_label, 1)
        labels_layout.addWidget(chat_label, 2)
        right_layout.addLayout(labels_layout)

        users_chat_layout = QHBoxLayout()
        users_chat_layout.setSpacing(20)
        self.users_list = QListWidget()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        users_chat_layout.addWidget(self.users_list, 1)
        users_chat_layout.addWidget(self.chat_display, 2)

        right_layout.addLayout(users_chat_layout)

        main_layout.addWidget(right_panel, 3)

        cmd_layout = QHBoxLayout()
        cmd_label = QLabel("Command:", self)
        cmd_layout.addWidget(cmd_label)

        self.cmd_input = QLineEdit(self)
        cmd_layout.addWidget(self.cmd_input)

        self.cmd_button = QPushButton("Execute", self)
        cmd_layout.addWidget(self.cmd_button)

        outer_layout.addLayout(cmd_layout)
