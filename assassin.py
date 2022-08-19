"""blablabla"""
import json
import pandas as pd
# pylint: disable=line-too-long
class Assassin:
    """BLABLABLA!"""
    def __init__(self):
        """initialization"""
    def update_values(self):
        """update the values file"""
        dfs = self._get_dataframes()
        values = self._curate_values(dfs)
        with open("values.json", "w", encoding="UTF-8") as data_file:
            json.dump(values, data_file, indent=4)
        return {'status': 'success'}

    def _curate_values(self, dfs):
        """reshape the dataframe into a neat json object"""
        values_json = [json.loads(df.to_json()) for df in dfs]
        # values_json.pop(0)
        rarities = ["Info", "Dream", "Mythic", "Exotic", "Legendary", "Rare", "Common", "???"]
        values = {}
        for i, category in enumerate(values_json):
            print(i)
            for key, value in category["Unnamed: 2"].items():
                if not value or value == "NAME":
                    continue
                values[value] = {
                    "demand": category["Unnamed: 3"][key],
                    "value": category["Unnamed: 4"][key],
                    "obtain": category["Unnamed: 5"][key],
                    "origin": category["Unnamed: 7"][key],
                    "rarity": rarities[i],
                    "exoticvalue": self._get_exotic_value(rarities[i], category["Unnamed: 4"][key])
                }
        return values

    def _get_exotic_value(self, rarity: str, value: str):
        """get the exotic value from a given value"""
        try:
            value = int(value)
        except (ValueError, TypeError):
            return "Unknown"
        if rarity in {"Dream", "Mythic", "Exotic"}:
            return value
        if rarity == "Legendary":
            return value[0]/6
        if rarity == "Rare":
            return value[0]/30
        if rarity == "Common":
            return value[0]/120

    def _get_dataframes(self):
        """get the dataframes"""
        return pd.read_html("https://docs.google.com/spreadsheets/d/e/2PACX-1vTSEzyLExxmRJE-YgEkG82hCEzikPPU0dG-EMY3vy7pSYiCgFQofWXpXypyuRkejYlBVwwkOSdpitTI/pubhtml", encoding='utf8')
