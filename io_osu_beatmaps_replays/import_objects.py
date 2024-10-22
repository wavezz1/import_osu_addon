# import_objects.py

import bpy
from .circles import CircleCreator
from .slider import SliderCreator
from .spinner import SpinnerCreator
from .hitobjects import HitObjectsProcessor
from .utils import create_collection

def import_hitobjects(osu_parser, speed_multiplier):

    circles_collection = create_collection("Circles")
    sliders_collection = create_collection("Sliders")
    spinners_collection = create_collection("Spinners")

    processor = HitObjectsProcessor(osu_parser)

    settings = {
        'speed_multiplier': speed_multiplier,
    }

    global_index = 1
    for circle in processor.circles:
        CircleCreator(circle, global_index, circles_collection, settings)
        global_index += 1

    for slider in processor.sliders:
        SliderCreator(slider, global_index, sliders_collection, settings, osu_parser)
        global_index += 1

    for spinner in processor.spinners:
        SpinnerCreator(spinner, global_index, spinners_collection, settings)
        global_index += 1
