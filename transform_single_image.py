#!/usr/bin/env python3
"""
Transform a single image using OpenAI's image-to-image API.
"""

import os
import sys
import base64
import argparse
from openai import OpenAI


def transform_image(input_path, output_path, api_key, prompt, output_size="1024x1024", n=1):
    """
    Transform a single image using OpenAI's image-to-image API.
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path to save the output image
        api_key (str): OpenAI API key
        prompt (str): Text prompt for image transformation
        output_size (str): Size of the output image (default: "1024x1024")
        n (int): Number of output images to generate (default: 1)
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist")
        return False
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # Set API key for OpenAI client
    client = OpenAI(api_key=api_key)
    
    try:
        # Call the OpenAI API to edit the image
        # Use a context manager to ensure the file gets closed properly
        with open(input_path, "rb") as image_file:
            result = client.images.edit(
                model="gpt-image-1",
                prompt=prompt,
                n=n,
                size=output_size,
                image=[image_file]
            )
        
        # Process each generated image
        for i, image in enumerate(result.data):
            # Determine the output file path
            if n > 1:
                # If multiple images, use a numbered naming scheme
                base, ext = os.path.splitext(output_path)
                current_output_path = f"{base}_{i+1}{ext}"
            else:
                current_output_path = output_path
                
            # Decode the base64 image and save to file
            image_bytes = base64.b64decode(image.b64_json)
            with open(current_output_path, "wb") as f:
                f.write(image_bytes)
            
            print(f"Transformed image saved to {current_output_path}")
            
        return True
        
    except Exception as e:
        print(f"Error transforming image: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Transform a single image using OpenAI's image-to-image API")
    parser.add_argument("input_path", help="Path to the input image")
    parser.add_argument("output_path", help="Path to save the output image")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY environment variable)")
    parser.add_argument("--prompt", required=True, help="Text prompt for image transformation")
    parser.add_argument("--output-size", default="1024x1024", help="Size of output image (default: 1024x1024)")
    parser.add_argument("--n", type=int, default=1, help="Number of output images to generate (default: 1)")
    
    args = parser.parse_args()
    
    # Get API key from command line or environment variable
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: API key must be provided via --api-key or OPENAI_API_KEY environment variable")
        sys.exit(1)
        
    success = transform_image(
        args.input_path,
        args.output_path,
        api_key,
        args.prompt,
        args.output_size,
        args.n
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
