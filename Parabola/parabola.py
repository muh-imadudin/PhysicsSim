import sys, time
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QFrame, QPushButton
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QIcon

GRAVITY = 0.2  # px/frame², (assume g=10 m/s²)

class SimulationCanvas(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black;")
        self.ball_radius = 15

        # initial parameters
        self.reset_params()

        self.start_time = time.time()

    def reset_params(self):
        self.ball_x = 50
        self.ball_y = 400
        self.vx = 3.0        # horizontal speed
        self.vy = -8.0       # vertical speed (negative = upward)
        self.bouncy = 0.7    # bounce factor

    def update_physics(self):
        # update position
        self.ball_x += self.vx
        self.vy += GRAVITY
        self.ball_y += self.vy

        # bounce on bottom
        if self.ball_y + self.ball_radius > self.height():
            self.ball_y = self.height() - self.ball_radius

            if (abs(self.vy) < 0.5 and abs(self.vx) < 0.5) or self.bouncy == 0:
                self.vy = 0
                self.parent().config.update_velocity()
                self.parent().config.stop_timer()
            else:
                self.vy *= -self.bouncy

        # stop if leaves right side
        if self.ball_x + self.ball_radius > self.width():
            self.ball_x = self.width() - self.ball_radius 
            
            if (abs(self.vx) < 0.5 and abs(self.vy) < 0.5) or self.bouncy == 0:
                self.vx = 0
                self.parent().config.update_velocity()
                self.parent().config.stop_timer()
            else:
                self.vx *= -self.bouncy
                
        # stop if leaves left side
        elif self.ball_x - self.ball_radius < 0:
            self.ball_x = self.ball_radius 
            
            if (abs(self.vx) < 0.5 and abs(self.vy) < 0.5) or self.bouncy == 0:
                self.vx = 0
                self.parent().config.update_velocity()
                self.parent().config.stop_timer()
            else:
                self.vx *= -self.bouncy

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(
            int(self.ball_x - self.ball_radius),
            int(self.ball_y - self.ball_radius),
            self.ball_radius * 2,
            self.ball_radius * 2
        )

    def set_bouncy(self, bouncy):
        self.bouncy = bouncy

    def go_simul(self):
        self.reset_params()
        self.start_time = time.time()
        self.parent().config.timer_label.setText("0.000 s")
        self.parent().timer.start(16)  # ~60 FPS


class MassConfigurator(QWidget):
    def __init__(self, canvas: SimulationCanvas):
        super().__init__()
        self.canvas = canvas

        # --------- Bouncyness ----------
        self.label_bouncy = QLabel(f"Bouncyness: {self.canvas.bouncy}")
        self.label_bouncy.setStyleSheet("color: black; font-size: 16px;")

        self.slider_bouncy = QSlider(Qt.Horizontal)
        self.slider_bouncy.setRange(0, 99)
        self.slider_bouncy.setValue(int(self.canvas.bouncy * 100))
        self.slider_bouncy.valueChanged.connect(self.change_bouncy)

        # --------------------- Go Button ------------------
        self.go_button = QPushButton("Go..!!")
        self.go_button.setStyleSheet("""
            QPushButton {
                color: black;
                font-size: 16px;
                text-align: center;
                background-color: lightgreen;
            }
            QPushButton:hover {
                color: white;
                background-color: green;
            }
        """)
        self.go_button.clicked.connect(self.canvas.go_simul)

        # ------------- Real-Time Stopwatch -------------
        time_sentence = QLabel("Time =")
        time_sentence.setStyleSheet("font-size: 18px; color: black;")

        self.timer_label = QLabel("0.000 s")
        self.timer_label.setStyleSheet("font-size: 18px; color: black;")
        self.timer_label.setAlignment(Qt.AlignLeft)

        timer_layout = QHBoxLayout()
        timer_layout.addWidget(time_sentence)
        timer_layout.addWidget(self.timer_label)

        # --------------------- Velocity ----------------
        velo_sentence = QLabel("Velocity =")
        velo_sentence.setStyleSheet("font-size: 18px; color: black;")

        self.velo_label = QLabel("0.000 m/s")
        self.velo_label.setStyleSheet("font-size: 18px; color: black;")
        self.velo_label.setAlignment(Qt.AlignLeft)

        velo_layout = QHBoxLayout()
        velo_layout.addWidget(velo_sentence)
        velo_layout.addWidget(self.velo_label)

        velo_formula = QLabel("vₜ = v₀ + at")
        velo_formula.setStyleSheet("font-size: 24px; background-color: white; border: 1px solid black;")
        velo_formula.setAlignment(Qt.AlignLeft)
        velo_formula.setAutoFillBackground(True)

        # --------------------- X Distance ----------------
        xdist_sentence = QLabel("X Distance =")
        xdist_sentence.setStyleSheet("font-size: 18px; color: black;")

        self.xdist_label = QLabel("0.000 m")
        self.xdist_label.setStyleSheet("font-size: 18px; color: black;")
        self.xdist_label.setAlignment(Qt.AlignLeft)

        xdist_layout = QHBoxLayout()
        xdist_layout.addWidget(xdist_sentence)
        xdist_layout.addWidget(self.xdist_label)

        xdist_formula = QLabel("x = v₀ cos α t")
        xdist_formula.setStyleSheet("font-size: 24px; background-color: white; border: 1px solid black;")
        xdist_formula.setAlignment(Qt.AlignLeft)
        xdist_formula.setAutoFillBackground(True)

        # --------------------- Y Distance ----------------
        ydist_sentence = QLabel("Y Distance =")
        ydist_sentence.setStyleSheet("font-size: 18px; color: black;")

        self.ydist_label = QLabel("0.000 m")
        self.ydist_label.setStyleSheet("font-size: 18px; color: black;")
        self.ydist_label.setAlignment(Qt.AlignLeft)

        ydist_layout = QHBoxLayout()
        ydist_layout.addWidget(ydist_sentence)
        ydist_layout.addWidget(self.ydist_label)

        ydist_formula = QLabel("y = v₀ sin α - ½ g t")
        ydist_formula.setStyleSheet("font-size: 24px; background-color: white; border: 1px solid black;")
        ydist_formula.setAlignment(Qt.AlignLeft)
        ydist_formula.setAutoFillBackground(True)

        # ----------------------------------------------------
        layout = QVBoxLayout()
        layout.addWidget(self.label_bouncy)
        layout.addWidget(self.slider_bouncy)
        layout.addWidget(self.go_button)
        layout.addLayout(timer_layout)
        layout.addLayout(velo_layout)
        layout.addLayout(xdist_layout)
        layout.addLayout(ydist_layout)
        layout.addWidget(velo_formula)
        layout.addWidget(xdist_formula)
        layout.addWidget(ydist_formula)
        layout.addStretch()
        self.setLayout(layout)

    def change_bouncy(self, value):
        self.label_bouncy.setText(f"Bouncyness: {value / 100}")
        self.canvas.set_bouncy(value / 100)

    def update_timer(self):
        self.elapsed = time.time() - self.canvas.start_time
        self.timer_label.setText(f"{self.elapsed:.3f} s")

    def update_velocity(self):
        v = (self.canvas.vx**2 + self.canvas.vy**2) ** 0.5
        self.velo_label.setText(f"{v:.3f} m/s")

    def update_distance(self):
        self.xdist_label.setText(f"{self.canvas.ball_x:.3f} m")
        self.ydist_label.setText(f"{self.canvas.ball_y:.3f} m")

    def stop_timer(self):
        self.parent().timer.stop()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projectile Simulation")
        self.setGeometry(300, 200, 800, 500) 
        self.setWindowIcon(QIcon("icon.ico"))

        # Left: Simulation
        self.canvas = SimulationCanvas()

        # Right: Configurator
        self.config = MassConfigurator(self.canvas)

        layout = QHBoxLayout()
        layout.addWidget(self.canvas, 3)
        layout.addWidget(self.config, 1)
        self.setLayout(layout)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.canvas.update_physics)
        self.timer.timeout.connect(self.config.update_timer)
        self.timer.timeout.connect(self.config.update_velocity)
        self.timer.timeout.connect(self.config.update_distance)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
