
from numpy import array, float32
import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame
import ctypes


SKYBOX_VERTEX_SHADER = '''
#version 450 core

layout (location = 0) in vec3 inPosition;

uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

out vec3 texCoords;

void main()
{
    texCoords = inPosition;
    mat4 vm = mat4(mat3(viewMatrix));
    gl_Position = projectionMatrix * vm * vec4(inPosition, 1.0);
}
'''


SKYBOX_FRAGMENT_SHADER = '''
#version 450 core

uniform samplerCube skybox;

in vec3 texCoords;

out vec4 fragColor;

void main()
{
    fragColor = texture(skybox, texCoords);
}
'''


class EnvironmentMap:
    """
    Cubemap-based skybox for environment rendering.
    Uses a different implementation approach from the class version.
    """
    
    def __init__(self, cubemap_texture_paths):
        self._camera_reference = None
        self._shader_program = None
        self._cubemap_texture_id = None
        self._vbo_id = None
        self._vertex_data = None
        
        self._initialize_geometry()
        self._compile_shaders()
        self._load_cubemap_textures(cubemap_texture_paths)
    
    def _initialize_geometry(self):
        """Creates the cube geometry for skybox rendering."""
        # Cube vertices for skybox
        cube_vertices = [
            -1.0,  1.0, -1.0,  -1.0, -1.0, -1.0,   1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,   1.0,  1.0, -1.0,  -1.0,  1.0, -1.0,
            
            -1.0, -1.0,  1.0,  -1.0, -1.0, -1.0,  -1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,  -1.0,  1.0,  1.0,  -1.0, -1.0,  1.0,
            
             1.0, -1.0, -1.0,   1.0, -1.0,  1.0,   1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,   1.0,  1.0, -1.0,   1.0, -1.0, -1.0,
            
            -1.0, -1.0,  1.0,  -1.0,  1.0,  1.0,   1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,   1.0, -1.0,  1.0,  -1.0, -1.0,  1.0,
            
            -1.0,  1.0, -1.0,   1.0,  1.0, -1.0,   1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,  -1.0,  1.0,  1.0,  -1.0,  1.0, -1.0,
            
            -1.0, -1.0, -1.0,  -1.0, -1.0,  1.0,   1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,  -1.0, -1.0,  1.0,   1.0, -1.0,  1.0
        ]
        
        self._vertex_data = array(cube_vertices, dtype=float32)
        self._vbo_id = glGenBuffers(1)
    
    def _compile_shaders(self):
        """Compiles the skybox shader program."""
        self._shader_program = compileProgram(
            compileShader(SKYBOX_VERTEX_SHADER, GL_VERTEX_SHADER),
            compileShader(SKYBOX_FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        )
    
    def _load_cubemap_textures(self, texture_paths):
        """
        Loads 6 textures and creates a cubemap.
        
        Args:
            texture_paths: List of 6 image paths [right, left, top, bottom, front, back]
        """
        self._cubemap_texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self._cubemap_texture_id)
        
        cubemap_targets = [
            GL_TEXTURE_CUBE_MAP_POSITIVE_X,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z
        ]
        
        for i, texture_path in enumerate(texture_paths):
            texture_surface = pygame.image.load(texture_path)
            
            # Cubemap faces must be square - resize if needed
            width = texture_surface.get_width()
            height = texture_surface.get_height()
            if width != height:
                # Use the larger dimension to avoid quality loss
                size = max(width, height)
                texture_surface = pygame.transform.scale(texture_surface, (size, size))
            
            texture_data = pygame.image.tostring(texture_surface, "RGB", False)
            
            glTexImage2D(
                cubemap_targets[i],
                0,
                GL_RGB,
                texture_surface.get_width(),
                texture_surface.get_height(),
                0,
                GL_RGB,
                GL_UNSIGNED_BYTE,
                texture_data
            )
        
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    
    def attach_camera(self, camera):
        """Attaches a camera for proper skybox rendering."""
        self._camera_reference = camera
    
    def draw(self):
        """Renders the skybox."""
        if not self._shader_program:
            return
        
        glUseProgram(self._shader_program)
        
        # Set camera matrices
        if self._camera_reference:
            view_loc = glGetUniformLocation(self._shader_program, "viewMatrix")
            glUniformMatrix4fv(
                view_loc, 1, GL_FALSE,
                glm.value_ptr(self._camera_reference.view_matrix)
            )
            
            proj_loc = glGetUniformLocation(self._shader_program, "projectionMatrix")
            glUniformMatrix4fv(
                proj_loc, 1, GL_FALSE,
                glm.value_ptr(self._camera_reference.projection_matrix)
            )
        
        # Disable depth writing
        glDepthMask(GL_FALSE)
        
        # Bind cubemap
        glBindTexture(GL_TEXTURE_CUBE_MAP, self._cubemap_texture_id)
        
        # Setup vertex buffer
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_id)
        glBufferData(
            GL_ARRAY_BUFFER,
            self._vertex_data.nbytes,
            self._vertex_data,
            GL_STATIC_DRAW
        )
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0, 3, GL_FLOAT, GL_FALSE,
            4 * 3, ctypes.c_void_p(0)
        )
        
        # Draw skybox
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        glDisableVertexAttribArray(0)
        glDepthMask(GL_TRUE)
		
