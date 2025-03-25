# EVE Online Tick Bombing Calculator

A web-based utility for EVE Online players to calculate precise bomb launch timing during warp operations. This tool helps players determine the optimal moment to launch bombs to hit targets that are in warp.

## Features

- Calculate warp time based on distance, warp speed, and sub-warp speed
- Break down warp phases (acceleration, cruise, deceleration)
- Precisely time bomb launches to intercept warping targets
- Interactive countdown timer with visual indicators
- Voice alerts for critical timing events ("ALIGN" and "LAUNCH")

## How to Use

1. Enter the target information (warp distance, speed parameters)
2. Click "Calculate" to get detailed timing information
3. Set your align and bomb alert timings
4. Click "Start Timer" to begin the countdown
5. Listen for voice alerts and follow the visual cues

## Technical Details

- Built with Python (Flask) backend
- Frontend uses vanilla JavaScript with Web Speech API for voice alerts
- Responsive design for use on various devices

## Local Development

1. Clone this repository
2. Install dependencies: `pip install flask gunicorn`
3. Run the application: `python web_app.py`

## Deployment

This application can be deployed on various platforms including Render, Heroku, or any other Python-compatible hosting service.

## License

This project is available for free use by the EVE Online community.