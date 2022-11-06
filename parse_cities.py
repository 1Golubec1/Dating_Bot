import json


class Parse_cities:
    def __init__(self, filename):
        self.cities_file = open("russian-cities.json", "r", encoding="UTF-8")

    def get_cities(self):
        cities = json.load(self.cities_file)
        cities_list = []

        for i in cities:
            cities_list.append(i["name"])

        return cities_list
