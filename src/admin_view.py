import flet as ft
import os
import pathlib
import base64
from cloud_upload import upload_image_to_cloudinary
from database import add_product, get_all_products, delete_product, update_config, get_config


class AdminView(ft.View):
    def __init__(self, page):
        super().__init__(route="/admin")
        self.page = page
        self.page.title = "Panel de Administración - Inventario CCTV"

        # Carpeta local para escritorio
        self.images_dir = os.path.join(pathlib.Path.cwd(), "storage", "images")
        os.makedirs(self.images_dir, exist_ok=True)

        # Campos de entrada
        self.nombre = ft.TextField(label="Nombre del producto", width=250)
        self.tipo = ft.Dropdown(
            label="Tipo",
            options=[
                ft.dropdown.Option("Cámara"),
                ft.dropdown.Option("DVR"),
                ft.dropdown.Option("Otro"),
            ],
            width=150,
        )
        self.precio = ft.TextField(
            label="Precio ($)", width=150, keyboard_type=ft.KeyboardType.NUMBER
        )
        self.stock = ft.TextField(
            label="Stock", width=100, keyboard_type=ft.KeyboardType.NUMBER, hint_text="Ej: 10"
        )

        self.img_path = None

        self.mano_obra = ft.TextField(
            label="Costo mano de obra por cámara ($)",
            value=get_config("mano_obra") or "150",
            width=250,
        )

        # Tabla de productos
        self.product_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("Imagen")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
        )

        self.load_products()

        # FilePickers para imágenes y logo
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self.logo_picker = ft.FilePicker(on_result=self.on_logo_picked)
        self.page.overlay.extend([self.file_picker, self.logo_picker])

        # Layout
        self.controls = [
            ft.AppBar(
                title=ft.Text("Panel de Administración"),
                bgcolor=ft.Colors.INDIGO_200,
                leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/")),
            ),
            ft.Column(
                [
                    ft.Text("Agregar producto", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([self.nombre, self.tipo, self.precio, self.stock]),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Seleccionar imagen",
                                on_click=lambda _: self.file_picker.pick_files(allow_multiple=False),
                            ),
                            ft.ElevatedButton("Agregar producto", on_click=self.add_product),
                        ]
                    ),
                    ft.Divider(),
                    ft.Text("Configuración general", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            self.mano_obra,
                            ft.ElevatedButton(
                                "Guardar mano de obra", on_click=self.save_mano_obra
                            ),
                            ft.ElevatedButton(
                                "Subir logo",
                                on_click=lambda _: self.logo_picker.pick_files(allow_multiple=False),
                            ),
                        ]
                    ),
                    ft.Divider(),
                    ft.Text("Inventario actual", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(self.product_table, expand=True, padding=10),
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
        ]

    # ==============================
    # Subida de imagen de producto
    # ==============================
    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return

        file = e.files[0]
        try:
            image_url = None

            # 🖥️ Modo escritorio
            if hasattr(file, "path") and file.path and os.path.exists(file.path):
                print("📁 Subiendo imagen desde ruta local:", file.path)
                image_url = upload_image_to_cloudinary(file.path)

            # 🌐 Modo web
            elif hasattr(file, "get_bytes"):
                print("🌐 Modo web detectado — subiendo imagen desde memoria...")
                file_bytes = file.get_bytes()  # Esto devuelve los bytes del archivo
                image_url = upload_image_to_cloudinary(file_bytes)

            else:
                raise Exception("No se pudo acceder al archivo (sin path ni contenido)")

            # Resultado
            if image_url:
                self.img_path = image_url
                self.page.snack_bar = ft.SnackBar(ft.Text("✅ Imagen subida correctamente"))
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("⚠️ Error al subir imagen"))

        except Exception as ex:
            print("❌ Excepción al subir imagen:", ex)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error: {ex}"))

        self.page.snack_bar.open = True
        self.page.update()


    # ==============================
    # Subida de logo
    # ==============================
    def on_logo_picked(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return

        file = e.files[0]
        try:
            logo_url = None

            if hasattr(file, "path") and file.path and os.path.exists(file.path):
                print("📁 Subiendo logo desde ruta local:", file.path)
                logo_url = upload_image_to_cloudinary(file.path)
            elif hasattr(file, "content") and file.content:
                print("🌐 Subiendo logo desde memoria (web)")
                try:
                    image_bytes = base64.b64decode(file.content)
                except Exception:
                    image_bytes = file.content
                logo_url = upload_image_to_cloudinary(image_bytes)
            else:
                raise Exception("No se pudo acceder al logo")

            if logo_url:
                update_config("logo", logo_url)
                self.page.snack_bar = ft.SnackBar(ft.Text("✅ Logo actualizado correctamente"))
                print(f"✅ Logo actualizado correctamente: {logo_url}")
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("⚠️ Error al subir el logo"))

        except Exception as ex:
            print("❌ Excepción al subir logo:", ex)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error: {ex}"))

        self.page.snack_bar.open = True
        self.page.update()

    # ==============================
    # Agregar producto
    # ==============================
    def add_product(self, e):
        if not all([self.nombre.value, self.tipo.value, self.precio.value]):
            self.page.dialog = ft.AlertDialog(title=ft.Text("Faltan campos obligatorios"))
            self.page.dialog.open = True
            self.page.update()
            return

        add_product(
            self.nombre.value,
            self.tipo.value,
            float(self.precio.value),
            int(self.stock.value or 0),
            self.img_path or "",
        )

        self.page.snack_bar = ft.SnackBar(ft.Text("✅ Producto agregado correctamente"))
        self.page.snack_bar.open = True
        self.page.update()

        self.load_products()

        # Reset campos
        self.nombre.value = ""
        self.tipo.value = None
        self.precio.value = ""
        self.stock.value = ""
        self.img_path = None
        self.update()

    # ==============================
    # Guardar mano de obra
    # ==============================
    def save_mano_obra(self, e):
        valor = self.mano_obra.value.strip()
        if valor.replace(".", "", 1).isdigit():
            update_config("mano_obra", valor)
            self.page.snack_bar = ft.SnackBar(ft.Text("✅ Valor de mano de obra actualizado"))
            self.page.snack_bar.open = True
            self.page.update()

    # ==============================
    # Cargar productos
    # ==============================
    def load_products(self):
        productos = get_all_products()
        self.product_table.rows.clear()
        for p in productos:
            imagen_path = p[5]
            image_widget = (
                ft.Image(src=imagen_path, width=50, height=50, fit=ft.ImageFit.CONTAIN)
                if imagen_path
                else ft.Text("—")
            )

            self.product_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(p[0]))),
                        ft.DataCell(ft.Text(p[1])),
                        ft.DataCell(ft.Text(p[2])),
                        ft.DataCell(ft.Text(f"${p[3]:.2f}")),
                        ft.DataCell(ft.Text(str(p[4]))),
                        ft.DataCell(image_widget),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color="red",
                                tooltip="Eliminar",
                                on_click=lambda e, pid=p[0]: self.delete_product(pid),
                            )
                        ),
                    ]
                )
            )
        self.update()

    # ==============================
    # Eliminar producto
    # ==============================
    def delete_product(self, product_id):
        delete_product(product_id)
        self.load_products()
        self.page.snack_bar = ft.SnackBar(ft.Text("🗑️ Producto eliminado"))
        self.page.snack_bar.open = True
        self.page.update()
