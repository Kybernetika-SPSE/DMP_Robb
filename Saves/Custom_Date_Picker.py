from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from datetime import datetime
from kivy.app import App
import calendar
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivymd.app import MDApp

KV = '''
MDBoxLayout:
    orientation: 'vertical'    
    ToggleButton:
        font_size: 12
        on_release: app.root.current = "other"
        size: 75, 50
        size_hint: None, None # <---

Label:
    font_size: 30
'''

class Layout(GridLayout):
    def __init__(self, **kwargs):
        self.input_day_array = []

        self.month_add = Button(text="Next Month")
        self.month_subtract = Button(text="Previous Month")

        #save and cancel button
        self.save_button = Button(text="Save")
        self.save_button.bind(on_press=self.save)

        self.cancel_button = Button(text="Cancel")
        self.cancel_button.bind(on_press=self.cancel)

        # pri stisknuti tlacitka zmeni mesic
        self.month_add.bind(on_press=self.change_month)
        self.month_subtract.bind(on_press=self.change_month)

        # zobrazeni minulych nebo budoucich mesicu
        self.displayed_month = datetime.now().month
        self.displayed_year = datetime.now().year
        month_dict = {1: "Leden", 2: "Únor", 3: "Březen", 4: "Duben", 5: "Květen", 6: "Červen", 7: "Červenec",
                      8: "Srpen", 9: "Září", 10: "Říjen", 11: "Listopad", 12: "Prosinec"}

        #self.month_heading = Label(Text=month_dict[self.displayed_month])
        super(Layout, self).__init__(**kwargs)
        self.rows = 1
        self.label1 = Label(text=month_dict[self.displayed_month], font_size=30)
        self.add_widget(self.label1)

        self.add_widget(self.save_button)
        self.add_widget(self.cancel_button)

        super(Layout, self).__init__(**kwargs)
        self.rows = 3

        # pridani widgetu na obrazovku
        self.add_widget(self.month_add)
        self.add_widget(self.month_subtract)

        #pro dynamicke tvoreni tlacitek podle poctu dni v zobrazenem mesici na obrazovce
        dates = {}
        for i in range(1,calendar.monthrange(self.displayed_year,self.displayed_month)[1]+1):
            btn_text = f"{i}"
            self.button = ToggleButton(text=btn_text)
            self.add_widget(self.button)
            self.button.bind(on_press=self.callback)

    def callback(self,instance):
        if instance.state=='down':
            print(f"{instance.text} is down")
            self.input_day_array.append(instance.text)
        if instance.state=='normal':
            self.input_day_array.remove(instance.text)
        print(f"{self.input_day_array}")


    def save(self, instance):
        print(f"save:{self.input_day_array}")


    def cancel(self, instance):
        self.input_day_array = []
        print("cancel")

    def change_month(self,instance):
        if instance.text == "Next Month":
            print(f"{instance.text} was pressed!")
            if self.displayed_month == 12:
                self.displayed_month = 1
                self.displayed_year = datetime.now().year + 1
            else:
                self.displayed_month = self.displayed_month + 1
        else:
            print(f"{instance.text} was pressed!")
            if self.displayed_month == 1:
                self.displayed_month = 12
                self.displayed_year = datetime.now().year - 1

            else:
                self.displayed_month = self.displayed_month - 1
        print(self.displayed_month)

class MyApp(App):
    def build(self):
        return Layout()

if __name__ == '__main__':
    MyApp().run()