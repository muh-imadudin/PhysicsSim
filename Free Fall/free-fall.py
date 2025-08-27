import sys, time
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QFrame, QPushButton
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QIcon

dt = 0.016 # 0.016=60 FPS, dalam detik
GRAVITY = 9.81 # px
ball_start_y = 150
velocity_start = 0

class SimulationCanvas(QFrame):
    def __init__(self): # awal berjalan
        super().__init__()
        self.setStyleSheet("background-color: black;")
        self.ball_y = ball_start_y
        self.ball_radius = 20
        self.velocity = 0
        self.mass = 10
        self.bouncy = 0.7 #bounce factor
        self.start_time = time.time()

    def update_physics(self):
        self.velocity_prev = self.velocity
        self.velocity += GRAVITY * dt  # acceleration
        self.ball_y += self.velocity * dt

        # Bounce on bottom
        if self.ball_y + self.ball_radius > self.height():
            self.ball_y = self.height() - self.ball_radius

            if abs(self.velocity) < 0.5 or self.bouncy == 0:
                # print(self.velocity)
                self.velocity = 0
                self.parent().config.update_velocity() 
                self.parent().config.stop_timer() 
                
            else:
                self.velocity *= -self.bouncy  # lose energy and bouncing
            
        self.update() #repaint widget

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) #for smooth edges
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(
            self.width() // 2 - self.ball_radius,
            int(self.ball_y - self.ball_radius),
            self.ball_radius * 2,
            self.ball_radius * 2
        )

    def set_mass(self, mass):
        self.mass = mass

    def set_bouncy(self, bouncy):
        self.bouncy = bouncy
    
    def go_simul(self):
        self.start_time = time.time()
        self.velocity = velocity_start
        self.ball_y = ball_start_y

        self.parent().config.distance = 0
    
        self.parent().config.timer_label.setText("0.000 s")

        self.parent().timer.start(dt*1000)  # ~60 FPS

class MassConfigurator(QWidget):
    def __init__(self, canvas: SimulationCanvas):
        super().__init__()
        self.canvas = canvas

        #--------- Mass ---------------
        self.label_mass = QLabel(f"Mass: {self.canvas.mass} kg")
        self.label_mass.setStyleSheet("color: black; font-size: 16px;")

        self.slider_mass = QSlider(Qt.Horizontal)
        self.slider_mass.setRange(1, 50)
        self.slider_mass.setValue(self.canvas.mass) #default mass
        self.slider_mass.valueChanged.connect(self.change_mass)

        #--------- Bouncyness -----------
        self.label_bouncy = QLabel(f"Bouncyness: {self.canvas.bouncy}")
        self.label_bouncy.setStyleSheet("color: black; font-size: 16px;")

        self.slider_bouncy = QSlider(Qt.Horizontal)
        self.slider_bouncy.setRange(0, 99)
        self.slider_bouncy.setValue(self.canvas.bouncy * 100) #times 100 because slider only works with integers
        self.slider_bouncy.valueChanged.connect(self.change_bouncy)

        #--------------------- Reset ------------------
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
                background-color: green; /* Optional background change */
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

        # --------------------- Distance ----------------
        dist_sentence = QLabel("Distance =")
        dist_sentence.setStyleSheet("font-size: 18px; color: black;")
        
        self.dist_label = QLabel("0.000 m")
        self.dist_label.setStyleSheet("font-size: 18px; color: black;")
        self.dist_label.setAlignment(Qt.AlignLeft)

        dist_layout = QHBoxLayout()
        dist_layout.addWidget(dist_sentence)
        dist_layout.addWidget(self.dist_label)

        dist_formula = QLabel("s = v₀t + ½at²")
        dist_formula.setStyleSheet("font-size: 24px; background-color: white; border: 1px solid black;")
        dist_formula.setAlignment(Qt.AlignLeft)
        dist_formula.setAutoFillBackground(True)

        #----------------------------------------------------
        layout = QVBoxLayout() 
        layout.addWidget(self.label_mass)
        layout.addWidget(self.slider_mass)
        layout.addWidget(self.label_bouncy)
        layout.addWidget(self.slider_bouncy)
        layout.addWidget(self.go_button)
        layout.addLayout(timer_layout)
        layout.addLayout(velo_layout)
        layout.addLayout(dist_layout)
        layout.addWidget(velo_formula)
        layout.addWidget(dist_formula)
        layout.addStretch()
        self.setLayout(layout)

    def change_mass(self, value):
        self.label_mass.setText(f"Mass: {value} kg")
        self.canvas.set_mass(value)

    def change_bouncy(self, value):
        self.label_bouncy.setText(f"Bouncyness: {value / 100}") #/ 100 to convert back to actual value
        self.canvas.set_bouncy(value / 100)
    
    def update_timer(self):
        self.elapsed = time.time() - self.canvas.start_time
        self.timer_label.setText(f"{self.elapsed:.3f} s")

    def update_velocity(self):
        # self.velo_label.setText(f"{GRAVITY * self.elapsed:.3f} m/s")
        self.velo_label.setText(f"{self.parent().canvas.velocity:.3f} m/s")

    distance = 0
    def update_distance(self):
        self.distance += (abs(self.parent().canvas.velocity) + abs(self.parent().canvas.velocity_prev)) / 2 * dt
        # self.dist_label.setText(f"{1/2 * GRAVITY * self.elapsed**2:.3f} m")
        self.dist_label.setText(f"{self.distance:.3f} m")
        
    def stop_timer(self):
        self.parent().timer.stop()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Free Fall Simulation")
        self.setGeometry(300, 200, 800, 500)
        self.setWindowIcon(QIcon("icon.ico")) 

        # Left: Simulation
        self.canvas = SimulationCanvas()

        # Right: Mass configurator
        self.config = MassConfigurator(self.canvas)

        layout = QHBoxLayout()
        layout.addWidget(self.canvas, 3)  # Larger left panel
        layout.addWidget(self.config, 1)  # Smaller right panel
        self.setLayout(layout)

        # Timer for animation
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
