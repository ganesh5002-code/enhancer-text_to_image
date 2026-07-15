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

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Accept": "image/png"
}


def generate_image_from_text(prompt):
    payload = {"inputs": prompt}
    last_err = None

    for model in MODELS:
        url = f"https://router.huggingface.co/hf-inference/models/{model}"

        for _ in range(3):
            response = requests.post(
                url,
                headers=HEADERS,
                json=payload,
                timeout=120
            )

            content_type = (response.headers.get("content-type") or "").lower()

            if response.status_code == 503 and "application/json" in content_type:
                try:
                    wait_time = int(response.json().get("estimated_time", 5))
                except Exception:
                    wait_time = 5

                print(f"Model loading... Waiting {wait_time} seconds.")
                time.sleep(wait_time + 1)
                continue

            if response.status_code == 200 and "application/json" not in content_type:
                try:
                    return Image.open(BytesIO(response.content)).convert("RGB")
                except Exception as e:
                    last_err = f"Could not decode image: {e}"
                    break

            try:
                body = response.json() if "application/json" in content_type else response.text
            except Exception:
                body = response.text

            last_err = f"Request failed ({response.status_code}): {body}"
            break

    raise Exception(last_err or "Unknown error occurred.")


def day(image):
    image = ImageEnhance.Brightness(image).enhance(1.3)
    image = ImageEnhance.Contrast(image).enhance(1.1)
    image = image.filter(ImageFilter.GaussianBlur(radius=2))
    return image


def night(image):
    image = ImageEnhance.Brightness(image).enhance(0.8)
    image = ImageEnhance.Contrast(image).enhance(1.5)
    image = image.filter(ImageFilter.GaussianBlur(radius=1))
    return image


def main():
    print("Welcome to the Post-Processing Magic Workshop")
    print("This program generates an AI image from text.")
    print("It creates a Daylight Edition and a Night Mood version.")
    print("Type 'exit' or 'quit' to leave.\n")

    while True:
        user_input = input(
            "Enter a description for the image (or 'exit'/'quit' to leave):\n"
        ).strip()

        if user_input.lower() in ("exit", "quit"):
            print("Bye!")
            break

        try:
            print("\nGenerating image...")
            image = generate_image_from_text(user_input)

            print("Creating Daylight Edition...")
            daylight_image = day(image)

            print("Creating Night Mood...")
            night_image = night(image)

            print("Displaying images...")
            daylight_image.show()
            night_image.show()

            save_option = input(
                "Do you want to save the processed images? (yes/no): "
            ).strip().lower()

            if save_option == "yes":
                file_name = input(
                    "Enter a name for the image files (without extension): "
                ).strip()

                daylight_image.save(f"{file_name}_daylight.png")
                night_image.save(f"{file_name}_night.png")

                print(f"Daylight Edition saved as {file_name}_daylight.png")
                print(f"Night Mood saved as {file_name}_night.png\n")

            print("-" * 80 + "\n")

        except Exception as e:
            print("An error occurred:", e, "\n")


if __name__ == "__main__":
    main()