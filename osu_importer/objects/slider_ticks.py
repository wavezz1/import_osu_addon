import bpy
from osu_importer.utils.utils import evaluate_curve_at_t, tag_imported

class SliderTicksCreator:
    def __init__(self, slider, slider_duration_ms, repeat_count, sliders_collection, settings, import_type):
        self.slider = slider
        self.slider_duration_ms = slider_duration_ms
        self.repeat_count = repeat_count
        self.sliders_collection = sliders_collection
        self.settings = settings
        self.import_type = import_type
        self.tick_interval_ms = 100

    def create(self):
        tick_interval_ms = self.settings.get('tick_interval_ms', self.tick_interval_ms)
        total_ticks = int(self.slider_duration_ms / tick_interval_ms) * self.repeat_count

        for tick in range(total_ticks):
            t = (tick * tick_interval_ms) / (self.slider_duration_ms * self.repeat_count)
            t = min(max(t, 0.0), 1.0)

            tick_position = evaluate_curve_at_t(self.slider, t)

            if self.import_type == 'FULL':
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(tick_position.x, tick_position.y, tick_position.z))
                tick_obj = bpy.context.object
            elif self.import_type == 'BASE':
                mesh = bpy.data.meshes.new(f"{self.slider.name}_tick_{tick}")
                mesh.vertices.add(1)
                mesh.vertices[0].co = (0, 0, 0)
                tick_obj = bpy.data.objects.new(f"{self.slider.name}_tick_{tick}", mesh)
                tick_obj.location = tick_position

            tick_obj.name = f"{self.slider.name}_tick_{tick}"

            tag_imported(tick_obj)

            self.sliders_collection.objects.link(tick_obj)
            if tick_obj.users_collection:
                for col in tick_obj.users_collection:
                    if col != self.sliders_collection:
                        col.objects.unlink(tick_obj)

        print(f"Slider ticks created for {self.slider.name}")
