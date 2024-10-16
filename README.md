# Blender Importer for osu! Beatmaps and Replays

First and foremost, I don’t know what I’m doing, but I had a goal: importing osu! beatmaps and replays into Blender, ready for Geometry Nodes, so I can create some fancy simulation node setups.

That’s where trusty ol’ ChatGPT came into play. The code is roughly based on 90% of GPT’s work and 10% me banging my head against the wall trying to fix things after GPT broke them.

This addon builds on [`osrparse`](https://github.com/kszlim/osu-replay-parser), which helped with parsing `.osr` files.

## What it Does

This addon imports a rough version of both the replay and the beatmap, applying a Geometry Nodes modifier that stores attributes based on drivers referencing offset variables for timings, etc.

You can then add a separate Geometry Nodes object that, for example, takes all hitobjects and spawns them in a simulation zone according to the offset attributes.

The Driver system is based on the properties of individual hitobjects, whose values can be keyframed. I wanted to avoid using viewport and render keyframes and instead used a more flexible solution.

## Current Issues

- **Broken Offsets:** The cursor is way out of sync with the beatmap’s hit keyframes. I divided a calculated offset by 2, which seems to line things up... more or less. If the "automatically import" checkbox is not checked, you'll need to import with a custom offset in milliseconds.

- **Sliders??:** Honestly, I’m not entirely sure what I’ve created here. It kind of resembles sliders? I used a Bézier curve algorithm, but I don’t think osu! sliders work the same way they did back in 2007.

- **Hit Circle Click Detection:** I’m still unsure when a hit circle should actually be marked as clicked. I added some geometry attributes as offsets, and it seems like it’s moving in the right direction. But it’s definitely not there yet.

## Installation

```bash
pip install osrparse
```
Add Addon .zip in Preferences

Rest TBD

## Blender Proof of Concept

[Download the .blend file](blendfile/[blender_4.2]osu_in_blender_proof_of_concept.blend)

## Ending Words

I only have basic Python knowledge, so please don’t murder me over bad code. Any help to make this work correctly is highly appreciated. Feel free to do whatever you want with the code.

At the end of the day, getting osu! replays and beatmaps into Blender for dynamic 3D replays would be really cool, right?

