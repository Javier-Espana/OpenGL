import glm
import ctypes
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from src.camera import PerspectiveCamera
from src.skybox import EnvironmentMap
from src.lighting import LightManager


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
        
        # Lighting system
        self.light_manager = LightManager()
        
        # Animation parameters
        self.shader_param_value = 0.0
        self.elapsed_time = 0.0
        
        # Shader toggle states
        self.vertex_shaders_enabled = True
        self.fragment_shaders_enabled = True
        self.postprocess_shaders_enabled = True
        
        # Framebuffer setup
        self._setup_framebuffers()
        
        # Post-processing quad setup
        self._setup_postprocess_quad()
    
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
    
    def _setup_postprocess_quad(self):
        """
        Creates a fullscreen quad for post-processing effects.
        Sets up VAO and VBO with vertex positions and texture coordinates.
        """
        import numpy as np
        
        # Fullscreen quad vertices: position (x, y) and texcoords (u, v)
        quad_vertices = np.array([
            # x,    y,   u,   v
            -1.0, -1.0, 0.0, 0.0,  # Bottom-left
             1.0, -1.0, 1.0, 0.0,  # Bottom-right
             1.0,  1.0, 1.0, 1.0,  # Top-right
            -1.0,  1.0, 0.0, 1.0   # Top-left
        ], dtype=np.float32)
        
        # Create VAO and VBO
        self._postprocess_vao = glGenVertexArrays(1)
        self._postprocess_vbo = glGenBuffers(1)
        
        glBindVertexArray(self._postprocess_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self._postprocess_vbo)
        glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)
        
        # Position attribute (location 0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
        
        # Texture coordinate attribute (location 1)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))
        
        # Unbind
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
    
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
        # Render to framebuffer if post-processing is enabled AND toggle is on
        if self._postprocess_shader_program and self.postprocess_shaders_enabled:
            glBindFramebuffer(GL_FRAMEBUFFER, self._fbo_id)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Update camera matrices
        self.camera.update_view_matrix()
        
        # Render environment map
        if self.environment_map:
            self.environment_map.draw()
        
        # Render each object in scene with its own shader if provided
        for scene_obj in self.scene_objects:
            # Decide which shader program to use based on toggles
            custom_program = getattr(scene_obj, "shader_program", None)
            
            # Si vertex_shaders_enabled o fragment_shaders_enabled están desactivados,
            # usar el shader básico en lugar del personalizado
            if custom_program and self.vertex_shaders_enabled and self.fragment_shaders_enabled:
                program = custom_program
            else:
                # Usar el shader por defecto sin efectos
                program = self._main_shader_program
            
            if program:
                glUseProgram(program)
                # camera
                self._set_uniform_mat4("viewMatrix", self.camera.view_matrix, program)
                self._set_uniform_mat4("projectionMatrix", self.camera.projection_matrix, program)
                
                # lighting - send all lights to shader
                self._set_lighting_uniforms(program)
                
                # animation
                self._set_uniform_float("value", self.shader_param_value, program)
                # Only drive time-based animations for models that enable it
                # Si vertex shaders están deshabilitados, no animar
                time_val = self.elapsed_time if (getattr(scene_obj, 'animated', False) and self.vertex_shaders_enabled) else 0.0
                self._set_uniform_float("time", time_val, program)
                # samplers
                self._set_uniform_int("tex0", 0, program)
                self._set_uniform_int("tex1", 1, program)
                # model transform
                model_matrix = scene_obj.compute_model_matrix()
                self._set_uniform_mat4("modelMatrix", model_matrix, program)
            scene_obj.draw()
        
        # Apply post-processing only if enabled
        if self._postprocess_shader_program and self.postprocess_shaders_enabled:
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
        
        # Draw fullscreen quad using proper VAO
        glBindVertexArray(self._postprocess_vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)
        
        glEnable(GL_DEPTH_TEST)
    
    def _set_lighting_uniforms(self, program):
        """Sets lighting uniforms for all lights in the scene"""
        # Ambient light
        self._set_uniform_float("ambientIntensity", self.light_manager.get_ambient_intensity(), program)
        self._set_uniform_vec3("ambientColor", self.light_manager.get_ambient_color(), program)
        
        # Directional lights
        dir_lights = [l for l in self.light_manager.directional_lights if l.enabled]
        num_dir = min(len(dir_lights), 4)  # Max 4 directional lights
        self._set_uniform_int("numDirLights", num_dir, program)
        
        for i, light in enumerate(dir_lights[:4]):
            self._set_uniform_vec3(f"dirLightDirections[{i}]", light.direction, program)
            self._set_uniform_vec3(f"dirLightColors[{i}]", light.color, program)
            self._set_uniform_float(f"dirLightIntensities[{i}]", light.intensity, program)
        
        # Point lights
        point_lights = [l for l in self.light_manager.point_lights if l.enabled]
        num_point = min(len(point_lights), 4)  # Max 4 point lights
        self._set_uniform_int("numPointLights", num_point, program)
        
        for i, light in enumerate(point_lights[:4]):
            self._set_uniform_vec3(f"pointLightPositions[{i}]", light.position, program)
            self._set_uniform_vec3(f"pointLightColors[{i}]", light.color, program)
            self._set_uniform_float(f"pointLightIntensities[{i}]", light.intensity, program)
    
    def _set_uniform_mat4(self, name, matrix, program=None):
        """Sets a 4x4 matrix uniform."""
        prg = program or self._main_shader_program
        location = glGetUniformLocation(prg, name)
        glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(matrix))
    
    def _set_uniform_vec3(self, name, vector, program=None):
        """Sets a vec3 uniform."""
        prg = program or self._main_shader_program
        location = glGetUniformLocation(prg, name)
        glUniform3fv(location, 1, glm.value_ptr(vector))
    
    def _set_uniform_float(self, name, value, program=None):
        """Sets a float uniform."""
        prg = program or self._main_shader_program
        location = glGetUniformLocation(prg, name)
        glUniform1f(location, value)
    
    def _set_uniform_int(self, name, value, program=None):
        """Sets an integer uniform."""
        prg = program or self._main_shader_program
        location = glGetUniformLocation(prg, name)
        glUniform1i(location, value)

