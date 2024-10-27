# import_objects.py

from .circles import CircleCreator
from .slider import SliderCreator
from .spinner import SpinnerCreator
from .utils import create_collection

def import_hitobjects(data_manager, settings, props):
    circles_collection = create_collection("Circles")
    sliders_collection = create_collection("Sliders")
    spinners_collection = create_collection("Spinners")

    global_index = 1

    # Importiere Kreise, wenn die Option aktiviert ist
    if props.import_circles:
        for hitobject in data_manager.hitobjects_processor.circles:
            CircleCreator(hitobject, global_index, circles_collection, settings, data_manager)
            global_index += 1

    # Importiere Slider, wenn die Option aktiviert ist
    if props.import_sliders:
        for hitobject in data_manager.hitobjects_processor.sliders:
            SliderCreator(hitobject, global_index, sliders_collection, settings, data_manager)
            global_index += 1

    # Importiere Spinner, wenn die Option aktiviert ist
    if props.import_spinners:
        for hitobject in data_manager.hitobjects_processor.spinners:
            SpinnerCreator(hitobject, global_index, spinners_collection, settings, data_manager)
            global_index += 1