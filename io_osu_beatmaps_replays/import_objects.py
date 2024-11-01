# import_objects.py

from .circles import CircleCreator
from .slider import SliderCreator
from .spinner import SpinnerCreator
from .cursor import CursorCreator
from .utils import create_collection


def import_hitobjects(data_manager, settings, props):
    circles_collection = create_collection("Circles")
    sliders_collection = create_collection("Sliders")
    slider_balls_collection = create_collection("Slider Balls")  # Hinzugefügt
    spinners_collection = create_collection("Spinners")
    cursor_collection = create_collection("Cursor")

    global_index = 1

    if props.import_circles:
        for hitobject in data_manager.hitobjects_processor.circles:
            CircleCreator(hitobject, global_index, circles_collection, settings, data_manager)
            global_index += 1

    if props.import_sliders:
        for hitobject in data_manager.hitobjects_processor.sliders:
            SliderCreator(hitobject, global_index, sliders_collection, slider_balls_collection, settings, data_manager)
            global_index += 1

    if props.import_spinners:
        for hitobject in data_manager.hitobjects_processor.spinners:
            SpinnerCreator(hitobject, global_index, spinners_collection, settings, data_manager)
            global_index += 1

    if props.import_cursors:
        cursor_creator = CursorCreator(cursor_collection, settings, data_manager)
        cursor_creator.animate_cursor()