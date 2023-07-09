import os
import cv2
from PIL import Image

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import (
    QLabel,  QWidget, QLineEdit,
    QFileDialog, QMessageBox
)

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

        
class ModelFunction1(QWidget):
    def __init__(self, model):
        super().__init__()

        self.model = model

        self.text_name = PyLineEdit(
            text="",
            place_holder_text="Enter name",
            radius=8,
            border_size=2,
            color="#2c313c",
            selection_color="#3c4454",
            bg_color=" #FCCB6E",
            bg_color_active="#FCCB6E",
            context_color="#f26f21",
        )
        self.text_name.setMinimumHeight(30)

        self.canvas_image = QLabel()
        self.canvas_image.setAlignment(Qt.AlignCenter)

        self.image_path = None
        self.image_pixmap = None

    def open_image(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Image Files (*.jpg)")
        if file_dialog.exec():
            self.image_path = file_dialog.selectedFiles()[0]

            image = Image.open(self.image_path)

            image_data = image.convert("RGB").tobytes("raw", "RGB")
            q_image = QImage(
                image_data, image.size[0], image.size[1], QImage.Format_RGB888
            )
            self.image_pixmap = QPixmap.fromImage(q_image)

            max_width = self.canvas_image.width()
            max_height = self.canvas_image.height()
            resized_pixmap = self.image_pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio)

            self.canvas_image.setPixmap(resized_pixmap)

            
    def save_face(self):
        if self.image_path is not None:
            if self.image_pixmap is not None:
                image = cv2.imread(self.image_path)
                try:
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    faces = self.model.get(image_rgb)
                    if len(faces) == 1:
                        # norm_crop
                        face_image = face_align.norm_crop(image_rgb, faces[0].kps)

                        name = self.text_name.text()
                        if name != "":
                            # Remove diacritical marks from the name
                            name_without_diacritics = name

                            # Replace spaces with underscores in directory name and image name
                            name_without_spaces = name_without_diacritics.replace(" ", "_")

                            # Create the directory path
                            directory_path = os.path.join("./gui/aligned", name_without_spaces)

                            # Check if the directory exists
                            if not os.path.exists(directory_path):
                                os.makedirs(directory_path)

                            # Count the number of face images in the directory
                            image_count = len([name for name in os.listdir(directory_path) if
                                                os.path.isfile(os.path.join(directory_path, name))])

                            # Save the face image with the numbered filename
                            face_filename = f"{image_count + 1}.jpg"
                            face_path = os.path.join(directory_path, face_filename)
                            cv2.imwrite(face_path, face_image)

                            # Get bounding box coordinates
                            bbox = faces[0].bbox
                            x1, y1, x2, y2 = bbox
                            
                            # Get detected score
                            det_score = faces[0].det_score

                            # Draw bounding box and text on the QPixmap
                            painter = QPainter(self.image_pixmap)
                            painter.setPen(QPen(QColor("#f26f21"), 2))
                            painter.setFont(QFont("Segoe UI", 32, QFont.Bold))
                            painter.drawRect(int(x1), int(y1), int(x2 - x1), int(y2 - y1))
                            painter.setPen(QPen(QColor("#f26f21")))
                            painter.drawText(QPoint(int(x1), int(y1) - 10), f"{name}: {det_score:.2f}")
                            painter.end()

                            max_width = self.canvas_image.width()
                            max_height = self.canvas_image.height()
                            resized_pixmap = self.image_pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio)
                            self.canvas_image.setPixmap(resized_pixmap)

                            QMessageBox.information(self, "Information", "Face saved successfully")
                            self.text_name.setText("")
                        else:
                            QMessageBox.warning(self, "Warning", "Please enter a name")
                    elif len(faces) == 0:
                        QMessageBox.warning(self, "Warning", "No face found in the image")
                    else:
                        QMessageBox.warning(self, "Warning", "Multiple faces found in the image")
                except:
                    QMessageBox.warning(
                        self, "Error", "Your image does not follow the standard color format, so accurate detection cannot be performed!"
                    )

