# main.py
import flet as ft 
from database import init_db 
from app_logic import display_contacts, add_contact 
 
def main(page: ft.Page): 
    page.title = "Contact Book" 
    page.vertical_alignment = ft.MainAxisAlignment.START 
    page.window_width = 450 
    page.window_height = 700 
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#F8FAFF"  # Very light blue background
    
    # Custom theme with beautiful blue
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#4A90E2",  # Beautiful aesthetic blue
            on_primary="#FFFFFF",
            primary_container="#E3F2FD",
            surface="#FFFFFF",
            background="#F8FAFF",
        )
    )
 
    db_conn = init_db() 
 
    # Theme toggle button with blue aesthetic
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            page.bgcolor = "#0A1929"
            theme_icon.icon = ft.Icons.LIGHT_MODE
            theme_icon.tooltip = "Switch to Light Mode"
            theme_icon.icon_color = "#FFFFFF"
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            page.bgcolor = "#F8FAFF"
            theme_icon.icon = ft.Icons.DARK_MODE
            theme_icon.tooltip = "Switch to Dark Mode"
            theme_icon.icon_color = "#FFFFFF"
        page.update()
    
    theme_icon = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        tooltip="Switch to Dark Mode",
        on_click=toggle_theme,
        icon_color="#FFFFFF",
        icon_size=24
    )
 
    # Input fields with aesthetic blue styling
    name_input = ft.TextField(
        label="Name", 
        hint_text="Enter contact name",
        border_radius=12,
        filled=True,
        bgcolor="#FFFFFF",
        border_color="#4A90E2",
        focused_border_color="#2E7BD4",
        focused_border_width=2,
        label_style=ft.TextStyle(color="#4A90E2"),
        cursor_color="#4A90E2",
        color="#000000"
    ) 
    phone_input = ft.TextField(
        label="Phone", 
        hint_text="Enter phone number",
        border_radius=12,
        filled=True,
        bgcolor="#FFFFFF",
        border_color="#4A90E2",
        focused_border_color="#2E7BD4",
        focused_border_width=2,
        label_style=ft.TextStyle(color="#4A90E2"),
        cursor_color="#4A90E2",
        color="#000000",
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.NumbersOnlyInputFilter()
    ) 
    email_input = ft.TextField(
        label="Email", 
        hint_text="Enter email address",
        border_radius=12,
        filled=True,
        bgcolor="#FFFFFF",
        border_color="#4A90E2",
        focused_border_color="#2E7BD4",
        focused_border_width=2,
        label_style=ft.TextStyle(color="#4A90E2"),
        cursor_color="#4A90E2",
        color="#000000",
        keyboard_type=ft.KeyboardType.EMAIL,
        on_change=lambda e: setattr(email_input, 'value', email_input.value.replace(' ', '')) or page.update()
    ) 
 
    inputs = (name_input, phone_input, email_input)
    
    # Search field with blue aesthetic
    search_input = ft.TextField(
        hint_text="Search contacts...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=25,
        filled=True,
        bgcolor="#FFFFFF",
        border_color="#4A90E2",
        focused_border_color="#2E7BD4",
        focused_border_width=2,
        cursor_color="#4A90E2",
        color="#000000",
        on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, search_input.value)
    )
 
    contacts_list_view = ft.ListView(expand=1, spacing=12, padding=10) 
 
    add_button = ft.ElevatedButton(
        text="Add Contact",
        icon=ft.Icons.PERSON_ADD_ROUNDED,
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn, search_input),
        bgcolor="#4A90E2",
        color="#FFFFFF",
        height=50,
        elevation=0,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
        )
    ) 
 
    page.add( 
        ft.Container(
            content=ft.Column( 
                [ 
                    # Header section with blue gradient background
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.CONTACTS_ROUNDED, color="#FFFFFF", size=32),
                                ft.Text(
                                    "Contact Book", 
                                    size=28, 
                                    weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF"
                                ),
                                ft.Container(expand=True),
                                theme_icon
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        padding=20,
                        bgcolor="#4A90E2",
                        border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20)
                    ),
                    
                    # Main content
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(height=10),
                                ft.Text(
                                    "Add New Contact", 
                                    size=18, 
                                    weight=ft.FontWeight.W_600,
                                    color="#4A90E2"
                                ), 
                                name_input, 
                                phone_input, 
                                email_input, 
                                add_button,
                                ft.Container(height=10),
                                ft.Divider(height=1, color="#E3F2FD", thickness=2),
                                ft.Container(height=10),
                                ft.Text(
                                    "Your Contacts", 
                                    size=18, 
                                    weight=ft.FontWeight.W_600,
                                    color="#4A90E2"
                                ),
                                search_input,
                            ],
                            spacing=12
                        ),
                        padding=20
                    ),
                    
                    # Contacts list
                    ft.Container(
                        content=contacts_list_view,
                        expand=True,
                        padding=ft.padding.only(left=10, right=10, bottom=10)
                    )
                ],
                spacing=0
            ),
            expand=True
        )
    ) 
 
    display_contacts(page, contacts_list_view, db_conn) 
 
if __name__ == "__main__": 
    ft.app(target=main)