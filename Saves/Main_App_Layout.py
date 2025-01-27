from kivy.uix.anchorlayout import AnchorLayout
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton
from kivymd.uix.toolbar import MDTopAppBar
from kivy.core.window import Window

Window.size = (360, 600)

class DropdownMenuApp(MDApp):
    def build(self):
        # Create the main screen
        screen = Screen()

        # Create a main vertical layout
        main_layout = MDBoxLayout(orientation="vertical")

        # Add a top app bar with a search bar
        top_app_bar = MDTopAppBar(
            pos_hint={"top": 1},
            elevation=0,
            md_bg_color=(0.2, 0.6, 0.8, 1),  # Customize background color
            height=100,  # App bar height

        )

        # Add a horizontal layout inside the top app bar
        top_bar_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=1,
            padding=(0, 0),
            spacing = 20
        )

        # Add a search icon as an MDIconButton
        search_icon = MDIconButton(
            icon="magnify",  # Material Design magnifying glass icon
            size_hint_x=None,
            icon_size="30sp",  # Adjust icon size as needed
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),  # Set the color of the icon
            pos_hint={"center_y": 1}
        )

        # Add a search field
        search_field = MDTextField(
            hint_text="Search",
            size_hint_x=1,
            size_hint_y = None,
            height = 40,
            line_color_focus=(1, 1, 1, 1),
            line_color_normal=(1, 1, 1, 1),
            text_color_normal=(1, 1, 1, 1),
            text_color_focus=(1, 1, 1, 1),
            mode="rectangle",
            pos_hint={"center_y": 1.1},

        )

        # Add widgets to the horizontal layout
        top_bar_layout.add_widget(search_field)
        top_bar_layout.add_widget(search_icon)

        # Add the horizontal layout to the top app bar
        top_app_bar.add_widget(top_bar_layout)

        barcode_scan_button = MDIconButton(
            icon = 'barcode-scan'
        )
        scan_button_layout = AnchorLayout(
            anchor_x = 'right',
            anchor_y = 'bottom',
            padding = 10,
        )
        scan_button_layout.add_widget(barcode_scan_button)
        sort_button = MDIconButton(
            icon='sort'
        )
        sort_button_layout = AnchorLayout(
            anchor_x = 'left',
            anchor_y = 'bottom',
            padding = 10,)
        sort_button_layout.add_widget(sort_button)
        # ScrollView to hold all the buttons
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
        )

        # Create a vertical BoxLayout to hold the buttons
        layout = MDBoxLayout(
            orientation="vertical",
            spacing=20,
            padding=20,
            size_hint_y=None,
        )
        layout.bind(minimum_height=layout.setter("height"))  # Adjust the height dynamically

        menu_items = [
            {
                "text": f"Option {i + 1}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"Option {i + 1}": self.menu_callback(x),
            }
            for i in range(5)  # Generate 5 options
        ]

        # Generate multiple buttons
        for i in range(15):
            dropdown_button = MDRaisedButton(
                text=f"Open Menu {i + 1}",
                size_hint=(None, None),
                size=(200, 50),
                pos_hint={"center_x": 0.5},
                elevation=1,
            )
            layout.add_widget(dropdown_button)

            # Create a dropdown menu for each button
            dropdown_menu = MDDropdownMenu(
                caller=dropdown_button,
                items=menu_items,
                width_mult=4,
            )
            dropdown_button.bind(on_release=lambda btn, menu=dropdown_menu: menu.open())

        # Add the layout to the ScrollView
        scroll_view.add_widget(layout)

        # Add the top app bar and the ScrollView to the main layout
        main_layout.add_widget(top_app_bar)
        main_layout.add_widget(scroll_view)

        # Add the main layout to the screen

        screen.add_widget(main_layout)
        screen.add_widget(scan_button_layout)
        screen.add_widget(sort_button_layout)
        return screen

    def menu_callback(self, text):
        """Handle the menu item selection."""
        print(f"Selected: {text}")

    def search_action(self, query):
        """Handle search action."""
        print(f"Searching for: {query}")


if __name__ == "__main__":
    DropdownMenuApp().run()
