import cv2
import numpy as np
from insightface.app import FaceAnalysis

app = FaceAnalysis(
    root="~/.cache/insightface",
    providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
)
app.prepare(ctx_id=0, det_size=(640, 640))
img = cv2.imread("../imgs/generated_faces.webp")
faces = app.get(img)
rimg = app.draw_on(img, faces)
cv2.imwrite("../imgs/faces_output.jpg", rimg)

color = (200, 160, 75)
for face in faces:
    lmk = face.landmark_2d_106
    lmk = np.round(lmk).astype(int)
    for i in range(lmk.shape[0]):
        p = tuple(lmk[i])
        cv2.circle(img, p, 1, color, 1, cv2.LINE_AA)
        cv2.putText(
            img,
            f"{i}",
            p,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.2,
            (255, 0, 0),
            1,
            cv2.LINE_AA,
        )

cv2.imwrite("../imgs/faces2_dots.jpg", img)
