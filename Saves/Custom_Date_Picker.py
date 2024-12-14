from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
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


'''

class Layout(GridLayout):
    def __init__(self, **kwargs):
        self.input_day_array = []
        self.output_day_array = []

        self.displayed_month = datetime.now().month
        self.displayed_year = datetime.now().year

        #slovnik pro prevedeni poradi na nazev mesice
        self.month_dict = {1: "Leden", 2: "Únor", 3: "Březen", 4: "Duben", 5: "Květen", 6: "Červen", 7: "Červenec",
                           8: "Srpen", 9: "Září", 10: "Říjen", 11: "Listopad", 12: "Prosinec"}

        #self.month_heading = Label(Text=month_dict[self.displayed_month])
        super().__init__(**kwargs)
        self.cols = 1

        #inicializace textu zobrazujiciho rok a mesic, ve kterem se vybiraji data
        self.label1 = Label(text=f"{self.month_dict[self.displayed_month]} {self.displayed_year}", font_size=30)
        #self.label2 = Label(text=str(self.displayed_year), font_size=30)

        #inicializace layutu pro zobrazeni mesice a roku
        self.header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        #pridani textu na obrazovku
        self.header_layout.add_widget(self.label1)
        #self.header_layout.add_widget(self.label2)
        #pridani header layoutu na obrazovku
        self.add_widget(self.header_layout)

        #inicializace tlacitek pro meneni mesice a roku
        self.month_add = Button(text="Next Month")
        self.month_subtract = Button(text="Previous Month")
        #----------------
        self.year_add = Button(text="Next Year")
        self.year_subtract = Button(text="Previous Year")

        #inicializace tlacitek pro ulozeni vyberu a zruseni
        self.save_button = Button(text="Save")
        self.save_button.bind(on_press=self.save)
        #----------------
        self.cancel_button = Button(text="Cancel")
        self.cancel_button.bind(on_press=self.cancel)

        #pri stisknuti tlacitka zmeni mesic
        self.month_add.bind(on_press=self.change_date)
        self.month_subtract.bind(on_press=self.change_date)

        #vytvoreni layoutu pro navigaci v kalendari
        self.navigation_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        #pridani tlacitek pro meneni mesicu na obrazovku
        self.navigation_layout.add_widget(self.month_subtract)
        self.navigation_layout.add_widget(self.month_add)
        #pridani navigacniho layoutu na obrazovku
        self.add_widget(self.navigation_layout)

        self.date_layout = GridLayout(cols=7, spacing=10, padding=10)
        #dynamicke tvoreni tlacitek podle poctu dni v zobrazenem mesici
        for i in range(1,calendar.monthrange(self.displayed_year,self.displayed_month)[1]+1):
            self.btn_text = f"{i}"
            self.button = ToggleButton(text=self.btn_text)
            self.button.bind(on_press=self.callback)
            self.date_layout.add_widget(self.button)
        self.add_widget(self.date_layout)

        self.save_cancel_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        #pridani tlacitek pro ulozeni nebo zruseni na obrazovku
        self.save_cancel_layout.add_widget(self.cancel_button)
        self.save_cancel_layout.add_widget(self.save_button)
        #pridani layoutu na obrazovku
        self.add_widget(self.save_cancel_layout)

    def delete_date_buttons(self):
        #vymazani predeslich tlacitek pro vyber data
        for child in self.date_layout.children[:]:
            if isinstance(child, Button) and child.text in [str(i) for i in range(1, 32)]:
                self.date_layout.remove_widget(child)

    def change_date(self, instance):
        #vymazani predeslich tlacitek
        self.delete_date_buttons()

        #vymazani predelsleho zobrazeneho mesice a roku
        self.header_layout.remove_widget(self.label1)
        #self.header_layout.remove_widget(self.label2)

        #meneni mesice podle stisknuteho tlacitka
        if instance.text == "Next Month":
            #pokud je stisknute tlacitko "Next Month"

            #pokud je 12 mesic musi byt dalsi mesic 1
            if self.displayed_month == 12:
                self.displayed_month = 1
                self.displayed_year += 1
            else:
                self.displayed_month = self.displayed_month + 1
        else:
            #pokud je stisknute jine tlacitko
            #pokud je zobrazen 1. mesic tak predchozi musi byt 12. mesic
            if self.displayed_month == 1:
                self.displayed_month = 12
                self.displayed_year = self.displayed_year - 1
            else:
                self.displayed_month = self.displayed_month - 1

        self.label1 = Label(text=f"{self.month_dict[self.displayed_month]} {self.displayed_year}", font_size=30)
        #self.label2 = Label(text=str(self.displayed_year), font_size=30)
        self.header_layout.add_widget(self.label1)
        #self.header_layout.add_widget(self.label2)

        for i in range(1,calendar.monthrange(self.displayed_year,self.displayed_month)[1]+1):
            btn_text = f"{i}"
            self.button = ToggleButton(text=btn_text)
            self.button.bind(on_press=self.callback)
            self.date_layout.add_widget(self.button)


    def callback(self,instance):
        if instance.state=="down":

            year = int(self.displayed_year)
            month = int(self.displayed_month)
            day = int(instance.text)

            #print(f"{instance.text} is down")
            #print(f"year:{year}")
            # print(f"month:{month}")
            #print(f"day:{day}")
            self.input_day_array.append(date( year, month, day))
            
        if instance.state=="normal":
            self.input_day_array.remove(instance.text)
        #print(f"{self.input_day_array}")


    def save(self,instance):
        print(f"save:{self.input_day_array}")
        self.output_day_array = self.input_day_array


    def cancel(self,instance):
        self.input_day_array = []  #vymaze vsechny
        for child in self.date_layout.children:  # iteruje mezi vsemi widgety v layoutu
            if isinstance(child, ToggleButton):  # pokud je widget ToggleButton tak ho hodi do normalniho nestlaceneho modu
                child.state = 'normal'


class MyApp(App):
    def build(self):
        return Layout()

if __name__ == '__main__':
    MyApp().run()