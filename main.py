import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class MainWindow(QMainWindow):
    g_map: QLabel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('main_window.ui', self)
        self.press_delta = 0.5
        self.points = []
        self.map_zoom = 5
        self.map_ll = [37.977751, 55.757718]
        self.map_l = 'map'
        self.map_key = ''
        self.cords = ''
        self.refresh_map()
        self.radioButton.toggled.connect(self.refresh_map)
        self.button.clicked.connect(self.find)
        self.dell.clicked.connect(self.delete_point)

    def delete_point(self):
        self.cords = ''
        self.refresh_map()


    def find(self):
        geocode = self.lineEdit.text()
        API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
        server_address = "http://geocode-maps.yandex.ru/1.x/?"
        request = f'{server_address}apikey={API_KEY}&geocode={geocode}&format=json'
        ll = requests.get(request).json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['boundedBy'][
        'Envelope']['lowerCorner']
        self.map_ll = [float(i) for i in ll.split()]
        self.cords = self.map_ll[:]
        self.refresh_map()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp and self.map_zoom < 17:
            self.map_zoom += 1
        if event.key() == Qt.Key_PageDown and self.map_zoom > 0:
            self.map_zoom -= 1
        if event.key() == Qt.Key_Up:
            self.map_ll[1] += self.press_delta

        if event.key() == Qt.Key_Down:
            self.map_ll[1] -= self.press_delta

        if event.key() == Qt.Key_Left:
            self.map_ll[0] -= self.press_delta

        if event.key() == Qt.Key_Right:
            self.map_ll[0] += self.press_delta

        self.refresh_map()

    def refresh_map(self):
        t = 'dark' if self.radioButton.isChecked() else 'light'
        map_params = {
            "ll": ','.join(map(str, self.map_ll)),
            "l": self.map_l,
            'z': self.map_zoom,
            'pt': f"{','.join(map(str, self.map_ll))},pmgrs"
        }
        session = requests.Session()
        retry = Retry(total=10, connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        n = ','.join(map(str, self.map_ll))
        point = f"{','.join(map(str, self.cords))}"
        print(point)
        if self.cords:
            d = f"https://static-maps.yandex.ru/v1?ll={n}&l={self.map_l}&z={self.map_zoom}&theme={t}&apikey=f3a0fe3a-b07e-4840-a1da-06f18b2ddf13&pt={point},pm2rdm"
        else:
            d = f"https://static-maps.yandex.ru/v1?ll={n}&l={self.map_l}&z={self.map_zoom}&theme={t}&apikey=f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
        response = session.get(d)
        with open('tmp.png', mode='wb') as tmp:
            tmp.write(response.content)

        pixmap = QPixmap()
        pixmap.load('tmp.png')
        self.g_map.setPixmap(pixmap)


def clip(v, _min, _max):
    if v < _min:
        return _min
    if v > _max:
        return _max
    return v


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
