try:
    from calais import Calais
except ImportError:  # pragma: no cover
    Calais = None  # NOQA


if Calais is not None:
    def process_calais(content, key):
        calais = Calais(key)
        response = calais.analyze(content)

        people = [entity["name"] for entity in getattr(response, "entities", []) if entity["_type"] == "Person"]

        return {"people": people}
