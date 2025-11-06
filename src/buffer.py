import glm
from OpenGL.GL import *
from numpy import array, float32
import ctypes


class VertexBufferObject:
    """
    Encapsulates vertex buffer management for OpenGL rendering.
    Handles VBO creation, binding, and attribute configuration.
    """
    
    def __init__(self, vertex_data):
        self._raw_data = vertex_data
        self._buffer_data = array(self._raw_data, dtype=float32)
        self._vbo_id = glGenBuffers(1)
        self._is_bound = False
    
    def bind_and_configure(self, attribute_location, component_count):
        """
        Binds the VBO and configures vertex attribute pointer.
        
        Args:
            attribute_location: The shader attribute location index
            component_count: Number of components per vertex attribute
        """
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_id)
        self._is_bound = True
        
        # Upload buffer data to GPU
        glBufferData(
            GL_ARRAY_BUFFER,
            self._buffer_data.nbytes,
            self._buffer_data,
            GL_STATIC_DRAW
        )
        
        # Configure vertex attribute pointer
        glVertexAttribPointer(
            attribute_location,
            component_count,
            GL_FLOAT,
            GL_FALSE,
            0,
            ctypes.c_void_p(0)
        )
        
        glEnableVertexAttribArray(attribute_location)
    
    def unbind(self):
        """Unbinds the current VBO."""
        if self._is_bound:
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            self._is_bound = False
    
    def cleanup(self):
        """Releases GPU resources."""
        if self._vbo_id:
            glDeleteBuffers(1, [self._vbo_id])
            self._vbo_id = None
		