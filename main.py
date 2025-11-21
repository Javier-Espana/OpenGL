"""
OpenGL 3D Model Viewer - Lab 10
A comprehensive 3D visualization system with orbital camera controls,
shader effects, and post-processing capabilities.
"""

import pygame
from pygame.locals import *
import glm
import os

from src.gl import OpenGLRenderer
from src.model import Mesh3D
from src.vertexShaders import *
from src.fragmentShaders import *
from src.postProcessingShaders import *


# Window configuration
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
## Visibility control: now using direct boolean literals at load time
# To hide a model, change the corresponding visible=True to visible=False in load_models()

# Solo debug mode (set to name to isolate one model or None)
DEBUG_SOLO_NAME = None  # e.g. "eye_monster"
##

def clamp(value, min_val, max_val):
    """Clamps a value between min and max."""
    return max(min_val, min(max_val, value))

# Camera orbital controls
class OrbitalCameraController:
    """Manages orbital camera movement around a target."""
    
    def __init__(self, camera, target=glm.vec3(0, 0, -5)):
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
        
        # Auto-orbit settings (disabled by default; toggle with Space)
        self.auto_orbit_enabled = False
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
    """Loads the tree scene."""
    models = []

    def add_model(model_path, texture_path=None, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1), 
                  name=None, visible=True, vertex_shader=None, fragment_shader=None, postprocess_shader=None):
        # If the flag is False, skip loading entirely (do not create the mesh)
        if not visible:
            return
        if not os.path.exists(model_path):
            print(f"[warn] Model file not found: {model_path} (skipped)")
            return
        m = Mesh3D(model_path)
        if texture_path and os.path.exists(texture_path):
            m.load_texture(texture_path)
        # transforms
        m.position = glm.vec3(*position)
        m.rotation = glm.vec3(*rotation)
        m.scale = glm.vec3(*scale)
        m.is_visible = True
        m.debug_name = name or os.path.basename(model_path)
        
        # Marcar como animado si tiene vertex shader personalizado (que probablemente usa time)
        m.animated = (vertex_shader is not None)
        
        # Apply shaders if provided
        vs = vertex_shader if vertex_shader else globals().get('vertex_shader')
        fs = fragment_shader if fragment_shader else globals().get('fragment_shader')
        if vs and fs:
            m.set_shaders(vs, fs)
        
        # Apply postprocess shader if provided
        if postprocess_shader:
            try:
                # Get viewport dimensions from renderer (will be set later in main)
                m.set_postprocess_shaders(960, 540, globals().get('vertex_postProcess'), postprocess_shader)
            except Exception as e:
                print(f"[warn] Postprocess setup failed for {name}: {e}")
        
        models.append(m)

    # Ground - Large grass patch CON SHADER DE VIENTO
    add_model(
        "models/10450_Rectangular_Grass_Patch_L3.123c827d110a-1347-4381-9208-e4f735762647/10450_Rectangular_Grass_Patch_v1_iterations-2.obj",
        texture_path="models/10450_Rectangular_Grass_Patch_L3.123c827d110a-1347-4381-9208-e4f735762647/10450_Rectangular_Grass_Patch_v1_Diffuse.jpg",
        position=(0, -2, 0),
        rotation=(-90, 0, -90),
        scale=(0.3, 0.3, 0.3),
        name="grass_ground",
        visible=True,
        vertex_shader=wind_grass_shader,
        fragment_shader=grass_vibrant_shader,
        postprocess_shader=nature_ambient_postProcess
    )

    # Main Tree (original) CON SHADER DE ÁRBOL
    add_model(
        "models/Tree/Tree.obj",
        texture_path="models/Tree/bark_0021.jpg",
        position=(12, 0, -10),
        rotation=(0, 0, 0),
        scale=(1.6, 1.6, 1.6), 
        name="tree", 
        visible=True,
        vertex_shader=tree_sway_shader,
        fragment_shader=bark_shader,
        postprocess_shader=sunny_day_postProcess
    )

    # Cottage CON SHADER CÁLIDO
    add_model(
        "models/85-cottage_obj/cottage_obj.obj",
        texture_path="models/85-cottage_obj/cottage_textures/cottage_diffuse.png",
        position=(0, 0, -10),
        rotation=(0, 0, 0),
        scale=(0.3, 0.3, 0.3), 
        name="cottage", 
        visible=True,
        fragment_shader=cottage_warm_shader
    )

    # === PLANTS AND VEGETATION ===
    
    # Palm tree near cottage (left side) CON SHADER DE PALMERA
    add_model(
        "models/Palm_01/Palm_01.obj",
        texture_path="models/Palm_01/stalk_003_gradient.jpg",
        position=(-12, 0, -12),
        rotation=(0, 45, 0),
        scale=(0.2, 0.2, 0.2),
        name="palm_1",
        visible=True,
        vertex_shader=palm_wave_shader,
        fragment_shader=foliage_shader
    )

    # Second palm tree (right side) CON SHADER DE PALMERA
    add_model(
        "models/Palm_01/Palm_01.obj",
        texture_path="models/Palm_01/stalk_003_gradient.jpg",
        position=(8, 0, -8),
        rotation=(0, -30, 0),
        scale=(0.1, 0.1, 0.1),
        name="palm_2",
        visible=True,
        vertex_shader=palm_wave_shader,
        fragment_shader=foliage_shader
    )


    # Tree2 (Tree1.obj) - left side
    add_model(
        "models/Tree2/Tree1.obj",
        texture_path="models/Tree2/BarkDecidious0143_5_S.jpg",
        position=(-12, 0, -8),
        rotation=(0, 60, 0),
        scale=(0.8, 0.8, 0.8),
        name="tree2",
        visible=True
    )



    # Plant model (kijz846ur3sw-plant) - decorative bushes
    add_model(
        "models/kijz846ur3sw-plant/plants1.obj",
        texture_path="models/k830ot7e4ge8-Free_v10_model/Textures/leaves_02.jpg",
        position=(-6, 0, -9),
        rotation=(0, 30, 0),
        scale=(0.6, 0.6, 0.6),
        name="plant_bush_1",
        visible=True
    )

    add_model(
        "models/kijz846ur3sw-plant/plants1.obj",
        texture_path="models/k830ot7e4ge8-Free_v10_model/Textures/leaves_02.jpg",
        position=(6, 0, -11),
        rotation=(0, -45, 0),
        scale=(0.55, 0.55, 0.55),
        name="plant_bush_2",
        visible=True
    )

    add_model(
        "models/kijz846ur3sw-plant/plants1.obj",
        texture_path="models/k830ot7e4ge8-Free_v10_model/Textures/leaves_02.jpg",
        position=(10, 0, -8),
        rotation=(0, 60, 0),
        scale=(0.5, 0.5, 0.5),
        name="plant_bush_3",
        visible=True
    )


  
    # Additional bushes using kijz846ur3sw-plant
    add_model(
        "models/kijz846ur3sw-plant/plants1.obj",
        texture_path="models/k830ot7e4ge8-Free_v10_model/Textures/leaves_01.jpg",
        position=(-10, 0, -12),
        rotation=(0, 90, 0),
        scale=(0.65, 0.65, 0.65),
        name="plant_bush_4",
        visible=True
    )

    add_model(
        "models/kijz846ur3sw-plant/plants1.obj",
        texture_path="models/k830ot7e4ge8-Free_v10_model/Textures/leaves_03.jpg",
        position=(14, 0, -12),
        rotation=(0, -90, 0),
        scale=(0.6, 0.6, 0.6),
        name="plant_bush_5",
        visible=True
    )

    return models

def setup_lights(renderer):
    """
    Configures all lights in the scene.
    You can add/modify lights here just like adding models.
    """
    from src.lighting import AmbientLight, DirectionalLight, PointLight
    
    # Ambient light - soft base illumination
    ambient = AmbientLight(
        color=glm.vec3(0.8, 0.85, 1.0),  # Slight blue tint for sky ambient
        intensity=0.15
    )
    renderer.light_manager.add_light(ambient)
    
    # Sun - directional light from skybox (front face where sun is)
    sun = DirectionalLight(
        direction=glm.vec3(-0.9, -0.5, -1.0),  # Coming from front-right and slightly down
        color=glm.vec3(1.0, 0.95, 0.8),  # Warm sunlight
        intensity=0.9
    )
    renderer.light_manager.add_light(sun)
    
    # Point light near cottage (like a lamp)
    cottage_light = PointLight(
        position=glm.vec3(-5, 3, -10),  # Above and to the left of cottage
        color=glm.vec3(1.0, 0.8, 0.6),  # Warm orange light
        intensity=0.5
    )
    renderer.light_manager.add_light(cottage_light)
    
    print("[debug] Lighting setup:")
    print(f"  - Ambient light: intensity={ambient.intensity}, color={ambient.color}")
    print(f"  - Sun (directional): direction={sun.direction}, intensity={sun.intensity}")
    print(f"  - Cottage light (point): pos={cottage_light.position}, intensity={cottage_light.intensity}")

def compute_scene_center_and_radius(models):
    if not models:
        return glm.vec3(0, 0, -5), 10.0
    # center
    cx = sum(m.position.x for m in models) / len(models)
    cy = sum(m.position.y for m in models) / len(models)
    cz = sum(m.position.z for m in models) / len(models)
    center = glm.vec3(cx, cy, cz)
    # radius (max distance from center)
    import math
    radius = 0.0
    for m in models:
        d = math.sqrt((m.position.x - cx) ** 2 + (m.position.y - cy) ** 2 + (m.position.z - cz) ** 2)
        if d > radius:
            radius = d
    return center, max(radius, 10.0)


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


# Removed model switching; all models are always visible.


def main():
    """Main application loop."""
    display, clock, renderer = initialize_application()
    
    # Load models and setup scene
    models = load_models()
    renderer.scene_objects = models
    print("[debug] Loaded models and their positions:")
    for m in models:
        print(f"  - {getattr(m, 'debug_name', '<unnamed>')}: {m.position}")
    
    # Setup lighting
    setup_lights(renderer)
    
    # Setup skybox
    setup_skybox(renderer)
    
    # Solo debug override
    if DEBUG_SOLO_NAME:
        for m in models:
            m.is_visible = (getattr(m, 'debug_name', None) == DEBUG_SOLO_NAME)
    
    # Initialize shaders (global fallback)
    current_vertex_shader = vertex_shader
    current_fragment_shader = fragment_shader
    renderer.compile_shaders(current_vertex_shader, current_fragment_shader)
    renderer.compile_postprocess_shaders(vertex_postProcess, none_postProcess)
    
    # Setup camera controller centered on scene
    camera_controller = OrbitalCameraController(renderer.camera)
    scene_center, scene_radius = compute_scene_center_and_radius(models)
    camera_controller.target = scene_center
    camera_controller.orbit_distance = scene_radius * 1.8
    
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
    current_postprocess_index = 0
    running = True
    
    # Shader toggle state - un solo toggle para TODOS los shaders
    shaders_enabled = True
    
    print("\n=== CONTROLES DE SHADERS ===")
    print("V: Toggle TODOS los Shaders (ON/OFF)")
    print("================================\n")
    
    while running:
        delta_time = clock.tick(60) / 1000.0
        renderer.elapsed_time += delta_time
        
        keys = pygame.key.get_pressed()
        mouse_rel = pygame.mouse.get_rel()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Removed model cycling by mouse click
            
            elif event.type == pygame.MOUSEWHEEL:
                # Zoom control
                camera_controller.zoom(-event.y * camera_controller.zoom_speed * delta_time)
            
            elif event.type == pygame.KEYDOWN:
                # Removed model selection by number keys; all models are shown simultaneously
                
                # Rendering mode toggle
                if event.key == K_f:
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
                
                # === SHADER TOGGLE ÚNICO ===
                # Toggle para TODOS los shaders con una sola tecla
                elif event.key == K_v:
                    shaders_enabled = not shaders_enabled
                    estado = "ENABLED ✓" if shaders_enabled else "DISABLED ✗"
                    print(f"[shader] Todos los Shaders: {estado}")


        
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
        
        # Pasar estado de toggle al renderer (un solo estado para todos)
        renderer.vertex_shaders_enabled = shaders_enabled
        renderer.fragment_shaders_enabled = shaders_enabled
        renderer.postprocess_shaders_enabled = shaders_enabled
        
        renderer.render_frame()
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()