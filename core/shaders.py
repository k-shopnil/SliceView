# ==========================================
# core/shaders.py
# ==========================================

# Vertex Shader: Handles positions and passes world coordinates to the fragment shader
VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec3 in_position;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

out vec3 v_world_pos;

void main() {
    // Calculate world position for the clipping logic and lighting
    v_world_pos = (u_model * vec4(in_position, 1.0)).xyz;

    // Final position on screen
    gl_Position = u_projection * u_view * u_model * vec4(in_position, 1.0);
}
"""

# Fragment Shader: Handles slicing (discard), flat shading (lighting), and edge glow
FRAGMENT_SHADER = """
#version 330 core
in vec3 v_world_pos;

uniform vec3 u_plane_normal;
uniform float u_plane_dist;
uniform vec3 u_color;
uniform vec3 u_light_dir; // Dynamic Light Direction from UI

out vec4 f_color;

void main() {
    // 1. Slicing Logic (The Virtual Scalpel)
    float dist = dot(v_world_pos, u_plane_normal) + u_plane_dist;

    if (dist < 0.0) {
        discard; // Instantly discard pixels behind the cutting plane
    }

    // 2. Automatic Flat Shading (Calculates lighting on the fly)
    // Using screen-space derivatives to find the face normal dynamically
    vec3 xTangent = dFdx(v_world_pos);
    vec3 yTangent = dFdy(v_world_pos);
    vec3 faceNormal = normalize(cross(xTangent, yTangent));

    // Use the UI's dynamic light direction
    vec3 lightDir = normalize(u_light_dir); 

    // Calculate diffuse lighting (diff) with a minimum ambient light of 0.2
    float diff = max(dot(faceNormal, lightDir), 0.2); 

    // 3. Visual Polish
    if (dist < 0.05) {
        f_color = vec4(0.0, 1.0, 1.0, 1.0); // Cyan laser cut edge
    } else {
        f_color = vec4(u_color * diff, 1.0); // Lit mesh color
    }
}
"""