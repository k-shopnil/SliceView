import numpy as np
import math


def identity():
    return np.eye(4, dtype='float32')


def translate(x, y, z):
    m = identity()
    m[3, 0:3] = [x, y, z]  # The bottom row handles translation
    return m


def scale(s):
    m = identity()
    m[0, 0] = m[1, 1] = m[2, 2] = s
    return m


def rotate_y(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    m = identity()
    m[0, 0], m[0, 2] = c, -s
    m[2, 0], m[2, 2] = s, c
    return m

def rotate_x(angle):
    """Rotation around the X-axis (Pitch)"""
    c = math.cos(angle)
    s = math.sin(angle)
    m = identity()
    m[1, 1], m[1, 2] = c, -s
    m[2, 1], m[2, 2] = s, c
    return m

def rotate_z(angle):
    """Rotation around the Z-axis (Roll)"""
    c = math.cos(angle)
    s = math.sin(angle)
    m = identity()
    m[0, 0], m[0, 1] = c, -s
    m[1, 0], m[1, 1] = s, c
    return m


def perspective(fovy, aspect, near, far):
    """
    Manually creates a Perspective Projection Matrix.
    This mimics how a camera lens works, making distant objects smaller.
    """
    f = 1.0 / math.tan(fovy / 2.0)
    m = np.zeros((4, 4), dtype='float32')
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = -1.0
    m[3, 2] = (2.0 * far * near) / (near - far)
    return m


def look_at(eye, target, up):
    """
    Creates a View Matrix. It defines where the camera is (eye)
    and what it's looking at (target).
    """
    # Force float32 to avoid "UFuncOutputCastingError"
    eye = np.array(eye, dtype='float32')
    target = np.array(target, dtype='float32')
    up = np.array(up, dtype='float32')

    z_axis = (eye - target)
    # This division now works because z_axis is a float array
    z_axis /= np.linalg.norm(z_axis)

    x_axis = np.cross(up, z_axis)
    x_axis /= np.linalg.norm(x_axis)

    y_axis = np.cross(z_axis, x_axis)

    m = identity()
    m[0, 0:3] = x_axis
    m[1, 0:3] = y_axis
    m[2, 0:3] = z_axis
    m[3, 0:3] = [-np.dot(x_axis, eye), -np.dot(y_axis, eye), -np.dot(z_axis, eye)]
    return m