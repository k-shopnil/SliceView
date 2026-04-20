from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
from core.shaders import VERTEX_SHADER, FRAGMENT_SHADER


class Renderer:
    def __init__(self):
        # Create and bind a VAO first (Required for macOS Core Profile)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        try:
            self.shader = compileProgram(
                compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
                compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
            )
        except Exception as e:
            print(f"Shader Error: {e}")
            raise

        self.vbo = glGenBuffers(1)
        self.vertex_count = 0

    def set_data(self, data):
        self.vertex_count = len(data) // 3
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

    # Update the method signature
    def draw(self, model, view, projection, plane_n, plane_d, color, light_dir):
        glUseProgram(self.shader)

        glUniformMatrix4fv(glGetUniformLocation(self.shader, "u_model"), 1, GL_FALSE, model)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "u_view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "u_projection"), 1, GL_FALSE, projection)

        glUniform3fv(glGetUniformLocation(self.shader, "u_plane_normal"), 1, plane_n)
        glUniform1f(glGetUniformLocation(self.shader, "u_plane_dist"), plane_d)
        glUniform3fv(glGetUniformLocation(self.shader, "u_color"), 1, color)

        # NEW: Send light direction to the GPU
        glUniform3fv(glGetUniformLocation(self.shader, "u_light_dir"), 1, light_dir)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)