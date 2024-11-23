![Logo](Logo%20v0.2_1280x640.png)
# Blender Importer for osu! Beatmaps and Replays

First and foremost, I don’t know what I’m doing, but I had a goal in mind: importing [osu!](https://osu.ppy.sh/) beatmaps and replays into [Blender](https://www.blender.org/), ready for Geometry Nodes, so I can create some fancy simulation node setups.

That’s where trusty ol’ ChatGPT came into play. The code is roughly based on 90% of GPT’s work and 10% me banging my head against the wall trying to fix things after GPT broke them.

This addon builds on [osrparse](https://github.com/kszlim/osu-replay-parser), which helped with parsing .osr files.

**CAUTION: Replays with the intro skipped are broken due to an issue in osrparse's latest versions. osrparse v6.0.2 is currently used**
## Features

### General Importing
- Supports `.osu` (beatmaps) and `.osr` (replays).
- Imports **all hitobject types**: circles, sliders (with slider balls and ticks), and spinners.

### Replay Data
- Fully animated cursor movements based on replay data.
- Includes keypress states (`k1`, `k2`, `m1`, `m2`).

### Geometry Nodes Integration
The addon utilizes dedicated Geometry Nodes modifiers for osu! elements, making it easy to customize and animate them. All modifiers expose attributes for flexible control.

#### Modifiers
- **Cursor**: Animates paths and keypress states.
- **Circles**: Manages visibility and hit detection.
- **Sliders**: Adjusts duration, repeat count, and completion state.
- **Spinners**: Controls spinner duration and completion.

### Geometry Nodes Integration
- Geometry Nodes modifiers for easy animation and customization:
  - **Cursor**: Animate paths and keypress states.
  - **Circles**: Manage visibility and hit detection.
  - **Sliders**: Adjust properties like duration and repeat count.
  - **Spinners**: Customize duration and spin completion.
- Exposed attributes for flexible setups:
  - `show`, `was_hit`, `slider_duration_frames`, `repeat_count`, `spinner_duration_frames`, and more.

### Flexible Import Options
- **Base Import**: Lightweight meshes optimized for Geometry Nodes.
- **Full Import**: Fully rendered meshes with keyframed visibility. No Geometry Nodes.

### Skin/Shader Options
- Auto-creates basic shaders for imported elements.

### Metadata Display
- Shows detailed beatmap and replay information:
  - Title, artist, difficulty, BPM, total hitobjects, mods used, player name, and more.

### Tools and Transformations
- Flip maps or cursor paths horizontally/vertically.
- Developer tools for quick loading and overriding mods.

### Comprehensive Deletion
- Removes all imported osu! data, including objects, node groups, materials, and sounds.

## Installation

### Step 1: Install the Addon
1. Download the latest `.zip` from the [Releases](https://github.com/wavezz1/import_osu_addon/releases).
2. In Blender, go to `Edit > Preferences > Add-ons`.
3. Click **Install...**, select the downloaded `.zip`, and enable the addon.

### Step 2: Install `osrparse`
1. In the addon preferences, locate the **Install osrparse** button.
2. Click the button to install `osrparse v6.0.2`. If a higher version is installed, it will be replaced.

## Usage

1. Open the **osu! Importer** panel in the sidebar (`N` key).
2. Provide the paths to your `.osu` (beatmap) and `.osr` (replay) files.
3. Configure your import preferences:
   - Select hitobject types (circles, sliders, spinners).
   - Adjust slider options (ticks, balls, resolution).
   - Enable/disable cursor animation and audio import.
4. Click **Import** and enjoy!

## General Geometry Nodes Setup (Blender 4.2)
##### General Overview:
![General Geometry Nodes Setup](geo_setup/geo_nodes_setup_general.png)

##### Circle Hitobjects:
![Circle Geometry Nodes Setup](geo_setup/geo_nodes_setup_circle.png)

##### Sliders:
![Slider Geometry Nodes Setup](geo_setup/geo_nodes_setup_slider.png)

##### Spinners:
![Spinner Geometry Nodes Setup](geo_setup/geo_nodes_setup_spinner.png)
[Download Proof of Concept .blend (Blender 4.2)](blendfile/%5Bblender_4.2%5Dosu_in_blender_proof_of_concept.blend)

## Known Issues

1. **osrparse Limitations**: Skipped replay intros may result in broken animations.
2. **Replay Orientation**: Replays may appear flipped on the Z-axis. You can flip the cursor/map under "Tools".
4. **Slider Ticks**: Slider ticks are not calculated and implemented correctly at the moment.
5. **Crashes**: It propably will crash. Use Quick Load in "Tools" to force a given map path, won't crash then. Adjust in utils/utils.py update_quick_load. 

## Roadmap

### 1.0 Release Goals
The 1.0 release will include all **basic functionalities** required for importing osu! beatmaps and replays into Blender:
- Full support for hitobjects (circles, sliders, spinners, slider balls, approach circles).
- Replay cursor animations.
- Integration of Geometry Nodes for customization.
- Accurate synchronization of audio and replay data.
- Detect flipped maps/cursor.
- Crash fixes.
- Fully optimized import and timeline playback.

### Post-1.0 Features
- **Full Skin Import Support**: Import all visual elements from osu! skins, including custom slider balls, hitcircle overlays, and spinner graphics.

## Support

Feel free to report issues or contribute via the [GitHub repository](https://github.com/wavezz1/import_osu_addon/issues).

## Credits

This addon utilizes [`osrparse`](https://github.com/kszlim/osu-replay-parser) by kszlim and contributors. Blender version 4.2+ is required.

## Ending Words

I only have basic Python knowledge, so please don’t murder me over bad code. Any help to make this work correctly is highly appreciated.

At the end of the day, getting osu! replays and beatmaps into Blender for dynamic 3D replays would be really cool, right?
