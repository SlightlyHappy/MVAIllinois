import cv2
from gtts import gTTS
import pytesseract
import os
from moviepy.editor import VideoFileClip, concatenate_audioclips, AudioFileClip

# Specify the path to the Tesseract executable (update this based on your installation)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Get the absolute path of the script's directory
script_directory = os.path.abspath(os.path.dirname(__file__))

# Specify the folder containing images
images_folder = os.path.join(script_directory, "images")

# Get a list of folders in the "images" folder
folders = [f for f in os.listdir(images_folder) if os.path.isdir(os.path.join(images_folder, f))]

# Ask the user to select a folder
print("Select a folder:")
for i, folder in enumerate(folders, 1):
    print(f"{i}. {folder}")

# Ensure the user selects a valid option
selected_index = -1
while selected_index not in range(len(folders)):
    try:
        selected_index = int(input("Enter the number corresponding to the folder: ")) - 1
        if selected_index not in range(len(folders)):
            print("Invalid selection. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number.")

# Set the selected folder within the "images" folder
selected_folder = folders[selected_index]
image_folder = os.path.join(images_folder, selected_folder)

# Specify the absolute path to the output folder
output_folder = os.path.join(script_directory, "output")

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Get a list of image files in the selected folder
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

# Initialize text-to-speech
language = 'en'  # You can change the language code if needed

# Set video resolution to HD (1920x1080)
width, height = 1920, 1080

# Set frames per second (fps)
fps = 30

# Create VideoWriter object with HD resolution and specify the output folder
output_filename = 'output_video.mp4'
output_path = os.path.join(output_folder, output_filename)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Create a list to store audio clips and their paths
audio_clips = []
audio_clip_paths = []

# Loop through image files
for image_file in image_files:
    # Read the image
    image_path = os.path.join(image_folder, image_file)
    frame = cv2.imread(image_path)

    # Extract text from the image using Tesseract OCR
    text = pytesseract.image_to_string(frame, config='--psm 6')

    # Use text-to-speech to convert text to audio
    tts = gTTS(text=text, lang=language, slow=False)

    # Save the audio clip directly
    audio_clip_path = os.path.join(script_directory, f"temp_audio_{image_file}.mp3")
    tts.save(audio_clip_path)

    # Add the audio clip path to the list
    audio_clip_paths.append(audio_clip_path)

    # Add the text audio to the video for the entire duration of the audio clip
    audio_clip = AudioFileClip(audio_clip_path)
    for _ in range(int(audio_clip.duration * fps)):
        # Resize the image to match HD resolution
        frame = cv2.resize(frame, (width, height))
        # Add the resized image to the video
        out.write(frame)

    # Append the audio clip to the list
    audio_clips.append(audio_clip)

# Release the VideoWriter
out.release()

# Concatenate all audio clips into a single audio file
if audio_clips:
    final_audio_clip = concatenate_audioclips(audio_clips)

    # Write the final video with synchronized audio
    final_output_path = os.path.join(output_folder, "final_output.mp4")
    final_audio_clip.write_audiofile(final_output_path, codec="aac", fps=44100)

    # Remove temporary audio clips
    for audio_clip, audio_clip_path in zip(audio_clips, audio_clip_paths):
        audio_clip.close()
        os.remove(audio_clip_path)  # Remove the temporary audio file
else:
    print("No audio clips to concatenate.")

# Specify the name for the final merged output
final_merged_output_filename = input("Enter the name for the final merged output (without extension): ") + '.mp4'
final_merged_output_path = os.path.join(output_folder, final_merged_output_filename)

# Load the video file with images
video_clip = VideoFileClip(output_path)

# Load the audio file with synchronized content
audio_file_path = os.path.join(output_folder, "final_output.mp4")
audio_clip = AudioFileClip(audio_file_path)

# Combine the video and audio clips
final_clip = video_clip.set_audio(audio_clip)

# Write the final merged video with synchronized audio
final_clip.write_videofile(final_merged_output_path, codec="libx264", audio_codec="aac")

# Release the VideoFileClip
video_clip.reader.close()
if video_clip.audio:  # Check if video_clip has audio before attempting to close the audio reader
    video_clip.audio.reader.close_proc()
audio_clip.reader.close()
audio_clip.audio.reader.close_proc()

# Remove the temporary video and audio files
os.remove(output_path)
os.remove(audio_file_path)
