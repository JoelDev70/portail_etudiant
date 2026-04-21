"""Portail Étudiant — point d'entrée Flet."""
import flet as ft
from auth import load_session, logout
from pages.login_page import login_view
from pages.student_pages import (
    profil_view, notes_view, emploi_view, documents_view, paiements_view,
)
from pages.admin_pages import dashboard_view, etudiants_view, saisie_notes_view, paiements_admin_view, documents_admin_view, enseignants_view


def main(page: ft.Page):
    page.title = "Portail Étudiant"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_100
    page.padding = 0

    state = {"user": load_session()}

    # ---------- Routage ----------
    def route_change(e=None):
        page.views.clear()
        if not state["user"]:
            page.views.append(login_view(page, on_login_success))
        else:
            page.views.append(main_view())
        page.update()

    def on_login_success(user):
        state["user"] = user
        page.snack_bar = ft.SnackBar(ft.Text(f"Bienvenue {user['login']}"),
                                     bgcolor=ft.Colors.GREEN_600)
        page.snack_bar.open = True
        route_change()

    def do_logout(e):
        logout(); state["user"] = None; route_change()

    # ---------- Vue principale ----------
    def main_view():
        user = state["user"]
        is_admin = user["role"] == "admin"

        content = ft.Container(expand=True, padding=25, bgcolor=ft.Colors.WHITE)

        if is_admin:
            menu = [
                ("Tableau de bord", ft.Icons.DASHBOARD, lambda: dashboard_view(user)),
                ("Étudiants", ft.Icons.PEOPLE, lambda: etudiants_view(page)),
                ("Saisie notes", ft.Icons.EDIT_NOTE, lambda: saisie_notes_view(page)),
                ("Enseignants", ft.Icons.SCHOOL, lambda: enseignants_view(page)),
                ("Paiements", ft.Icons.PAYMENTS, lambda: paiements_admin_view(page)),
                ("Documents", ft.Icons.FOLDER, lambda: documents_admin_view(page))
            ]
        else:
            menu = [
                ("Mon profil", ft.Icons.PERSON, lambda: profil_view(user, page)),
                ("Mes notes", ft.Icons.GRADE, lambda: notes_view(user)),
                ("Emploi du temps", ft.Icons.CALENDAR_MONTH, lambda: emploi_view(user)),
                ("Supports", ft.Icons.FOLDER, lambda: documents_view(user, page)),
                ("Paiements", ft.Icons.PAYMENTS, lambda: paiements_view(user, page)),
            ]

        def select(idx):
            content.content = menu[idx][2]()
            page.update()

        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100, min_extended_width=200, extended=True,
            bgcolor=ft.Colors.BLUE_GREY_900,
            indicator_color=ft.Colors.BLUE_400,
            destinations=[
                ft.NavigationRailDestination(
                    icon=m[1], label=ft.Text(m[0], color=ft.Colors.WHITE),
                ) for m in menu
            ],
            on_change=lambda e: select(e.control.selected_index),
            leading=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SCHOOL, size=40, color=ft.Colors.WHITE),
                    ft.Text("Portail", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=15,
            ),
            trailing=ft.Container(
                content=ft.Column([
                    ft.Text(user["login"], color=ft.Colors.WHITE, size=12),
                    ft.Text(user["role"].upper(), color=ft.Colors.BLUE_200, size=10),
                    ft.IconButton(ft.Icons.LOGOUT, icon_color=ft.Colors.WHITE,
                                  tooltip="Déconnexion", on_click=do_logout),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=10, expand=True,
                # alignment removed: some flet versions don't expose bottom_center constant
            ),
        )

        content.content = menu[0][2]()

        return ft.View(
            route="/app",
            controls=[ft.Row([rail, ft.VerticalDivider(width=1), content], expand=True)],
            padding=0,
        )

    route_change()
