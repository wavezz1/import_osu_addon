# osu_importer/utils.py

import bpy

def get_ms_per_frame():
    """
    Berechnet die Anzahl der Millisekunden pro Frame basierend auf der aktuellen FPS-Einstellung der Szene.
    Returns:
        float: Millisekunden pro Frame.
    """
    fps = bpy.context.scene.render.fps
    return 1000 / fps  # Millisekunden pro Frame

def create_collection(name):
    """
    Erstellt eine neue Collection mit dem gegebenen Namen oder gibt eine vorhandene zurück.
    Args:
        name (str): Der Name der Collection.
    Returns:
        bpy.types.Collection: Die erstellte oder vorhandene Collection.
    """
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection

def shift_cursor_keyframes(cursor_object_name, offset_ms):
    """
    Verschiebt die Keyframes des Cursors um den angegebenen Offset in Millisekunden.
    Args:
        cursor_object_name (str): Der Name des Cursor-Objekts.
        offset_ms (float): Der Offset in Millisekunden.
    """
    cursor = bpy.data.objects.get(cursor_object_name)
    if cursor is None:
        print(f"Objekt '{cursor_object_name}' nicht gefunden.")
        return

    if cursor.animation_data is None or cursor.animation_data.action is None:
        print(f"Keine Animation gefunden für Objekt '{cursor_object_name}'.")
        return

    action = cursor.animation_data.action
    fcurves = action.fcurves

    frame_offset = offset_ms / get_ms_per_frame()

    for fcurve in fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.co.x += frame_offset
            keyframe.handle_left.x += frame_offset
            keyframe.handle_right.x += frame_offset

        # Aktualisiere die FCurve
        fcurve.update()
