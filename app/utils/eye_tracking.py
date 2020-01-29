from flask_login import current_user
from .gaze_tracking import GazeTracking
import cv2
import os


def eye_tracking(video_file, save_directory):

    webcam = cv2.VideoCapture(video_file)

    frame_width = int(webcam.get(3))
    frame_height = int(webcam.get(4))

    # Define the codec and filename.
    fourcc = cv2.VideoWriter_fourcc('V', 'P', '8', '0')
    output = cv2.VideoWriter(os.path.join(save_directory, 'output.webm'), fourcc, 25, (frame_width, frame_height))

    gaze = GazeTracking()

    try:
        while True:
            # We get a new frame from the webcam
            _, frame = webcam.read()

            # We send this frame to GazeTracking to analyze it
            gaze.refresh(frame)

            frame = gaze.annotated_frame()
            text = ""
            if gaze.is_blinking():
                text = "User is Blinking"
            elif gaze.is_right():
                text = "User is Looking right"
            elif gaze.is_left():
                text = "User is Looking left"
            elif gaze.is_center():
                text = "User is Looking center"

            cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

            left_pupil = gaze.pupil_left_coords()
            right_pupil = gaze.pupil_right_coords()
            cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
            cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

            cv2.imshow("Demo", frame)
            output.write(frame)
            if cv2.waitKey(1) == 27:
                break

        cv2.destroyAllWindows()
        output.release()

    except Exception:
        cv2.destroyAllWindows()
        output.release()
        pass


