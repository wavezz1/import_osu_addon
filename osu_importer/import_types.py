# osu_importer/import_types.py

from abc import ABC, abstractmethod

class BaseImportTypeStrategy(ABC):
    @abstractmethod
    def should_include_osu_gameplay(self, props):
        """Gibt zurück, ob Osu_Gameplay hinzugefügt werden soll."""
        pass

    @abstractmethod
    def setup_osu_gameplay(self, data_manager, settings, props, collections, operator):
        """Fügt Osu_Gameplay hinzu, falls nötig."""
        pass

    # Hier könntest du weitere abstrakte Methoden hinzufügen, wenn du weitere Unterschiede bei anderen Import-Typen brauchst.
    # Zum Beispiel handle_approach_circles(...) oder handle_cursor(...), je nachdem was du dynamisch gestalten möchtest.

class BaseMapStrategy(BaseImportTypeStrategy):
    def should_include_osu_gameplay(self, props):
        # Im BASE-Modus soll Include Osu_Gameplay das Verhalten bestimmen
        return props.include_osu_gameplay

    def setup_osu_gameplay(self, data_manager, settings, props, collections, operator):
        # Im BASE-Modus wird Osu_Gameplay tatsächlich eingerichtet, falls include_osu_gameplay=True ist.
        # Hier übernehmen wir die Logik aus import_objects.py, die vorher unter if import_type == 'BASE' stand.
        from .import_objects import setup_osu_gameplay_collections_and_materials
        from .utils.utils import tag_imported

        gameplay_collection = setup_osu_gameplay_collections_and_materials(
            cursor=collections.get("Cursor"),
            approach_circle=collections.get("Approach Circles"),
            circles=collections.get("Circles"),
            sliders=collections.get("Sliders"),
            slider_balls=collections.get("Slider Balls"),
            spinners=collections.get("Spinners"),
            slider_heads_tails=collections.get("Slider Heads Tails"),
            operator=operator
        )

        if gameplay_collection:
            tag_imported(gameplay_collection)

class FullMapStrategy(BaseImportTypeStrategy):
    def should_include_osu_gameplay(self, props):
        # Im FULL-Modus wollen wir beispielsweise kein Osu_Gameplay hinzufügen
        # oder es verhält sich anders. Hier mal als Beispiel: kein Gameplay.
        return False

    def setup_osu_gameplay(self, data_manager, settings, props, collections, operator):
        # Im FULL-Modus wird kein Osu_Gameplay eingerichtet, daher tun wir hier nichts.
        pass

# Hier kannst du weitere Strategien hinzufügen, z.B. für einen CUSTOM-Importtype:
# class CustomMapStrategy(BaseImportTypeStrategy):
#     ...

IMPORT_TYPE_STRATEGIES = {
    'BASE': BaseMapStrategy(),
    'FULL': FullMapStrategy(),
    # Weitere Import-Typen hier einfügen
}

def get_import_strategy(import_type):
    # Falls der import_type nicht gefunden wird, nehmen wir FULL als Default
    return IMPORT_TYPE_STRATEGIES.get(import_type, FullMapStrategy())
