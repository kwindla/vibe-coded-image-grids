# Vibe coding some image grid scripts

![Grid example](examples/grid-11x2.png)

## Overview

I wanted to do something fun with headshots of the guest speakers for the [Voice AI and Voice Agents](https://maven.com/pipecat/voice-ai-and-voice-agents-a-technical-deep-dive) online class.

In the past I would have fired up ImageMagick, Python, and Photoshop and hacked together some scripts. But, you know, vibe coding!

So I wrote a [project plan](project-plan.md) and asked Windsurf to implement the plan.

The result is a collection of Python scripts.

## Usage

### transform_single_image.py

This script takes a prompt and an image and calls the OpenAI API to generate a new image.

```python
python transform_single_image.py --prompt "Transform this portrait into a studio ghibli style. Retain the circular mask and black background." --resize orig-headshots/0003.png --n 3 working
```

### resize_crop_image.py

This script resizes and crops an image to a specified width, preserving the aspect ratio.

```python
python resize_crop_image.py orig-headshots/0001.png test-8x8-higher-tolerance.png --width 500
```

### transform_image_directory.py

This script transforms all images in a directory, optionally resizing/cropping.

```python
python transform_image_directory.py three-more /tmp --prompt "Transform this portrait into a studio ghibli style. Retain the circular mask and black background." --resize
```

### create_image_grid.py

This script creates a grid of images.

```python
python create_image_grid.py --rows 5 --cols 5 --width 2000 --spacing 10 grid.png outputs-02/*
```

## Notes

So, vibe coding ...

I've been trying to get into the habit of asking LLMs to write code for me, as often as possible and in a variety of contexts.

In general, I find that LLMs are now functioning 
  - really well as a kind of super-autocomplete,
  - moderately well at writing loops and blocks of conditional code,
  - sometimes okay at writing whole functions,
  - and generally not well at implementing projects from scratch.
  
Your mileage will vary. Two big determinants of success are my skill using these tools and the general domain of the project.

This particular project actually was an amazing success. At least it was, until we got into a loop trying to fix issues in `resize_crop_image.py` having to do with bounding box detection. (Notice the "we" here. What's the right first-person plural for the LLM and me?)

Claude Sonnet 3.7 got the first version of all the scripts working in one big try plus two small bug fix chat mode iterations. **That's pretty great!**

It took maybe 10 minutes to write the project plan, wait for Windsurf/Claude, try the scripts, suggest a fix, try again, and suggest one more fix. I've been writing these kinds of scripts for a long time, so if I'd done this from scratch, I would have said to myself "This code is going to take me 10 minutes to write but really it will take me half an hour." :-)

The LLM did whiff pretty badly creating the `requirements.txt` file. Which is maybe an interesting tiny window into thinking about what Claude-plus-Windsurf "understands" about a Python project like this. 

I made some image grids. Made some more image grids. A couple of images weren't being cropped correctly. Not surprising; the background color threshold wasn't sensitive enough. I figured that would be an easy thing to fix with a little chat prompting. Nope. I didn't understand the PIL function being called. Neither did Claude, as it turned out. We went round and round for half an hour.

So I read the docs and half-way fixed it myself, sort of. Good enough for now. Par for the course, both for a throway project like this no matter how the code is written, and for this specific moment in LLM code generation capabilities.

The big thing I came away from this project thinking about, though, wasn't code gen capabilities. It was that this shouldn't have been a programming project at all. I can think of two much more natural ways to do this kind of image manipulation.

One, I could have just asked Photoshop to do this for me. "Hey, Photoshop, here's a workflow I'm imagining. Do it once. If I like the result, we'll do it a bunch of times."

Or, I could just ask the Universal LLM Chat App That We May Soon Do All Our Work Inside to do this for me. The LLM can write code. The LLM can manipulate filesystem-like entities. The LLM can call out to tools. The inference environment or the application environment or both can include scaffolding that runs code.

I don't ever have to see the code. I mean, I personally want to see the code, maybe. I like code. But maybe even I don't even care that much about the code, for something like this. And certainly most people don't.




