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




