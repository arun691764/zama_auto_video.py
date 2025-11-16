import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import textwrap
import tempfile
import os
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

WIDTH = 1920
HEIGHT = 1080
BG_COLOR = (11, 18, 32)
TEXT_COLOR = (255, 255, 255)

def fetch_text(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    texts = []
    for tag in soup.find_all(["h1", "h2", "h3", "p"]):
        t = tag.get_text(" ", strip=True)
        if len(t) > 5:
            texts.append(t)
    return texts

def make_image(text, index):
    wrapped = "\n".join(textwrap.wrap(text, width=40))
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.multiline_text((100, 100), wrapped, fill=TEXT_COLOR, font=font, spacing=8)
    path = f"slide_{index}.png"
    img.save(path)
    return path

def generate_video(url, output="zama_video.mp4"):
    blocks = fetch_text(url)
    full_text = ". ".join(blocks)

    audio_path = os.path.join(tempfile.gettempdir(), "tts.mp3")
    gTTS(full_text, lang="en").save(audio_path)
    audio = AudioFileClip(audio_path)

    per_slide = max(3, min(8, audio.duration / len(blocks)))

    images = [make_image(t, i) for i, t in enumerate(blocks)]
    clips = [ImageClip(img).set_duration(per_slide) for img in images]

    final = concatenate_videoclips(clips, method="compose")
    final = final.set_audio(audio)

    final.write_videofile(output, fps=24, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    generate_video("https://www.zama.org/blog")
