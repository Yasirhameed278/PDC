import os
import time
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---
INPUT_DIR = 'dataset'
OUTPUT_DIR = 'output_seq'
IMG_SIZE = (128, 128) # Resize to 128x128 [cite: 24]
WATERMARK_TEXT = "PDC Exam"
# --- End Configuration ---

def process_image(input_path, output_path):
    """
    Reads an image, resizes it, adds a watermark, and saves it.
    """
    try:
        # Read image [cite: 23]
        img = Image.open(input_path)
        
        # Resize image [cite: 24]
        img = img.resize(IMG_SIZE, Image.LANCZOS)
        
        # Add watermark [cite: 25]
        # Ensure image is in RGBA mode to handle transparency
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        # Create a drawing context
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fallback to default
        try:
            # You might need to change this path to a font on your system
            font = ImageFont.truetype("arial.ttf", 10)
        except IOError:
            font = ImageFont.load_default()
            
        # Create a transparent overlay for the text
        text_overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_overlay)
        
        # Position watermark at bottom right
        text_pos = (img.width - 70, img.height - 15)
        text_draw.text(text_pos, WATERMARK_TEXT, font=font, fill=(255, 255, 255, 128)) # Semi-transparent white
        
        # Composite the text overlay onto the image
        img = Image.alpha_composite(img, text_overlay)
        
        # Ensure output directory exists 
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the processed image 
        # Convert back to RGB to save as JPEG
        img.convert('RGB').save(output_path, 'JPEG')
        
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def main():
    print("Starting sequential processing...")
    
    # Start the timer [cite: 72]
    start_time = time.perf_counter()
    
    total_files = 0
    # Walk through all subfolders and files in the input directory
    for root, dirs, files in os.walk(INPUT_DIR):
        for file in files:
            # Check for image files
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Construct full input path
                input_path = os.path.join(root, file)
                
                # Construct relative output path to keep folder structure intact 
                relative_path = os.path.relpath(root, INPUT_DIR)
                output_subdir = os.path.join(OUTPUT_DIR, relative_path)
                output_path = os.path.join(output_subdir, file)
                
                # Process the single image
                process_image(input_path, output_path)
                total_files += 1

    # Stop the timer
    end_time = time.perf_counter()
    
    # Print total execution time [cite: 26, 28]
    total_time = end_time - start_time
    print(f"Processed {total_files} images.")
    print(f"Sequential Processing Time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()