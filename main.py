"""
OpenGL 3D Model Viewer - Lab 10
A comprehensive 3D visualization system with orbital camera controls,
shader effects, and post-processing capabilities.
"""

import pygame
from pygame.locals import *
import glm

from src.gl import OpenGLRenderer
from src.model import Mesh3D
from src.vertexShaders import *
from src.fragmentShaders import *
from src.postProcessingShaders import *


# Window configuration
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540


def clamp(value, min_val, max_val):
    """Clamps a value between min and max."""
    return max(min_val, min(max_val, value))

# Camera orbital controls
class OrbitalCameraController:
    """Manages orbital camera movement around a target."""
    
    def __init__(self, camera, target=glm.vec3(0, 0, 0)):
        self.camera = camera
        self.target = target
        
        # Orbital parameters
        self.azimuth_angle = 0.0  # Horizontal rotation
        self.elevation_angle = 0.0  # Vertical rotation
        self.orbit_distance = 5.0
        
        # Control limits
        self.min_distance = 1.0
        self.max_distance = 50.0
        self.min_elevation = -85.0
        self.max_elevation = 85.0
        
        # Control sensitivity
        self.rotation_speed = 100.0
        self.mouse_sensitivity = 0.3
        self.zoom_speed = 15.0
        
        # Auto-orbit settings
        self.auto_orbit_enabled = True
        self.auto_orbit_speed = 20.0  # degrees per second
    
    def update_position(self):
        """Updates camera position based on orbital parameters."""
        from math import cos, sin, radians
        
        # Convert to radians
        azimuth_rad = radians(self.azimuth_angle)
        elevation_rad = radians(self.elevation_angle)
        
        # Calculate position on sphere
        self.camera.position.x = self.target.x + cos(elevation_rad) * sin(azimuth_rad) * self.orbit_distance
        self.camera.position.y = self.target.y + sin(elevation_rad) * self.orbit_distance
        self.camera.position.z = self.target.z + cos(elevation_rad) * cos(azimuth_rad) * self.orbit_distance
        
        # Look at target
        self.camera.look_at_target(self.target)
    
    def rotate_horizontal(self, delta_angle):
        """Rotates camera horizontally around target."""
        self.azimuth_angle += delta_angle
        self.azimuth_angle %= 360
    
    def rotate_vertical(self, delta_angle):
        """Rotates camera vertically with clamping."""
        self.elevation_angle += delta_angle
        self.elevation_angle = clamp(self.elevation_angle, self.min_elevation, self.max_elevation)
    
    def zoom(self, delta):
        """Adjusts orbit distance with limits."""
        self.orbit_distance += delta
        self.orbit_distance = clamp(self.orbit_distance, self.min_distance, self.max_distance)
    
    def update_auto_orbit(self, delta_time):
        """Updates automatic orbital rotation."""
        if self.auto_orbit_enabled:
            self.azimuth_angle += self.auto_orbit_speed * delta_time
            self.azimuth_angle %= 360
    
    def toggle_auto_orbit(self):
        """Toggles automatic orbital rotation on/off."""
        self.auto_orbit_enabled = not self.auto_orbit_enabled


def initialize_application():
    """Sets up pygame and creates the main renderer."""
    pygame.init()
    display = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.DOUBLEBUF | pygame.OPENGL
    )
    pygame.display.set_caption("3D Model Viewer - Lab 10")
    
    clock = pygame.time.Clock()
    renderer = OpenGLRenderer(display)
    
    return display, clock, renderer


def load_models():
    """Loads the three required models: Mario, Creature, and Stone."""
    models = []
    
    # Model 1: Mario
    mario = Mesh3D("models/Mario Models/Mario.obj")
    mario.load_texture("textures/Mario Textures/mario_main.png")
    mario.position.z = -5
    mario.rotation.x = 90  # Rotated 90 degrees on X axis
    mario.rotation.y = 180
    mario.scale = glm.vec3(1.5, 1.5, 1.5)
    mario.is_visible = True
    models.append(mario)
    
    # Model 2: Creature (Eye Monster)
    creature = Mesh3D("models/Eye Models/Demo Winged Eye Monster.obj")
    creature.load_texture("textures/Eye Textures/Monster_Color.jpg")
    creature.position.y = -1.5  # Lowered position
    creature.position.z = -5
    creature.scale = glm.vec3(0.3, 0.3, 0.3)  # Made smaller
    creature.is_visible = False
    models.append(creature)
    
    # Model 3: Stone
    stone = Mesh3D("models/Stone Models/rock.obj")
    stone.load_texture("textures/Stone Textures/rock_diffuse.png")
    stone.position.y = -2.0  # Lowered position
    stone.position.z = -5
    stone.scale = glm.vec3(0.5, 0.5, 0.5)  # Made much smaller
    stone.is_visible = False
    models.append(stone)
    
    return models


def setup_skybox(renderer):
    """Configures the environment skybox."""
    skybox_textures = [
        "skybox/right.png",
        "skybox/left.png",
        "skybox/top.png",
        "skybox/bottom.png",
        "skybox/front.png",
        "skybox/back.png"
    ]
    renderer.set_environment_map(skybox_textures)


def handle_keyboard_input(keys, camera_controller, delta_time):
    """Processes keyboard input for camera controls."""
    # Horizontal rotation
    if keys[K_LEFT]:
        camera_controller.rotate_horizontal(-camera_controller.rotation_speed * delta_time)
    if keys[K_RIGHT]:
        camera_controller.rotate_horizontal(camera_controller.rotation_speed * delta_time)
    
    # Vertical rotation
    if keys[K_UP]:
        camera_controller.rotate_vertical(camera_controller.rotation_speed * delta_time)
    if keys[K_DOWN]:
        camera_controller.rotate_vertical(-camera_controller.rotation_speed * delta_time)


def switch_active_model(models, new_index):
    """Changes which model is visible."""
    for i, model in enumerate(models):
        model.is_visible = (i == new_index)


def main():
    """Main application loop."""
    display, clock, renderer = initialize_application()
    
    # Load models and setup scene
    models = load_models()
    renderer.scene_objects = models
    
    setup_skybox(renderer)
    
    # Initialize shaders
    current_vertex_shader = vertex_shader
    current_fragment_shader = fragment_shader
    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
    renderer.compile_postprocess_shaders(vertex_postProcess, none_postProcess)
    
    # Setup camera controller
    camera_controller = OrbitalCameraController(renderer.camera)
    camera_controller.orbit_distance = 10.0
    
    # Post-processing effects list
    postprocess_effects = [
        none_postProcess,
        grayScale_postProcess,
        negative_postProcess,
        hurt_postProcess,
        depth_postProcess,
        fog_postProcess,
        dof_postProcess,
        edgeDetection_postProcess,
        outline_postProcess
    ]
    
    # State variables
    current_model_index = 0
    current_postprocess_index = 0
    running = True
    
    while running:
        delta_time = clock.tick(60) / 1000.0
        renderer.elapsed_time += delta_time
        
        keys = pygame.key.get_pressed()
        mouse_rel = pygame.mouse.get_rel()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Right click - cycle through models
                if event.button == 3:  # Right mouse button
                    current_model_index = (current_model_index + 1) % len(models)
                    switch_active_model(models, current_model_index)
            
            elif event.type == pygame.MOUSEWHEEL:
                # Zoom control
                camera_controller.zoom(-event.y * camera_controller.zoom_speed * delta_time)
            
            elif event.type == pygame.KEYDOWN:
                # Model selection with number keys
                if event.key == K_KP1:
                    current_model_index = 0
                    switch_active_model(models, current_model_index)
                elif event.key == K_KP2:
                    current_model_index = 1
                    switch_active_model(models, current_model_index)
                elif event.key == K_KP3:
                    current_model_index = 2
                    switch_active_model(models, current_model_index)
                
                # Rendering mode toggle
                elif event.key == K_f:
                    renderer.toggle_render_mode()
                
                # Auto-orbit toggle
                elif event.key == K_SPACE:
                    camera_controller.toggle_auto_orbit()
                
                # Post-processing cycle
                elif event.key == K_TAB:
                    current_postprocess_index = (current_postprocess_index + 1) % len(postprocess_effects)
                    renderer.compile_postprocess_shaders(
                        vertex_postProcess,
                        postprocess_effects[current_postprocess_index]
                    )
                
                # Fragment shader selection
                elif event.key == K_1:
                    current_fragment_shader = fragment_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_2:
                    current_fragment_shader = toon_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_3:
                    current_fragment_shader = negative_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_4:
                    current_fragment_shader = magma_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_5:
                    current_fragment_shader = rainbow_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_6:
                    current_fragment_shader = ghost_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_r:
                    current_fragment_shader = chromatic_aberration_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_h:
                    current_fragment_shader = hologram_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_x:
                    current_fragment_shader = xray_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                
                # Vertex shader selection
                elif event.key == K_7 or event.key == K_KP7:
                    current_vertex_shader = vertex_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_8 or event.key == K_KP8:
                    current_vertex_shader = fat_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_9 or event.key == K_KP9:
                    current_vertex_shader = water_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_0 or event.key == K_KP0:
                    current_vertex_shader = twist_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_t:
                    current_vertex_shader = explode_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_g:
                    current_vertex_shader = ghost_distortion_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_y:
                    current_vertex_shader = ripple_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
                elif event.key == K_u:
                    current_vertex_shader = spike_shader
                    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
        
        # Mouse drag for camera rotation
        if pygame.mouse.get_pressed()[0]:
            camera_controller.rotate_horizontal(mouse_rel[0] * camera_controller.mouse_sensitivity)
            camera_controller.rotate_vertical(-mouse_rel[1] * camera_controller.mouse_sensitivity)
        
        # Keyboard camera control
        handle_keyboard_input(keys, camera_controller, delta_time)
        
        # Update auto-orbit
        camera_controller.update_auto_orbit(delta_time)
        
        # Shader value control (usando + y -)
        if keys[K_MINUS] and renderer.shader_param_value > 0.0:
            renderer.shader_param_value -= delta_time
        if keys[K_EQUALS] and renderer.shader_param_value < 1.0:
            renderer.shader_param_value += delta_time
        
        # Update camera position and render
        camera_controller.update_position()
        renderer.render_frame()
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()