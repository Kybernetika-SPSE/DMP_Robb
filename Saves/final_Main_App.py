from final_product_Handling import upload_product_to_database, execute_mysql_querry, update_mysql_dtb, search_mysql_dtb
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDIconButton
from kivymd.uix.toolbar import MDTopAppBar
from final_Date_Picker import MyDatePicker
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivymd.uix.list import MDList
import mysql.connector as database
import final_Barcode_Scan as fBS
from kivymd.app import MDApp
from kivy.metrics import dp
import json

#nacteni prohlasovacich udaju databaze z json souboru
with open("dtb_config.json","r") as config_file:
    config = json.load(config_file)
conn = database.connect(**config)
cursor = conn.cursor()

#testovaci pevne dana velikost okna
Window.size = (360, 600)

class Content(MDBoxLayout):
    def __init__(self, items, id, product_container, **kwargs):
        #zdedeni parametru materske tridy
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint_y = None
        self.id = id
        self.product_container = product_container

        # prizpusobeni vysky podle poctu dat expirace
        self.dates_array = items
        self.items = len(items)
        self.height = dp(35 * self.items) #old dp 48

        #generovani jednotlivych exp dat v expansion listu
        for i in range(self.items):
            horizontal_layout = MDBoxLayout(orientation="horizontal", spacing=10, padding=10, id = f"{i}")
            label = MDLabel(text=f"{items[i]}", font_style="Subtitle2")

            #tlacitko pro smazani jednotlivych exp dat
            icon_button = MDIconButton(icon="close", size_hint=(None, None), pos_hint={"center_y": 0.5})
            icon_button.bind(on_release=self.delete_expiration_date)
            horizontal_layout.add_widget(label)
            horizontal_layout.add_widget(icon_button)

            self.add_widget(horizontal_layout)

    def delete_expiration_date(self, instance):
        #smazani data expirace po kliknuti cancel icon button
        parent_parent_layout = instance.parent.parent
        parent_layout = instance.parent

        #update vysky contentu expansion panelu
        parent_parent_layout.remove_widget(parent_layout)
        self.height -= dp(35)

        removed_date = ""
        for child in parent_layout.children[:]:
            if isinstance(child, MDLabel):
                removed_date = child.text
        self.dates_array.remove(removed_date)

        #odebrani data a prevedeni na string retezec pro odeslani
        dates_array_to_string = ""
        for date in self.dates_array:
            dates_array_to_string += f"{date}" + ", "
        self.str_id = str(self.id)

        #pokud uzivatel smaze vsechna data expirace zaznam/radek se vymaze
        if len(dates_array_to_string)>0:
            update_mysql_dtb("UPDATE client_food_table SET expiration_date = %s WHERE ID = %s ", (dates_array_to_string, self.str_id))
            #conn.reconnect()
            #sql = """UPDATE client_food_table SET expiration_date = %s WHERE ID = %s """
            #cursor.execute(sql, (dates_array_to_string, self.str_id))
            #conn.commit()
            #conn.close()

        else:
            #kdyz vymazeme posledni datum expirace vymaze se i produkt
            update_mysql_dtb("DELETE FROM client_food_table WHERE ID = %s;", (dates_array_to_string, self.str_id))
            #conn.reconnect()
            #sql = """DELETE FROM client_food_table WHERE ID = %s;"""
            #cursor.execute(sql, (self.str_id,))
            #conn.commit()
            #conn.close()

            self.product_container.remove_widget(parent_parent_layout.parent)

class MainApp(MDApp):

    def build(self):
        #ziskat vsechny data z tabulky/databaze
        #sql = """SELECT * FROM client_food_table"""
        #cursor.execute(sql)
        #self.result = cursor.fetchall()
        self.result = execute_mysql_querry("SELECT * FROM client_food_table")

        self.dates = []
        self.str_id = []
        self.product_array = []

        #rozlozit do jednotlivych stringu oznacene ke kterym produktum patri
        for i in range(len(self.result)):
            raw_dates_str = self.result[i][7][:-2]
            raw_dates = raw_dates_str.replace(" ", "")
            self.dates.append(raw_dates.split(","))
            self.str_id.append(self.result[i][0])

        #layout obrazovky
        screen = Screen()

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
            icon = "barcode-scan",
            md_bg_color = (0.2, 0.6, 0.8, 1)
        )

        scan_button_layout = AnchorLayout(
            anchor_x = "right",
            anchor_y = "bottom",
            padding = 10,
        )
        barcode_scan_button.bind(on_press=self.scan_barcode)
        scan_button_layout.add_widget(barcode_scan_button)

        #pridavani tlacitka pro zadavani filtru na obrazovku
        sort_button = MDIconButton(
            icon= "sort",
            md_bg_color = (0.2, 0.6, 0.8, 1)
        )
        sort_button_layout = AnchorLayout(
            anchor_x = "left",
            anchor_y = "bottom",
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

        #layout pro scrolovani
        scroll_view = ScrollView(
            size_hint=(1, 0),
            do_scroll_x=False,
            do_scroll_y=True,
            height = Window.height,
        )

        #layout urceny pro expansion panely
        self.panel_list = MDList()

        scroll_view.add_widget(self.panel_list)
        layout.add_widget(scroll_view)

        #vypis hodnot do expansion panelu na obrazovce
        for i in range(len(self.result)):
            self.panel = MDExpansionPanel(
                content=Content(
                    items=self.dates[i],
                    id = str(self.str_id[i]),
                    product_container = self.panel_list
                ),
                #kolik radku zabira expantion list?
                panel_cls=MDExpansionPanelOneLine(
                    text=f"{self.result[i][1]}",
                )
            )
            self.panel_list.add_widget(self.panel)

        #pridani na scroll view
        screen.add_widget(layout)

        #vse do main layoutu
        screen.add_widget(top_app_bar)
        screen.add_widget(scan_button_layout)
        screen.add_widget(sort_button_layout)
        return screen

    def refresh_app(self, *args ):
        for child in self.panel_list.children[:]:  # Iterate over a copy to avoid errors
            self.panel_list.remove_widget(child)

        #conn.reconnect()
        #sql = """SELECT * FROM client_food_table"""
        #cursor = conn.cursor()
        #cursor.execute(sql)
        result = execute_mysql_querry("SELECT * FROM client_food_table")
        #conn.close()

        row_id = []
        for i in range(len(result)):
            row_id.append(result[i][0])

        for child in self.panel_list.children[:]:
            if isinstance(child, MDExpansionPanel):
                self.panel_list.remove_widget(child)

        if len(result) > 0:
            dates = []

            # rozlozit do jednotlivych stringu oznacene ke kterym produktum patri
            for i in range(len(result)):
                raw_dates_str = result[i][7][:-2]
                raw_dates = raw_dates_str.replace(" ", "")
                dates.append(raw_dates.split(","))

            for i in range(len(result)):
                panel = MDExpansionPanel(
                    content=Content(
                        items = dates[i],
                        id = str(row_id[i]),
                        product_container=self.panel_list
                    ),
                    panel_cls = MDExpansionPanelOneLine(
                        text =f"{result[i][1]}",
                    ),
                )
                self.panel_list.add_widget(panel)

    #otevreni popoutu ctecky caroveho kodu
    def scan_barcode(self, instance):
        self.barcode_scanner = fBS.BarcodeScannerApp(self.get_scanned_barcode)
        self.barcode_scanner.open_barcode_scanner()

    #ziskani hodnoty caroveho kodu produktu z popoutu
    def get_scanned_barcode(self, barcode):
        self.product_array.clear()
        self.product_array.append(barcode)
        self.barcode_scanner.close_self()
        self.date_picker_popup()

    def date_picker_popup(self):
        self.date_Picker_Overlay = MyDatePicker(self.get_exp_dates)
        self.date_Picker_Overlay.open_date_picker()

    def get_exp_dates(self, exp_dates):
        self.product_array.append(exp_dates)
        upload_product_to_database(self.product_array, self.refresh_app)

    def search_action(self, instance):
        conn.reconnect()
        #sql = """SELECT * FROM client_food_table WHERE keywords LIKE %s OR category_tags LIKE %s"""
        val = f'%{self.search_field.text}%'
        #cursor.execute(sql, (val,val))
        #time.sleep(0.1)
        #result = cursor.fetchall()
        #conn.close()

        result = search_mysql_dtb("SELECT * FROM client_food_table WHERE keywords LIKE %s OR category_tags LIKE %s", (val, val))

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

            for i in range(len(result)):
                panel = MDExpansionPanel(
                    content=Content(
                        items=dates[i],
                        id = str(row_id[i]),
                        product_container=self.panel_list
                    ),
                    panel_cls=MDExpansionPanelOneLine(
                        text=f"{result[i][1]}",
                    ),
                )
                self.panel_list.add_widget(panel)
        else:
            pass

if __name__ == "__main__":
    MainApp().run()