# import_objects.py

from .circles import CircleCreator
from .slider import SliderCreator
from .spinner import SpinnerCreator
from .cursor import CursorCreator
from .utils import create_collection, timeit


def import_hitobjects(data_manager, settings, props):
    with timeit("Erstellen der Sammlungen"):
        circles_collection = create_collection("Circles")
        sliders_collection = create_collection("Sliders")
        slider_balls_collection = create_collection("Slider Balls")  # Hinzugefügt
        spinners_collection = create_collection("Spinners")
        cursor_collection = create_collection("Cursor")

        global_index = 1

        import_type = settings.get('import_type', 'FULL')

        if props.import_circles:
            for hitobject in data_manager.hitobjects_processor.circles:
                CircleCreator(hitobject, global_index, circles_collection, settings, data_manager, import_type)
                global_index += 1

        if props.import_sliders:
            for hitobject in data_manager.hitobjects_processor.sliders:
                SliderCreator(hitobject, global_index, sliders_collection, slider_balls_collection, settings, data_manager, import_type)
                global_index += 1

        if props.import_spinners:
            for hitobject in data_manager.hitobjects_processor.spinners:
                SpinnerCreator(hitobject, global_index, spinners_collection, settings, data_manager, import_type)
                global_index += 1

        if props.import_cursors and import_type == 'BASE':
            cursor_creator = CursorCreator(cursor_collection, settings, data_manager, import_type)
            cursor_creator.animate_cursor()
        elif props.import_cursors and import_type == 'FULL':
            cursor_creator = CursorCreator(cursor_collection, settings, data_manager, import_type)
            cursor_creator.animate_cursor_full()
