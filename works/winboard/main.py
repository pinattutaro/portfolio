import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, Signal, Slot
import winsound
import threading
import numpy as np
import sounddevice as sd
import json


current_thread = None
stop_flag = threading.Event()

with open("piano.html", encoding="utf8") as f:
    html = f.read()

notes = {
    "C": 261,
    "C#": 277,
    "D": 293,
    "D#": 311,
    "E": 329,
    "F": 349,
    "F#": 370, 
    "G": 392,
    "G#": 415,
    "A": 440,
    "A#": 466,
    "B": 493
}

sample_rate = 44100
duration = 0.5  # 最大1秒再生（途中でキャンセルされる可能性あり）

def play_sound(freq, vol):
    """指定した周波数の音を再生"""
    global stop_flag

    # サイン波を生成
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * freq * t) * 0.5
    wave = wave * vol
    wave = wave.astype(np.float32)

    # 停止フラグをリセット
    stop_flag.clear()

    # 音を再生（別スレッドから停止可能）
    stream = sd.OutputStream(samplerate=sample_rate, channels=1, blocksize=256)
    stream.start()
    for i in range(len(wave)):
        if stop_flag.is_set():
            break
        stream.write(wave[i:i+1])
    stream.stop()
    stream.close()

# Python と JavaScript 間の通信を行うクラス
class Bridge(QObject):
    text_received = Signal(str)

    @Slot(str)
    def receive_text(self, text):
        print(f"Pythonで受信: {text}")
        self.text_received.emit(text)


app = QApplication(sys.argv)

# メインウィンドウの設定
window = QWidget()
window.resize(800, 400)
window.setWindowTitle("pythonﾊｽｺﾞｲﾖｰ")
layout = QVBoxLayout()

# WebEngineView の作成
web_view = QWebEngineView()

# JavaScript と Python を接続するためのブリッジ
bridge = Bridge()
channel = QWebChannel()
channel.registerObject("bridge", bridge)
web_view.page().setWebChannel(channel)

# HTML コンテンツ

html_content = html

# HTML を WebEngineView にセット
web_view.setHtml(html_content)

# レイアウトに WebView を追加
layout.addWidget(web_view)
window.setLayout(layout)

# Python 側で受信したデータを処理
def handle_text_received(text):
    data = json.loads(text)
    global current_thread, stop_flag
    stop_flag.set()
    if current_thread and current_thread.is_alive():
        current_thread.join()  # スレッドが終了するのを待つ

    # 新しいスレッドで音を鳴らす
    current_thread = threading.Thread(target=play_sound, args=(notes[data["tone"]],data["volume"],))
    current_thread.start()

bridge.text_received.connect(handle_text_received)

# ウィンドウの表示
window.show()
sys.exit(app.exec())
