import bpy

class OSU_OT_Delete(bpy.types.Operator):
    bl_idname = "osu_importer.delete"
    bl_label = "Delete Imported Data"
    bl_description = "Deletes all imported osu! data and clears references"

    def execute(self, context):
        try:
            objects_to_delete = [obj for obj in bpy.data.objects if obj.get("osu_imported")]
            for obj in objects_to_delete:
                try:
                    bpy.data.objects.remove(obj, do_unlink=True)
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to delete object {obj.name}: {e}")

            collections_to_delete = [
                collection for collection in bpy.data.collections
                if collection.get("osu_imported")
            ]
            for collection in collections_to_delete:
                try:
                    bpy.data.collections.remove(collection)
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to delete collection {collection.name}: {e}")

            node_groups_to_delete = [
                gn_tree for gn_tree in bpy.data.node_groups
                if gn_tree.get("osu_imported")
            ]
            for gn_tree in node_groups_to_delete:
                try:
                    bpy.data.node_groups.remove(gn_tree)
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to delete node group {gn_tree.name}: {e}")

            sounds_to_delete = [
                sound for sound in bpy.data.sounds
                if sound.get("osu_imported")
            ]
            for sound in sounds_to_delete:
                try:
                    bpy.data.sounds.remove(sound)
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to delete sound {sound.name}: {e}")

            materials_to_delete = [
                material for material in bpy.data.materials
                if material.get("osu_imported")
            ]
            for material in materials_to_delete:
                try:
                    bpy.data.materials.remove(material)
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to delete material {material.name}: {e}")


            bpy.ops.outliner.orphans_purge(do_recursive=True)

            self.report({'INFO'}, "All tagged osu! data removed successfully, including audio.")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error deleting imported data: {e}")
            return {'CANCELLED'}
