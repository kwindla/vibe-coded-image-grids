#!/usr/bin/env python3
"""
Resize an image to detect the visual bounding box independent of the background,
crop, and resize to a specified width, preserving the aspect ratio.
"""

import os
import sys
import argparse
from PIL import Image


def trim_image(im, debug_output=None):
    """
    Detect and trim empty (background) space around an image using background color detection.

    Args:
        im: PIL Image object
        debug_output: If provided, save the difference image to this path for debugging

    Returns:
        PIL Image object with background trimmed
    """
    print(f"Original image size: {im.size}, mode: {im.mode}")

    # Convert image to RGB if it's not already
    if im.mode != "RGB":
        print(f"Converting image from {im.mode} to RGB")
        im = im.convert("RGB")

    # Sample background color from an 8x8 area in the top-left corner
    print("Sampling background color from 8x8 pixel area in top-left corner")
    sample_size = 8
    r_total, g_total, b_total = 0, 0, 0
    sample_count = 0
    
    # Ensure we don't go out of bounds for small images
    max_x = min(sample_size, im.width)
    max_y = min(sample_size, im.height)
    
    # Sample the pixels
    for y in range(max_y):
        for x in range(max_x):
            pixel = im.getpixel((x, y))
            r_total += pixel[0]
            g_total += pixel[1]
            b_total += pixel[2]
            sample_count += 1
    
    # Calculate average
    avg_r = r_total // sample_count
    avg_g = g_total // sample_count
    avg_b = b_total // sample_count
    bg_color = (avg_r, avg_g, avg_b)
    print(f"Background color (averaged from {sample_count} pixels): {bg_color}")

    # Create a binary difference image with moderate tolerance
    tolerance = 10  # Increased tolerance threshold
    print(f"Creating binary difference image with tolerance of {tolerance}")
    width, height = im.size
    diff = Image.new('L', im.size, 0)  # Create a blank grayscale image
    
    # Load pixel data for faster access
    img_data = im.load()
    diff_data = diff.load()
    
    # Track if any pixels are different
    different_pixels = 0
    
    # Create a binary difference with small tolerance
    for y in range(height):
        for x in range(width):
            pixel = img_data[x, y]
            
            # Check with tolerance threshold
            if isinstance(pixel, int):  # Handle grayscale
                is_different = abs(pixel - bg_color) > tolerance
            else:  # Handle RGB/RGBA
                r_diff = abs(pixel[0] - bg_color[0])
                g_diff = abs(pixel[1] - bg_color[1])
                b_diff = abs(pixel[2] - bg_color[2])
                is_different = (r_diff > tolerance or 
                               g_diff > tolerance or 
                               b_diff > tolerance)
            
            if is_different:
                different_pixels += 1
                
            # Set to white (255) if different, black (0) if same
            diff_data[x, y] = 255 if is_different else 0
    
    print(f"Found {different_pixels} pixels different from background color")
    
    # Save difference image if debug output is requested
    if debug_output:
        print(f"Saving difference image to {debug_output}")
        diff.save(debug_output)
    
    # Get the bounding box of non-background areas
    print("Getting bounding box")
    bbox = diff.getbbox()
    print(f"Detected bounding box: {bbox}")

    # Try fallbacks with increasingly relaxed comparison if no bbox was found
    if not bbox:
        print("No bounding box found with exact match, trying with tolerance for small differences")
        # First fallback: allow small differences in color (within 5 units)
        tolerance = 5
        for y in range(height):
            for x in range(width):
                pixel = img_data[x, y]
                
                if isinstance(pixel, int):  # Handle grayscale
                    is_different = abs(pixel - bg_color) > tolerance
                else:  # Handle RGB/RGBA
                    # Check if any channel differs by more than tolerance
                    r_diff = abs(pixel[0] - bg_color[0]) 
                    g_diff = abs(pixel[1] - bg_color[1])
                    b_diff = abs(pixel[2] - bg_color[2])
                    is_different = (r_diff > tolerance or g_diff > tolerance or b_diff > tolerance)
                
                diff_data[x, y] = 255 if is_different else 0
        
        bbox = diff.getbbox()
        print(f"First fallback approach bounding box: {bbox}")

    if not bbox:
        print("No bounding box found with first fallback, trying with higher tolerance")
        # Second fallback: allow larger differences (within 15 units)
        tolerance = 15
        for y in range(height):
            for x in range(width):
                pixel = img_data[x, y]
                
                if isinstance(pixel, int):  # Handle grayscale
                    is_different = abs(pixel - bg_color) > tolerance
                else:  # Handle RGB/RGBA
                    r_diff = abs(pixel[0] - bg_color[0])
                    g_diff = abs(pixel[1] - bg_color[1])
                    b_diff = abs(pixel[2] - bg_color[2])
                    is_different = (r_diff > tolerance or g_diff > tolerance or b_diff > tolerance)
                
                diff_data[x, y] = 255 if is_different else 0
        
        bbox = diff.getbbox()
        print(f"Final approach bounding box: {bbox}")

    # Save the entire image if no bounding box was found
    if bbox:
        print(f"Cropping image to {bbox}")
        cropped = im.crop(bbox)
        print(f"Cropped image size: {cropped.size}")
        return cropped

    print("No bounding box detected, returning original image")
    return im


def resize_image(input_path, output_path, width, debug=False):
    """
    Resize an image to detect the visual bounding box independent of the background,
    crop, and resize to a specified width, preserving the aspect ratio.

    Args:
        input_path (str): Path to the input image
        output_path (str): Path to save the output image
        width (int): Desired width of the output image
        debug (bool): If True, save debug images showing the difference calculation

    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist")
        return False

    # Create the output directory if it doesn't exist
    os.makedirs(
        os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True
    )

    try:
        # Open the image
        with Image.open(input_path) as img:
            # Prepare debug output path if needed
            debug_output = None
            if debug:
                debug_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else "."
                debug_basename = os.path.basename(output_path)
                debug_name = f"diff_{debug_basename}"
                debug_output = os.path.join(debug_dir, debug_name)
            
            # Trim the image to remove background
            trimmed_img = trim_image(img, debug_output)

            # Calculate the new height to maintain aspect ratio
            aspect_ratio = trimmed_img.height / trimmed_img.width
            new_height = int(width * aspect_ratio)

            # Resize the image
            resized_img = trimmed_img.resize((width, new_height), Image.LANCZOS)

            # Save the resized image
            resized_img.save(output_path)

            print(f"Resized image saved to {output_path}")

        return True

    except Exception as e:
        print(f"Error resizing image: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Resize and crop an image")
    parser.add_argument("input_path", help="Path to the input image")
    parser.add_argument("output_path", help="Path to save the output image")
    parser.add_argument(
        "--width", type=int, default=1024, help="Desired width of the output image (default: 1024)"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Generate a difference image for debugging"
    )

    args = parser.parse_args()

    success = resize_image(args.input_path, args.output_path, args.width, args.debug)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
