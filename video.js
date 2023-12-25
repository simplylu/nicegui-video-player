const playPauseBtn = document.querySelector(".play-pause");
let video = document.querySelector(".video");
let position = document.querySelector(".position-progress");
let controls = document.querySelector(".control-container");

function setupControls() {
    let video_rect = video.getBoundingClientRect();

    // Set position of controls based on the video rectangle
    controls.style.backgroundColor = "#2a2a2acc"
    controls.style.zIndex = 99;
    controls.style.position = "absolute";
    controls.style.width = `${video.clientWidth}px`;   
    controls.style.marginTop = `${video_rect.height+8}px`;

    // Set position of progress slider based on the video rectangle
    position.style.zIndex = 100;
    position.style.position = "absolute";
    position.style.width = `${video.clientWidth}px`;
    position.style.marginTop = `${video_rect.height+28}px`;
    console.log(video_rect);
}

// Call the setupControls function initially
setupControls();

// Add event listener for resize events on both video and window
window.addEventListener("resize", setupControls);

// Add event listener for the 'loadeddata' event on the video element
video.addEventListener("loadeddata", setupControls);


// Check if 'mediaSession' is supported in the browser
if ('mediaSession' in navigator) {
    // Handle 'play' action
    navigator.mediaSession.setActionHandler('play', () => {
        video.play();
        playPauseBtn.querySelector(".material-icons").textContent = "pause";
    });
    // Handle 'pause' action
    navigator.mediaSession.setActionHandler('pause', () => {
        video.pause();
        playPauseBtn.querySelector(".material-icons").textContent = "play_arrow";
    });
    // Handle 'previoustrack' action (set current time to the beginning of the video)
    navigator.mediaSession.setActionHandler('previoustrack', () => {
        video.currentTime = 0;
    });
    // Handle 'nexttrack' action (set current time to the end of the video)
    navigator.mediaSession.setActionHandler('nexttrack', () => {
        video.currentTime = video.duration;
    });
}