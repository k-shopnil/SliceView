import numpy as np


def load_obj(file_path):
    """
    Manually parses a Wavefront .obj file into a format OpenGL can render.
    Returns a flattened NumPy array of vertex positions.
    """
    vertices = []
    indices = []
    final_data = []

    with open(file_path, 'r') as f:
        for line in f:

            if not line.strip() or line.startswith('#'):
                continue

            parts = line.split()
            prefix = parts[0]

            if prefix == 'v':
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])

            elif prefix == 'f':

                face_indices = [int(p.split('/')[0]) - 1 for p in parts[1:]]

                for i in range(1, len(face_indices) - 1):
                    indices.append(face_indices[0])
                    indices.append(face_indices[i])
                    indices.append(face_indices[i + 1])


    for idx in indices:
        final_data.extend(vertices[idx])

    return np.array(final_data, dtype='float32')