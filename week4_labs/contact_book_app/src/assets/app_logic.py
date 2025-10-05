# app_logic.py
import flet as ft 
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db 

def display_contacts(page, contacts_list_view, db_conn, search_term=None): 
    """
    Fetches and displays all contacts in the ListView.
    Supports filtering by search term with beautiful blue aesthetic.
    """
    contacts_list_view.controls.clear() 
    contacts = get_all_contacts_db(db_conn, search_term)
     
    if not contacts:
        # Show message when no contacts found
        contacts_list_view.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.Icons.CONTACT_PAGE_OUTLINED, 
                            size=80, 
                            color="#B8D4F1"
                        ),
                        ft.Text(
                            "No contacts found" if search_term else "No contacts yet",
                            size=18,
                            weight=ft.FontWeight.W_500,
                            color="#4A90E2",
                        ),
                        ft.Text(
                            "Start by adding your first contact!" if not search_term else "Try a different search",
                            size=14,
                            color="#8AB4E5",
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.alignment.center,
                padding=40
            )
        )
    else:
        for contact in contacts: 
            contact_id, name, phone, email = contact 
            
            # Create a minimal, modern card with blue aesthetic
            contacts_list_view.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    # Avatar with blue gradient
                                    ft.Container(
                                        content=ft.Text(
                                            name[0].upper(),
                                            size=22,
                                            weight=ft.FontWeight.BOLD,
                                            color="#FFFFFF"
                                        ),
                                        width=50,
                                        height=50,
                                        bgcolor="#4A90E2",
                                        border_radius=25,
                                        alignment=ft.alignment.center
                                    ),
                                    ft.Container(width=12),
                                    # Contact info
                                    ft.Column(
                                        [
                                            ft.Text(
                                                name, 
                                                size=18, 
                                                weight=ft.FontWeight.W_600,
                                                color="#2C3E50"
                                            ),
                                            ft.Row(
                                                [
                                                    ft.Icon(
                                                        ft.Icons.PHONE_ROUNDED, 
                                                        size=16, 
                                                        color="#4A90E2"
                                                    ),
                                                    ft.Text(
                                                        phone if phone else "No phone",
                                                        size=13,
                                                        color="#7A8A99"
                                                    ),
                                                ],
                                                spacing=6
                                            ),
                                            ft.Row(
                                                [
                                                    ft.Icon(
                                                        ft.Icons.EMAIL_ROUNDED, 
                                                        size=16, 
                                                        color="#4A90E2"
                                                    ),
                                                    ft.Text(
                                                        email if email else "No email",
                                                        size=13,
                                                        color="#7A8A99"
                                                    ),
                                                ],
                                                spacing=6
                                            ),
                                        ],
                                        spacing=4,
                                        expand=True
                                    ),
                                    # Action menu
                                    ft.PopupMenuButton(
                                        icon=ft.Icons.MORE_VERT_ROUNDED,
                                        icon_color="#4A90E2",
                                        items=[
                                            ft.PopupMenuItem(
                                                text="Edit",
                                                icon=ft.Icons.EDIT_ROUNDED,
                                                on_click=lambda _, c=contact: open_edit_dialog(
                                                    page, c, db_conn, contacts_list_view
                                                )
                                            ),
                                            ft.PopupMenuItem(),
                                            ft.PopupMenuItem(
                                                text="Delete",
                                                icon=ft.Icons.DELETE_ROUNDED,
                                                on_click=lambda _, cid=contact_id, cname=name: show_delete_confirmation(
                                                    page, cid, cname, db_conn, contacts_list_view
                                                )
                                            ),
                                        ],
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                            ),
                        ],
                        spacing=0
                    ),
                    padding=16,
                    bgcolor="#FFFFFF",
                    border_radius=16,
                    border=ft.border.all(1, "#E3F2FD"),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=8,
                        color="#4A90E210",
                        offset=ft.Offset(0, 2)
                    )
                )
            )
    
    page.update() 
 
def add_contact(page, inputs, contacts_list_view, db_conn, search_input=None): 
    """
    Adds a new contact with input validation.
    Prevents adding contacts with empty names and invalid emails.
    """
    name_input, phone_input, email_input = inputs 
    
    # Validation: Check if name is empty
    if not name_input.value or not name_input.value.strip():
        name_input.error_text = "Name cannot be empty"
        page.update()
        return
    
    # Clear any previous error
    name_input.error_text = None
    
    # Validation: Check if email is provided and contains @
    if email_input.value and email_input.value.strip() and "@" not in email_input.value:
        email_input.error_text = "Email must contain @"
        page.update()
        return
    
    # Clear any previous error
    email_input.error_text = None
    
    # Add contact to database
    add_contact_db(db_conn, name_input.value.strip(), phone_input.value, email_input.value) 
 
    # Clear input fields
    for field in inputs: 
        field.value = "" 
    
    # Clear search field to show all contacts including the new one
    if search_input:
        search_input.value = ""
 
    display_contacts(page, contacts_list_view, db_conn) 
    page.update() 

def show_delete_confirmation(page, contact_id, contact_name, db_conn, contacts_list_view):
    """
    Shows a beautiful confirmation dialog before deleting a contact.
    """
    def confirm_delete(e):
        delete_contact_db(db_conn, contact_id)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)
    
    def cancel_delete(e):
        dialog.open = False
        page.update()
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(ft.Icons.WARNING_ROUNDED, color="#4A90E2", size=28),
                ft.Text("Confirm Delete", color="#4A90E2", weight=ft.FontWeight.BOLD)
            ],
            spacing=10
        ),
        content=ft.Text(
            f"Are you sure you want to delete '{contact_name}'?\nThis action cannot be undone.",
            size=15
        ),
        actions=[
            ft.TextButton(
                "Cancel", 
                on_click=cancel_delete,
                style=ft.ButtonStyle(color="#7A8A99")
            ),
            ft.ElevatedButton(
                "Delete",
                on_click=confirm_delete,
                bgcolor="#E74C3C",
                color="#FFFFFF",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8)
                )
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    
    page.open(dialog)
 
def delete_contact(page, contact_id, db_conn, contacts_list_view): 
    """Deletes a contact and refreshes the list.""" 
    delete_contact_db(db_conn, contact_id) 
    display_contacts(page, contacts_list_view, db_conn) 
 
def open_edit_dialog(page, contact, db_conn, contacts_list_view): 
    """Opens a beautiful dialog to edit a contact's details with validation.""" 
    contact_id, name, phone, email = contact 
 
    edit_name = ft.TextField(
        label="Name", 
        value=name,
        border_radius=10,
        border_color="#4A90E2",
        focused_border_color="#2E7BD4",
        cursor_color="#4A90E2"
    ) 
    edit_phone = ft.TextField(
        label="Phone", 
        value=phone,
        border_radius=10,
        border_color="#4A90E2",
        focused_border_color="#2E7BD4",
        cursor_color="#4A90E2",
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.NumbersOnlyInputFilter()
    ) 
    edit_email = ft.TextField(
        label="Email", 
        value=email,
        border_radius=10,
        border_color="#4A90E2",
        focused_border_color="#2E7BD4",
        cursor_color="#4A90E2",
        keyboard_type=ft.KeyboardType.EMAIL,
        on_change=lambda e: setattr(edit_email, 'value', edit_email.value.replace(' ', '')) or page.update()
    ) 
 
    def save_and_close(e):
        # Validate name is not empty
        if not edit_name.value or not edit_name.value.strip():
            edit_name.error_text = "Name cannot be empty"
            page.update()
            return
        
        edit_name.error_text = None
        
        # Validate email contains @
        if edit_email.value and edit_email.value.strip() and "@" not in edit_email.value:
            edit_email.error_text = "Email must contain @"
            page.update()
            return
        
        edit_email.error_text = None
        update_contact_db(db_conn, contact_id, edit_name.value.strip(), edit_phone.value, edit_email.value) 
        dialog.open = False 
        page.update() 
        display_contacts(page, contacts_list_view, db_conn) 
 
    dialog = ft.AlertDialog( 
        modal=True, 
        title=ft.Row(
            [
                ft.Icon(ft.Icons.EDIT_ROUNDED, color="#4A90E2", size=26),
                ft.Text("Edit Contact", color="#4A90E2", weight=ft.FontWeight.BOLD)
            ],
            spacing=10
        ),
        content=ft.Column(
            [edit_name, edit_phone, edit_email],
            tight=True,
            spacing=15
        ), 
        actions=[ 
            ft.TextButton(
                "Cancel", 
                on_click=lambda e: setattr(dialog, 'open', False) or page.update(),
                style=ft.ButtonStyle(color="#7A8A99")
            ), 
            ft.ElevatedButton(
                "Save", 
                on_click=save_and_close,
                bgcolor="#4A90E2",
                color="#FFFFFF",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8)
                )
            ), 
        ],
        actions_alignment=ft.MainAxisAlignment.END
    ) 
 
    page.open(dialog)