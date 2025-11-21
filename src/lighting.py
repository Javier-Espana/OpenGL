"""
Lighting System for OpenGL Renderer
Supports multiple light types: ambient, directional, point, and spot lights
"""

import glm


class Light:
    """Base class for all light types"""
    def __init__(self, light_type, color=glm.vec3(1.0, 1.0, 1.0), intensity=1.0):
        self.type = light_type
        self.color = color
        self.intensity = intensity
        self.enabled = True


class AmbientLight(Light):
    """Ambient light - uniform illumination from all directions"""
    def __init__(self, color=glm.vec3(1.0, 1.0, 1.0), intensity=0.1):
        super().__init__("ambient", color, intensity)


class DirectionalLight(Light):
    """Directional light - parallel rays from a direction (like the sun)"""
    def __init__(self, direction=glm.vec3(0.0, -1.0, 0.0), color=glm.vec3(1.0, 1.0, 1.0), intensity=1.0):
        super().__init__("directional", color, intensity)
        self.direction = glm.normalize(direction)


class PointLight(Light):
    """Point light - emits light in all directions from a position"""
    def __init__(self, position=glm.vec3(0.0, 0.0, 0.0), color=glm.vec3(1.0, 1.0, 1.0), intensity=1.0):
        super().__init__("point", color, intensity)
        self.position = position
        # Attenuation parameters (distance falloff)
        self.constant = 1.0
        self.linear = 0.09
        self.quadratic = 0.032


class SpotLight(Light):
    """Spot light - cone of light from a position in a direction"""
    def __init__(self, position=glm.vec3(0.0, 0.0, 0.0), direction=glm.vec3(0.0, -1.0, 0.0), 
                 color=glm.vec3(1.0, 1.0, 1.0), intensity=1.0, cutoff_angle=12.5, outer_cutoff_angle=17.5):
        super().__init__("spot", color, intensity)
        self.position = position
        self.direction = glm.normalize(direction)
        self.cutoff_angle = cutoff_angle  # Inner cone angle in degrees
        self.outer_cutoff_angle = outer_cutoff_angle  # Outer cone angle in degrees
        # Attenuation
        self.constant = 1.0
        self.linear = 0.09
        self.quadratic = 0.032


class LightManager:
    """Manages multiple lights in the scene"""
    def __init__(self):
        self.lights = []
        self.ambient_light = None
        self.directional_lights = []
        self.point_lights = []
        self.spot_lights = []
    
    def add_light(self, light):
        """Add a light to the scene"""
        self.lights.append(light)
        
        if isinstance(light, AmbientLight):
            self.ambient_light = light
        elif isinstance(light, DirectionalLight):
            self.directional_lights.append(light)
        elif isinstance(light, PointLight):
            self.point_lights.append(light)
        elif isinstance(light, SpotLight):
            self.spot_lights.append(light)
    
    def remove_light(self, light):
        """Remove a light from the scene"""
        if light in self.lights:
            self.lights.remove(light)
            
            if isinstance(light, AmbientLight) and self.ambient_light == light:
                self.ambient_light = None
            elif isinstance(light, DirectionalLight):
                self.directional_lights.remove(light)
            elif isinstance(light, PointLight):
                self.point_lights.remove(light)
            elif isinstance(light, SpotLight):
                self.spot_lights.remove(light)
    
    def get_ambient_intensity(self):
        """Get total ambient light intensity"""
        if self.ambient_light and self.ambient_light.enabled:
            return self.ambient_light.intensity
        return 0.0
    
    def get_ambient_color(self):
        """Get ambient light color"""
        if self.ambient_light and self.ambient_light.enabled:
            return self.ambient_light.color
        return glm.vec3(1.0, 1.0, 1.0)
