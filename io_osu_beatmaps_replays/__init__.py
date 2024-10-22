# osu_importer/__init__.py

bl_info = {
    "name": "osu! Beatmap and Replay Importer",
    "author": "wavezz",
    "version": (0, 3),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > osu! Importer",
    "description": "Imports osu! Beatmaps and Replays into Blender",
    "category": "Import-Export",
    "wiki_url": "https://github.com/wavezz1/import_osu_addon",
    "tracker_url": "https://github.com/wavezz1/import_osu_addon/issues",
    "support": "COMMUNITY",
}

import bpy

from .ui import OSUImporterProperties, OSU_PT_ImporterPanel, OSU_OT_Import

classes = (
    OSUImporterProperties,
    OSU_PT_ImporterPanel,
    OSU_OT_Import,
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