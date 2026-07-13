# \\\\ Modules ////
import time
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

POSE_CONNECTIONS = frozenset([
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5),
    (5, 6), (6, 8), (9, 10), (11, 12), (11, 13),
    (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),
    (18, 20), (11, 23), (12, 24), (23, 24), (23, 25),
    (24, 26), (25, 27), (26, 28), (27, 29), (28, 30),
    (29, 31), (30, 32), (27, 31), (28, 32)
])

# \\\\ Variables ////

model_path = "pose_landmarker_lite.task"

pet_state = {
    "pet_name" : "Koky",
    "health" : 100,
    "xp" : 0,
    "status" : "Happy"
}

# --- Global variables to safely share data between async callback and main thread ---
latest_result = None
latest_image = None 
# ------------------------------------------------------------------------------------

# -------------------------------------------------------------- Setting up Mediapipe --------------------------------------------------------------

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# \\\\ Functions ////

def print_result(result, output_image: mp.Image, timestamp_ms: int):

    global latest_result, latest_image

    latest_result = result
    latest_image = output_image.numpy_view()


options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback = print_result,
    output_segmentation_masks=True)


def draw_landmarks_on_stream(bgr_stream, detection_result):
   
    if not detection_result or not getattr(detection_result, 'pose_landmarks', None) or not detection_result.pose_landmarks:
        return bgr_stream

    # pose_landmarks_list = detection_result.pose_landmarks
    annotated_stream = np.copy(bgr_stream)
    height, width, _ = annotated_stream.shape

    for pose_landmarks in detection_result.pose_landmarks:  

        for connection in POSE_CONNECTIONS:
            start_idx, end_idx = connection
            
            start_landmark = pose_landmarks[start_idx]
            end_landmark = pose_landmarks[end_idx]
            
            # Convert normalized coordinates [0.0 - 1.0] to pixel coordinates
            start_point = (int(start_landmark.x * width), int(start_landmark.y * height))
            end_point = (int(end_landmark.x * width), int(end_landmark.y * height))
            
            # Draw a green line
            cv2.line(annotated_stream, start_point, end_point, (0, 255, 0), 2)
            
        # 2. Draw the landmarks (joints)
        for landmark in pose_landmarks:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            
            # Draw a red dot
            cv2.circle(annotated_stream, (x, y), 5, (0, 0, 255), -1)

    return annotated_stream

# -------------------------------------------------------------- Start Of The Game --------------------------------------------------------------
print("-" * 20, "Sit up perfectly straight and look at the camera for calibration.", "-" * 20 , sep=" ")

with PoseLandmarker.create_from_options(options) as landmarker:

# -------------------------------------- Calibration phase --------------------------------------
# \\\\ Setting up Open CV ////

    cap = cv2.VideoCapture(0)

    start = time.time()

    while True:

        _, frame = cap.read()

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        timestamp_ms = int(time.time() * 1000)

        landmarker.detect_async(mp_image, timestamp_ms)


        if latest_result is not None and latest_image is not None:

            display_frame = cv2.cvtColor(latest_image, cv2.COLOR_RGB2BGR)

            annotated_frame = draw_landmarks_on_stream(display_frame, latest_result)
            
            if latest_result.pose_landmarks:
                # Get the landmarks for the first detected person
                landmarks = latest_result.pose_landmarks[0]
                
                # Get the normalized data for Nose (0), Left Shoulder (11), Right Shoulder (12)
                nose = landmarks[0]
                left_shoulder = landmarks[11]
                right_shoulder = landmarks[12]
                
                # Convert normalized coordinates (0.0 - 1.0) to actual screen pixels
                h, w, _ = annotated_frame.shape
                nose_px = (int(nose.x * w), int(nose.y * h))
                l_shoulder_px = (int(left_shoulder.x * w), int(left_shoulder.y * h))
                r_shoulder_px = (int(right_shoulder.x * w), int(right_shoulder.y * h))

                nose_y = nose_px[1]
                leftShoulder_y = l_shoulder_px[1]
                rightShoulder_y = r_shoulder_px[1]

                sMidpoint = (leftShoulder_y + rightShoulder_y) / 2

                perfect_posture_baseline = sMidpoint - nose_y
                

            cv2.imshow("Pose Tracking", annotated_frame)


        if cv2.waitKey(1) and time.time() - start >= 3:

            if perfect_posture_baseline is not None:

                print(perfect_posture_baseline)

                break

            else:

                print("Calibration failed to detect you. Retrying...")

                start = time.time()

    cap.release()
    cv2.destroyAllWindows()

    

# -------------------------------------- End Of Calibration Phase --------------------------------------

# -------------------------------------- Including pet states --------------------------------------
    cap = cv2.VideoCapture(0)

    start_time = time.time()

    while True:
        
        _, frame = cap.read()

        # cv2.imshow("Frame", frame)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        timestamp_ms = int(time.time() * 1000)

        landmarker.detect_async(mp_image, timestamp_ms)


        if latest_result is not None and latest_image is not None:

            display_frame = cv2.cvtColor(latest_image, cv2.COLOR_RGB2BGR)

            annotated_frame = draw_landmarks_on_stream(display_frame, latest_result)
                
            if latest_result.pose_landmarks:
                # Get the landmarks for the first detected person
                landmarks = latest_result.pose_landmarks[0]
                    
                # Get the normalized data for Nose (0), Left Shoulder (11), Right Shoulder (12)
                nose = landmarks[0]
                left_shoulder = landmarks[11]
                right_shoulder = landmarks[12]
                    
                # Convert normalized coordinates (0.0 - 1.0) to actual screen pixels
                h, w, _ = annotated_frame.shape
                nose_px = (int(nose.x * w), int(nose.y * h))
                l_shoulder_px = (int(left_shoulder.x * w), int(left_shoulder.y * h))
                r_shoulder_px = (int(right_shoulder.x * w), int(right_shoulder.y * h))

                nose_y = nose_px[1]
                leftShoulder_y = l_shoulder_px[1]
                rightShoulder_y = r_shoulder_px[1]

                sMidpoint = (leftShoulder_y + rightShoulder_y) / 2

                current_distance = sMidpoint - nose_y

                if ((perfect_posture_baseline - current_distance) / perfect_posture_baseline) * 100 > 15 :

                    current_posture = "Slouching"

                else:

                    current_posture = "Good"


                end_time = time.time()

                box_offset = 30 

                l_top_left = (l_shoulder_px[0] - box_offset, l_shoulder_px[1] - box_offset)
                l_bottom_right = (l_shoulder_px[0] + box_offset, l_shoulder_px[1] + box_offset)

                r_top_left = (r_shoulder_px[0] - box_offset, r_shoulder_px[1] - box_offset)
                r_bottom_right = (r_shoulder_px[0] + box_offset, r_shoulder_px[1] + box_offset)

                if current_posture == "Slouching" :

                    cv2.rectangle(annotated_frame, l_top_left, l_bottom_right, (0, 0, 255), 2)
                    cv2.rectangle(annotated_frame, r_top_left, r_bottom_right, (0, 0, 255), 2)
                    cv2.imshow("Pose Tracking", annotated_frame)

                elif current_posture == "Good" :
                    
                    cv2.rectangle(annotated_frame, l_top_left, l_bottom_right, (0, 255, 0), 2)
                    cv2.rectangle(annotated_frame, r_top_left, r_bottom_right, (0, 255, 0), 2)
                    cv2.imshow("Pose Tracking", annotated_frame)

                    
                if  end_time - start_time >= 1 :
                    
                    start_time = end_time

                    if current_posture == "Slouching" :
                        
                        pet_state["health"] -= 5
                        pet_state["status"] = "In Pain"

                        print("Warning ! Your pet is in pain !!")

                    elif current_posture == "Good" :
                        
                        pet_state["xp"] += 1

                        print("You are good")

                        if pet_state["health"] < 100:

                            pet_state["health"] += 2

            else:

                if latest_image is not None:
                    print("No player detected !")
                    cv2.imshow("Pose Tracking", cv2.cvtColor(latest_image, cv2.COLOR_RGB2BGR))

        if cv2.waitKey(1) & 0xFF == ord('q') or pet_state["health"] == 0:

            break

cap.release()
cv2.destroyAllWindows()

# -------------------------------------------------------------- End Of The Game --------------------------------------------------------------

if pet_state["health"] == 0:    # Game Over

    print("Game Over ! Please, take care of your back. Health is more precious than money.")

