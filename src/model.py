from OpenGL.GL import *
from src.obj import ObjFileParser
from src.buffer import VertexBufferObject
import glm
import pygame


class Mesh3D:
    """
    Represents a 3D mesh loaded from an OBJ file.
    Handles geometry data, textures, transformations, and rendering.
    """
    
    def __init__(self, obj_filepath):
        self._obj_data = ObjFileParser(obj_filepath)
        
        # Transformation properties
        self.position = glm.vec3(0, 0, 0)
        self.rotation = glm.vec3(0, 0, 0)
        self.scale = glm.vec3(1, 1, 1)
        
        # Rendering properties
        self.is_visible = True
        self._texture_ids = []
        self._vertex_count = 0
        # By default models are static (no automatic time-based animation)
        # Set this to True if you want shader 'time' uniforms to be driven.
        self.animated = False

        # Per-object shader programs
        self.shader_program = None  # Compiled vertex+fragment program for this mesh
        self.postprocess_program = None  # Optional post-process program
        self._fbo_id = None
        self._color_tex = None
        self._depth_tex = None

        # Vertex buffer objects
        self._position_vbo = None
        self._texcoord_vbo = None
        self._normal_vbo = None

        self._initialize_buffers()
    
    def compute_model_matrix(self):
        """
        Calculates the model transformation matrix.
        Combines translation, rotation, and scale transformations.
        
        Returns:
            4x4 transformation matrix
        """
        identity = glm.mat4(1)
        
        # Translation
        translation_matrix = glm.translate(identity, self.position)
        
        # Rotation (pitch, yaw, roll)
        pitch_matrix = glm.rotate(
            identity, 
            glm.radians(self.rotation.x), 
            glm.vec3(1, 0, 0)
        )
        yaw_matrix = glm.rotate(
            identity, 
            glm.radians(self.rotation.y), 
            glm.vec3(0, 1, 0)
        )
        roll_matrix = glm.rotate(
            identity, 
            glm.radians(self.rotation.z), 
            glm.vec3(0, 0, 1)
        )
        
        rotation_matrix = pitch_matrix * yaw_matrix * roll_matrix
        
        # Scale
        scale_matrix = glm.scale(identity, self.scale)
        
        return translation_matrix * rotation_matrix * scale_matrix
    
    def _initialize_buffers(self):
        """
        Processes OBJ data and creates GPU buffers for rendering.
        Triangulates quads and organizes vertex data.
        """
        position_data = []
        texcoord_data = []
        normal_data = []
        
        self._vertex_count = 0
        
        for face in self._obj_data.faces:
            # Extract face data - handle cases where some data might be missing
            face_positions = []
            face_texcoords = []
            face_normals = []
            
            for idx in face:
                # Vertex positions (required)
                face_positions.append(self._obj_data.vertices[idx[0] - 1])
                
                # Texture coordinates (optional)
                if len(idx) > 1 and idx[1] and len(self._obj_data.texCoords) > 0:
                    face_texcoords.append(self._obj_data.texCoords[idx[1] - 1])
                else:
                    face_texcoords.append([0.0, 0.0])
                
                # Normals (optional)
                if len(idx) > 2 and idx[2] and len(self._obj_data.normals) > 0:
                    face_normals.append(self._obj_data.normals[idx[2] - 1])
                else:
                    face_normals.append([0.0, 1.0, 0.0])
            
            # First triangle
            for i in range(3):
                position_data.extend(face_positions[i])
                texcoord_data.extend(face_texcoords[i])
                normal_data.extend(face_normals[i])
            
            self._vertex_count += 3
            
            # Handle quad faces (create second triangle)
            if len(face) == 4:
                for i in [0, 2, 3]:
                    position_data.extend(face_positions[i])
                    texcoord_data.extend(face_texcoords[i])
                    normal_data.extend(face_normals[i])
                
                self._vertex_count += 3
        
        # Create VBOs
        self._position_vbo = VertexBufferObject(position_data)
        self._texcoord_vbo = VertexBufferObject(texcoord_data)
        self._normal_vbo = VertexBufferObject(normal_data)
    
    def load_texture(self, texture_filepath):
        """
        Loads a texture from file and uploads it to GPU.
        
        Args:
            texture_filepath: Path to the texture image file
        """
        texture_surface = pygame.image.load(texture_filepath)
        texture_data = pygame.image.tostring(texture_surface, "RGB", True)
        
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            texture_surface.get_width(),
            texture_surface.get_height(),
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            texture_data
        )
        
        glGenerateMipmap(GL_TEXTURE_2D)
        
        self._texture_ids.append(texture_id)

    # ---------------- Per-object shaders -----------------
    def set_shaders(self, vertex_src, fragment_src):
        """Compiles and assigns a dedicated shader program to this mesh."""
        if vertex_src and fragment_src:
            try:
                from OpenGL.GL.shaders import compileProgram, compileShader
                self.shader_program = compileProgram(
                    compileShader(vertex_src, GL_VERTEX_SHADER),
                    compileShader(fragment_src, GL_FRAGMENT_SHADER)
                )
            except Exception as e:
                print(f"[error] Failed compiling mesh shaders: {e}")
                self.shader_program = None
        else:
            self.shader_program = None

    def set_postprocess_shaders(self, viewport_width, viewport_height, vertex_src, fragment_src):
        """Creates per-object post-process program and FBO if sources provided."""
        if not (vertex_src and fragment_src):
            self.postprocess_program = None
            return
        try:
            from OpenGL.GL.shaders import compileProgram, compileShader
            self.postprocess_program = compileProgram(
                compileShader(vertex_src, GL_VERTEX_SHADER),
                compileShader(fragment_src, GL_FRAGMENT_SHADER)
            )
        except Exception as e:
            print(f"[error] Failed compiling postprocess shaders: {e}")
            self.postprocess_program = None
            return

        # Create per-mesh FBO if not exists
        if self._fbo_id is None:
            self._fbo_id = glGenFramebuffers(1)
            glBindFramebuffer(GL_FRAMEBUFFER, self._fbo_id)
            # Color tex
            self._color_tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self._color_tex)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, viewport_width, viewport_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._color_tex, 0)
            # Depth tex
            self._depth_tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self._depth_tex)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, viewport_width, viewport_height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self._depth_tex, 0)
            glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def has_postprocess(self):
        return self.postprocess_program is not None and self._fbo_id is not None
    
    def draw(self):
        """
        Renders the mesh using OpenGL draw calls.
        Binds textures and vertex buffers, then issues draw command.
        """
        if not self.is_visible:
            return
        
        # Bind all textures
        for texture_index, texture_id in enumerate(self._texture_ids):
            glActiveTexture(GL_TEXTURE0 + texture_index)
            glBindTexture(GL_TEXTURE_2D, texture_id)
        
        # Configure vertex attributes
        self._position_vbo.bind_and_configure(0, 3)
        self._texcoord_vbo.bind_and_configure(1, 2)
        self._normal_vbo.bind_and_configure(2, 3)
        
        # Draw triangles
        glDrawArrays(GL_TRIANGLES, 0, self._vertex_count)
        
        # Cleanup
        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)




