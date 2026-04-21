"""Page de connexion."""
import flet as ft
from auth import login

def login_view(page: ft.Page, on_success):
    login_field = ft.TextField(label="Identifiant", width=320, autofocus=True)
    pwd_field = ft.TextField(label="Mot de passe", password=True, can_reveal_password=True, width=320)
    error = ft.Text("", color=ft.Colors.RED_400)

    def do_login(e):
        user = login(login_field.value.strip(), pwd_field.value)
        if user:
            on_success(user)
        else:
            error.value = "Identifiants incorrects."
            page.update()

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.SCHOOL, size=64, color=ft.Colors.BLUE_700),
                        ft.Text("Portail Étudiant", size=28, weight=ft.FontWeight.BOLD),
                        ft.Text("Connectez-vous à votre espace", color=ft.Colors.GREY_700),
                        ft.Container(height=20),
                        login_field,
                        pwd_field,
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Se connecter", icon=ft.Icons.LOGIN,
                            width=320, height=45, on_click=do_login,
                        ),
                        error,
                        ft.Container(height=10),
                        ft.Text("Démo : admin / etudiant1 — mot de passe : password123",
                                size=11, color=ft.Colors.GREY_600),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                expand=True,
                padding=40,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
