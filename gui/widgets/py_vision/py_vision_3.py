import cv2
import glob
import os
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap, Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class ModelFunction3(QWidget):
    def __init__(self, detection_model, recognition_model):
        super().__init__()

        # Khởi tạo mô hình phát hiện khuôn mặt
        self.detection_model = detection_model
        self.recognition_model = recognition_model

        # Đường dẫn đến thư mục chứa các khuôn mặt đã aligned
        self.aligned_faces_dir = './gui/aligned'

        # Load danh sách các khuôn mặt đã aligned và trích xuất embedding
        self.faces_aligned = []  # List lưu đường dẫn và embedding
        aligned_face_dirs = glob.glob(self.aligned_faces_dir + '/*')
        for face_dir in aligned_face_dirs:
            name_file = os.path.join(face_dir)
            face_files = glob.glob(os.path.join(face_dir, '*.jpg'))
            if len(face_files) > 0:
                face_images = [cv2.imread(file) for file in face_files]
                face_embeddings = self.recognition_model.get_feat(face_images[0:])
                self.faces_aligned.append((name_file, face_embeddings))

        # Đường dẫn đến file trạng thái
        self.status_file = './gui/status.txt'
        self.status = 0
        self.cap = None  # VideoCapture instance
        self.open_webcam()

        # Khung hình hiển thị video từ webcam
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        
        # Tạo QVBoxLayout và thêm video_label vào layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        # Biến lưu trữ tên khuôn mặt đã nhận dạng
        self.recognized_label = ""

        # Bắt đầu vòng lặp video
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

    def update_frame(self):
        # Đọc nội dung từ file trạng thái
        try:
            with open(self.status_file, 'r') as file:
                self.status = file.read().strip()
        except:
            pass

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
                faces = self.detection_model.get(frame)
                if not faces:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.display_frame(frame)
                    return

                # Duyệt qua các khuôn mặt đã phát hiện và thực hiện recognition 
                for face in faces:
                    bbox = face.bbox.astype(int)
                    
                    # detected_face_img = frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]
                    detected_embedding = self.recognition_model.get(frame, face)
                    max_similarity = 0
                    recognized_face_name = ""

                    # So sánh với các khuôn mặt đã aligned để tìm khuôn mặt giống nhất
                    for name, aligned_embedding in self.faces_aligned:
                        similarity = 0
                        if len(aligned_embedding) > 1:
                            cnt = 0
                            for embedding in aligned_embedding:
                                similarity = max(similarity, self.recognition_model.compute_sim(embedding, detected_embedding))
                        else:
                            similarity = self.recognition_model.compute_sim(aligned_embedding, detected_embedding)

                        if similarity > max_similarity:
                            max_similarity = similarity
                            recognized_face_name = name
                        
                    if recognized_face_name:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        recognized_label = recognized_face_name.split("\\")[1].replace('_', ' ')

                        # Kiểm tra độ chính xác của khuôn mặt nhận dạng
                        if max_similarity >= 0.5:
                            self.recognized_label = recognized_label
                        else:
                            self.recognized_label = "Unknown"
                
                        # Hiển thị khuôn mặt phát hiện được và tên của khuôn mặt đã nhận dạng lên khung hình
                        cv2.rectangle(frame_rgb, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (242, 111, 33), 2)
                        # Lấy tọa độ các điểm landmark từ faces[0].kps
                        landmarks = face.kps

                        # Chọn chỉ số của 5 điểm landmark muốn vẽ
                        landmark_indices = [0, 1, 2, 3, 4]

                        # Vẽ các điểm landmark
                        for index in landmark_indices:
                            x, y = landmarks[index]
                            cv2.circle(frame_rgb, (int(x), int(y)), 2, (0, 255, 0), -1)
                            
                        text = f"{self.recognized_label} {round(max_similarity * 100, 2)}%"
                        cv2.putText(frame_rgb, text, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (242, 111, 33), 2)

                        self.display_frame(frame_rgb)
                    else:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        self.display_frame(frame_rgb)
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
            self.cap.set(cv2.CAP_PROP_FPS, 60)  # Set frame rate to 60 FPS
        else:
            # Đóng webcam nếu đã mở
            self.close_webcam()

    def close_webcam(self):
        if self.cap is not None and self.status != '4':
            self.cap.release()
            self.cap = None

    def display_frame(self, frame_rgb):
        # Chuyển đổi khung hình từ OpenCV BGR sang RGB để hiển thị trên QLabel
        image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        # Dừng webcam và giải phóng tài nguyên khi đóng ứng dụng
        self.close_webcam()
        cv2.destroyAllWindows()
        super().closeEvent(event)