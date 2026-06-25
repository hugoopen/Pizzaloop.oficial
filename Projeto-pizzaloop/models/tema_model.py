import os
import json


class TemaModel:
    _ARQUIVO = os.path.join(os.path.dirname(__file__), "..", ".tema.json")

    def __init__(self):
        self.tema = self._carregar()

    def _carregar(self):
        try:
            with open(self._ARQUIVO, "r") as f:
                return json.load(f).get("tema", "light")
        except Exception:
            return "light"

    def salvar(self, novo_tema: str):
        self.tema = novo_tema
        try:
            with open(self._ARQUIVO, "w") as f:
                json.dump({"tema": novo_tema}, f)
        except Exception:
            pass