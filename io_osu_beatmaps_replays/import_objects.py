# import_objects.py

from .circles import CircleCreator
from .slider import SliderCreator
from .spinner import SpinnerCreator
from .hitobjects import HitObjectsProcessor
from .utils import create_collection

def import_hitobjects(data_manager, speed_multiplier):
    circles_collection = create_collection("Circles")
    sliders_collection = create_collection("Sliders")
    spinners_collection = create_collection("Spinners")

    processor = HitObjectsProcessor(data_manager.osu_parser)

    settings = {
        'speed_multiplier': speed_multiplier,
        'audio_lead_in': data_manager.beatmap_info.get("audio_lead_in", 0),
    }

    global_index = 1
    for circle in processor.circles:
        CircleCreator(circle, global_index, circles_collection, settings, data_manager)
        global_index += 1

    for slider in processor.sliders:
        SliderCreator(slider, global_index, sliders_collection, settings, data_manager)
        global_index += 1

    for spinner in processor.spinners:
        SpinnerCreator(spinner, global_index, spinners_collection, settings, data_manager)
        global_index += 1
