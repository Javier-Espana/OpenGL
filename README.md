# OpenGL 3D Model Viewer

Visor de modelos 3D desarrollado en OpenGL con sistema de cámara orbital, múltiples shaders y efectos de post-procesamiento.

## Modelos

El proyecto incluye tres modelos 3D con sus respectivas texturas:

1. **Mario** - Personaje de Nintendo con textura mario_main.png
2. **Creature** - Monstruo ojo alado con textura Monster_Color.jpg
3. **Stone** - Roca con textura rock_diffuse.png

## Shaders Implementados

### Fragment Shaders (9)
- Standard - Iluminación Phong
- Toon - Cell shading
- Negative - Inversión de colores
- Magma - Efecto de lava
- Rainbow - Gradiente HSV
- Ghost - Transparencia espectral
- Chromatic Aberration - Separación de canales RGB
- Hologram - Efecto holográfico
- X-Ray - Visualización de bordes

### Vertex Shaders (8)
- Standard - Sin deformación
- Fat - Expansión de geometría
- Water - Ondas animadas
- Twist - Rotación por altura
- Explode - Expansión pulsante
- Ghost Distortion - Distorsión espectral
- Ripple - Ondas concéntricas
- Spike - Picos procedurales

### Post-Procesamiento (9)
- None
- Grayscale
- Negative
- Hurt
- Depth
- Fog
- DOF
- Edge Detection
- Outline

## Controles

### Modelos Simultáneos
Los tres modelos (Mario, Creature y Stone) se cargan y renderizan al mismo tiempo. Ya no existe selección individual; todos permanecen visibles simultáneamente.

### Cámara Orbital
- **Flechas Izquierda/Derecha** - Rotación horizontal (azimuth)
- **Flechas Arriba/Abajo** - Rotación vertical (elevación)
- **Clic Izquierdo + Arrastrar** - Control de cámara con mouse
- **Rueda del Mouse** - Zoom in/out
- **Espacio** - Activar/Desactivar órbita automática

*La cámara orbita automáticamente alrededor del grupo de modelos (centro compartido). Usa Espacio para pausar/reanudar la órbita automática.*

### Fragment Shaders
- **1-6** - Standard, Toon, Negative, Magma, Rainbow, Ghost
- **R** - Chromatic Aberration
- **H** - Hologram
- **X** - X-Ray

### Vertex Shaders
- **7 (o Numpad 7)** - Standard
- **8 (o Numpad 8)** - Fat
- **9 (o Numpad 9)** - Water
- **0 (o Numpad 0)** - Twist
- **T** - Explode
- **G** - Ghost Distortion
- **Y** - Ripple
- **U** - Spike

### Otros Controles
- **TAB** - Ciclar efectos de post-procesamiento
- **-/=** - Ajustar parámetros de shader
- **F** - Alternar modo wireframe/sólido
- **Espacio** - Activar/Desactivar órbita automática de cámara

## Ejecución

### Requisitos
- Python 3.8+
- pygame
- PyOpenGL
- PyGLM

### Instalación de Dependencias

```bash
# Activar entorno virtual (si existe)
source .venv/bin/activate

# O instalar dependencias
pip install pygame PyOpenGL PyGLM
```

### Ejecutar el Programa

```bash
python main.py
```

O con el intérprete del entorno virtual:

```bash
./.venv/bin/python main.py
```

## Estructura del Proyecto

```
OpenGL/
├── main.py                 # Punto de entrada
├── src/
│   ├── gl.py              # Renderer OpenGL
│   ├── camera.py          # Sistema de cámara
│   ├── model.py           # Carga de modelos
│   ├── obj.py             # Parser OBJ
│   ├── buffer.py          # Buffers OpenGL
│   ├── skybox.py          # Skybox/Environment map
│   ├── vertexShaders.py   # Shaders de vértices
│   ├── fragmentShaders.py # Shaders de fragmentos
│   └── postProcessingShaders.py
├── models/                # Archivos .obj
├── textures/              # Texturas
└── skybox/                # Texturas de skybox
```

## Características Técnicas

- Sistema de cámara orbital con coordenadas esféricas
- Órbita automática alrededor del modelo activo (configurable con Espacio)
- Límites de elevación (-85° a +85°) para prevenir gimbal lock
- Zoom configurable (1.0 a 50.0 unidades)
- 72 combinaciones posibles de shaders (9 fragment x 8 vertex)
- Framebuffers para post-procesamiento
- Compatibilidad completa entre todos los modelos y shaders
- Skybox personalizado con environment mapping

## Autor

Proyecto desarrollado para Laboratorio 10 - Gráficas por Computadora
