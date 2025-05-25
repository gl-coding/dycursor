import sys
import pyautogui
import threading
import time
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import QTimer, Qt, QEvent

SETTINGS_FILE = "settings.json"

class MouseControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("鼠标控制器")
        self.setGeometry(0, 0, 500, 200)  # 启动时放在屏幕左上角 (0,0)

        # 输入框
        self.left_input = QLineEdit("10")
        self.right_input = QLineEdit(str(pyautogui.size().width - 10))
        self.y_input = QLineEdit(str(pyautogui.size().height // 2))
        self.scroll_input = QLineEdit("-10")  # 新增滚轮滑动值输入框

        self.load_settings()  # 加载本地设置

        # 按钮
        self.move_btn = QPushButton("执行鼠标动作")
        self.move_btn.clicked.connect(self.on_move_mouse)

        # 坐标显示
        self.coord_label = QLabel("当前鼠标坐标: x=0, y=0")

        # 布局
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("左边X:"))
        h_layout.addWidget(self.left_input)
        h_layout.addWidget(QLabel("右边X:"))
        h_layout.addWidget(self.right_input)
        h_layout.addWidget(QLabel("Y:"))
        h_layout.addWidget(self.y_input)
        h_layout.addWidget(QLabel("滚轮滑动值:"))
        h_layout.addWidget(self.scroll_input)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.move_btn)
        v_layout.addWidget(self.coord_label)
        self.setLayout(v_layout)

        # 定时器实时刷新坐标
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_mouse_position)
        self.timer.start(50)

        self.stop_flag = False
        self.installEventFilter(self)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.left_input.setText(str(data.get("left_x", "10")))
                    self.right_input.setText(str(data.get("right_x", str(pyautogui.size().width - 10))))
                    self.y_input.setText(str(data.get("y", str(pyautogui.size().height // 2))))
                    self.scroll_input.setText(str(data.get("scroll", "-10")))
            except Exception as e:
                print("加载设置失败：", e)

    def save_settings(self):
        data = {
            "left_x": self.left_input.text(),
            "right_x": self.right_input.text(),
            "y": self.y_input.text(),
            "scroll": self.scroll_input.text()
        }
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print("保存设置失败：", e)

    def update_mouse_position(self):
        x, y = pyautogui.position()
        self.coord_label.setText(f"当前鼠标坐标: x={x}, y={y}")

    def on_move_mouse(self):
        try:
            start_x = int(self.left_input.text())
            end_x = int(self.right_input.text())
            y = int(self.y_input.text())
            scroll_value = int(self.scroll_input.text())
        except ValueError:
            self.coord_label.setText("请输入有效的数字！")
            return

        self.save_settings()  # 保存设置
        self.stop_flag = False  # 每次开始前重置
        threading.Thread(target=self.move_mouse, args=(start_x, end_x, y, scroll_value), daemon=True).start()

    def move_mouse(self, start_x, end_x, y, scroll_value):
        pyautogui.moveTo(986, 55, duration=0.5)
        pyautogui.click()
        time.sleep(0.5)

        pyautogui.moveTo(start_x, y, duration=0.5)
        time.sleep(0.5)

        for i in range(1000):
            if self.stop_flag:
                break
            pyautogui.moveTo(end_x, y, duration=5)
            time.sleep(0.5)
            pyautogui.scroll(scroll_value)

            if self.stop_flag:
                break
            pyautogui.moveTo(start_x, y, duration=5)
            time.sleep(0.5)
            pyautogui.scroll(scroll_value)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.stop_flag = True
            self.coord_label.setText("已停止鼠标控制（按下ESC）")
            return True
        return super().eventFilter(obj, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MouseControlApp()
    window.show()
    sys.exit(app.exec_()) 