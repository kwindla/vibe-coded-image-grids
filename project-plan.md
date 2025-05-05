# Project plan.

Utilities to transform a directory full of images using an image-to-image API. All code will be in either Python or shell scripts that call standard image processing utilities.

# Functions

This code needs to:

1. Transform a single image. This function will need an image input path, an image output path, an API key, a text prompt, and optionally an output size and how many output images to generate. The output size should default to 1024x1024 and the number of output images should default to 1.
2. Resize an image to detect the visual bounding box independent of the background, crop, and resize to a specified width, preserving the aspect ratio.
3. Transform a directory of images. This function will need a directory of images, an output directory, an API key, a text prompt, and whether to resize the output images as per (2).
4. Arrange images in a grid. This function takes an output path, output image width and height, grid row and column count, background color, optional spacing between images, and a list of input image paths.

Each of these four functions should be implemented in a separate .py file. The main function in each file should allow the user to run the function from the command line.

When you are finished implementing the scripts, create a `requirements.txt` file listing the dependencies.

# Documentation

Here is sample code from the OpenAI docs for the image-to-image API.

https://platform.openai.com/docs/guides/image-generation?image-generation-model=gpt-image-1

```python
from openai import OpenAI
import base64
client = OpenAI()

prompt = """
A children's book drawing of a veterinarian using a stethoscope to 
listen to the heartbeat of a baby otter.
"""

result = client.images.edit(
    model="gpt-image-1",
    prompt=prompt,
    n=1,
    size="1024x1024",
    image=[open("image-filename.png", "rb")]
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("otter.png", "wb") as f:
    f.write(image_bytes)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("otter.png", "wb") as f:
    f.write(image_bytes)
```



