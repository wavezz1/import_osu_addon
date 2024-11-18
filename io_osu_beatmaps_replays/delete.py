import bpy

class OSU_OT_Delete(bpy.types.Operator):
    bl_idname = "osu_importer.delete"
    bl_label = "Delete Imported Data"
    bl_description = "Deletes all imported osu! data and clears references"

    def execute(self, context):
        try:
            # Remove osu!-specific objects
            objects_to_delete = [
                obj for obj in bpy.data.objects if (
                    obj.name.startswith("Circle") or
                    obj.name.startswith("Slider") or
                    obj.name.startswith("Spinner") or
                    obj.name.startswith("Cursor") or
                    obj.name.startswith("OsuAudioSpeaker") or
                    obj.name.startswith("Osu_Gameplay")
                )
            ]
            for obj in objects_to_delete:
                try:
                    bpy.data.objects.remove(obj, do_unlink=True)
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to delete object {obj.name}: {e}")

            # Remove osu!-specific collections
            collections_to_delete = ["Circles", "Sliders", "Slider Balls", "Spinners", "Cursor", "Osu_Gameplay"]
            for collection_name in collections_to_delete:
                collection = bpy.data.collections.get(collection_name)
                if collection:
                    try:
                        bpy.data.collections.remove(collection)
                    except Exception as e:
                        self.report({'WARNING'}, f"Failed to delete collection {collection_name}: {e}")

            # Remove osu!-specific geometry node groups
            node_groups_to_delete = [
                gn_tree for gn_tree in bpy.data.node_groups
                if gn_tree.name.startswith("Geometry Nodes")
                if gn_tree.name.startswith("GN_Osu")
            ]
            for gn_tree in node_groups_to_delete:
                try:
                    bpy.data.node_groups.remove(gn_tree)
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to delete node group {gn_tree.name}: {e}")

            # Remove osu!-specific audio data
            sounds_to_delete = [
                sound for sound in bpy.data.sounds
                if sound.name.startswith("OsuAudioSpeaker")
            ]
            for sound in sounds_to_delete:
                try:
                    bpy.data.sounds.remove(sound)
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to delete sound {sound.name}: {e}")

            # Purge orphan data
            bpy.ops.outliner.orphans_purge(do_recursive=True)

            self.report({'INFO'}, "All osu! data removed successfully, including audio.")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error deleting imported data: {e}")
            return {'CANCELLED'}
