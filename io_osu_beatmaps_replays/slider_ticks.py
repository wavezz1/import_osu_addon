# slider_ticks.py
import bpy
from .utils import evaluate_curve_at_t
from .constants import SCALE_FACTOR

class SliderTicksCreator:
    def __init__(self, slider, slider_duration_ms, repeat_count, sliders_collection, settings):
        self.slider = slider
        self.slider_duration_ms = slider_duration_ms
        self.repeat_count = repeat_count
        self.sliders_collection = sliders_collection
        self.settings = settings
        self.tick_interval_ms = 100  # Default-Wert für Slider-Ticks

    def create(self):
        tick_interval_ms = self.settings.get('tick_interval_ms', self.tick_interval_ms)
        total_ticks = int(self.slider_duration_ms / tick_interval_ms) * self.repeat_count

        for tick in range(total_ticks):
            t = (tick * tick_interval_ms) / (self.slider_duration_ms * self.repeat_count)
            t = min(max(t, 0.0), 1.0)

            tick_position = evaluate_curve_at_t(self.slider, t)

            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05 * SCALE_FACTOR, location=(tick_position.x, tick_position.y, tick_position.z))
            tick_obj = bpy.context.object
            tick_obj.name = f"{self.slider.name}_tick_{tick}"

            self.sliders_collection.objects.link(tick_obj)
            bpy.context.collection.objects.unlink(tick_obj)

        print(f"Slider ticks created for {self.slider.name}")
