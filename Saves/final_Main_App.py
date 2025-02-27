from kivy.uix.anchorlayout import AnchorLayout
from kivymd.app import MDApp
from kivymd.uix.filemanager.filemanager import IconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton
from kivymd.uix.toolbar import MDTopAppBar
from kivy.core.window import Window
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivymd.uix.list import MDList
#from datetime import date,datetime
import mysql.connector as database
from final_Date_Picker import MyDatePicker
from kivy.uix.screenmanager import Screen, ScreenManager
from final_Barcode_Scan import BarcodeScannerApp
from final_product_Handling import upload_product_to_database
from time import sleep
from kivy.clock import Clock

conn = database.connect(host="localhost",
                        user="root",
                        passwd="AhOj159/*@",
                        database="food_schem",
                        )

cursor = conn.cursor()

Window.size = (360, 600)

if cursor:
    print("Connected to MySQL database")

class Content(MDBoxLayout):
    def __init__(self, items, id, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None

        self.id = id

        # prizpusobeni vysky podle poctu dat expirace
        self.dates_array = items
        self.items = len(items)
        self.height = dp(35 * self.items) #old dp 48

        for i in range(self.items):
            horizontal_layout = MDBoxLayout(orientation="horizontal", spacing=10, padding=10, id = f"{i}")
            label = MDLabel(text=f"{items[i]}", font_style='Subtitle2')

            icon_button = MDIconButton(icon="close", size_hint=(None, None), pos_hint={"center_y": 0.5})
            icon_button.bind(on_release=self.delete_expiration_date)
            horizontal_layout.add_widget(label)
            horizontal_layout.add_widget(icon_button)

            self.add_widget(horizontal_layout)

    def delete_expiration_date(self, instance):

        #smazani data expirace po kliknuti cancel icon button
        parent_parent_layout = instance.parent.parent
        parent_layout = instance.parent
        layout_id = []
        #print(f"before: {parent_layout.id}")
        parent_parent_layout.remove_widget(parent_layout)
        self.height -= dp(35)

        #update vysky contentu expansion panelu
        #self.parent.parent.do_layout()
        #self.parent.do_layout()

        removed_date = ""
        for child in parent_layout.children[:]:
            if isinstance(child, MDLabel):
                removed_date = child.text
        self.dates_array.remove(removed_date)
        #print(self.dates_array)

        #odebrani data a prevedeni na string retezec pro odeslani
        dates_array_to_string = ""
        for date in self.dates_array:
            dates_array_to_string += f"{date}" + ", "
        #print(dates_array_to_string)
        self.str_id = str(self.id)
        #print(self.str_id)

        #update databaze
        sql = """UPDATE client_food_table SET expiration_date = %s WHERE ID = %s """
        cursor.execute(sql, (dates_array_to_string, self.str_id))
        conn.commit()

class MainApp(MDApp):

    def build(self):
        #ziskat vsechny data z tabulky/databaze
        sql = """SELECT * FROM client_food_table"""
        cursor.execute(sql)
        self.result = cursor.fetchall()

        self.dates = []
        self.str_id = []
        self.product_array = []
        #print(result)

        #rozlozit do jednotlivych stringu oznacene ke kterym produktum patri
        for i in range(len(self.result)):
            raw_dates_str = self.result[i][7][:-2]
            raw_dates = raw_dates_str.replace(" ", "")
            self.dates.append(raw_dates.split(","))
            self.str_id.append(self.result[i][0])
        #print(dates)
        #print(id)

        #layout obrazovky
        screen = Screen()

        #layout pro expantion menu
        main_layout = MDBoxLayout(orientation="vertical")

        #iniciace top app radku
        top_app_bar = MDTopAppBar(
            pos_hint={"top": 1},
            elevation=0,
            md_bg_color=(0.2, 0.6, 0.8, 1),  # Customize background color
            height=100,  # App bar height

        )

        #layout unvitr top app radku
        top_bar_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=1,
            padding=(0, 0),
            spacing = 20
        )

        #tlacitko pro hledani v top app radku
        search_icon = MDIconButton(
            icon="magnify",
            size_hint_x=None,
            md_bg_color=(0.2, 0.6, 0.8, 1), #barva a alfa/pruhlednost tlacitka
            icon_size="30sp",  # velikost
            theme_text_color="Custom",
            pos_hint={"center_y": 1},

        )
        search_icon.bind(on_press=self.search_action)
        #radek pro zadavani hledanych slov
        self.search_field = MDTextField(
            hint_text="Search",
            size_hint_x=1,
            size_hint_y = None,
            height = 40,
            line_color_normal=(0, 0, 0, 1),
            text_color_normal=(0, 0, 0, 1),

            #pri kliknuti na textove pole se muze zmenit barva car a textu
            line_color_focus=(0, 0, 0, 1),
            text_color_focus=(0, 0, 0, 1),

            mode="rectangle",
            pos_hint={"center_y": 1.15},

        )

        #skladani layoutu top app radku
        top_bar_layout.add_widget(self.search_field)
        top_bar_layout.add_widget(search_icon)
        top_app_bar.add_widget(top_bar_layout)

        #pridavani tlacitka pro skenovani caroveho kodu na obrazovku
        barcode_scan_button = MDIconButton(
            icon = 'barcode-scan',
            md_bg_color = (0.2, 0.6, 0.8, 1)
        )
        scan_button_layout = AnchorLayout(
            anchor_x = 'right',
            anchor_y = 'bottom',
            padding = 10,
        )
        barcode_scan_button.bind(on_press=self.scan_barcode)
        scan_button_layout.add_widget(barcode_scan_button)

        #pridavani tlacitka pro zadavani filtru na obrazovku
        sort_button = MDIconButton(
            icon='sort',
            md_bg_color = (0.2, 0.6, 0.8, 1)
        )
        sort_button_layout = AnchorLayout(
            anchor_x = 'left',
            anchor_y = 'bottom',
            padding = 10,)
        sort_button_layout.add_widget(sort_button)

        #vertikalni layout pro expansion panely (MDList())
        layout = MDBoxLayout(
            orientation="vertical",
            spacing=20,
            padding=20,
            size_hint_y=None,
            pos_hint={"center_y": -0.05},
        )
        #layout.bind(minimum_height=layout.setter("height"))  # dynamicka vyska

        #layout pro scrolovani
        scroll_view = ScrollView(
            size_hint=(1, 0),
            do_scroll_x=False,
            do_scroll_y=True,
            height = Window.height,
        )

        #layout primo pro expansion panely
        self.panel_list = MDList()

        scroll_view.add_widget(self.panel_list)
        layout.add_widget(scroll_view)

        #vypis hodnot do expansion panelu na obrazovce
        for i in range(len(self.result)):
            self.panel = MDExpansionPanel(
                content=Content(
                    items=self.dates[i],
                    id = str(self.str_id[i]),
                ),
                panel_cls=MDExpansionPanelOneLine(
                    text=f"{self.result[i][1]}",
                )
            )
            self.panel_list.add_widget(self.panel)

        #pridani na scroll view
        screen.add_widget(layout)
        #vse do main layoutu
        screen.add_widget(top_app_bar)
        #main_layout.add_widget(top_app_bar)

        #main layout na obrazovku
        #screen.add_widget(main_layout)
        screen.add_widget(scan_button_layout)
        screen.add_widget(sort_button_layout)
        return screen

    #def close_popup(self):
    def refresh_app(self, *args ):
        print("refresh app =============================================")
        self.panel_list.clear_widgets()

        fetched_dates = []
        fetched_str_id = []

        sql = """SELECT * FROM client_food_table"""

        cursor.execute(sql)
        sleep(0.5)
        fetched_result = cursor.fetchall()

        print(f"fetched result: {fetched_result}")
        # rozlozit do jednotlivych stringu oznacene ke kterym produktum patri
        for i in range(len(fetched_result)):
            raw_dates_str = fetched_result[i][7][:-2]
            raw_dates = raw_dates_str.replace(" ", "")
            fetched_dates.append(raw_dates.split(","))
            print(fetched_dates[i])
            fetched_str_id.append(fetched_result[i][0])

            # Create new expansion panels with the refreshed data
        for i in range(len(fetched_result)):
            self.panel = MDExpansionPanel(
                content=Content(
                    items=fetched_dates[i],
                    id=str(fetched_str_id[i]),
                ),
                panel_cls=MDExpansionPanelOneLine(
                    text=f"{fetched_result[i][1]}",
                )
            )
            self.panel_list.add_widget(self.panel)
        print("Updated dates:", fetched_dates)
        print("Updated str_id:", fetched_str_id)
    def scan_barcode(self, instance):


        #self.barcode_Scan_Overlay = BarcodeScannerApp()
        #self.barcode_Scan_Overlay.open_barcode_scanner()

        self.barcode_scanner = BarcodeScannerApp(self.get_scanned_barcode)
        self.barcode_scanner.open_barcode_scanner()

        #print(f"scan barcode")

    def get_scanned_barcode(self, barcode):
        self.product_array.clear()
        self.product_array.append(barcode)

        self.barcode_scanner.close_self()

        #self.barcode_scanner.close_self()
        #print(f"product array with barcode {self.product_array}")
        self.date_picker_popup()




    #def close_self(self):
    #    self.capture.release()
    #    self.dismiss()

    def date_picker_popup(self):
        #print("date_picker_popup")
        self.date_Picker_Overlay = MyDatePicker(self.get_exp_dates)
        self.date_Picker_Overlay.open_date_picker()

    def get_exp_dates(self, exp_dates):
        print(f"product_array: {self.product_array}")
        self.product_array.append(exp_dates)
        #print(self.product_array)
        print("product_uploaded")
        upload_product_to_database(self.product_array)
        Clock.schedule_once(self.refresh_app, 0.5)


    def search_action(self, instance):

        #print(f"Searching for: {self.search_field.text}")
        sql = """SELECT * FROM client_food_table  WHERE keywords LIKE %s OR category_tags LIKE %s"""
        val = f"%{self.search_field.text}%"
        cursor.execute(sql, (val,val))
        result = cursor.fetchall()
        row_id = []
        for i in range(len(result)):
            row_id.append(result[i][0])

        for child in self.panel_list.children[:]:
            if isinstance(child, MDExpansionPanel):
                self.panel_list.remove_widget(child)

        if len(result)>0:
            dates = []

            # rozlozit do jednotlivych stringu oznacene ke kterym produktum patri
            for i in range(len(result)):
                raw_dates_str = result[i][7][:-2]
                raw_dates = raw_dates_str.replace(" ", "")
                dates.append(raw_dates.split(","))
                # print(dates)

            for i in range(len(result)):
                panel = MDExpansionPanel(
                    content=Content(
                        items=dates[i],
                        id = str(row_id[i])
                    ),
                    panel_cls=MDExpansionPanelOneLine(
                        text=f"{result[i][1]}",
                    ),
                )
                self.panel_list.add_widget(panel)
        else:
            #print("No results found")
            pass

if __name__ == "__main__":
    MainApp().run()