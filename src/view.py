import gettext
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject
import requests
import threading

_ = gettext.gettext
N_ = gettext.ngettext


class View:
    def __init__(self, controller):
        self.controller = controller
        self.window = Gtk.Window(title="IPM")
        self.window.set_default_size(1500, 900)
        self.window.connect("destroy", Gtk.main_quit)

        self.cocktail_grid = None
        self.cocktail_error = None

        # Contenedor principal
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.window.add(self.hbox)

        # Menu lateral (izquierda)
        self.lbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.hbox.pack_start(self.lbox, expand=False, fill=False, padding=10)
        self.lbox.set_size_request(300, -1)

        # Menu principal (derecha)
        self.mbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.hbox.pack_start(self.mbox, expand=True, fill=True, padding=10)

        # Titulo TheCocktail
        markup = '<span size="xx-large" font_weight="bold" font_family="Arial">TheCocktail</span>'
        self.label1 = Gtk.Label()
        self.label1.set_markup(markup)
        self.mbox.pack_start(self.label1, expand=False, fill=False, padding=50)

        # Barra de busqueda en la parte superior izquierda
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        search_label = Gtk.Label()
        search_box.pack_start(search_label, expand=False, fill=False, padding=10)
        self.searchentry = Gtk.SearchEntry()
        search_box.pack_start(self.searchentry, expand=False, fill=False, padding=10)
        self.error_label = Gtk.Label("")
        search_box.pack_start(self.error_label, expand=False, fill=False, padding=10)

        # Boton de busqueda
        search_button = Gtk.Button.new_with_label(label = _("Search"))
        search_button.connect("clicked", self.search_clicked)
        search_box.pack_start(search_button, expand=False, fill=False, padding=10)

        search_box.set_margin_top(50)

        self.lbox.pack_start(search_box, expand=False, fill=False, padding=10)

        # Menu grid
        menu_grid = Gtk.Grid()
        menu_grid.set_column_spacing(10)
        self.mbox.pack_start(menu_grid, expand=False, fill=False, padding=10)

        # Etiquetas para mostrar resultados en una cuadricula

        result_label = Gtk.Label()
        result_label.set_markup('<span size="large"><b> </b></span>')
        menu_grid.attach(result_label, 0, 0, 1, 1)

        self.image = Gtk.Image()
        menu_grid.attach(self.image, 1, 0, 1, 3)

        self.cocktail_label = Gtk.Label()
        self.cocktail_label.set_markup('<span size="large"></span>')
        menu_grid.attach(self.cocktail_label, 2, 0, 1, 1)

        self.description_label = Gtk.Label()
        self.description_label.set_markup('<span size="large"></span>')
        self.description_label.set_line_wrap(True)  # Configura el wrap en True
        menu_grid.attach(self.description_label, 2, 1, 1, 1)

        self.glass_label = Gtk.Label()
        self.glass_label.set_markup('<span size="large"></span>')
        menu_grid.attach(self.glass_label, 2, 2, 1, 1)

        self.display_random_cocktails()

    def display_random_cocktails(self, num_cocktails=8):
        self.cocktail_grid = Gtk.Grid()
        self.cocktail_grid.set_column_spacing(250)
        self.cocktail_grid.set_row_spacing(50)
        self.mbox.pack_start(self.cocktail_grid, expand=False, fill=False, padding=10)

        # Meterlo en el bucle para que devuelva un coctel aleatorio en cada iteracion
        random_cocktails = self.controller.get_random_cocktails(num_cocktails)

        for i, cocktail in enumerate(random_cocktails):
            row = i // 4
            col = i % 4
            self.display_cocktail(self.cocktail_grid, row, col, cocktail)

    def display_cocktail(self, grid, row, col, cocktail):

        cocktail_name = cocktail["strDrink"]
        image_url = cocktail["strDrinkThumb"]

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        cocktail_label = Gtk.Label()
        cocktail_label.set_markup(f'<span size="small"><b>{cocktail_name}</b></span>')

        image = Gtk.Image()
        if image_url:
            filename = f"cocktail_{cocktail_name}.jpg"
            image_data = requests.get(image_url, stream=True)
            if image_data.status_code == 200:
                with open(filename, "wb") as f:
                    for chunk in image_data:
                        f.write(chunk)
                image.set_from_file(filename)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 200, 200)
                image.set_from_pixbuf(pixbuf)

        box.pack_start(image, expand=False, fill=False, padding=0)
        box.pack_start(cocktail_label, expand=False, fill=False, padding=5)

        # Agregar el Gtk.Box al Gtk.Grid
        grid.attach(box, col, row, 2, 1)

    def run(self):
        self.window.show_all()
        Gtk.main()

    def search_clicked(self, widget):
        cocktail_name = self.searchentry.get_text()

        # Muestra un mensaje de "cargando" en la interfaz de usuario
        self.cocktail_label.set_text("")
        self.description_label.set_text("")
        self.glass_label.set_text("")
        self.image.set_from_file("")

        # Utiliza threading.Thread para realizar la llamada a la API en un hilo separado
        api_thread = threading.Thread(target=self.fetch_and_update_data, args=(cocktail_name,))
        api_thread.start()

    def new_error(self, text):
        if hasattr(self, "infobar"):
            self.infobar.hide()
            del self.infobar
        self.cocktail_grid.set_visible(False)
        self.infobar = Gtk.InfoBar()
        self.infobar.connect("response", self.on_infobar_response)
        self.infobar.set_show_close_button(True)
        self.infobar.set_message_type(Gtk.MessageType.ERROR)
        self.infobar.show()

        self.mbox.pack_start(self.infobar, expand=False, fill=False, padding=10)
        texto = Gtk.Label(text)
        texto.show()
        content = self.infobar.get_content_area()
        content.add(texto)
        self.infobar.set_message_type(Gtk.MessageType.ERROR)

    def on_infobar_response(self, infobar, respose_id):
        self.infobar.hide()

    def fetch_and_update_data(self, cocktail_name):
        results = self.controller.model.search_cocktail(cocktail_name)
        if results is not None and 'drinks' in results:
            drinks = results['drinks']
            if drinks is not None and len(drinks) > 0:
                # Si volvemos a buscar algo valido se borra el mensaje de error
                self.error_label.set_text("")
                # Oculta el grid de los cocteles
                self.cocktail_grid.set_visible(False)
                drink = results['drinks'][0]
                self.cocktail_label.set_markup(_(f'<span size="large"><b>{drink["strDrink"]}</b></span>'))
                self.description_label.set_markup(_(f'<span size="large"><i>{drink["strInstructions"]}</i></span>'))
                self.glass_label.set_markup(_(f'<span size="large">{drink["strGlass"]}</span>'))
                # Descargar la imagen en un hilo separado
                image_url = drink["strDrinkThumb"]
                if image_url:
                    filename = "cocktail.jpg"
                    download_thread = threading.Thread(target=self.download_image, args=(image_url, filename))
                    download_thread.start()
            else:
                self.new_error(_("ERROR: The cocktail searched does not exist"))

    def download_image(self, image_url, filename):
        image_data = requests.get(image_url, stream=True)
        if image_data.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in image_data:
                    f.write(chunk)

            # Actualiza la imagen en el hilo principal
            GObject.idle_add(self.update_image, filename)

    def update_image(self, filename):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 500, 500)
        self.image.set_from_pixbuf(pixbuf)
