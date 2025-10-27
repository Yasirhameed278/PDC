import os
import time
import multiprocessing
from functools import partial
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---
INPUT_DIR = 'dataset'
OUTPUT_DIR = 'output_parallel'
IMG_SIZE = (128, 128)
WATERMARK_TEXT = "PDC Exam"

# IMPORTANT: Replace this with YOUR time from Task 1
SEQUENTIAL_TIME = 1.18  # 
# --- End Configuration ---

def process_image_worker(input_path, input_root, output_root):
    """
    Worker function to be run by each process.
    Reads, resizes, watermarks, and saves a single image.
    """
    try:
        # Construct output path, preserving subfolders 
        relative_path = os.path.relpath(os.path.dirname(input_path), input_root)
        output_subdir = os.path.join(output_root, relative_path)
        output_path = os.path.join(output_subdir, os.path.basename(input_path))
        
        # Ensure output directory exists
        os.makedirs(output_subdir, exist_ok=True)

        # Read image
        img = Image.open(input_path)
        
        # Resize
        img = img.resize(IMG_SIZE, Image.LANCZOS)
        
        # Add watermark
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 10)
        except IOError:
            font = ImageFont.load_default()
        
        text_overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_overlay)
        text_pos = (img.width - 70, img.height - 15)
        text_draw.text(text_pos, WATERMARK_TEXT, font=font, fill=(255, 255, 255, 128))
        img = Image.alpha_composite(img, text_overlay)
        
        # Save
        img.convert('RGB').save(output_path, 'JPEG')
        
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def main():
    print("Starting parallel processing test...")
    
    # 1. Get a list of all image paths to process
    all_image_paths = []
    for root, dirs, files in os.walk(INPUT_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                all_image_paths.append(os.path.join(root, file))
                
    print(f"Found {len(all_image_paths)} images to process.")

    # 2. Define worker counts to test 
    # The example shows 1, 4, 8[cite: 37, 39, 41]. We'll test 1, 2, 4, and 8.
    worker_counts = [1, 2, 4, 8]
    results = []

    # 3. Use functools.partial to "freeze" the input/output dir arguments
    # The Pool.map function can only pass one argument (the image path)
    # partial creates a new function with the other arguments pre-filled.
    worker_func = partial(process_image_worker, 
                          input_root=INPUT_DIR, 
                          output_root=OUTPUT_DIR)

    # 4. Loop through each worker configuration and time it [cite: 33]
    for n_workers in worker_counts:
        print(f"--- Testing with {n_workers} workers ---")
        start_time = time.perf_counter()
        
        # Create the multiprocessing Pool
        with multiprocessing.Pool(processes=n_workers) as pool:
            # map applies the worker_func to every item in all_image_paths
            # and blocks until all are complete.
            pool.map(worker_func, all_image_paths)
            
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Calculate speedup
        speedup = SEQUENTIAL_TIME / total_time
        results.append((n_workers, total_time, speedup))
        print(f"Time taken: {total_time:.2f}s, Speedup: {speedup:.2f}x")

    # 5. Display the final speedup table [cite: 34, 35]
    print("\n--- Final Speedup Table ---")
    print(f"{'Workers':<8} | {'Time (s)':<10} | {'Speedup':<8}")
    print("-" * 30)
    for n, t, s in results:
        # Use the 1-worker time as the baseline for the table if it was run
        if n == 1:
            baseline_time = t
            speedup_display = 1.0
        else:
            # Use the actual sequential time for speedup calculation
            baseline_time_from_seq = SEQUENTIAL_TIME
            speedup_display = baseline_time_from_seq / t

        # Format matches example output [cite: 37-42]
        if n == 1:
            print(f"{n:<8} | {t:<10.2f} | {speedup_display:.2f}x")
        else:
            print(f"{n:<8} | {t:<10.2f} | {speedup_display:.2f}x")


if __name__ == "__main__":
    # This is crucial for multiprocessing to work correctly on Windows
    multiprocessing.freeze_support()
    main()