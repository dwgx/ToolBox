# top/dwgx/Modules.傻逼
#
# import random
# import math
# from PyQt6.QtWidgets import QWidget, QApplication, QLabel
# from PyQt6.QtGui import QPainter, QColor, QFont, QBrush
# from PyQt6.QtCore import QTimer, Qt
#
#
# class Example2(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.x_screen = 1200
#         self.y_screen = 800
#         self.colors = [(255, 32, 83), (255, 222, 250), (255, 0, 0), (255, 2, 2), (255, 0, 8), (255, 5, 5)]
#         self.points = []
#         self.create_data()
#         self.setFixedSize(self.x_screen, self.y_screen)
#
#         # Set up a timer for refreshing the display
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update)
#         self.timer.start(20)
#
#         # Create text label
#         self.text_label = QLabel("爱来自 DWGX", self)
#         font = QFont("Arial", 20)  # Smaller font size
#         font.setWeight(QFont.Weight.Bold)
#         self.text_label.setFont(font)
#         self.text_label.setStyleSheet("color: white;")
#         self.text_label.move(random.randint(0, self.x_screen - 200), self.y_screen - 100)
#         self.text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
#
#         # Timer for moving text
#         self.text_timer = QTimer(self)
#         self.text_timer.timeout.connect(self.move_text)
#         self.text_timer.start(100)
#
#     def create_data(self):
#         for theta in range(0, 180, 5):  # Polar angle
#             for phi in range(0, 360, 5):  # Azimuthal angle
#                 rad_theta = math.radians(theta)
#                 rad_phi = math.radians(phi)
#                 x = 16 * (math.sin(rad_theta) ** 3)
#                 y = 13 * math.cos(rad_theta) - 5 * math.cos(2 * rad_theta) - 2 * math.cos(3 * rad_theta) - math.cos(4 * rad_theta)
#                 color = random.choice(self.colors)
#                 self.points.append({'color': color, 'x': x, 'y': y})
#
#         # Create the left half of the heart shape
#         for theta in range(0, 180, 5):
#             rad_theta = math.radians(theta)
#             x = -16 * (math.sin(rad_theta) ** 3)  # Mirror x for left half
#             y = 13 * math.cos(rad_theta) - 5 * math.cos(2 * rad_theta) - 2 * math.cos(3 * rad_theta) - math.cos(4 * rad_theta)
#             color = random.choice(self.colors)
#             self.points.append({'color': color, 'x': x, 'y': y})
#
#     def paintEvent(self, event):
#         painter = QPainter(self)
#
#         # Draw 3D heart shape with shading
#         for point in self.points:
#             projected_x = int(point['x'] * 20 + self.x_screen // 2)
#             projected_y = int(-point['y'] * 20 + self.y_screen // 2)
#             size = 8  # Larger size for better visibility
#             color = QColor(*point['color'])
#
#             # Create a gradient effect for depth
#             brush = QBrush(color)
#             painter.setBrush(brush)
#             painter.drawEllipse(projected_x, projected_y, size, size)
#
#         # Draw a darker outline for the 3D effect
#         painter.setPen(QColor(0, 0, 0, 100))  # Semi-transparent black for depth
#         for point in self.points:
#             projected_x = int(point['x'] * 20 + self.x_screen // 2)
#             projected_y = int(-point['y'] * 20 + self.y_screen // 2)
#             painter.drawEllipse(projected_x, projected_y, size, size)
#
#     def move_text(self):
#         current_pos = self.text_label.pos()
#         if current_pos.y() < -50:
#             self.text_label.move(random.randint(0, self.x_screen - 200), self.y_screen)
#         else:
#             self.text_label.move(current_pos.x(), current_pos.y() - 2)  # Slightly slower for smoothness
#
#
# if __name__ == "__main__":
#     import sys
#
#     app = QApplication(sys.argv)
#     example = Example2()
#     example.show()
#     sys.exit(app.exec())
