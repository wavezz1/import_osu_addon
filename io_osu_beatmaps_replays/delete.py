import bpy


class OSU_OT_Delete(bpy.types.Operator):
    bl_idname = "osu_importer.delete"
    bl_label = "Delete Imported Data"
    bl_description = "Deletes all imported osu! data and clears references"

    def execute(self, context):
        try:
            # Remove all objects
            bpy.ops.object.select_all(action='DESELECT')
            for obj in bpy.data.objects:
                if obj.name.startswith("Circle") or obj.name.startswith("Slider") or obj.name.startswith(
                        "Spinner") or obj.name == "Cursor":
                    obj.select_set(True)
                    bpy.data.objects.remove(obj, do_unlink=True)

            # Remove all collections created for osu!
            for collection_name in ["Circles", "Sliders", "Slider Balls", "Spinners", "Cursor"]:
                collection = bpy.data.collections.get(collection_name)
                if collection:
                    bpy.data.collections.remove(collection)

            # Remove all geometry node trees used for osu!
            for gn_tree in bpy.data.node_groups:
                if gn_tree.name.startswith("Geometry Nodes"):
                    bpy.data.node_groups.remove(gn_tree)

            self.report({'INFO'}, "All osu! data removed successfully.")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error deleting imported data: {e}")
            return {'CANCELLED'}
