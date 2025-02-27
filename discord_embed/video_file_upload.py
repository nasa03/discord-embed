import os
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from discord_embed import settings
from discord_embed.generate_html import generate_html_for_videos
from discord_embed.video import Resolution, make_thumbnail, video_resolution


@dataclass
class VideoFile:
    """A video file.

    filename: The filename of the video file.
    location: The location of the video file.
    """

    filename: str
    location: str


def save_to_disk(file: UploadFile) -> VideoFile:
    """Save the uploaded file to disk.

    If spaces in the filename, replace with dots.

    Args:
        file: Our uploaded file.

    Returns:
        VideoFile object with the filename and location.
    """
    # Create the folder where we should save the files
    folder_video: str = os.path.join(settings.upload_folder, "video")
    Path(folder_video).mkdir(parents=True, exist_ok=True)

    # Replace spaces with dots in the filename.
    filename: str = file.filename.replace(" ", ".")

    # Save the uploaded file to disk.
    file_location: str = os.path.join(folder_video, filename)
    with open(file_location, "wb+") as f:
        f.write(file.file.read())

    return VideoFile(filename, file_location)


async def do_things(file: UploadFile) -> str:
    """Save video to disk, generate HTML, thumbnail, and return a .html URL.

    Args:
        file: Our uploaded file.

    Returns:
        Returns URL for video.
    """

    video_file: VideoFile = save_to_disk(file)

    file_url: str = f"{settings.serve_domain}/video/{video_file.filename}"
    res: Resolution = video_resolution(video_file.location)
    screenshot_url: str = make_thumbnail(video_file.location, video_file.filename)
    html_url: str = generate_html_for_videos(
        url=file_url,
        width=res.width,
        height=res.height,
        screenshot=screenshot_url,
        filename=video_file.filename,
    )
    return html_url
