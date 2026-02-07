import numpy as np
from sklearn.cluster import KMeans

def get_player_color(frame, box):
    x1, y1, x2, y2 = map(int, box)

    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return None

    # focus on upper 40% (jersey area)
    h = crop.shape[0]
    crop = crop[0:int(h * 0.4), :]

    pixels = crop.reshape(-1, 3)

    # remove green grass pixels
    pixels = pixels[np.linalg.norm(pixels - [0, 255, 0], axis=1) > 60]
    if len(pixels) < 10:
        return None

    kmeans = KMeans(n_clusters=1, n_init=5)
    kmeans.fit(pixels)

    return kmeans.cluster_centers_[0]

def cluster_players(colors):
    if len(colors) < 2:
        return [0] * len(colors)

    kmeans = KMeans(n_clusters=2, n_init=10)
    labels = kmeans.fit_predict(colors)
    return labels

