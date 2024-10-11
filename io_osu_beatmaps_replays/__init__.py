# osu_importer/__init__.py

import bpy

from .bl_info import bl_info

from .properties import OSUImporterProperties
from .operators import OSU_OT_Import, OSU_OT_AdjustCursorOffset
from .panels import OSU_PT_ImporterPanel
from .utils import register_utils, unregister_utils  # Falls nötig

classes = (
    OSUImporterProperties,
    OSU_OT_Import,
    OSU_OT_AdjustCursorOffset,
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
