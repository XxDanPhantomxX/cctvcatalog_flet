import flet as ft
from database import init_db
from admin_view import AdminView
from user_view import UserView
from dotenv import load_dotenv
import subprocess
import os

MODE = os.getenv("MODE", "desktop").lower()

def main(page: ft.Page):
    page.title = "Sistema de Inventario CCTV"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    ft.Page.width.setter(1000)
    ft.Page.height.setter (800)

    init_db()

    # Campos de login
    usuario_input = ft.TextField(label="Usuario", width=300)
    password_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)

    def login(e):
        user = usuario_input.value.strip()  # type: ignore
        pwd = password_input.value.strip()  # type: ignore
        if user == "admin" and pwd == "1234":
            page.go("/admin")
    
    def access_catalog(e):
        page.go("/user")

    login_btn = ft.ElevatedButton("Iniciar sesión", on_click=login)
    users_btn = ft.ElevatedButton("Acceso Catálogo", on_click=access_catalog, icon=ft.Icons.SHOP_2_ROUNDED)

    # ==============================
    # BOTÓN PARA LANZAR WEB + LOCALTUNNEL
    # ==============================
    def launch_web_lt(e):
        try:
            bat_path = os.path.join(os.getcwd(), "run_all.bat")
            subprocess.Popen([bat_path], shell=True)
            launch_btn.visible = False
            page.update()
        except Exception as ex:
            pass
        page.update()

    launch_btn = ft.ElevatedButton("Lanzar Web", on_click=launch_web_lt, icon=ft.Icons.WEB)

    # 🔹 Si está en modo web, ocultar el botón
    if MODE == "web":
        launch_btn.visible = False

    info_text = ft.Text("Ingrese Usuario y Contraseña para entrar como Administrador", size=12, italic=True, color=ft.Colors.GREY)

    login_view = ft.View(
        route="/",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Inicio de sesión", size=26, weight=ft.FontWeight.BOLD),
                        usuario_input,
                        password_input,
                        login_btn,
                        info_text,
                        users_btn,
                        launch_btn,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        ],
    )

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(login_view)
        elif page.route == "/admin":
            page.views.append(AdminView(page))
        elif page.route == "/user":
            page.views.append(UserView(page))
        page.update()

    page.on_route_change = route_change
    page.go("/")

load_dotenv()
ft.app(target=main, assets_dir="storage")
