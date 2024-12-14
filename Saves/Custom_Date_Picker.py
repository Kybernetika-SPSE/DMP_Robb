from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from datetime import datetime,date
from kivy.app import App
import calendar
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
#from kivymd.app import MDApp

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

        self.displayed_month = datetime.now().month
        self.displayed_year = datetime.now().year
        print(f"{self.displayed_month}")

        #slovnik pro prevedeni poradi na nazev mesice
        self.month_dict = {1: "Leden", 2: "Únor", 3: "Březen", 4: "Duben", 5: "Květen", 6: "Červen", 7: "Červenec",
                           8: "Srpen", 9: "Září", 10: "Říjen", 11: "Listopad", 12: "Prosinec"}

        #self.month_heading = Label(Text=month_dict[self.displayed_month])
        super(Layout, self).__init__(**kwargs)
        self.rows = 1

        #inicializace textu zobrazujiciho rok a mesic, ve kterem se vybiraji data
        self.label1 = Label(text=self.month_dict[self.displayed_month], font_size=30)
        self.label2 = Label(text=str(self.displayed_year), font_size=30)

        #pridani textu na obrazovku
        self.add_widget(self.label1)
        self.add_widget(self.label2)

        #inicializace tlacitek pro meneni mesice a roku
        self.month_add = Button(text="Next Month")
        self.month_subtract = Button(text="Previous Month")
        self.year_add = Button(text="Next Year")
        self.year_subtract = Button(text="Previous Year")

        #inicializace save a cancel tlacitek
        self.save_button = Button(text="Save")
        self.save_button.bind(on_press=self.save)
        self.cancel_button = Button(text="Cancel")
        self.cancel_button.bind(on_press=self.cancel)

        # pri stisknuti tlacitka zmeni mesic
        self.month_add.bind(on_press=self.change_date)
        self.month_subtract.bind(on_press=self.change_date)
        #self.year_add.bind(on_press=self.change_year)
        #self.year_subtract.bind(on_press=self.change_year)

        #layout start
        super(Layout, self).__init__(**kwargs)
        self.rows = 3

        #pridani tlacitek pro ulozeni nebo zruseni na obrazovku
        self.add_widget(self.save_button)
        self.add_widget(self.cancel_button)

        #pridani tlacitek pro meneni mesicu na obrazovku
        self.add_widget(self.month_add)
        self.add_widget(self.month_subtract)

        #dynamicke tvoreni tlacitek podle poctu dni v zobrazenem mesici
        for i in range(1,calendar.monthrange(self.displayed_year,self.displayed_month)[1]+1):
            self.btn_text = f"{i}"
            self.button = ToggleButton(text=self.btn_text)
            self.add_widget(self.button)
            self.button.bind(on_press=self.callback)


    def delete_date_buttons(self):
        #vymazani predeslich tlacitek pro vyber data
        for child in self.children[:]:
            if isinstance(child, Button) and child.text in [str(i) for i in range(1, 32)]:
                self.remove_widget(child)


    def change_date(self, instance):
        self.delete_date_buttons()

        self.remove_widget(self.label1)
        self.remove_widget(self.label2)

        if instance.text == "Next Month":

            if self.displayed_month == 12:
                self.displayed_month = 1
                self.displayed_year += 1
            else:
                self.displayed_month = self.displayed_month + 1
        else:

            if self.displayed_month == 1:
                self.displayed_month = 12
                self.displayed_year = datetime.now().year - 1
            else:
                self.displayed_month = self.displayed_month - 1

        self.label1 = Label(text=self.month_dict[self.displayed_month], font_size=30)
        self.label2 = Label(text=str(self.displayed_year), font_size=30)

        self.add_widget(self.label1)
        self.add_widget(self.label2)

        for i in range(1,calendar.monthrange(self.displayed_year,self.displayed_month)[1]+1):
            btn_text = f"{i}"
            self.button = ToggleButton(text=btn_text)
            self.add_widget(self.button)
            self.button.bind(on_press=self.callback)


    def callback(self,instance):
        if instance.state=="down":
            print(f"{instance.text} is down")
            year = (self.displayed_year)
            print(f"year:{year}")
            month = int(self.displayed_month)
            print(f"month:{month}")
            day = int(instance.text)
            print(f"day:{day}")
            self.input_day_array.append(date( year, month, day))
            
        if instance.state=="normal":
            self.input_day_array.remove(instance.text)
        #print(f"{self.input_day_array}")


    def save(self,instance):
        print(f"save:{self.input_day_array}")
        self.output_day_array = self.input_day_array


    def cancel(self,instance):
        self.input_day_array = []  #vymaze vsechny
        for child in self.children:  # iteruje mezi vsemi widgety v layoutu
            if isinstance(child, ToggleButton):  # pokud je widget ToggleButton tak ho hodi do normalniho nestlaceneho modu
                child.state = 'normal'


class MyApp(App):
    def build(self):
        return Layout()

if __name__ == '__main__':
    MyApp().run()