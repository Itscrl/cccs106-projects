import flet as ft
import mysql.connector
from db_connection import connect_db


def main(page: ft.Page):
    page.window.center()
    page.window.frameless = True
    page.window.title_bar_buttons_hidden = True
    page.title  = "User Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.height = 350
    page.window.width = 400
    page.bgcolor = ft.Colors.AMBER_ACCENT

    login_title = ft.Text(
        value="User Login",
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        text_align=ft.TextAlign.CENTER,
    )
    
    username_input = ft.TextField(
        label="User name",
        hint_text="Enter your username",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
        prefix_icon=ft.icons.PERSON,
    )
    
    password_input = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your unique identifier",
        width=300,
        password=True,
        can_reveal_password=True,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
        prefix_icon=ft.icons.LOCK,        
    )
    
    def login_click(e):
        def close_dialog(d):   # <<< changed: added parameter `d` so dialogs close properly
            d.open = False
            page.update()

        success_dialog = ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=40),
            title=ft.Text("Login Successful", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Text(f"Welcome, {username_input.value}!", text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(success_dialog))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        failure_dialog = ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.icons.ERROR, color=ft.Colors.RED, size=40),
            title=ft.Text("Login Failed", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Text("Invalid username or password", text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(failure_dialog))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        invalid_input_dialog = ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.icons.INFO, color=ft.Colors.BLUE, size=40),
            title=ft.Text("Input Error", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Text("Please enter username and password", text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(invalid_input_dialog))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        database_error_dialog = ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.icons.DATABASE, color=ft.Colors.ORANGE, size=40),
            title=ft.Text("Database Error", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Text("An error occurred while connecting to the database",
                            text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(database_error_dialog))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        # --- Validation and authentication ---
        if not username_input.value or not password_input.value:
            page.dialog = invalid_input_dialog
            invalid_input_dialog.open = True
            page.update()
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username_input.value, password_input.value)
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                page.dialog = success_dialog
                success_dialog.open = True
            else:
                page.dialog = failure_dialog
                failure_dialog.open = True

        except mysql.connector.Error:
            page.dialog = database_error_dialog
            database_error_dialog.open = True

        page.update()
            
    # ✅ fixed ElevatedButton
    login_button = ft.ElevatedButton(
        text="Login",           # <<< changed: added `text=`
        icon=ft.Icons.LOGIN,    # <<< changed: fixed typo (was ft.iconns.LOGIN)
        on_click=login_click,
        width=100
    )
        
    # UI components    
    page.add(login_title)
    page.add(username_input)
    page.add(password_input)
    page.add(login_button)   
    
    
ft.app(target=main)   # <<< changed: must use target=main
