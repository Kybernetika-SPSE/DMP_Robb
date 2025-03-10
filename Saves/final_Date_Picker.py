from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.stacklayout import StackLayout
from kivymd.uix.label import MDLabel
from kivy.uix.popup import Popup
from datetime import datetime
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from datetime import date
import calendar
from kivy.uix.gridlayout import GridLayout


class MyDatePicker(Popup):
    def __init__(self, callback,  **kwargs):
        super().__init__(**kwargs)

        #graficke parametry popoutu
        self.title = "Select Date"
        self.size_hint = (1, 1)
        self.background_color = (1, 1, 1, 0)
        self.spacing = [0,0,0,0]
        self.padding = [-20,0,0,0]
        self.input_day_array = []

        #definovani promennych a funkci, ktere jsou globalni ve teto tride
        self.output_day_array = []
        self.callback = callback

        #ziskani dnestniho data
        self.displayed_month = datetime.now().month
        self.displayed_year = datetime.now().year
        self.month_dict = {
            1: "Leden", 2: "Únor", 3: "Březen", 4: "Duben", 5: "Květen", 6: "Červen",
            7: "Červenec", 8: "Srpen", 9: "Září", 10: "Říjen", 11: "Listopad", 12: "Prosinec"
        }

        #zavilani funkce sestrojeni UI
        self.create_ui()

    def create_ui(self):
        #sestrojeni popoutu
        main_layout = StackLayout(
            orientation='tb-lr',
            size_hint=(1, None),
            height=600,
            padding=[10, 10],
            spacing=30,
            pos_hint={'top': 1}
        )

        #zobrazeni aktualniho mesice
        self.label1 = MDLabel(
            text=f"{self.month_dict[self.displayed_month]} {self.displayed_year}",
            halign='center',
            size_hint_y=None,
            height=30,
            font_style='Subtitle1',
            size_hint_x=1,
            theme_text_color='Custom',
            text_color=(0.2, 0.6, 0.8, 1)
        )

        main_layout.add_widget(self.label1)

        #vytvoreni layoutu pro zmenu mesice
        month_change_layout_container = AnchorLayout(anchor_x='center', size_hint=(1, None), height=40)
        month_change_layout = MDBoxLayout(orientation='horizontal', size_hint=(None, None), width=170, spacing=5, height=40)

        #definovani tlacitek pro zmenu mesice
        month_add = MDRaisedButton(text=">", size_hint=(None, None), size=(40, 40))
        month_subtract = MDRaisedButton(text="<", size_hint=(None, None), size=(40, 40))
        month_add.bind(on_press=self.change_date)
        month_subtract.bind(on_press=self.change_date)

        #pridani tlacitech pro zmenu mesice do layoutu
        month_change_layout.add_widget(month_subtract)
        month_change_layout.add_widget(month_add)
        #vystredení layoutu pro zmenu mesice
        month_change_layout_container.add_widget(month_change_layout)
        main_layout.add_widget(month_change_layout_container)

        self.selected_dates_displayed_layout = MDBoxLayout(
            orientation='horizontal', size_hint=(1, None), size=(300, 40), spacing=5, padding=[5, 0, 0, 0]
        )
        main_layout.add_widget(self.selected_dates_displayed_layout)

        date_layout_container = AnchorLayout(anchor_x='center', size_hint=(1, None), height=300)
        self.date_layout = GridLayout(cols=5, spacing=5, padding=[0, 10, 30, 10], size_hint_y=None)
        self.date_layout.bind(minimum_height=self.date_layout.setter('height'))

        self.generate_date_buttons()
        date_layout_container.add_widget(self.date_layout)
        main_layout.add_widget(date_layout_container)

        #definovani save a cancel tlacitek
        save_button = MDRaisedButton(text="Save")
        save_button.bind(on_press=self.save)

        cancel_button = MDRaisedButton(text="Cancel")
        cancel_button.bind(on_press=self.cancel)

        #zobrazenovani save a cancel tlacitek
        save_cancel_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        save_cancel_layout.add_widget(cancel_button)
        save_cancel_layout.add_widget(save_button)
        main_layout.add_widget(save_cancel_layout)

        self.add_widget(main_layout)

    def generate_date_buttons(self):
        #generuje tlacitka pro vyber expiracnich dat
        self.date_layout.clear_widgets()
        for i in range(1, calendar.monthrange(self.displayed_year, self.displayed_month)[1] + 1):
            btn_text = f"{i}"
            button = MDRaisedButton(text=btn_text, size_hint=(None, None), size=(200, 40))
            button.bind(on_press=self.date_buttons_callback)
            self.date_layout.add_widget(button)

    def open_date_picker(self):
        self.open()

    def change_date(self, instance):
        if instance.text == ">":
            if self.displayed_month == 12:
                self.displayed_month = 1
                self.displayed_year += 1
            else:
                self.displayed_month += 1
        else:
            if self.displayed_month == 1:
                self.displayed_month = 12
                self.displayed_year -= 1
            else:
                self.displayed_month -= 1

        self.label1.text = f"{self.month_dict[self.displayed_month]} {self.displayed_year}"
        self.generate_date_buttons()

    def date_buttons_callback(self, instance):
        year = self.displayed_year
        month = self.displayed_month
        day = int(instance.text)
        selected_date = date(year, month, day)
        self.input_day_array.append(selected_date)

        btn_text = f"{day}.{month}.{str(year)[2:]}"

        selected_date_button = MDRaisedButton(text=btn_text)
        selected_date_button.value = selected_date
        selected_date_button.bind(on_press=self.delete_selected_dates)
        self.selected_dates_displayed_layout.add_widget(selected_date_button)

    def delete_selected_dates(self, instance):
        self.input_day_array.remove(instance.value)
        self.selected_dates_displayed_layout.remove_widget(instance)

    def save(self, instance):
        #print(f"Saved values: {self.input_day_array}")
        self.output_day_array = self.input_day_array
        self.dates_picked(self.output_day_array)
        #self.close_callback()
        self.dismiss()

    def close_self(self):
        self.dismiss()

    def cancel(self, instance):
        self.input_day_array.clear()
        self.selected_dates_displayed_layout.clear_widgets()
        self.dismiss()

    def dates_picked(self, exp_dates):
        self.dates = exp_dates
        print("dates picked successfully")
        self.callback(self.dates)


