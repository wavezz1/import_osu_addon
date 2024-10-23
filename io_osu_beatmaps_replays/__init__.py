# __init__.py

bl_info = {
    "name": "osu! Beatmap and Replay Importer",
    "author": "wavezz",
    "version": (0, 4),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > osu! Importer",
    "description": "Imports osu! Beatmaps and Replays into Blender",
    "category": "Import-Export",
    "wiki_url": "https://github.com/wavezz1/import_osu_addon",
    "tracker_url": "https://github.com/wavezz1/import_osu_addon/issues",
    "support": "COMMUNITY",
}

import bpy
import subprocess
import sys
from .ui import OSUImporterProperties, OSU_PT_ImporterPanel, OSU_OT_Import
from bpy.types import Operator, AddonPreferences

classes = (
    OSUImporterProperties,
    OSU_PT_ImporterPanel,
    OSU_OT_Import,
)


# Funktion zum Prüfen, ob osrparse installiert ist
def is_osrparse_installed():
    try:
        import osrparse
        return True
    except ImportError:
        return False


# Operator zum Installieren von osrparse
class OSU_OT_InstallOsrparse(Operator):
    bl_idname = "osu_importer.install_osrparse"
    bl_label = "Install osrparse"
    bl_description = "Installiert osrparse, um das Addon zu verwenden"

    def execute(self, context):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "osrparse"])
            self.report({'INFO'}, "osrparse erfolgreich installiert")
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Fehler bei der Installation von osrparse: {e}")
        return {'FINISHED'}


# Addon Preferences für das Überprüfen und Installieren von osrparse
class OSUImporterPreferences(AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        if is_osrparse_installed():
            layout.label(text="osrparse ist installiert", icon='CHECKMARK')
        else:
            layout.label(text="osrparse ist nicht installiert", icon='ERROR')
            layout.operator("osu_importer.install_osrparse", text="Install osrparse")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(OSU_OT_InstallOsrparse)
    bpy.utils.register_class(OSUImporterPreferences)
    bpy.types.Scene.osu_importer_props = bpy.props.PointerProperty(type=OSUImporterProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.osu_importer_props


if __name__ == "__main__":
    register()
