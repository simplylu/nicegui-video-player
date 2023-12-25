from fastapi.responses import StreamingResponse
from nicegui import APIRouter, Client, app, ui
from nicegui.events import KeyEventArguments
import os

# Create an APIRouter instance
router = APIRouter()

# Function to load JavaScript code
def load_js():
    video_js = open("video.js", "r").read()
    ui.run_javascript(video_js)

# Convert float to timestamp format (minutes:seconds)
def float_to_timestamp(val: float) -> str:
    minutes, seconds = divmod(int(val), 60)
    return f"{minutes}:{seconds:02d}"

# Async function to check if the video is paused
async def is_paused() -> bool:
    return await ui.run_javascript("""(() => { return document.querySelector(".video").paused })()""")

# Async function to get the current time of the video
async def get_video_current_time() -> float:
    try:
        current_time = await ui.run_javascript("""(() => { return document.querySelector(".video").currentTime })()""")
    except:
        current_time = 0
    return float(current_time if current_time else 0)

# Async function to get the duration of the video
async def get_video_duration() -> float:
    try:
        duration = await ui.run_javascript("""(() => { return document.querySelector(".video").duration })()""")
    except:
        duration = 100
    return float(duration if duration else 100)

# Async function to set the audio volume of the video
async def set_audio_volume(vol: float) -> None:
    await ui.run_javascript("""(() => { return document.querySelector(".video").volume = """ + str(vol) + """; })()""")

@ui.page("/")
async def index(client: Client):
    # Function to toggle play/pause of the video
    async def toggle_play():
        # Check if the video is paused
        paused = await is_paused()
        if paused:
            # If paused, play the video and update button icon
            video.play()
            btn_start_stop.name = "pause"
        else:
            # If playing, pause the video and update button icon
            video.pause()
            btn_start_stop.name = "play_arrow"
        # Update the button in the UI
        btn_start_stop.update()

    # Function to seek 10 seconds back in the video
    async def seek_back():
        video.seek((await get_video_current_time()) - 10)

    # Function to seek 10 seconds forward in the video
    async def seek_forward():
        video.seek((await get_video_current_time()) + 10)

    # Function to seek to the start of the video
    async def seek_start():
        video.seek(0)

    # Function to seek to the end of the video
    async def seek_end():
        video.seek(await get_video_duration())

    # Function to update time information in the UI
    async def update_time_info():
        # Get video duration and current time
        duration = await get_video_duration()
        current_time = await get_video_current_time()

        # Update the maximum value of the position slider
        if position._props["max"] != duration:
            position._props["max"] = duration

        # Update the position and label in the UI
        position.value = current_time
        lbl_time.text = f"{float_to_timestamp(current_time)}/{float_to_timestamp(duration)}"
        position.update()

    # Function to change the volume of the video
    async def change_volume() -> None:
        # Set the audio volume based on the slider value
        await set_audio_volume(volume.value / 100)

    # Function to show video controls in the UI
    def show_controls() -> None:
        controls.classes(remove="hidden")

    # Function to hide video controls in the UI
    def hide_controls() -> None:
        controls.classes(add="hidden")

    # Function to mute the video
    def mute() -> None:
        # Set the volume slider value to 0
        volume.value = 0

    
    # Wait for the client to be connected
    await client.connected()

    # Create a card with an absolute center alignment
    with ui.card().classes("absolute-center"):
        # Display a label with information about the NiceGUI Video Player
        ui.label("NiceGUI Video Player (press h/? for help)")

        # Create a video container with a video element
        with ui.element("div").classes("video-container"):
            video = ui.video(src="/media/test.mp4", controls=False).classes("video").on("click", lambda: ui.notify("Clicked"))

        # Create a position slider for video playback progress
        position = ui.slider(min=0, max=await get_video_duration(), value=0).classes("position-progress cursor-pointer").props("selection-color=red thumb-size=0 dense").on("click", lambda: video.seek(position.value))

        # Create a row for control buttons and labels
        with ui.row().classes("control-container w-full justify-center") as controls:
            # Display the current time and duration label
            lbl_time = ui.label("0:00/0:00").classes("mr-auto ml-0 mt-auto mb-auto pl-4")

            # Create a row for playback control buttons
            with ui.row().classes("ml-auto mr-auto mt-auto mb-auto"):
                ui.icon(name="skip_previous", size="large", color="white").on("click", seek_start).classes("cursor-pointer")
                ui.icon(name="chevron_left", size="large", color="white").on("click", seek_back).classes("cursor-pointer")
                btn_start_stop = ui.icon(name="play_arrow", size="large", color="white").on("click", toggle_play).classes("cursor-pointer play-pause")
                ui.icon(name="chevron_right", size="large", color="white").on("click", seek_forward).classes("cursor-pointer")
                ui.icon(name="skip_next", size="large", color="white").on("click", seek_end).classes("cursor-pointer")

            # Create a volume icon and slider
            ui.icon(name="volume_up", size="large", color="white").classes("mt-auto mb-auto")
            volume = ui.slider(min=0, max=100, value=100, on_change=change_volume).classes("w-2/12").props("color=white thumb-size=16px")

            # Create a settings icon with a dropdown menu
            with ui.icon(name="settings", size="large", color="white").classes("cursor-pointer mb-auto mt-auto pr-4"):
                with ui.menu().props('anchor="top left" self="bottom right"') as menu:
                    ui.menu_item("Play", on_click=video.play)
                    ui.menu_item("Pause", on_click=video.pause)
                    ui.menu_item("Mute", on_click=mute)

        # Display attribution information in markdown format
        ui.markdown("""
                    **Attribution**
                    
                    - Filename: sample-3.mp4<br>
                    - Source: [getsamplefiles.com](https://getsamplefiles.com/sample-video-files/mp4)""")

    # Create a dialog with a card for help information
    with ui.dialog() as help_dialog, ui.card():
        ui.label("Help").classes("font-bold text-2xl")
        ui.label("Capturing of Media Keys is enabled. Press any of these keys on your keyboard to interact with the video player: ⏯︎ ⏮ ⏭")
        ui.label("Keystrokes for interacting with the video player are also enabled. Press any of the following keys: p, n, m, r, ←, →")
        ui.markdown("""
                    - p/⏮: jump back to start / previous video
                    - n/⏭: jump to the end / next video
                    - space/⏯︎: toggle play
                    - m: toggle mute (does not store previous volume)
                    - ←/→: seek 10s forward or backward
                    - ↓/↑: increase/decrease volume
                    - h/?: show this help dialog
        """)
        ui.button("Close", on_click=help_dialog.close)
    
    # Register event listeners for video events
    video.on("timeupdate", update_time_info)  # Update time information while playing
    video.on("loadeddata", update_time_info)  # Update time information when video data is loaded
    video.on("ended", video.play)  # Automatically play the video when it ends
    # Uncomment the following lines if you want to handle additional video events
    # Note: These are not working yet due to some errors I don't understand
    # video.on("onmouseover", show_controls)
    # video.on("onmouseout", hide_controls)
    # video.on("click", toggle_play)

    # Async function to handle keyboard events
    async def handle_key(e: KeyEventArguments):
        # Check if the key event is on keyup
        if not e.action.keyup:
            return
        elif e.key == "h" or e.key == "?":
            # Open the help dialog when 'h' or '?' is pressed
            help_dialog.open()
        if e.key == "m":
            # Toggle mute (set volume to 0 or restore previous volume)
            volume.value = 0 if volume.value != 0 else 100
        elif e.key == " ":
            # Toggle play/pause when the space key is pressed
            await toggle_play()
        elif e.key == "p":
            # Seek to the start of the video when 'p' is pressed
            await seek_start()
        elif e.key == "n":
            # Seek to the end of the video when 'n' is pressed
            await seek_end()
        elif e.key.arrow_down:
            # Decrease volume when the down arrow key is pressed
            volume.value = max(0, volume.value - 10)
        elif e.key.arrow_up:
            # Increase volume when the up arrow key is pressed
            volume.value = min(100, volume.value + 10)
        elif e.key.arrow_left:
            # Seek 10 seconds backward when the left arrow key is pressed
            await seek_back()
        elif e.key.arrow_right:
            # Seek 10 seconds forward when the right arrow key is pressed
            await seek_forward()

    # Register a keyboard event handler
    keyboard = ui.keyboard(on_key=handle_key)

    # Load additional JavaScript code
    load_js()


# Define a FastAPI endpoint to stream video files
@router.page("/media/{video}")
def media(video: str) -> StreamingResponse:
    # Construct the file path
    fpath = os.path.join(os.getcwd(), "media", video)
    
    # Check if the file exists
    if os.path.exists(fpath):
        # Define a generator function to stream the file in chunks
        def iter_file():
            try:
                with open(fpath, "rb") as file:
                    # Read and yield chunks of the file
                    while chunk := file.read(1024 * 1024):
                        yield chunk
            except Exception as e:
                # Handle potential exceptions and print an error message
                print(repr(e))

        # Return a StreamingResponse with the file stream and media type
        return StreamingResponse(iter_file(), media_type="video/mp4")

# Run the FastAPI app
if __name__ in {'__main__', '__mp_main__'}:
    # Include the router in the app
    app.include_router(router)

    # Run the NiceGUI app with a dark theme
    ui.run(dark=True)