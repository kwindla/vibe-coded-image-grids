#!/usr/bin/env python3
"""
Create a grid of images with customizable dimensions and spacing.
"""

import os
import sys
import argparse
from PIL import Image


def create_image_grid(output_path, output_width, grid_rows, grid_cols, 
                     bg_color=(0, 0, 0), spacing=0, input_image_paths=None):
    """
    Create a grid of images with customizable dimensions and spacing.
    
    Args:
        output_path (str): Path to save the output image
        output_width (int): Width of the output image in pixels
        grid_rows (int): Number of rows in the grid
        grid_cols (int): Number of columns in the grid
        bg_color (tuple): Background color in RGB format (default: black)
        spacing (int): Spacing between images in pixels (default: 0)
        input_image_paths (list): List of paths to input images
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not input_image_paths:
        print("Error: No input images provided")
        return False
    
    expected_image_count = grid_rows * grid_cols
    if len(input_image_paths) != expected_image_count:
        if len(input_image_paths) > expected_image_count:
            print(f"Warning: Grid is {grid_rows}x{grid_cols} ({expected_image_count} cells) but {len(input_image_paths)} images were provided")
            print(f"Only the first {expected_image_count} images will be used")
            input_image_paths = input_image_paths[:expected_image_count]
        else:  # fewer images than cells
            print(f"Warning: Grid is {grid_rows}x{grid_cols} ({expected_image_count} cells) but only {len(input_image_paths)} images were provided")
            print("Some grid cells will be empty")
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    try:
        # First, determine the aspect ratio using the first image
        first_image_path = input_image_paths[0]
        with Image.open(first_image_path) as first_img:
            first_img_aspect = first_img.width / first_img.height
            
        # Calculate cell dimensions (accounting for spacing)
        total_spacing_width = spacing * (grid_cols - 1)
        cell_width = (output_width - total_spacing_width) // grid_cols
        
        # Determine cell height based on the first image's aspect ratio
        cell_height = int(cell_width / first_img_aspect)
        
        # Calculate the total output height
        total_spacing_height = spacing * (grid_rows - 1)
        output_height = (cell_height * grid_rows) + total_spacing_height
        
        # Create a new image with the calculated dimensions
        grid_img = Image.new('RGB', (output_width, output_height), bg_color)
        
        print(f"Grid dimensions: {grid_rows}x{grid_cols}")
        print(f"Cell dimensions: {cell_width}x{cell_height}")
        print(f"Output dimensions: {output_width}x{output_height}")
        
        # Place each image in the grid
        for idx, img_path in enumerate(input_image_paths):
            if not os.path.exists(img_path):
                print(f"Warning: Image {img_path} does not exist, skipping")
                continue
            
            # Calculate the row and column for this image
            row = idx // grid_cols
            col = idx % grid_cols
            
            # Skip if we've filled all the grid cells
            if row >= grid_rows:
                print("Warning: Grid is full, skipping remaining images")
                break
            
            # Calculate the position to paste this image
            x = col * (cell_width + spacing)
            y = row * (cell_height + spacing)
            
            try:
                # Open and resize the image to fit the cell
                with Image.open(img_path) as img:
                    # Convert to RGB mode if needed
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize the image to fit within the cell while preserving aspect ratio
                    img_aspect = img.width / img.height
                    
                    # Always resize to fit within the cell boundaries
                    new_width = cell_width
                    new_height = int(cell_width / img_aspect)
                    
                    # If the height exceeds the cell height, scale down proportionally
                    if new_height > cell_height:
                        new_height = cell_height
                        new_width = int(cell_height * img_aspect)
                    
                    resized = img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Center the image in the cell
                    x_offset = (cell_width - new_width) // 2
                    y_offset = (cell_height - new_height) // 2
                    grid_img.paste(resized, (x + x_offset, y + y_offset))
                    
                    print(f"Placed image {idx+1}/{len(input_image_paths)} at position ({row},{col})")
            
            except Exception as e:
                print(f"Error processing image {img_path}: {e}")
                continue
        
        # Save the final grid image
        grid_img.save(output_path)
        print(f"Grid image saved to {output_path}")
        
        return True
        
    except Exception as e:
        print(f"Error creating image grid: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Create a grid of images")
    parser.add_argument("output_path", help="Path to save the output image")
    parser.add_argument("--width", type=int, default=1024, help="Width of the output image (default: 1024)")
    parser.add_argument("--rows", type=int, default=3, help="Number of rows in the grid (default: 3)")
    parser.add_argument("--cols", type=int, default=3, help="Number of columns in the grid (default: 3)")
    parser.add_argument("--bg-color", nargs=3, type=int, default=[0, 0, 0], 
                        help="Background color as R G B values (default: 0 0 0)")
    parser.add_argument("--spacing", type=int, default=0, 
                        help="Spacing between images in pixels (default: 0)")
    parser.add_argument("input_images", nargs='+', help="Paths to input images")
    
    args = parser.parse_args()
    
    success = create_image_grid(
        args.output_path,
        args.width,
        args.rows,
        args.cols,
        tuple(args.bg_color),
        args.spacing,
        args.input_images
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
