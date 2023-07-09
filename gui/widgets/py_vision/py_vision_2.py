import cv2
import os

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QLineEdit, QMessageBox, QWidget

from PIL import Image, ImageQt

from FPTvision.utils import face_align

style = '''
QLineEdit {{
	background-color: {_bg_color}; 
	border-radius: {_radius}px;
	border: {_border_size}px solid transparent;
	padding-left: 10px;
    padding-right: 10px;
	selection-color: {_selection_color};
	selection-background-color: {_context_color};
    color: {_color};
}}
QLineEdit:focus {{
	border: {_border_size}px solid {_context_color};
    background-color: {_bg_color_active};
}}
'''
class PyLineEdit(QLineEdit):
    def __init__(
        self, 
        text = "",
        place_holder_text = "",
        radius = 8,
        border_size = 2,
        color = "#FFF",
        selection_color = "#FFF",
        bg_color = "#333",
        bg_color_active = "#222",
        context_color = "#00ABE8"
    ):
        super().__init__()
        if text:
            self.setText(text)
        if place_holder_text:
            self.setPlaceholderText(place_holder_text)
        self.set_stylesheet(
            radius,
            border_size,
            color,
            selection_color,
            bg_color,
            bg_color_active,
            context_color
        )
    def set_stylesheet(
        self,
        radius,
        border_size,
        color,
        selection_color,
        bg_color,
        bg_color_active,
        context_color
    ):
        style_format = style.format(
            _radius = radius,
            _border_size = border_size,           
            _color = color,
            _selection_color = selection_color,
            _bg_color = bg_color,
            _bg_color_active = bg_color_active,
            _context_color = context_color
        )
        self.setStyleSheet(style_format)


class ModelFunction2(QWidget):
    def __init__(self, model):
        super().__init__()

        self.text_name = PyLineEdit(
            text="",
            place_holder_text="Enter name",
            radius=8,
            border_size=2,
            color="#2c313c",
            selection_color="#3c4454",
            bg_color="#FCCB6E",
            bg_color_active="#FCCB6E",
            context_color="#f26f21",
        )
        self.text_name.setMinimumHeight(30)

        self.canvas_widget = QtWidgets.QWidget(self)
        self.canvas_widget.setMinimumSize(640, 480)  # Set minimum size for the webcam screen
        self.canvas_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.canvas_layout = QtWidgets.QVBoxLayout(self.canvas_widget)
        self.canvas_image = QtWidgets.QLabel(self.canvas_widget)
        self.canvas_image.setAlignment(QtCore.Qt.AlignCenter)

        # Đường dẫn đến file trạng thái
        self.status_file = './gui/status.txt'
        self.status = 0

        # Initialize variables
        self.cap = None  # VideoCapture instance
        self.model = model  # Model instance
        self.faces = None

        self.check_status()

        # Open webcam
        self.open_webcam()

        # Start frame update
        self.update_frame()

        self.close_webcam()

    def check_status(self):
        with open(self.status_file, 'r') as file:
            self.status = file.read().strip()

    def update_frame(self):
        try:
            # Kiểm tra nội dung file trạng thái
            with open(self.status_file, 'r') as file:
                self.status = file.read().strip()
        except:
            pass

        if self.status == '3':
            if self.cap is None:
                # Mở camera khi trạng thái là "3"
                self.cap = cv2.VideoCapture(0)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set frame width to 1280
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set frame height to 720
        else:
            self.close_webcam()

        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)  # Flip the frame horizontally

                # Detect face using model
                self.faces = self.model.get(frame)
                if len(self.faces) > 0:
                    # Find the face with the largest bounding box area
                    max_area = 0
                    max_bbox = None
                    max_face = None
                    for face in self.faces:
                        bbox = face.bbox.astype(int)
                        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                        if area > max_area:
                            max_area = area
                            max_bbox = bbox
                            max_face = face

                if max_bbox is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Chuyển đổi frame thành màu RGB
                    cv2.rectangle(frame_rgb, (max_bbox[0], max_bbox[1]), (max_bbox[2], max_bbox[3]), (242, 111, 33), 2)
                    cv2.putText(frame_rgb, f'Score: {max_face.det_score:.2f}', (max_bbox[0], max_bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (242, 111, 33), 2)
                else:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Chuyển đổi frame thành màu RGB

                image = Image.fromarray(frame_rgb)

                # Calculate the scaled size for the image to fit the canvas
                canvas_width = self.canvas_widget.width()
                canvas_height = self.canvas_widget.height()
                image_ratio = image.width / image.height
                canvas_ratio = canvas_width / canvas_height
                if image_ratio > canvas_ratio:
                    new_width = canvas_width
                    new_height = int(canvas_width / image_ratio)
                else:
                    new_height = canvas_height
                    new_width = int(canvas_height * image_ratio)
                image = image.resize((new_width, new_height))

                qt_image = ImageQt.ImageQt(image)
                pixmap = QtGui.QPixmap.fromImage(qt_image)
                self.canvas_image.setPixmap(
                    pixmap.scaled(canvas_width, canvas_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                )
        else:
            self.canvas_image.clear()
            self.close_webcam()

        QtCore.QTimer.singleShot(15, self.update_frame)

    def open_webcam(self):
        if self.cap is None and self.status == '3':
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set frame width to 1280
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set frame height to 720
        else:
            self.close_webcam()

    def close_webcam(self):
        if self.cap is not None and self.status != '3':
            self.cap.release()
            self.cap = None

    def capture_face(self):
        ret, frame = self.cap.read()
        if ret:
            # Detect face using model
            self.faces = self.model.get(frame)
            if len(self.faces) > 0:
                # Find the face with the largest bounding box area
                max_area = 0
                max_bbox = None
                max_face = None
                for face in self.faces:
                    bbox = face.bbox.astype(int)
                    area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                    if area > max_area:
                        max_area = area
                        max_bbox = bbox
                        max_face = face

                if max_bbox is not None:                     
                    # norm crop
                    face_image = face_align.norm_crop(frame, max_face.kps)

                    # Save face image
                    name = self.text_name.text()
                    if name != "":
                        # Remove spaces in directory name and image name
                        name_without_spaces = name.replace(" ", "_")

                        # Create the directory path
                        directory_path = os.path.join("./gui/aligned", name_without_spaces)

                        # Check if the directory exists
                        if not os.path.exists(directory_path):
                            os.makedirs(directory_path)

                        # Count the number of face images in the directory
                        count = len([name for name in os.listdir(directory_path) if
                                    os.path.isfile(os.path.join(directory_path, name))])

                        # Save the face image
                        image_path = os.path.join(directory_path, f"{count + 1}.jpg")
                        cv2.imwrite(image_path, face_image)

                        QMessageBox.information(self, "Information", "Face captured and saved successfully!")

                        self.text_name.clear()
                    else:
                        QMessageBox.warning(self, "Warning", "Please enter a name!")
            else:
                QMessageBox.warning(self, "Warning", "No face found in the image!")

    def closeEvent(self, event):
        self.close_webcam()
        event.accept() 
