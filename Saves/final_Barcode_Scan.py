from cv2 import VideoCapture, flip, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from pyzbar.pyzbar import decode
from collections import Counter
from kivy.lang import Builder
from kivy.clock import Clock

KV = '''
MDBoxLayout:
    orientation: "vertical"
    padding: dp(10)
    spacing: dp(10)

    Image:
        id: camera_image  # Ensure this ID exists
        size_hint_y: None
        height: dp(400)

    MDIconButton:
        icon: "cancel"
        size_hint: None, None
        size: dp(56), dp(56)
        pos_hint: {'center_x': .5, 'center_y': .5}
        on_press: app.barcode_scanner.close_self()
'''

class BarcodeScannerApp(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Barcode Scanner"
        self.size_hint = (1, 1)  #fulscreen popout
        self.auto_dismiss = True
        self.background_color = (1, 1, 1, 0)

        #kv string
        self.content = Builder.load_string(KV)

        self.barcode = None
        self.callback = callback

        self.barcode_detected_array = []
        self.product_info = []
        self.capture = VideoCapture(0)
        self.capture.set(CAP_PROP_FRAME_WIDTH, 960)
        self.capture.set(CAP_PROP_FRAME_HEIGHT, 576)
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def scan_complete(self, scanned_code):
        self.barcode = scanned_code
        self.callback(self.barcode)

    def open_barcode_scanner(self):
        self.open()

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            #detekce carovych kodu
            decoded_objects = decode(frame)
            for obj in decoded_objects:
                barcode_data = obj.data.decode()
                self.barcode_detected_array.append(barcode_data)

            buf = flip(frame, -1).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            # Update feedu kamery
            if "camera_image" in self.content.ids:
                self.content.ids.camera_image.texture = texture

            # Samplovani carovych kodu
            if len(self.barcode_detected_array) >= 10:
                array_counter = Counter(self.barcode_detected_array)
                self.barcode = array_counter.most_common(1)[0][0]
                self.scan_complete(self.barcode)
                self.barcode_detected_array.clear()
                self.close_self()

    def close_self(self):

        self.capture.release()
        self.dismiss()

# Example usage inside a Kivy app
#class HlavniApka(MDApp):
#    def build(self):
#        BarcodeScannerApp().open_barcode_scanner()
#
#    def show_barcode_popup(self):
#        self.popup = BarcodeScannerApp()
#        self.popup.open_barcode_scanner()