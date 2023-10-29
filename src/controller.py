from view import View
from model import Model

class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self)

    def run(self):
        self.view.run()
    
    # Hacer la llamada a get_random_cocktails AQUI implementando concurrencia
    def get_random_cocktails(self, num_cocktails=8):
        return self.model.get_random_cocktails(num_cocktails)
    