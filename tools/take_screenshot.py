from PIL import ImageGrab
import os
from pathlib import Path

def take_screenshot():
    # Create docs/images directory if it doesn't exist
    image_dir = Path('docs/images')
    image_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Take screenshot
        image = ImageGrab.grab()

        # Save screenshot
        image_path = image_dir / 'storage-analyzer-main.png'
        image.save(str(image_path))
        print(f"Screenshot saved to {image_path}")
    except Exception as e:
        print(f"Error taking screenshot: {e}")

if __name__ == "__main__":
    take_screenshot()