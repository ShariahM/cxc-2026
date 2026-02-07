import numpy as np
import cv2
from sklearn.cluster import KMeans

def get_player_color(frame, box):
    """
    Extract dominant jersey color with optimized noise removal.
    
    Returns color in BGR format (compatible with detection.py).
    """
    x1, y1, x2, y2 = map(int, box)
    
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return None
    
    # Focus on upper 50% to 80% (jersey area only)
    h = crop.shape[0]
    w = crop.shape[1]
    crop = crop[int(h*0.25):int(h*0.6), int(w*0.3):int(w*0.7)]
    
    # Convert to HSV for better color analysis
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    h_img, s_img, v_img = cv2.split(hsv)
    
    # Multi-stage filtering
    saturation_mask = s_img > 45  # Jerseys are saturated
    brightness_mask = (v_img > 40) & (v_img < 230)  # Remove shadows and highlights
    grass_mask = (h_img >= 40) & (h_img <= 100) & (s_img < 50)  # Remove grass
    skin_mask = (
        ((h_img <= 25) | (h_img >= 155)) & 
        (s_img < 70) & 
        (v_img > 60) & 
        (v_img < 200)
    )  # Remove skin tones
    
    combined_mask = saturation_mask & brightness_mask & ~grass_mask & ~skin_mask
    filtered_pixels = hsv[combined_mask]
    
    if len(filtered_pixels) < 15:
        return None
    
    # Morphological cleaning
    mask_2d = combined_mask.astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask_2d = cv2.morphologyEx(mask_2d, cv2.MORPH_OPEN, kernel, iterations=1)
    mask_2d = cv2.morphologyEx(mask_2d, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    cleaned_pixels = hsv[mask_2d.astype(bool)]
    if len(cleaned_pixels) < 10:
        cleaned_pixels = filtered_pixels
    
    # Find dominant hue using histogram
    hues = cleaned_pixels[:, 0]
    hue_bins = np.histogram(hues, bins=36, range=(0, 180))[0]
    dominant_hue_bin = np.argmax(hue_bins)
    dominant_hue = dominant_hue_bin * 5
    
    # Get all pixels close to dominant hue
    hue_tolerance = 15
    hue_mask = np.abs(cleaned_pixels[:, 0].astype(int) - dominant_hue) <= hue_tolerance
    hue_group = cleaned_pixels[hue_mask]
    
    if len(hue_group) < 5:
        dominant_color_hsv = np.mean(cleaned_pixels, axis=0)
    else:
        dominant_color_hsv = np.mean(hue_group, axis=0)
    
    # Convert back to BGR for compatibility with detection.py
    dominant_color_hsv = np.uint8([[dominant_color_hsv]])
    dominant_color_bgr = cv2.cvtColor(dominant_color_hsv, cv2.COLOR_HSV2BGR)[0][0]
    
    return dominant_color_bgr

def cluster_players(colors, prev_team_centers=None):
    """
    Cluster player colors into 2 teams with frame-to-frame consistency.
    
    Args:
        colors: Array of player colors
        prev_team_centers: Optional team centers from previous frame for consistency
    
    Returns:
        tuple: (team_labels, team_centers) for tracking across frames
    """
    if len(colors) < 2:
        return [0] * len(colors), None
    
    colors = np.array(colors)
    
    # Filter outliers using Euclidean distance from median
    median_color = np.median(colors, axis=0)
    distances = np.linalg.norm(colors - median_color, axis=1)
    
    # Keep colors within 2 standard deviations of median
    std_dist = np.std(distances)
    valid_mask = distances <= (np.median(distances) + 2 * std_dist)
    
    valid_colors = colors[valid_mask]
    valid_indices = np.where(valid_mask)[0]
    
    # If we filtered out most colors, use all colors
    if len(valid_colors) < max(2, len(colors) // 2):
        valid_colors = colors
        valid_indices = np.arange(len(colors))
    
    # Cluster valid colors
    kmeans = KMeans(n_clusters=2, n_init=20, max_iter=300, random_state=42)
    valid_labels = kmeans.fit_predict(valid_colors)
    
    # Check if we need to flip labels for consistency with previous frame
    if prev_team_centers is not None:
        # Calculate distances from current cluster centers to previous team centers
        dist_0_to_prev_0 = np.linalg.norm(kmeans.cluster_centers_[0] - prev_team_centers[0])
        dist_0_to_prev_1 = np.linalg.norm(kmeans.cluster_centers_[0] - prev_team_centers[1])
        
        # If cluster 0 is closer to previous team 1, flip the labels
        if dist_0_to_prev_1 < dist_0_to_prev_0:
            valid_labels = 1 - valid_labels
    
    # Map back to original indices
    labels = np.zeros(len(colors), dtype=int)
    labels[valid_indices] = valid_labels
    
    # Assign outliers to nearest cluster center
    if len(valid_indices) < len(colors):
        outlier_indices = np.where(~valid_mask)[0]
        for idx in outlier_indices:
            distances_to_centers = [
                np.linalg.norm(colors[idx] - kmeans.cluster_centers_[0]),
                np.linalg.norm(colors[idx] - kmeans.cluster_centers_[1])
            ]
            labels[idx] = np.argmin(distances_to_centers)
    
    return labels.tolist(), kmeans.cluster_centers_


def assign_team_colors(frame, detections, track_colors=None):
    """
    Extract colors for all players in frame and assign teams.
    
    Args:
        frame: Image frame (numpy array)
        detections: List of dicts with keys: x1, y1, x2, y2, track_id
        track_colors: Optional dict to cache colors by track_id
    
    Returns:
        Dictionary mapping track_id to team (0 or 1)
    """
    colors = []
    track_ids = []
    
    # Extract color for each detection
    for det in detections:
        box = [det["x1"], det["y1"], det["x2"], det["y2"]]
        color = get_player_color(frame, box)
        
        if color is not None:
            colors.append(color)
            track_ids.append(int(det["track_id"]))
    
    if len(colors) < 2:
        # Not enough players to cluster
        return {tid: 0 for tid in track_ids}
    
    # Cluster colors into 2 teams
    team_labels = cluster_players(np.array(colors))
    
    # Create mapping of track_id to team
    team_assignment = {
        track_id: int(team_label)
        for track_id, team_label in zip(track_ids, team_labels)
    }
    
    return team_assignment


def assign_teams_frame_batch(frame, detections_list):
    """
    Process multiple detections and return team assignments with color info.
    
    Returns:
        {
            'team_map': {track_id: team},
            'colors': {track_id: [b, g, r]},
            'team_colors': {0: [b, g, r], 1: [b, g, r]}  # dominant color per team
        }
    """
    colors = []
    track_ids = []
    color_dict = {}
    
    # Extract colors
    for det in detections_list:
        box = [det["x1"], det["y1"], det["x2"], det["y2"]]
        color = get_player_color(frame, box)
        
        if color is not None:
            colors.append(color)
            track_ids.append(int(det["track_id"]))
            color_dict[int(det["track_id"])] = color
    
    if len(colors) < 2:
        return {
            'team_map': {tid: 0 for tid in track_ids},
            'colors': color_dict,
            'team_colors': {0: None, 1: None}
        }
    
    # Cluster into teams
    colors_array = np.array(colors)
    team_labels = cluster_players(colors_array)
    
    # Create team mapping
    team_map = {
        track_id: int(team_label)
        for track_id, team_label in zip(track_ids, team_labels)
    }
    
    # Calculate dominant color per team
    team_colors = {0: None, 1: None}
    for team in [0, 1]:
        team_color_indices = [i for i, label in enumerate(team_labels) if label == team]
        if team_color_indices:
            team_colors[team] = np.mean(colors_array[team_color_indices], axis=0)
    
    return {
        'team_map': team_map,
        'colors': color_dict,
        'team_colors': team_colors
    }

