import os
import time
import multiprocessing
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---
INPUT_DIR = 'dataset'
OUTPUT_DIR = 'output_distributed'
IMG_SIZE = (128, 128)
WATERMARK_TEXT = "PDC Exam"

# IMPORTANT: Replace this with YOUR time from Task 1
SEQUENTIAL_TIME = 2.86 # 
# --- End Configuration ---

def node_worker(node_id, image_paths, result_queue, input_root, output_root):
    """
    This function simulates a "node"[cite: 45].
    It processes its assigned subset of images and reports its time[cite: 46].
    """
    print(f"Node {node_id}: Starting to process {len(image_paths)} images.")
    start_time = time.perf_counter()
    
    for input_path in image_paths:
        try:
            # Construct output path
            relative_path = os.path.relpath(os.path.dirname(input_path), input_root)
            output_subdir = os.path.join(output_root, relative_path)
            output_path = os.path.join(output_subdir, os.path.basename(input_path))
            
            os.makedirs(output_subdir, exist_ok=True)

            # --- Image Processing (same as before) ---
            img = Image.open(input_path)
            img = img.resize(IMG_SIZE, Image.LANCZOS)
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
            img.convert('RGB').save(output_path, 'JPEG')
            # --- End Image Processing ---
            
        except Exception as e:
            print(f"Node {node_id} error on {input_path}: {e}")

    end_time = time.perf_counter()
    time_taken = end_time - start_time
    
    # Report completion time and image count back to master [cite: 46]
    result_queue.put({
        'id': node_id,
        'count': len(image_paths),
        'time': time_taken
    })
    print(f"Node {node_id}: Finished in {time_taken:.2f}s.")

def main():
    print("Starting simulated distributed processing...")
    
    # 1. Get a list of all image paths
    all_image_paths = []
    for root, dirs, files in os.walk(INPUT_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                all_image_paths.append(os.path.join(root, file))
                
    # 2. Divide total images "equally" among 2 nodes [cite: 45]
    total_images = len(all_image_paths)
    mid_point = total_images // 2
    
    node1_files = all_image_paths[:mid_point]
    node2_files = all_image_paths[mid_point:]
    
    # 3. Create a Queue for results 
    result_queue = multiprocessing.Queue()

    # 4. Start the overall timer (for the "Master process") [cite: 47]
    master_start_time = time.perf_counter()

    # 5. Create and start the 2 "node" processes [cite: 45]
    p1 = multiprocessing.Process(target=node_worker, 
                                 args=(1, node1_files, result_queue, INPUT_DIR, OUTPUT_DIR))
    p2 = multiprocessing.Process(target=node_worker, 
                                 args=(2, node2_files, result_queue, INPUT_DIR, OUTPUT_DIR))
    
    p1.start()
    p2.start()
    
    # 6. Wait for both processes to finish
    p1.join()
    p2.join()
    
    # 7. Stop the overall timer
    master_end_time = time.perf_counter()
    total_distributed_time = master_end_time - master_start_time

    # 8. Aggregate results from the queue [cite: 47]
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
        
    # Sort results by node ID
    results.sort(key=lambda r: r['id'])

    # 9. Print the summary as per the example output 
    print("\n--- Distributed Processing Summary ---")
    for res in results:
        # Example: "Node 1 processed 40 images in 5.8s" [cite: 50]
        print(f"Node {res['id']} processed {res['count']} images in {res['time']:.1f}s")
        
    # Example: "Total distributed time: 6.1s" [cite: 52]
    print(f"Total distributed time: {total_distributed_time:.1f}s")
    
    # Example: "Efficiency: 2.99x over sequential" [cite: 53]
    efficiency = SEQUENTIAL_TIME / total_distributed_time
    print(f"Efficiency: {efficiency:.2f}x over sequential")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()