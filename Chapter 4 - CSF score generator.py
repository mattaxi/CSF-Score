#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 09:15:05 2025
"""

import easygui
from PIL import Image
import numpy as np
import pandas as pd

def calculate_background_intensity(image_array):
    """Calculate background intensity using a robust method (90th percentile)."""
    background_intensity = np.percentile(image_array, 90)
    return background_intensity

def calculate_shadow_factor(image_path):
    """Calculate Combined Shadow Factor (CSF) based on intensity and size."""
    try:
        # Load image and convert to grayscale
        image = Image.open(image_path).convert('L')
        image_array = np.array(image, dtype=np.int32)

        # Calculate background intensity
        background_intensity = calculate_background_intensity(image_array)

        # Calculate darkness relative to background intensity
        darkness = background_intensity - image_array

        # Normalize darkness by dividing by the global maximum possible darkness (255)
        normalized_darkness = darkness / 255.0  # Normalize to [0, 1]

        normalized_darkness = np.clip(normalized_darkness, 0, 1)  # Clip negative values to zero

        # Intensity Factor (IF): Average darkness of shadow pixels
        shadow_pixels = normalized_darkness[normalized_darkness > 0]  # Only consider shadow pixels
        if len(shadow_pixels) > 0:
            intensity_factor = np.mean(shadow_pixels)
        else:
            intensity_factor = 0

        # Size Factor (SF): Proportion of shadow pixels in the image
        total_pixels = image_array.size
        size_factor = len(shadow_pixels) / total_pixels

        # Combined Shadow Factor (CSF)
        combined_shadow_factor = intensity_factor * size_factor

        # Multiply by 100 to express as percentage-like value
        combined_shadow_factor *= 100

        return combined_shadow_factor

    except FileNotFoundError:
        easygui.msgbox(f"Error: Image file not found at {image_path}", title="Error")
        return None
    except Exception as e:
        easygui.msgbox(f"Error processing image {image_path}: {e}", title="Error")
        return None

def process_images():
    """Opens a file dialog, processes selected images, calculates CSF, and displays a table using easygui."""
    image_paths = easygui.fileopenbox(msg="Select one or more image files",
                                      title="Shadow Factor Calculator",
                                      multiple=True,
                                      filetypes=["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff"])

    if not image_paths:
        easygui.msgbox("No images selected.", title="Information")
        return

    results = []
    for image_path in image_paths:
        score = calculate_shadow_factor(image_path)
        if score is not None:
            results.append({
                "Image Filename": image_path.split("/")[-1],  # Extract filename
                "Shadow Factor (%)": f"{score:.2f}%"  # Display score with two decimal places
            })

    if results:
        df = pd.DataFrame(results)
        df.set_index("Image Filename", inplace=True)
        table_string = df.to_string()
        easygui.textbox(msg="Shadow Factor Results",
                        title="Shadow Factor Calculator",
                        text=table_string)
    else:
        easygui.msgbox("No images processed successfully.", title="Information")

# Run the image processing function
if __name__ == "__main__":
    process_images()
