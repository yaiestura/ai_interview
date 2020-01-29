import cv2
import os

HAAR_CASCADE_PATH = "app/utils/haarcascade_frontalface_alt.xml"

def detect_faces(image, cascade):
    #print 'detect fn' #
    faces = []
    detected = cascade.detectMultiScale(image, 1.3, 4, cv2.CASCADE_SCALE_IMAGE,(40,40))
    print(detected)

    if detected!=[]:
        #print 'face detected' #
        for (x,y,w,h) in detected: #for (x,y,w,h),n in detected:
            faces.append((x,y,w,h))
    return faces

def head_movement_estimation(video_file, save_directory):
    #print 'creating window' #
    cv2.namedWindow("Video")

    capture = cv2.VideoCapture(video_file)
    cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

    frame_width = int(capture.get(3))
    frame_height = int(capture.get(4))

    # Define the codec and filename.
    fourcc = cv2.VideoWriter_fourcc('V', 'P', '8', '0')
    output = cv2.VideoWriter(os.path.join(save_directory, 'head.webm'), fourcc, 25, (frame_width, frame_height))

    faces = []

    i = 0
    c = -1
    while (c == -1):
        ret, image = capture.read()

        faces = detect_faces(image, cascade)

        for (x,y,w,h) in faces:
            cv2.rectangle(image, (x,y), (x+w,y+h), 255)
            cv2.putText(image, f"x:y = {x}:{y}, face = {w}:{h}", (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

        output.write(image)
        cv2.imshow("Video", image)
        i += 1
        c = cv2.waitKey(1)
        if(c==27):
            #escape
            break;

    cv2.destroyAllWindows()
    output.release()
    capture.release()
