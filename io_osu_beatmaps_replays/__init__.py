# __init__.py

bl_info = {
    "name": "osu! Beatmap and Replay Importer",
    "author": "wavezz",
    "version": (0, 6),
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
import importlib.metadata
from .ui import OSUImporterProperties, OSU_PT_ImporterPanel, OSU_OT_Import
from bpy.types import Operator, AddonPreferences

classes = (
    OSUImporterProperties,
    OSU_PT_ImporterPanel,
    OSU_OT_Import,
)

def is_osrparse_installed():
    try:
        import osrparse
        version = importlib.metadata.version('osrparse')
        return version
    except ImportError:
        return None

class OSU_OT_InstallOsrparse(Operator):
    bl_idname = "osu_importer.install_osrparse"
    bl_label = "Install osrparse 6.0.2"
    bl_description = "Installs osrparse 6.0.2 or replaces a higher version"

    def execute(self, context):
        try:
            installed_version = is_osrparse_installed()
            if installed_version and installed_version.startswith("7"):
                subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "osrparse"])
                self.report({'INFO'}, f"osrparse {installed_version} uninstalled")

            subprocess.check_call([sys.executable, "-m", "pip", "install", "osrparse==6.0.2"])
            self.report({'INFO'}, "osrparse 6.0.2 installed successfully")
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Error installing osrparse: {e}")
        return {'FINISHED'}

class OSUImporterPreferences(AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        installed_version = is_osrparse_installed()

        if installed_version == "6.0.2":
            layout.label(text="osrparse 6.0.2 is installed", icon='CHECKMARK')
        else:
            if installed_version and installed_version.startswith("7"):
                layout.label(text=f"osrparse {installed_version} installed (higher version)", icon='ERROR')
            else:
                layout.label(text="osrparse not installed", icon='ERROR')
            layout.operator("osu_importer.install_osrparse", text="Install osrparse 6.0.2")

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(OSU_OT_InstallOsrparse)
    bpy.utils.register_class(OSUImporterPreferences)
    bpy.types.Scene.osu_importer_props = bpy.props.PointerProperty(type=OSUImporterProperties)

def unregister():
    bpy.utils.unregister_class(OSU_OT_InstallOsrparse)
    bpy.utils.unregister_class(OSUImporterPreferences)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.osu_importer_props

if __name__ == "__main__":
    register()
