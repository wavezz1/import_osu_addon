# import_objects.py

import bpy
from .circle import CircleCreator
from .slider import SliderCreator
from .spinner import SpinnerCreator
from .hitobjects import HitObjectsProcessor
from .utils import create_collection

def import_hitobjects(osu_parser, final_offset_frames, speed_multiplier):
    circles_collection = create_collection("Circles")
    sliders_collection = create_collection("Sliders")
    spinners_collection = create_collection("Spinners")

    processor = HitObjectsProcessor(osu_parser)

    settings = {
        'speed_multiplier': speed_multiplier,
        'early_frames': 5,
        # Weitere Einstellungen
    }

    global_index = 1
    for circle in processor.circles:
        CircleCreator(circle, global_index, circles_collection, final_offset_frames, settings)
        global_index += 1

    for slider in processor.sliders:
        SliderCreator(slider, global_index, sliders_collection, final_offset_frames, settings, osu_parser)
        global_index += 1

    for spinner in processor.spinners:
        SpinnerCreator(spinner, global_index, spinners_collection, final_offset_frames, settings)
        global_index += 1
