# Blender Importer for osu! Beatmaps and Replays

First and foremost, I don’t know what I’m doing, but I had a goal: importing [`osu!`](https://osu.ppy.sh/) beatmaps and replays into [`Blender`](https://www.blender.org/), ready for Geometry Nodes, so I can create some fancy simulation node setups.

That’s where trusty ol’ ChatGPT came into play. The code is roughly based on 90% of GPT’s work and 10% me banging my head against the wall trying to fix things after GPT broke them.

This addon builds on [`osrparse`](https://github.com/kszlim/osu-replay-parser), which helped with parsing `.osr` files.

**CAUTION: Replays with the intro skipped are broken due to an issue in osrparse's latest versions. osrparse v6.0.2 is currently used**

## What it Does

This addon imports a comprehensive version of both the replay and the beatmap, applying Geometry Nodes modifiers that store attributes based on parsed keyframes and values.

### Key Features

- **Hitobject Importing:**
  - **Circles:** Import and visualize circle hitobjects.
  - **Sliders:** Import sliders with options for slider ticks and slider balls.
  - **Spinners:** Import spinner hitobjects.
  
- **Cursor Movements:**
  - Animate the cursor based on replay data, reflecting key presses and mouse movements.
  
- **Geometry Nodes Integration:**
  - Each hitobject type (`Cursor`, `Circle`, `Slider`, `Spinner`) comes with a dedicated Geometry Nodes modifier.
  
- **Audio Integration:**
  - Import the associated audio track as a speaker object in Blender.

## Installation

1. **Download the Addon:**
   - Download the `.zip` file of this addon from the [Releases](https://github.com/wavezz1/import_osu_addon/releases) page.

2. **Install the Addon in Blender:**
   - Open Blender.
   - Go to `Edit` > `Preferences` > `Add-ons`.
   - Click `Install...` at the top-right corner.
   - Select the downloaded `.zip` file.
   - Enable the addon by checking the box next to its name.

3. **Install `osrparse`:**
   - Within the addon preferences, click the **"Install osrparse"** button if you don't have it installed already. This ensures that the addon can correctly parse `.osr` replay files.
   
## Usage

1. **Access the osu! Importer Panel:**
   - In the 3D Viewport, open the Sidebar (`N` key).
   - Navigate to the **"osu! Importer"** tab.

2. **Select Files:**
   - **Beatmap (.osu) File:** Click the file selector and choose your `.osu` beatmap file.
   - **Replay (.osr) File:** Click the file selector and choose your `.osr` replay file.

3. **Configure Import Options:**
   - **Hit Objects:**
     - **Circles:** Toggle to import circle hitobjects.
     - **Sliders:** Toggle to import slider hitobjects.
     - **Spinners:** Toggle to import spinner hitobjects.
   - **Slider Options:** *(Visible only if sliders are enabled)*
     - **Slider Ticks:** Toggle to import slider ticks.
     - **Slider Balls:** Toggle to import slider balls.
     - **Slider Resolution:** Adjust the smoothness of sliders (higher values = smoother but more performance-intensive).
   - **Replay Options:**
     - **Cursor Movements:** Toggle to import cursor movements from the replay.
   - **Audio Options:**
     - **Audio Track:** Toggle to import the audio track associated with the beatmap.

4. **Import:**
   - Click the **"Import"** button to start the import process.
   - 
### Cursor Attributes

- **k1** (`Boolean`): Key status for K1.
- **k2** (`Boolean`): Key status for K2.
- **m1** (`Boolean`): Mouse button M1 status.
- **m2** (`Boolean`): Mouse button M2 status.

### Circle Attributes

- **show** (`Boolean`): Visibility of the hitobject.
- **was_hit** (`Boolean`): Whether the hitobject was hit.
- **ar** (`Float`): Approach Rate.
- **cs** (`Float`): Circle Size.

### Slider Attributes

- **show** (`Boolean`): Visibility of the hitobject.
- **slider_duration_ms** (`Float`): Duration of the slider in milliseconds.
- **slider_duration_frames** (`Float`): Duration of the slider in frames.
- **ar** (`Float`): Approach Rate.
- **cs** (`Float`): Circle Size.
- **was_hit** (`Boolean`): Whether the slider was hit.
- **was_completed** (`Boolean`): Whether the slider was fully played.
- **repeat_count** (`Int`): Number of repeats in the slider.
- **pixel_length** (`Float`): Pixel length of the slider.

### Spinner Attributes

- **show** (`Boolean`): Visibility of the hitobject.
- **spinner_duration_ms** (`Float`): Duration of the spinner in milliseconds.
- **spinner_duration_frames** (`Float`): Duration of the spinner in frames.
- **was_hit** (`Boolean`): Whether the spinner was hit.
- **was_completed** (`Boolean`): Whether the spinner was fully played.

## Beatmap and Replay Information

After importing, the addon displays detailed information about the beatmap and the replay:

### Beatmap Information

- **Title:** The title of the beatmap.
- **Artist:** The artist of the song.
- **Difficulty:** The difficulty level of the beatmap.
- **BPM:** Beats Per Minute of the song.
- **AR (Approach Rate):** Base and adjusted approach rate based on applied mods.
- **CS (Circle Size):** Base and adjusted circle size based on applied mods.
- **OD (Overall Difficulty):** Base and adjusted overall difficulty based on applied mods.
- **Total HitObjects:** The total number of hitobjects in the beatmap.

### Replay Information

- **Mods:** Mods applied during the replay (e.g., Double Time, Half Time).
- **Accuracy:** Player's accuracy percentage.
- **Misses:** Number of misses.
- **Max Combo:** Maximum combo achieved.
- **Total Score:** Total score obtained.

## Known Issues

- **osrparse Limitations:**
  - Replays with the intro skipped are broken due to an issue in higher versions of `osrparse`. This addon specifically uses `osrparse v6.0.2` to mitigate this issue.
  
- **Replay Orientation:**
  - Replays may sometimes appear flipped by 180° on the Z-axis.
  
- **Performance:**
  - High slider resolution settings may impact Blender's performance, especially with complex beatmaps.

## Geometry Nodes Setup (TBD for v0.7)

The addon creates Geometry Nodes modifiers for different hitobject types, each storing relevant attributes. Below are examples of the Geometry Nodes setups:

![General Geometry Nodes Setup](geo_setup/geo_nodes_setup_general.png)
*General Geometry Nodes setup.*

![Circle Geometry Nodes Setup](geo_setup/geo_nodes_setup_circle.png)
*Geometry Nodes setup for Circle hitobjects.*

![Slider Geometry Nodes Setup](geo_setup/geo_nodes_setup_slider.png)
*Geometry Nodes setup for Slider hitobjects.*

![Spinner Geometry Nodes Setup](geo_setup/geo_nodes_setup_spinner.png)
*Geometry Nodes setup for Spinner hitobjects.*

## Ending Words

I only have basic Python knowledge, so please don’t murder me over bad code. Any help to make this work correctly is highly appreciated. Feel free to do whatever you want with the code.

At the end of the day, getting osu! replays and beatmaps into Blender for dynamic 3D replays would be really cool, right?
