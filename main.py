import json
import shlex
import subprocess
from datetime import datetime

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "Uploads"


# function to find the resolution of the input video file
def find_video_resolution(path_to_video):
    cmd = "ffprobe -v quiet -print_format json -show_streams "
    args = shlex.split(cmd)
    args.append(path_to_video)
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobe_output = subprocess.check_output(args).decode("utf-8")
    ffprobe_output = json.loads(ffprobe_output)

    # find height and width
    height = ffprobe_output["streams"][0]["height"]
    width = ffprobe_output["streams"][0]["width"]

    return height, width


def generate_html(
    video_url, video_width, video_height, video_screenshot, video_filename
):
    video_html = f"""
    <!DOCTYPE html>

    <!-- Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->
    <head>
        <meta property="og:type" content="video.other">
        <meta property="twitter:player" content="{video_url}">
        <meta property="og:video:type" content="text/html">
        <meta property="og:video:width" content="{video_width}">
        <meta property="og:video:height" content="{video_height}">
        <meta name="twitter:image" content="{video_screenshot}">
        <meta http-equiv="refresh" content="0;url={video_url}">
    </head>
    """

    video_filename += ".html"
    html_url = f"https://killyoy.lovinator.space/{video_filename}"

    with open(f"Uploads/{video_filename}", "w") as file:
        file.write(video_html)
    return html_url


def get_first_frame(path_video, file_filename):
    cmd = f"ffmpeg -y -i {path_video} -vframes 1 Uploads/{file_filename}.jpg"
    args = shlex.split(cmd)

    subprocess.check_output(args).decode("utf-8")

    return f"https://killyoy.lovinator.space/{file_filename}.jpg"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            print(f"{filename=}")
            filepath = f"Uploads/{file.filename}"
            print(f"{filepath=}")
            file.save(filepath)

            height, width = find_video_resolution(filepath)
            print(f"{height=}")
            print(f"{width=}")

            screenshot_url = get_first_frame(filepath, file.filename)
            print(f"{screenshot_url=}")

            video_url = f"https://killyoy.lovinator.space/{file.filename}"
            print(f"{video_url=}")

            html_url = generate_html(
                video_url,
                width,
                height,
                screenshot_url,
                filename,
            )
            print(f"{html_url=}")
            return redirect(url_for("uploaded_file", filename=file.filename))
    return redirect(url_for("index"))


@app.route("/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
