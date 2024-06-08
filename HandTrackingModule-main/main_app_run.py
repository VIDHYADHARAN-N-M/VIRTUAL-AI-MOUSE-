import cv2
import mediapipe as mp
import pyautogui

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Unable to open video capture device.")
    exit(1)

hand_detector = mp.solutions.hands.Hands()
drawing_utils = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()
index_x, index_y = 0, 0
frame_count = 0
processing_interval = 5  # Process every 5 frames

while True:
    _, frame = cap.read()
    if frame is None:
        print("Error: Unable to read frame from video capture.")
        break

    frame_count += 1
    if frame_count % processing_interval != 0:
        continue  # Skip processing this frame

    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = hand_detector.process(rgb_frame)
    if output.multi_hand_landmarks:
        for hand in output.multi_hand_landmarks:
            drawing_utils.draw_landmarks(frame, hand)
            landmarks = hand.landmark
            for id, landmark in enumerate(landmarks):
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)
                if id == 8:
                    cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255))
                    index_x = int(screen_width * landmark.x)
                    index_y = int(screen_height * landmark.y)

                if id == 4:
                    cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255))
                    thumb_x = int(screen_width * landmark.x)
                    thumb_y = int(screen_height * landmark.y)
                    print('outside', abs(index_y - thumb_y))
                    if abs(index_y - thumb_y) < 20:
                        pyautogui.click()
                        pyautogui.sleep(1)
                    elif abs(index_y - thumb_y) < 200:
                        pyautogui.moveTo(index_x, index_y)
    cv2.imshow('Virtual Mouse', frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('r'):
        frame_count = 0  # Reset frame counter

cap.release()
cv2.destroyAllWindows()
