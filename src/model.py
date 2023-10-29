import requests


class Model:
    def search_cocktail(self, cocktail_name):
        url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={cocktail_name}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    # Modificar para que devuelva un solo cóctel de forma aleatoria
    def get_random_cocktails(self, num_cocktails=8):
        url = f"https://www.thecocktaildb.com/api/json/v1/1/random.php"
        random_cocktails = []

        for _ in range(num_cocktails):
            response = requests.get(url)
            data = response.json()
            if "drinks" in data:
                random_cocktails.append(data["drinks"][0])

        return random_cocktails
