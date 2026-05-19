import cv2
import mediapipe as mp
import pygame
import sys
import math
import random

# --- OS Logic: Memory Allocation ---
class MemorySim:
    def __init__(self):
        # Initial holes in memory [size, is_occupied, process_size]
        self.holes = [
            [100, False, 0],
            [500, False, 0],
            [200, False, 0],
            [300, False, 0],
            [600, False, 0]
        ]
        self.algo = "First Fit"
        self.zoom = 1.0
        self.rotation = 0
        # Standard process sizes for teaching purposes (in KB)
        self.process_sizes = [50, 100, 150, 200, 250]
        self.last_action = ""
        self.action_timer = 0

    def allocate(self, p_size):
        """Simulates allocation based on currently selected algorithm."""
        if self.algo == "First Fit":
            for hole in self.holes:
                if not hole[1] and hole[0] >= p_size:
                    hole[1] = True
                    hole[2] = p_size
                    self.last_action = f"✓ Allocated {p_size}KB (First Fit)"
                    self.action_timer = 60
                    return True
                    
        elif self.algo == "Best Fit":
            best_idx = -1
            for i, hole in enumerate(self.holes):
                if not hole[1] and hole[0] >= p_size:
                    if best_idx == -1 or hole[0] < self.holes[best_idx][0]:
                        best_idx = i
            if best_idx != -1:
                self.holes[best_idx][1] = True
                self.holes[best_idx][2] = p_size
                self.last_action = f"✓ Allocated {p_size}KB (Best Fit)"
                self.action_timer = 60
                return True
                
        elif self.algo == "Worst Fit":
            worst_idx = -1
            for i, hole in enumerate(self.holes):
                if not hole[1] and hole[0] >= p_size:
                    if worst_idx == -1 or hole[0] > self.holes[worst_idx][0]:
                        worst_idx = i
            if worst_idx != -1:
                self.holes[worst_idx][1] = True
                self.holes[worst_idx][2] = p_size
                self.last_action = f"✓ Allocated {p_size}KB (Worst Fit)"
                self.action_timer = 60
                return True
                
        self.last_action = f"✗ Failed to allocate {p_size}KB"
        self.action_timer = 60
        return False

    def deallocate_all(self):
        """Frees all allocated memory blocks."""
        count = sum(1 for hole in self.holes if hole[1])
        if count > 0:
            for hole in self.holes:
                hole[1] = False
                hole[2] = 0
            self.last_action = f"✓ Deallocated {count} block(s)"
            self.action_timer = 60
            return True
        return False

    def get_random_process_size(self):
        """Returns a random process size from standard sizes."""
        return random.choice(self.process_sizes)

# --- Setup MediaPipe for Gesture Tracking ---
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os

# Download hand landmarker model if not exists
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("Downloading hand landmarker model...")
    url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
    urllib.request.urlretrieve(url, model_path)
    print("Model downloaded successfully!")

# Initialize hand landmarker
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
detector = vision.HandLandmarker.create_from_options(options)
print("MediaPipe Hand Landmarker initialized successfully!")

# --- Setup Pygame for Simulation Visuals ---
pygame.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OS Memory Allocation Simulator - Gesture Control")
clock = pygame.time.Clock()
sim = MemorySim()

cap = cv2.VideoCapture(0)

def get_dist(p1, p2):
    """Calculate Euclidean distance between two landmarks."""
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

# Gesture cooldown to prevent multiple triggers
gesture_cooldown = 0
COOLDOWN_FRAMES = 30

print("=" * 60)
print("GESTURE CONTROLS:")
print("=" * 60)
print("👋 Open/Close Hand: Zoom (Expand/Collapse Memory View)")
print("🔄 Rotate Hand: Toggle Algorithm (First → Best → Worst Fit)")
print("👌 Pinch (Index + Thumb): Allocate Random Process")
print("✋ Pinch (Middle + Thumb): Deallocate All Memory")
print("❌ Press ESC or 'Q' to quit")
print("=" * 60)

running = True
while running and cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Failed to read from camera")
        break

    # Process Hand Landmarks
    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Convert to MediaPipe Image format
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    detection_result = detector.detect(mp_image)
    
    hand_landmarks_list = []
    
    # Extract landmarks and draw if hands detected
    if detection_result.hand_landmarks:
        for hand_landmarks in detection_result.hand_landmarks:
            hand_landmarks_list.append(hand_landmarks)
            
            # Draw hand landmarks on camera feed
            for idx, landmark in enumerate(hand_landmarks):
                h, w, c = image.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)
                if idx == 0:  # Wrist
                    cv2.circle(image, (cx, cy), 8, (255, 0, 0), -1)
                elif idx in [4, 8, 12, 16, 20]:  # Fingertips
                    cv2.circle(image, (cx, cy), 8, (0, 0, 255), -1)
            
            # Draw connections between landmarks
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
                (0, 5), (5, 6), (6, 7), (7, 8),  # Index
                (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
                (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
                (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
                (5, 9), (9, 13), (13, 17)  # Palm
            ]
            for connection in connections:
                start_idx, end_idx = connection
                start_landmark = hand_landmarks[start_idx]
                end_landmark = hand_landmarks[end_idx]
                h, w, c = image.shape
                start_pt = (int(start_landmark.x * w), int(start_landmark.y * h))
                end_pt = (int(end_landmark.x * w), int(end_landmark.y * h))
                cv2.line(image, start_pt, end_pt, (255, 255, 255), 2)
    
    # Decrease gesture cooldown
    if gesture_cooldown > 0:
        gesture_cooldown -= 1
    
    # Decrease action timer
    if sim.action_timer > 0:
        sim.action_timer -= 1
    
    # Process gestures if hand is detected
    if hand_landmarks_list:
        for landmarks in hand_landmarks_list:
            
            # 1. EXPAND/COLLAPSE (Based on distance between Thumb and Pinky)
            thumb_tip = landmarks[4]
            pinky_tip = landmarks[20]
            dist = get_dist(thumb_tip, pinky_tip)
            sim.zoom = max(0.5, min(2.0, dist * 5))
            
            # 2. ROTATE / ALGORITHM SWITCH (Based on hand tilt)
            wrist = landmarks[0]
            middle_mcp = landmarks[9]
            angle = math.degrees(math.atan2(middle_mcp.y - wrist.y, middle_mcp.x - wrist.x))
            
            if angle < -110:
                sim.algo = "Best Fit"
            elif angle > -70:
                sim.algo = "Worst Fit"
            else:
                sim.algo = "First Fit"

            # 3. PINCH TO ALLOCATE (Index + Thumb)
            index_tip = landmarks[8]
            index_thumb_dist = get_dist(thumb_tip, index_tip)
            
            if index_thumb_dist < 0.05 and gesture_cooldown == 0:
                process_size = sim.get_random_process_size()
                sim.allocate(process_size)
                gesture_cooldown = COOLDOWN_FRAMES

            # 4. PINCH TO DEALLOCATE ALL (Middle + Thumb)
            middle_tip = landmarks[12]
            middle_thumb_dist = get_dist(thumb_tip, middle_tip)
            
            if middle_thumb_dist < 0.05 and gesture_cooldown == 0:
                sim.deallocate_all()
                gesture_cooldown = COOLDOWN_FRAMES

    # --- Pygame Rendering ---
    screen.fill((25, 25, 40))
    
    # Title
    title_font = pygame.font.SysFont("Arial", 32, bold=True)
    title_text = title_font.render("Memory Allocation Simulator", True, (100, 200, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))
    
    # Algorithm and Zoom Info
    font = pygame.font.SysFont("Arial", 26, bold=True)
    info_text = font.render(
        f"ALGORITHM: {sim.algo}  |  ZOOM: {round(sim.zoom, 2)}x",
        True,
        (0, 255, 150)
    )
    screen.blit(info_text, (50, 80))
    
    # Action Feedback
    if sim.action_timer > 0:
        action_font = pygame.font.SysFont("Arial", 24)
        action_color = (100, 255, 100) if "✓" in sim.last_action else (255, 100, 100)
        action_text = action_font.render(sim.last_action, True, action_color)
        screen.blit(action_text, (50, 120))
    
    # Legend
    legend_font = pygame.font.SysFont("Arial", 20)
    legend_y = HEIGHT - 150
    legend_free = legend_font.render("█ Free Memory", True, (50, 200, 100))
    legend_alloc = legend_font.render("█ Allocated Memory", True, (200, 50, 50))
    screen.blit(legend_free, (50, legend_y))
    screen.blit(legend_alloc, (50, legend_y + 30))
    
    # Gesture Guide
    guide_font = pygame.font.SysFont("Arial", 18)
    guide_y = legend_y + 70
    guides = [
        "👌 Index+Thumb: Allocate  |  ✋ Middle+Thumb: Free All"
    ]
    for i, guide in enumerate(guides):
        guide_text = guide_font.render(guide, True, (180, 180, 200))
        screen.blit(guide_text, (50, guide_y + i * 25))
    
    # Render Memory Blocks
    x_pos = 100
    block_y = 300
    block_font = pygame.font.SysFont("Arial", 22)
    
    for size, occupied, proc_size in sim.holes:
        block_w = int(size * sim.zoom)
        color = (200, 50, 50) if occupied else (50, 200, 100)
        
        # Draw main block
        rect = pygame.Rect(x_pos, block_y, block_w, 120)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=8)
        
        # Draw labels
        size_lbl = block_font.render(f"{size}KB", True, (255, 255, 255))
        screen.blit(size_lbl, (x_pos + 10, block_y + 10))
        
        if occupied:
            proc_lbl = block_font.render(f"Process: {proc_size}KB", True, (255, 255, 200))
            screen.blit(proc_lbl, (x_pos + 10, block_y + 45))
            waste_lbl = block_font.render(f"Waste: {size - proc_size}KB", True, (255, 200, 200))
            screen.blit(waste_lbl, (x_pos + 10, block_y + 80))
        else:
            status_lbl = block_font.render("FREE", True, (200, 255, 200))
            screen.blit(status_lbl, (x_pos + 10, block_y + 50))
        
        x_pos += block_w + 30

    pygame.display.flip()
    
    # Show Camera Feed
    cv2.imshow('Hand Gesture Controls (Press ESC to exit)', image)
    key = cv2.waitKey(5) & 0xFF
    if key == 27 or key == ord('q'):  # ESC or Q
        running = False
    
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    clock.tick(30)  # 30 FPS

# Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
