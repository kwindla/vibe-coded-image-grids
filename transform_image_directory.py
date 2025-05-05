#!/usr/bin/env python3
"""
Transform a directory of images using OpenAI's image-to-image API.
"""

import os
import sys
import argparse
import glob
from concurrent.futures import ThreadPoolExecutor
from transform_single_image import transform_image
from resize_crop_image import resize_image


def transform_directory(input_dir, output_dir, api_key, prompt, 
                       should_resize=False, resize_width=1024,
                       output_size="1024x1024", n=1, max_workers=3):
    """
    Transform all images in a directory using OpenAI's image-to-image API.
    
    Args:
        input_dir (str): Directory containing input images
        output_dir (str): Directory to save the output images
        api_key (str): OpenAI API key
        prompt (str): Text prompt for image transformation
        should_resize (bool): Whether to resize the output images
        resize_width (int): Width to resize the output images to if should_resize is True
        output_size (str): Size of the output images (default: "1024x1024")
        n (int): Number of output images to generate per input image (default: 1)
        max_workers (int): Maximum number of parallel workers
        
    Returns:
        bool: True if all images were processed successfully, False otherwise
    """
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory {input_dir} does not exist")
        return False
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files in the input directory
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.tiff', '*.tif', '*.bmp']
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(input_dir, ext)))
        image_files.extend(glob.glob(os.path.join(input_dir, ext.upper())))
    
    if not image_files:
        print(f"Error: No image files found in {input_dir}")
        return False
    
    print(f"Found {len(image_files)} images to process")
    
    # Process each image
    success = True
    
    def process_image(img_path):
        try:
            filename = os.path.basename(img_path)
            base, ext = os.path.splitext(filename)
            
            # Set temporary and final output paths
            temp_output_path = os.path.join(output_dir, f"{base}_temp{ext}")
            final_output_path = os.path.join(output_dir, f"{base}{ext}")
            
            # Transform the image
            transform_success = transform_image(
                img_path,
                temp_output_path,
                api_key,
                prompt,
                output_size,
                n
            )
            
            if not transform_success:
                print(f"Failed to transform {img_path}")
                return False
            
            # Resize the image if requested
            if should_resize and transform_success:
                resize_success = resize_image(
                    temp_output_path,
                    final_output_path,
                    resize_width
                )
                
                # Remove the temporary file
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
                
                if not resize_success:
                    print(f"Failed to resize {temp_output_path}")
                    return False
            elif transform_success:
                # If no resize is needed, the temp file is the final file
                if n == 1:  # Only rename if we're generating a single output
                    os.rename(temp_output_path, final_output_path)
            
            return True
        
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            return False
    
    # Use ThreadPoolExecutor to process images in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_image, image_files))
    
    # Check if all images were processed successfully
    if not all(results):
        success = False
        print("Some images failed to process")
    
    return success


def main():
    parser = argparse.ArgumentParser(description="Transform a directory of images using OpenAI's image-to-image API")
    parser.add_argument("input_dir", help="Directory containing input images")
    parser.add_argument("output_dir", help="Directory to save the output images")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY environment variable)")
    parser.add_argument("--prompt", required=True, help="Text prompt for image transformation")
    parser.add_argument("--resize", action="store_true", help="Resize the output images")
    parser.add_argument("--resize-width", type=int, default=1024, help="Width to resize the output images to (default: 1024)")
    parser.add_argument("--output-size", default="1024x1024", help="Size of output images (default: 1024x1024)")
    parser.add_argument("--n", type=int, default=1, help="Number of output images to generate per input image (default: 1)")
    parser.add_argument("--max-workers", type=int, default=3, help="Maximum number of parallel workers (default: 3)")
    
    args = parser.parse_args()
    
    # Get API key from command line or environment variable
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: API key must be provided via --api-key or OPENAI_API_KEY environment variable")
        sys.exit(1)
        
    success = transform_directory(
        args.input_dir,
        args.output_dir,
        api_key,
        args.prompt,
        args.resize,
        args.resize_width,
        args.output_size,
        args.n,
        args.max_workers
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
