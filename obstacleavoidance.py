import signal
import sys
from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# ---------------- ULTRASONIC ----------------
TRIG = 23
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)


ALARM = 15
GPIO.setup(ALARM, GPIO.OUT)

# ---------------- SERVO ----------------
SERVO = 18
GPIO.setup(SERVO, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO, 50)
servo_pwm.start(0)

# ---------------- MOTOR PINS ----------------
IN1 = 5
IN2 = 6
IN3 = 13
IN4 = 19
ENA = 12   # Left motor speed
ENB = 26   # Right motor speed

motor_pins = [IN1, IN2, IN3, IN4, ENA, ENB]


for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)

# Create PWM for speed control
left_pwm = GPIO.PWM(ENA, 1000)
right_pwm = GPIO.PWM(ENB, 1000)

left_pwm.start(40)   # Initial speed 40%
right_pwm.start(40)

# ---------------- FUNCTIONS ----------------

def set_speed(left_speed, right_speed):
    left_pwm.ChangeDutyCycle(left_speed)
    right_pwm.ChangeDutyCycle(right_speed)

def set_servo_angle(angle):
    duty = 2 + (angle / 18)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.4)
    servo_pwm.ChangeDutyCycle(0)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.01)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    #pulse_start = 0.0
    #pulse_end = 0.0
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    duration = pulse_end - pulse_start
    distance = duration * 17150
    return round(distance, 2)

# -------- MOTOR CONTROL --------
def forward(speed=40):
    set_speed(speed, speed)
    GPIO.output(IN1, True)
    GPIO.output(IN2, False)
    GPIO.output(IN3, True)
    GPIO.output(IN4, False)
    
def backward(speed=40):
    set_speed(speed, speed)
    GPIO.output(IN1, False)
    GPIO.output(IN2, True)
    GPIO.output(IN3, False)
    GPIO.output(IN4, True)

def stop():
    GPIO.output(IN1, False)
    GPIO.output(IN2, False)
    GPIO.output(IN3, False)
    GPIO.output(IN4, False)

def turn_left():
    set_speed(40, 40)  # Slow left motor
    GPIO.output(IN1, True)
    GPIO.output(IN2, False)
    GPIO.output(IN3, False)
    GPIO.output(IN4, True)
    time.sleep(0.5)
    stop()

def turn_right():
    set_speed(40, 40)  # Slow right motor
    GPIO.output(IN1, False)
    GPIO.output(IN2, True)
    GPIO.output(IN3, True)
    GPIO.output(IN4, False)
    time.sleep(0.5)
    stop()
    
def cleanup(sig,frame):
    print("Cleaning up GPIO...")
    GPIO.cleanup()
    sys.exit(0)
    
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)
    
# Load trained model
model = YOLO('/home/proekt/python/plastic_bottles.pt')

# Initialize camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 640)}
)
picam2.configure(config)
picam2.start()

print("Starting detection... Press 'q' to quit")

# ---------------- MAIN LOOP ----------------
try:
    while True:
        set_servo_angle(90)
        front_distance = get_distance()
        print("Front:", front_distance)

        if front_distance > 25:
            forward(25)
            frame = picam2.capture_array()

            # Run YOLO detection
            results = model(frame)
            # Process results
            for r in results:
               boxes = r.boxes
               print(r)
               for box in boxes:
                  conf = float(box.conf[0])
                  if conf > 0.55:
                      # Trigger alarm
                      GPIO.output(ALARM, GPIO.HIGH)
                      stop()
                      time.sleep(0.5)
                      forward(25)
                      GPIO.output(ALARM, GPIO.LOW)

                  annotated_frame = results[0].plot()

                  cv2.imshow("Plastic Bottle Detection", annotated_frame)

                  if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        else:
            stop()
            time.sleep(0.8)
            backward(40)
            time.sleep(0.8)
            stop()
            time.sleep(0.8)

            # Scan left
            set_servo_angle(150)
            left_distance = get_distance()
            print("Left:", left_distance)

            # Scan right
            set_servo_angle(30)
            right_distance = get_distance()
            print("Right:", right_distance)

            set_servo_angle(90)

            if left_distance > right_distance:
                turn_left()
            else:
                turn_right()

except KeyboardInterrupt:
    print("Stopping...")
    left_pwm.stop()
    right_pwm.stop()
    servo_pwm.stop()
    GPIO.cleanup()
    cv2.destroyAllWindows()
    picam2.stop()
