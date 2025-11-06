import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from src.camera import PerspectiveCamera
from src.skybox import EnvironmentMap


class OpenGLRenderer:
    """
    Main rendering engine for 3D scene visualization.
    Manages framebuffers, shaders, lighting, and post-processing effects.
    """
    
    def __init__(self, display_surface):
        self._surface = display_surface
        _, _, self._viewport_width, self._viewport_height = display_surface.get_rect()
        
        # Initialize OpenGL state
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, self._viewport_width, self._viewport_height)
        
        # Camera setup
        self.camera = PerspectiveCamera(self._viewport_width, self._viewport_height)
        
        # Scene management
        self.scene_objects = []
        self.environment_map = None
        
        # Rendering mode
        self._wireframe_mode = True
        self.toggle_render_mode()
        
        # Shader programs
        self._main_shader_program = None
        self._postprocess_shader_program = None
        
        # Lighting
        self.light_position = glm.vec3(0, 0, 0)
        self.ambient_intensity = 0.1
        
        # Animation parameters
        self.shader_param_value = 0.0
        self.elapsed_time = 0.0
        
        # Framebuffer setup
        self._setup_framebuffers()
    
    def set_environment_map(self, texture_paths):
        """
        Creates a skybox/environment map from texture files.
        
        Args:
            texture_paths: List of 6 texture paths for cubemap faces
        """
        self.environment_map = EnvironmentMap(texture_paths)
        self.environment_map.attach_camera(self.camera)
    
    def _setup_framebuffers(self):
        """
        Initializes framebuffer objects for post-processing.
        Creates color and depth attachments.
        """
        # Create framebuffer
        self._fbo_id = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fbo_id)
        
        # Color attachment
        self._color_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._color_texture)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, 
            self._viewport_width, self._viewport_height, 
            0, GL_RGBA, GL_UNSIGNED_BYTE, None
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(
            GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
            GL_TEXTURE_2D, self._color_texture, 0
        )
        
        # Depth attachment
        self._depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._depth_texture)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24,
            self._viewport_width, self._viewport_height,
            0, GL_DEPTH_COMPONENT, GL_FLOAT, None
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(
            GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
            GL_TEXTURE_2D, self._depth_texture, 0
        )
        
        # Unbind framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    def toggle_render_mode(self):
        """Toggles between wireframe and filled polygon rendering."""
        self._wireframe_mode = not self._wireframe_mode
        
        if self._wireframe_mode:
            glDisable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glEnable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT, GL_FILL)
    
    def compile_shaders(self, vertex_shader_src, fragment_shader_src):
        """
        Compiles and links vertex and fragment shaders.
        
        Args:
            vertex_shader_src: GLSL vertex shader source code
            fragment_shader_src: GLSL fragment shader source code
        """
        if vertex_shader_src and fragment_shader_src:
            self._main_shader_program = compileProgram(
                compileShader(vertex_shader_src, GL_VERTEX_SHADER),
                compileShader(fragment_shader_src, GL_FRAGMENT_SHADER)
            )
        else:
            self._main_shader_program = None
    
    def compile_postprocess_shaders(self, vertex_shader_src, fragment_shader_src):
        """
        Compiles shaders for post-processing effects.
        
        Args:
            vertex_shader_src: GLSL vertex shader source code
            fragment_shader_src: GLSL fragment shader source code
        """
        if vertex_shader_src and fragment_shader_src:
            self._postprocess_shader_program = compileProgram(
                compileShader(vertex_shader_src, GL_VERTEX_SHADER),
                compileShader(fragment_shader_src, GL_FRAGMENT_SHADER)
            )
        else:
            self._postprocess_shader_program = None
    
    def render_frame(self):
        """
        Main rendering loop. Renders scene to framebuffer,
        applies post-processing, and displays result.
        """
        # Render to framebuffer if post-processing is enabled
        if self._postprocess_shader_program:
            glBindFramebuffer(GL_FRAMEBUFFER, self._fbo_id)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Update camera matrices
        self.camera.update_view_matrix()
        
        # Render environment map
        if self.environment_map:
            self.environment_map.draw()
        
        # Render scene objects
        if self._main_shader_program:
            glUseProgram(self._main_shader_program)
            
            # Set camera matrices
            self._set_uniform_mat4("viewMatrix", self.camera.view_matrix)
            self._set_uniform_mat4("projectionMatrix", self.camera.projection_matrix)
            
            # Set lighting uniforms
            self._set_uniform_vec3("pointLight", self.light_position)
            self._set_uniform_float("ambientLight", self.ambient_intensity)
            
            # Set animation uniforms
            self._set_uniform_float("value", self.shader_param_value)
            self._set_uniform_float("time", self.elapsed_time)
            
            # Set texture samplers
            self._set_uniform_int("tex0", 0)
            self._set_uniform_int("tex1", 1)
        
        # Render each object in scene
        for scene_obj in self.scene_objects:
            if self._main_shader_program:
                model_matrix = scene_obj.compute_model_matrix()
                self._set_uniform_mat4("modelMatrix", model_matrix)
            
            scene_obj.draw()
        
        # Apply post-processing
        if self._postprocess_shader_program:
            self._apply_postprocessing()
    
    def _apply_postprocessing(self):
        """Renders post-processing pass."""
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)
        
        glUseProgram(self._postprocess_shader_program)
        
        # Bind framebuffer textures
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self._color_texture)
        
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self._depth_texture)
        
        # Set uniforms for post-processing shader
        location = glGetUniformLocation(self._postprocess_shader_program, "frameBuffer")
        if location != -1:
            glUniform1i(location, 0)
        
        location = glGetUniformLocation(self._postprocess_shader_program, "depthTexture")
        if location != -1:
            glUniform1i(location, 1)
        
        location = glGetUniformLocation(self._postprocess_shader_program, "time")
        if location != -1:
            glUniform1f(location, self.elapsed_time)
        
        # Draw fullscreen quad
        glDrawArrays(GL_QUADS, 0, 4)
        
        glEnable(GL_DEPTH_TEST)
    
    def _set_uniform_mat4(self, name, matrix):
        """Sets a 4x4 matrix uniform."""
        location = glGetUniformLocation(self._main_shader_program, name)
        glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(matrix))
    
    def _set_uniform_vec3(self, name, vector):
        """Sets a vec3 uniform."""
        location = glGetUniformLocation(self._main_shader_program, name)
        glUniform3fv(location, 1, glm.value_ptr(vector))
    
    def _set_uniform_float(self, name, value):
        """Sets a float uniform."""
        location = glGetUniformLocation(self._main_shader_program, name)
        glUniform1f(location, value)
    
    def _set_uniform_int(self, name, value):
        """Sets an integer uniform."""
        location = glGetUniformLocation(self._main_shader_program, name)
        glUniform1i(location, value)

