from kivy.app import App
#from kivymd.app import MDApp

import cv2 #analyza obrazku

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture #zobrazeni kamery

from pyzbar.pyzbar import decode #detekce caroveho kodu

#from kivy.utils import platform
from collections import Counter #pro hledani nejcetnejsiho kodu

#from kivy.uix.button import Button
#from kivy.lang import Builder


KV = '''
MDBoxLayout:
    orientation: "vertical"
    padding: dp(10)
    spacing: dp(10)
    md_bg_color: app.theme_cls.bg_light  # Set background color

    MDIconButton:
        icon: "keyboard"
        size_hint: None, None
        size: dp(56), dp(56)  # Set size for the icon button
        pos_hint: {"center_x": .5}
        on_press: app.on_icon_button_press()
'''

class BarcodeScannerApp(App):
    def build(self):
        #promenne
        self.barcode = 0
        self.barcode_detected_array = []
        self.img = Image()

        #vse ohledne tlacitka

        #zacatek videa/jednotlivych snimku
        self.capture = cv2.VideoCapture(0)

        #nastaveni rozliseni videa
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 960) #sirka
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 576) #vyska

        #obnovovací frekvence 30 fps
        Clock.schedule_interval(self.update, 1.0 / 30.0)

        return self.img

    def update(self, dt):
        #ulozi jeden snimek
        ret, frame = self.capture.read()

        #pokud je snimek zachycen uspesne
        if ret:
            #detekce caroveho kodu
            decoded_objects = decode(frame)

            #pro kazdy carovy kod vypise jeho cislo
            for i in decoded_objects:
                print("Detected: ", i.data.decode())
                self.barcode_detected_array.append(i.data.decode())

            #samply detekce caroveho kodu
            if len(self.barcode_detected_array)>=10:
                print("deset")

                #spracovani detekovanych kodu
                array_Counter = Counter(self.barcode_detected_array)

                #najde nejcetnejsi carovy kod z 10 mereni
                self.barcode = array_Counter.most_common(1)[0]

                print(f"nejcetnejsi nactena hodnota: {self.barcode}")

                #vymaze pola detekovanych carovych kodu
                self.barcode_detected_array.clear()

                #prestane detekovat carove kody po zmereni
                self.capture.release()

            #uprava snimku aby nebyl prevraceny
            buf = cv2.flip(frame, -1).tobytes()

            #vytvoreni textury
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')

            #nacteni textury
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            #zobrazeni textury
            self.img.texture = texture

    def on_elevated_button_press(self):
        print("Elevated button pressed!")

    def on_stop(self):
        self.capture.release()  # pokud je kamera nedostupna program se ukonci

#hlavní "loop"
if __name__ == "__main__":
    BarcodeScannerApp().run()