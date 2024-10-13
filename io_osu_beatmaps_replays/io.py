# osu_importer/io.py

def load_hitobject_times(osu_file):
    """
    Lädt die Zeiten der HitObjects aus der .osu-Datei.
    Args:
        osu_file (str): Pfad zur .osu-Datei.
    Returns:
        list: Liste der HitObject-Zeiten in Millisekunden.
    """
    hitobject_times = []
    try:
        with open(osu_file, 'r', encoding='utf-8') as file:
            hit_objects_section = False
            for line in file:
                line = line.strip()
                if line == '[HitObjects]':
                    hit_objects_section = True
                    continue
                if hit_objects_section and line:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        time = int(parts[2])
                        hitobject_times.append(time)
    except Exception as e:
        print(f"Fehler beim Laden der HitObject-Zeiten: {e}")
    return hitobject_times

def get_audio_lead_in(osu_file):
    """
    Liest den AudioLeadIn-Wert aus der .osu-Datei.
    Args:
        osu_file (str): Pfad zur .osu-Datei.
    Returns:
        int: AudioLeadIn-Wert in Millisekunden.
    """
    audio_lead_in = 0
    try:
        with open(osu_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.startswith("AudioLeadIn:"):
                    audio_lead_in = int(line.split(':')[1].strip())
                    break
    except Exception as e:
        print(f"Fehler beim Lesen des AudioLeadIns: {e}")
    return audio_lead_in

def get_first_replay_event_time(replay_data):
    """
    Bestimmt die Zeit des ersten Replay-Events, bei dem der Cursor auf dem Bildschirm ist.
    Args:
        replay_data (list): Liste der Replay-Events.
    Returns:
        float: Zeit des ersten relevanten Replay-Events in Millisekunden.
    """
    total_time = 0
    for event in replay_data:
        total_time += event.time_delta
        if event.x != -256 and event.y != -256:
            return total_time
    return total_time  # Falls alle Events bei (-256, -256) sind

def parse_timing_points(osu_file):
    """
    Parst die TimingPoints aus der .osu-Datei.
    Args:
        osu_file (str): Pfad zur .osu-Datei.
    Returns:
        list: Liste der TimingPoints als Tupel (offset, beat_length).
    """
    timing_points = []
    try:
        with open(osu_file, 'r', encoding='utf-8') as file:
            timing_points_section = False
            for line in file:
                line = line.strip()
                if line == '[TimingPoints]':
                    timing_points_section = True
                    continue
                if timing_points_section:
                    if line == '':
                        break  # Ende der TimingPoints-Sektion
                    parts = line.split(',')
                    if len(parts) >= 2:
                        offset = float(parts[0])
                        beat_length = float(parts[1])
                        timing_points.append((offset, beat_length))
    except Exception as e:
        print(f"Fehler beim Parsen der TimingPoints: {e}")
    return timing_points
