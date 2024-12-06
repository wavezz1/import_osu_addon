# osu_importer/import_types.py

from abc import ABC, abstractmethod

class BaseImportTypeStrategy(ABC):
    @abstractmethod
    def should_include_osu_gameplay(self, props):
        pass

    @abstractmethod
    def setup_osu_gameplay(self, data_manager, settings, props, collections, operator):
        pass

    # handle_approach_circles(...) , handle_cursor(...), etc if necessary

class BaseMapStrategy(BaseImportTypeStrategy):
    def should_include_osu_gameplay(self, props):
        return props.include_osu_gameplay

    def setup_osu_gameplay(self, data_manager, settings, props, collections, operator):
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
        return False

    def setup_osu_gameplay(self, data_manager, settings, props, collections, operator):
        pass

# class CustomMapStrategy(BaseImportTypeStrategy):
#     ...

IMPORT_TYPE_STRATEGIES = {
    'BASE': BaseMapStrategy(),
    'FULL': FullMapStrategy(),
    # Add Import-Types
}

def get_import_strategy(import_type):
    return IMPORT_TYPE_STRATEGIES.get(import_type, FullMapStrategy())
