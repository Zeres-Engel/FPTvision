import cv2
import glob
import numpy as np
import os

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import FPTvision

from FPTvision.model_zoo.arcface_onnx import ArcFaceONNX
from FPTvision.app import FaceAnalysis


class ModelFunction3(QWidget):
    def __init__(self):
        super().__init__()

        # Khởi tạo mô hình phát hiện khuôn mặt
        self.app = FaceAnalysis(allowed_modules=['detection'])  # enable detection model only
        self.app.prepare(ctx_id=-1, det_size=(640, 640))  # Thay đổi kích thước det_size

        # Khởi tạo lớp ArcFaceONNX
        self.arcface = ArcFaceONNX(model_file='./gui/models/model.onnx')  # Thay đổi đường dẫn tới model_file của bạn

        # Đường dẫn đến thư mục chứa các khuôn mặt đã aligned
        self.aligned_faces_dir = './gui/aligned'

        # Load danh sách các khuôn mặt đã aligned và trích xuất embedding
        self.aligned_faces = []
        self.aligned_labels = []
        self.aligned_embeddings = []
        aligned_face_files = glob.glob(self.aligned_faces_dir + '/*.jpg')
        for face_file in aligned_face_files:
            face_image = cv2.imread(face_file)
            self.aligned_faces.append(face_image)
            self.aligned_labels.append(os.path.basename(face_file).split('.')[0])  # Lấy tên file làm nhãn

        self.aligned_embeddings = self.arcface.get_feat(self.aligned_faces)
        # Đường dẫn đến file trạng thái
        self.status_file = './gui/status.txt'
        self.status = 0
        self.cap = None  # VideoCapture instance
        self.open_webcam()

        # Khung hình hiển thị video từ webcam
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)

        # Tạo layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)

        self.setLayout(layout)
        self.setWindowTitle('Face Recognition App')

        # Biến lưu trữ tên khuôn mặt đã nhận dạng
        self.recognized_label = ""

        # Bắt đầu vòng lặp video
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(60)

    def update_frame(self):
        # Đọc nội dung từ file trạng thái
        with open(self.status_file, 'r') as file:
            self.status = file.read().strip()

        # Kiểm tra nội dung file trạng thái
        if self.status == '4':
            # Mở webcam nếu chưa mở
            self.open_webcam()

            # Kiểm tra xem webcam đã mở thành công chưa
            if self.cap is None:
                return

            # Đọc khung hình từ webcam
            ret, frame = self.cap.read()

            # Lật ngược khung hình
            frame = cv2.flip(frame, 1)

            # Phát hiện khuôn mặt trong khung hình
            try:
                faces = self.app.get(frame)
                if not faces:
                    self.display_frame(frame)
                    return

                # Duyệt qua các khuôn mặt đã phát hiện và thực hiện recognition
                for detected_face in faces:
                    bbox = detected_face.bbox.astype(int)
                    detected_face_img = frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]
                    detected_embedding = self.arcface.get_feat([detected_face_img])
                    max_similarity = 0
                    recognized_face_idx = -1

                    # So sánh với các khuôn mặt đã aligned để tìm khuôn mặt giống nhất
                    for idx, aligned_embedding in enumerate(self.aligned_embeddings):
                        similarity = self.arcface.compute_sim(aligned_embedding, detected_embedding)
                        if similarity > max_similarity:
                            max_similarity = similarity
                            recognized_face_idx = idx

                    if recognized_face_idx != -1:
                        recognized_face = self.aligned_faces[recognized_face_idx]
                        recognized_label = os.path.basename(self.aligned_labels[recognized_face_idx])

                        # Kiểm tra độ chính xác của khuôn mặt nhận dạng
                        if max_similarity >= 0.30:
                            self.recognized_label = recognized_label
                        else:
                            self.recognized_label = "Unknown"

                        # Hiển thị khuôn mặt phát hiện được và tên của khuôn mặt đã nhận dạng lên khung hình
                        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                        text = f"{self.recognized_label}-{round(max_similarity * 100, 2)}%"
                        cv2.putText(frame, text, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                        self.display_frame(frame)
                    else:
                        self.display_frame(frame)
            except:
                pass
        else:
            # Đóng webcam nếu đã mở
            self.close_webcam()


    def open_webcam(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set frame width to 1280
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set frame height to 720
        else:
            # Đóng webcam nếu đã mở
            self.close_webcam()

    def close_webcam(self):
        if self.cap is not None and self.status != '4':
            self.cap.release()
            self.cap = None


    def display_frame(self, frame):
        # Chuyển đổi khung hình từ OpenCV BGR sang RGB để hiển thị trên QLabel
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        # Dừng webcam và giải phóng tài nguyên khi đóng ứng dụng
        self.close_webcam()
        cv2.destroyAllWindows()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    window = ModelFunction3()
    window.show()
    app.exec()
