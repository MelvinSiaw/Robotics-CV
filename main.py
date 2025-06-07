#### README ####

## Keyboard Instructions:
# 'Q' = Switch Color Detection between 'Red' & 'Blue'
# 'Esc' = Kill Program
# 'W' = To increase to contours by 50px
# 'S' = To decrease to contours by 50px

#### end of README ####


#### Libraries ####

import cv2
import numpy as np

#### end of Libraries ####


#### Variables ####

# Global variables to store the current X and Y positions
current_position_x = None
current_position_y = None

#### End of Variables ####


#### Helper Functions ####

# Function to find the midpoint of the frame

# Function to define the color range for tracking
def define_color_range(color_name):
    # Define Colors
    if color_name == "Blue":
        return np.array([90, 50, 50]), np.array([130, 255, 255])
    elif color_name == "Red":
        return np.array([40, 50, 50]), np.array([80, 255, 255])
    else:
        raise ValueError(f"Unsupported color: {color_name}")

# Function to track a specific color in the frame
def track_color(frame, color_lower, color_upper, min_contour_area):
    # Convert the frame to the HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create a binary mask by thresholding based on the specified color range
    mask = cv2.inRange(hsv_frame, color_lower, color_upper)
    
    # Find contours in the binary mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours based on area
    large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]
    
    # Check if large contours are found
    if large_contours:
        # Find the largest contour
        largest_contour = max(large_contours, key=cv2.contourArea)
        
        # Calculate the moments of the largest contour
        moments = cv2.moments(largest_contour)
        
        # Check if the area (m00) of the contour is not zero
        if moments['m00'] != 0:
            # Calculate the centroid of the contour
            centroid_x = int(moments['m10'] / moments['m00'])
            centroid_y = int(moments['m01'] / moments['m00'])
            return centroid_x, centroid_y, large_contours  # Return the centroid coordinates
    return None, None, None  # Return None if no large contours are found

# Find midpoint
def find_midpoint(frame):
    height, width, _ = frame.shape
    midpoint = (width // 2, height // 2)
    return midpoint

# Function to determine the position of the color relative to the frame midpoint
def determine_position(coord_x, coord_y, midpoint_x, midpoint_y):
    global current_position_x, current_position_y
    
    if coord_x is not None and coord_y is not None:
        # Determine position in X direction
        current_position_x = coord_x - midpoint_x
        
        # Determine position in Y direction
        current_position_y = midpoint_y - coord_y
        
        # Position Location
        location_position = ''

        # Determine vertical position (UP, DOWN, MIDDLE)
        if current_position_y > midpoint_y / 3:
            location_position += "UPPER"
        elif current_position_y < -midpoint_y / 3:
            location_position += "DOWN"
        else:
            location_position += "MIDDLE"

        # Determine horizontal position (LEFT, RIGHT, MIDDLE)
        if current_position_x < -midpoint_x / 3:
            location_position += " LEFT"
        elif current_position_x > midpoint_x / 3:
            location_position += " RIGHT"
        else:
            if location_position != "MIDDLE":
                location_position += " MIDDLE"

        # Return the X and Y positions
        return location_position, current_position_x, current_position_y
    else:
        # Return default values when no contours are found
        return "NO CONTOURS", None, None


# Function to draw a 3x3 grid on the frame
def draw_grid(frame, midpoint):
    height, width, _ = frame.shape
    
    # Define the size of the grid cells
    cell_size_x = width // 3
    cell_size_y = height // 3
    
    # Draw vertical lines
    for i in range(1, 3):
        x = i * cell_size_x
        cv2.line(frame, (x, 0), (x, height), (255, 255, 255), 1)
    
    # Draw horizontal lines
    for i in range(1, 3):
        y = i * cell_size_y
        cv2.line(frame, (0, y), (width, y), (255, 255, 255), 1)
    
def process_frame(frame, color_name, color_lower, color_upper, min_contour_area):
    # Find the midpoint of the frame and draw a circle at that point
    midpoint = find_midpoint(frame)
    cv2.circle(frame, midpoint, 5, (0, 0, 255), -1)

    # Track the specified color in the frame
    color_coordX = 0
    color_coordY = 0
    large_contours = []
    color_coordX, color_coordY, large_contours = track_color(frame, color_lower, color_upper, min_contour_area)
    
    color_coords = (color_coordX, color_coordY)

    # Check if color coordinates are found
    if color_coords:
        # Draw the frame elements
        draw_frame_elements(frame, midpoint, color_coords, color_name, current_position_x, current_position_y, min_contour_area)

        # Draw the grid on the frame
        draw_grid(frame, midpoint)

    # Display the mask with filtered contours
    maskframe = cv2.drawContours(np.zeros_like(frame), large_contours, -1, (255, 255, 255), thickness=cv2.FILLED)
    cv2.imshow('Mask', maskframe) 

    # Display the original frame
    cv2.imshow('Video', frame)
    
def draw_frame_elements(frame, midpoint, color_coords, color_name, current_position_x, current_position_y, min_contour_area):
    # Draw a circle at the color centroid 
    print(color_coords)
    cv2.circle(frame, color_coords, 10, (0, 255, 0), -1)

    # Draw a line connecting the midpoint to the color centroid
    cv2.line(frame, midpoint, color_coords, (255, 0, 0), 2)
    
    #Determine the position of the color
    location_position, current_position_x, current_position_y = determine_position(
        color_coords[0], color_coords[1], midpoint[0], midpoint[1]
        )

    # Display the currently detected color in the top left of the screen
    if color_name == "Blue":
        color_text_color = (255, 0, 0)  # Red
    else:
        color_text_color = (0, 0, 255)  # Blue
    cv2.putText(
            frame,                              # Image on which the text will be drawn
            f"Detecting Color: {color_name}",   # Text string
            (10, 30),                           # Bottom-left corner of the text string in the image (x, y) coordinates
            cv2.FONT_HERSHEY_SIMPLEX,           # Font type (here, simple font)
            1,                                  # Font scale (size multiplier)
            color_text_color,                   # Text color (in BGR format; here, it's white)
            2                                   # Thickness of the text
            )                             

    # Display keyboard instructions in the top right corner
    cv2.putText(frame, "'Q' = Switch Color", (frame.shape[1] - 250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, "'W' = Increase Contours", (frame.shape[1] - 250, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, "'S' = Decrease Contours", (frame.shape[1] - 250, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, "'Esc' = Kill Program", (frame.shape[1] - 250, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Display position information on the video frame at the bottom
    text_y = frame.shape[0] - 10
    cv2.putText(frame, location_position, (10, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"X: {current_position_x}, Y: {current_position_y}", (10, text_y - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Display min_contour_area at the bottom right corner
    cv2.putText(frame, f"Min Contour Area: {min_contour_area}", (frame.shape[1] - 260, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#### End of Helper Functions ####


#### Main function ####

def main():
    cap = cv2.VideoCapture(0)
    
    # Default Color
    color_name = "Blue"
    color_lower, color_upper = define_color_range(color_name)
    
    # Set min contour area (Threshold) by pixel
    min_contour_area = 200

    # Enter loop to run the program until it is break
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame
        process_frame(frame, color_name, color_lower, color_upper, min_contour_area)

        # Check if 'q' is pressed to switch colors
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            color_name = "Red" if color_name == "Blue" else "Blue"
            color_lower, color_upper = define_color_range(color_name)

        # Break the loop if 'esc' is pressed
        elif key & 0xFF == 27:  # '27' is the ASCII code for 'esc'
            break

        # Check if 'w' key is pressed to increase min_contour_area
        elif key == ord('w'):
            min_contour_area += 50

        # Check if 's' key is pressed to decrease min_contour_area
        elif key == ord('s'):
            min_contour_area = max(0, min_contour_area - 50)

    cap.release()
    cv2.destroyAllWindows()

#### End of Main function ####

# Check if the script is run as the main program
if __name__ == "__main__":
    main()