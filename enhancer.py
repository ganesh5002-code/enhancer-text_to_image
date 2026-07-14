import time
import requests
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from config import HF_API_KEY

MODELS = [
"ByteDance/SDXL-Lightning",
"black-forest-labs/FLUX.1-dev",
"stabilityai/stable-diffusion-xl-base-1.0",
]

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}", "Accept": "image/png"}

def generate_image_from_text(prompt):
    payload, last_err = {"inputs": prompt}, None
    
    for model in MODELS:
        url = f"https://router.huggingface.co/hf-inference/models/{model}"
        
        for _ in range(3):
            r = requests.post(url, headers=HEADERS, json=payload, timeout=120)
            ct = (r.headers.get("content-type") or "").lower()
            
            if r.status_code == 503 and "application/json" in ct:
                try:
                    wait_s = int(r.json().get("estimated_time", 5))
                except Exception:
                    wait_s = 5
                time.sleep(wait_s + 1)
                continue
            
            if r.status_code == 200 and "application/json" not in ct:
                try:
                    return Image.open(BytesIO(r.content)).convert("RGB")
                except Exception as e:
                    last_err = f"Request failed with status code 200: Could not decode image bytes: {e}"
                    break
            
            try:
                body = r.json() if "application/json" in ct else r.text
            except Exception:
                body = r.text
            last_err = f"Request failed with status code {r.status_code}: {body}"
            break
    raise Exception(last_err or "Request failed with status code 500: unknown error")

def post_process_image(image):
    image = ImageEnhance.Brightness(image).enhance(1.2)
    image = ImageEnhance.Contrast(image).enhance(1.3)
    return image.filter(ImageFilter.GaussianBlur(radius=2))

def main():
    print("Welcome ot the Post-Processing Magic Workshop")
    print("This program generates an image from text and applies post processing effects.")
    print("Type 'exit or quit to leave.\n")
    
    while True:
        user_input = input("Enter a description for the image(or 'exit or quit to leave):\n")
        if user_input.lower() == 'exit' or 'quit':
            print("Bye!")
            break
        
        try:
            print("\nGenerating image...")
            image = generate_image_from_text(user_input)
            print("Applying post-processing effects and techniques...\n")
            processed_image = post_process_image(image)
            processed_image.show()
            
            save_option = input("Do you want to save the processed image? (yes/no):").strip()
            if save_option.lower() == 'yes':
                file_name = input("Enter a name for the image file (without extension): ").strip()
                processed_image.save(f"(file name).png")
                print(f"Image saved as {file_name}.png\n")
                
            print("-" * 80 + "\n")
        except Exception as e:
            print("An error occurred", e, "\n")
            
if __name__ == "__main__":
    main()