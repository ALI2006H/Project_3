# 🎮 PosturePet: Koky's Spine Saver

An interactive, real-time **posture-tracking game** that transforms your spinal health into a virtual pet companion. Keep your posture sharp to level up your pet, or slouch and watch their health decline!



## 📝 About the Project

This project leverages computer vision to gamify ergonomic wellness. By tracking your upper body alignment, it ensures you stay upright while working or gaming, turning healthy habits into a game survival mechanic.

* **Virtual Pet Mechanics**: Monitor your pet Koky, whose health and XP are directly tied to your posture.

* **Real-time AI Tracking**: Utilizes MediaPipe's lightweight pose landmark model for ultra-fast tracking.

* **Visual Feedback**: Draws dynamic bounding boxes around your shoulders (Green for good posture, Red for slouching).

* **Gamified Consequences**: Lose 5 HP per second when slouching, or heal and gain XP when sitting straight.


> [!CAUTION]
> **Prerequisite:** Download the pose_landmarker_lite.task model from Google MediaPipe and place it in the root folder before running.


## 🚀 How It Works

1. **Calibration Phase**

When the script starts, you have 3 seconds to sit up perfectly straight and face the webcam.

* The system calculates a baseline distance between your nose and the midpoint of your shoulders.

* This baseline sets your personal "perfect posture" metric.




2. **Live Tracking & Pet Care**

Once calibrated, the game enters a continuous loop where it evaluates your seating position:

* **Good Posture**: If you stay within 15% of your baseline, your pet stays happy, recovers health (+2 HP/s), and gains experience (+1 XP/s).

* **Slouching detected**: If your posture drops past the 15% threshold, boxes on your shoulders turn red, Koky enters "In Pain" status, and loses health (-5 HP/s).




3. **Game Over**

If you don't correct your posture and Koky's health hits 0, the game ends with a friendly reminder: "Please, take care of your back. Health is more precious than money." You can also press 'q' at any time to quit safely.