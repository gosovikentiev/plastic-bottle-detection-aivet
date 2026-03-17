# Plastic Bottle Detection Robot

A simple robot that detects plastic bottles using a YOLO model.

## Hardware
- Raspberry Pi 5
- PiCamera2
- Ultrasonic sensors (obstacle detection)
- 3-wheel chassis
- Speaker

## Software
- Python 3
- YOLO (object detection model)
- PiCamera2
- OpenCV
- RPi.GPIO / gpiozero (motor & sensor control)

## Features
- Real-time bottle detection (YOLO)
- Camera input via PiCamera2
- Obstacle avoidance using ultrasonic sensors
- Beeps when it detects plastic

## Usage
Run the detection script on the Raspberry Pi to start the system.

## Installation

`git clone https://github.com/gosovikentiev/plastic-bottle-detection-aivet`

`cd plastic-bottle-detection`

`python setup.py`

`reboot`