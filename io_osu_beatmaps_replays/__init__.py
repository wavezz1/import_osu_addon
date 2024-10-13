# osu_importer/__init__.py

bl_info = {
    "name": "osu! Beatmap and Replay Importer",
    "author": "wavezz",
    "version": (0, 1),
    "blender": (2, 80, 0),  # Bitte Blender-Version entsprechend anpassen
    "location": "View3D > Sidebar > osu! Importer",
    "description": "Imports osu! Beatmaps and Replays into Blender",
    "category": "Import-Export",
    "wiki_url": "https://github.com/dein-benutzername/osu_importer",
    "tracker_url": "https://github.com/dein-benutzername/osu_importer/issues",
    "support": "COMMUNITY",
}

import bpy

from .properties import OSUImporterProperties
from .operators import OSU_OT_Import
from .panels import OSU_PT_ImporterPanel

classes = (
    OSUImporterProperties,
    OSU_OT_Import,
    OSU_PT_ImporterPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.osu_importer_props = bpy.props.PointerProperty(type=OSUImporterProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.osu_importer_props

if __name__ == "__main__":
    register()
