import glm
from math import sin, cos, radians


class PerspectiveCamera:
    """
    Perspective camera with orbital controls and configurable projection.
    Supports LookAt functionality and Euler angle rotations.
    """
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.position = glm.vec3(0, 0, 0)
        self.rotation = glm.vec3(0, 0, 0)
        
        self._view_matrix = None
        self._projection_matrix = None
        self._use_lookat = False
        
        self.configure_projection(60, 0.1, 1000)
    
    def update_view_matrix(self):
        """
        Recalculates the view matrix based on position and rotation.
        Uses manual matrix construction unless LookAt was called.
        """
        if not self._use_lookat:
            identity_matrix = glm.mat4(1)
            
            # Build transformation matrices
            translation = glm.translate(identity_matrix, self.position)
            
            pitch_rotation = glm.rotate(
                identity_matrix, 
                glm.radians(self.rotation.x), 
                glm.vec3(1, 0, 0)
            )
            yaw_rotation = glm.rotate(
                identity_matrix, 
                glm.radians(self.rotation.y), 
                glm.vec3(0, 1, 0)
            )
            roll_rotation = glm.rotate(
                identity_matrix, 
                glm.radians(self.rotation.z), 
                glm.vec3(0, 0, 1)
            )
            
            rotation_matrix = pitch_rotation * yaw_rotation * roll_rotation
            camera_transform = translation * rotation_matrix
            
            self._view_matrix = glm.inverse(camera_transform)
        
        self._use_lookat = False
    
    def configure_projection(self, fov_degrees, near_clip, far_clip):
        """
        Sets up the perspective projection matrix.
        
        Args:
            fov_degrees: Field of view in degrees
            near_clip: Near clipping plane distance
            far_clip: Far clipping plane distance
        """
        aspect_ratio = self.screen_width / self.screen_height
        self._projection_matrix = glm.perspective(
            glm.radians(fov_degrees), 
            aspect_ratio, 
            near_clip, 
            far_clip
        )
    
    def look_at_target(self, target_position):
        """
        Makes the camera look at a specific point in 3D space.
        
        Args:
            target_position: The 3D point to look at
        """
        self._use_lookat = True
        up_vector = glm.vec3(0, 1, 0)
        self._view_matrix = glm.lookAt(
            self.position, 
            target_position, 
            up_vector
        )
    
    def set_orbital_position(self, center, radius, angle_degrees):
        """
        Positions the camera in an orbit around a center point.
        
        Args:
            center: Center point of orbit
            radius: Distance from center
            angle_degrees: Angle around the Y-axis in degrees
        """
        angle_rad = radians(angle_degrees)
        self.position.x = center.x + sin(angle_rad) * radius
        self.position.z = center.z + cos(angle_rad) * radius
    
    @property
    def view_matrix(self):
        """Returns the current view matrix."""
        return self._view_matrix
    
    @property
    def projection_matrix(self):
        """Returns the current projection matrix."""
        return self._projection_matrix