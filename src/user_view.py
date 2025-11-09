import flet as ft
import os
from database import get_all_products, get_config
from pdf_utils import generar_pdf


class UserView(ft.View):
    def __init__(self, page):
        super().__init__(route="/user")
        self.page = page
        self.page.title = "Catálogo CCTV"

        # Forzar pantalla completa
        self.page.window_maximized = True

        self.carrito = []
        self.total = 0.0
        self.mano_obra = float(get_config("mano_obra") or 150)

        # Creación de SnackBar
        self.snack_bar = ft.SnackBar(
            content=ft.Text("", text_align=ft.TextAlign.CENTER),
            bgcolor=ft.Colors.GREEN_400,
            show_close_icon=True,
            duration=2000,
        )

        # Campo de nombre del cliente
        self.nombre_cliente = ft.TextField(label="Nombre del Cliente", width=300)

        # === Contenedor de productos con scroll ===
        self.productos_container = ft.ResponsiveRow(
            spacing=10, run_spacing=10, vertical_alignment=ft.CrossAxisAlignment.START
        )
        self.productos_scroll = ft.Container(
            content=ft.Column(
                [self.productos_container], scroll=ft.ScrollMode.AUTO, expand=True
            ),
            expand=True,
        )

        # Cargar catálogo
        self.load_catalog()

        # === Carrito ===
        self.carrito_text = ft.Text("Carrito vacío", size=16)
        self.total_text = ft.Text("Total: $0.00", size=20, weight=ft.FontWeight.BOLD)
        self.generar_btn = ft.ElevatedButton(
            "Generar PDF",
            on_click=self.generar_pdf,
            disabled=True,
            icon=ft.Icons.PICTURE_AS_PDF_SHARP,
        )

        # === Layout principal ===
        self.controls = [
            ft.AppBar(
                title=ft.Text("Catálogo de Productos"),
                bgcolor=ft.Colors.INDIGO_200,
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/")
                ),
            ),
            ft.Row(
                [
                    # --- Columna izquierda: Catálogo ---
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Catálogo disponible",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                self.productos_scroll,
                            ],
                            expand=True,
                        ),
                        expand=True,
                    ),
                    # --- Columna derecha: Carrito con scroll ---
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Resumen de Compras",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            self.nombre_cliente,
                                            ft.Divider(),
                                            self.carrito_text,
                                            ft.Divider(),
                                            self.total_text,
                                            self.generar_btn,
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                        horizontal_alignment=ft.CrossAxisAlignment.START,
                                        scroll=ft.ScrollMode.AUTO,
                                    ),
                                    expand=True,
                                    height=self.page.window_height - 200,
                                ),
                            ]
                        ),
                        width=350,
                        padding=10,
                    ),
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            self.snack_bar,  # Snack Bar en el Layout
        ]

    # ==============================
    # CARGAR CATÁLOGO
    # ==============================
    def load_catalog(self):
        productos = get_all_products()
        self.productos_container.controls.clear()
        base_dir = os.path.join(os.getcwd(), "storage", "images")
        os.makedirs(base_dir, exist_ok=True)

        for p in productos:
            producto_id, nombre, tipo, precio, stock, imagen_rel = p

            # Si la ruta es una URL (Cloudinary u otra), usarla directamente
            if imagen_rel and (
                imagen_rel.startswith("http://") or imagen_rel.startswith("https://")
            ):
                imagen_src = imagen_rel
            else:
                # Si es ruta absoluta, usarla; si es relativa, buscar en storage/images
                imagen_src = (
                    imagen_rel
                    if imagen_rel and os.path.isabs(imagen_rel)
                    else os.path.join(base_dir, os.path.basename(imagen_rel))
                    if imagen_rel
                    else None
                )

            # Mostrar imagen si existe (local) o si es URL válida
            if imagen_src and (
                imagen_src.startswith("http") or os.path.exists(imagen_src)
            ):
                img_widget = ft.Image(
                    src=imagen_src, width=180, height=140, fit=ft.ImageFit.CONTAIN
                )
            else:
                img_widget = ft.Icon(
                    name=ft.Icons.IMAGE_NOT_SUPPORTED,
                    size=60,
                    color=ft.Colors.GREY,
                )

            producto_card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=img_widget,
                                alignment=ft.alignment.center,
                                height=150,
                            ),
                            ft.Text(
                                nombre,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(f"Tipo: {tipo}", size=14, text_align=ft.TextAlign.CENTER),
                            ft.Text(
                                f"Precio: ${precio:.2f}",
                                size=14,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(f"Stock: {stock}", size=14, text_align=ft.TextAlign.CENTER),
                            ft.IconButton(
                                icon=ft.Icons.ADD_SHOPPING_CART,
                                tooltip="Agregar al carrito",
                                on_click=lambda e, item=p: self.add_to_cart(item),
                            ),
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=10,
                    width=230,
                    height=320,
                    alignment=ft.alignment.center,
                ),
                elevation=3,
                margin=10,
            )

            self.productos_container.controls.append(
                ft.Container(
                    content=producto_card,
                    col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                    alignment=ft.alignment.center,
                )
            )

        self.update()

    # ==============================
    # AGREGAR PRODUCTO AL CARRITO
    # ==============================
    def add_to_cart(self, producto):
        self.carrito.append(producto)
        self.update_cart()

    # ==============================
    # ACTUALIZAR CARRITO
    # ==============================
    def update_cart(self):
        if not self.carrito:
            self.carrito_text.value = "Carrito vacío"
            self.total = 0.0
            self.total_text.value = "Total: $0.00"
            self.generar_btn.disabled = True
        else:
            desglose = []
            total_productos = 0
            camaras = 0
            for item in self.carrito:
                desglose.append(f"{item[1]} — ${item[3]:.2f}")
                total_productos += item[3]
                if item[2].lower() == "cámara":
                    camaras += 1

            total_mano_obra = camaras * self.mano_obra
            total_final = total_productos + total_mano_obra

            self.carrito_text.value = "\n".join(desglose)
            self.total_text.value = (
                f"Subtotal: ${total_productos:.2f}\n"
                f"Mano de obra ({camaras} cámaras): ${total_mano_obra:.2f}\n"
                f"Total: ${total_final:.2f}"
            )
            self.total = total_final
            self.generar_btn.disabled = False

        self.update()

    # ==============================
    # GENERAR PDF (SnackBar funcional)
    # ==============================
    def generar_pdf(self, e):
        if not self.nombre_cliente.value.strip():
            dlg = ft.AlertDialog(title=ft.Text("Por favor ingrese el nombre del cliente"))
            self.dialog = dlg
            dlg.open = True
            self.update()
            return

        try:
            generar_pdf(self.nombre_cliente.value.strip(), self.carrito, self.mano_obra)
            self.snack_bar.content = ft.Text(
                "PDF generado correctamente en carpeta Reports",
                text_align=ft.TextAlign.CENTER,
            )
            self.snack_bar.bgcolor = ft.Colors.GREEN_400
            self.snack_bar.open = True
            self.update()
        except Exception as ex:
            self.snack_bar.content = ft.Text(
                f"Error al generar PDF: {ex}", text_align=ft.TextAlign.CENTER
            )
            self.snack_bar.bgcolor = ft.Colors.RED_400
            self.snack_bar.open = True
            self.update()
