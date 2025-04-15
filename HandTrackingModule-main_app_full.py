import cv2
import mediapipe as mp
import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import comtypes
import math
import time

# Initialize mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)
screen_width, screen_height = pyautogui.size()

# Volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volume_change_delay = 0.2
last_volume_time = time.time()

# Drag state
dragging = False

# Distance calculator
def distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            lm = hand.landmark

            index_tip = lm[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = lm[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            ring_tip = lm[mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = lm[mp_hands.HandLandmark.PINKY_TIP]
            thumb_tip = lm[mp_hands.HandLandmark.THUMB_TIP]

            x = int(index_tip.x * screen_width)
            y = int(index_tip.y * screen_height)
            pyautogui.moveTo(x, y)

            select_dist = distance(index_tip, middle_tip)
            drag_dist = distance(index_tip, thumb_tip)
            scroll_x_dist = abs(thumb_tip.x - pinky_tip.x)
            scroll_y_diff = thumb_tip.y - pinky_tip.y
            pinky_thumb_dist = distance(thumb_tip, pinky_tip)

            all_finger_open = (
                index_tip.y < thumb_tip.y and
                middle_tip.y < thumb_tip.y and
                ring_tip.y < thumb_tip.y and
                pinky_tip.y < thumb_tip.y
            )

            current_time = time.time()

            # Pointing Mode
            if index_tip.y < thumb_tip.y:
                print("Pointing Mode")

                if select_dist < 0.05:
                    pyautogui.click()
                    print("Click")

                elif drag_dist < 0.04:
                    if not dragging:
                        pyautogui.mouseDown()
                        dragging = True
                        print("Drag Start")
                else:
                    if dragging:
                        pyautogui.mouseUp()
                        dragging = False
                        print("Drag End")

            else:
                # Scroll: Only if thumb and pinky far apart (horizontal X direction)
                if scroll_x_dist > 0.08:
                    if scroll_y_diff > 0.02:
                        pyautogui.scroll(30)
                        print("Scroll Up")
                    elif scroll_y_diff < -0.02:
                        pyautogui.scroll(-30)
                        print("Scroll Down")

                # Volume down: Thumb + Pinky pinch
                elif pinky_thumb_dist < 0.04 and current_time - last_volume_time > volume_change_delay:
                    vol = volume.GetMasterVolumeLevelScalar()
                    volume.SetMasterVolumeLevelScalar(max(vol - 0.05, 0.0), None)
                    last_volume_time = current_time
                    print("Volume Down")

            # Volume up: All fingers open
            if all_finger_open and current_time - last_volume_time > volume_change_delay:
                vol = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(min(vol + 0.05, 1.0), None)
                last_volume_time = current_time
                print("Volume Up")

            mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Gesture Master Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
