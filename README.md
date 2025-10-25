# OpenGL Shader Lab - Documentación de Controles

Este proyecto implementa un laboratorio de shaders en OpenGL que incluye 11 shaders diferentes (6 requeridos y 5 adicionales) que pueden combinarse libremente para generar diversos efectos visuales.

---

## CONTROLES DEL TECLADO

### Fragment Shaders (Teclas numéricas y letras)

Los fragment shaders controlan el color y la apariencia visual del modelo renderizado.

| Tecla | Shader | Descripción |
|-------|--------|-------------|
| **1** | Standard | Implementa iluminación Phong básica con textura. Shader de referencia estándar. |
| **2** | Toon | Implementa cell shading con bandas de color discretas. |
| **3** | Negative | Invierte los valores de color de la textura generando un efecto de negativo fotográfico. |
| **4** | Magma | Genera un efecto de lava con animación de colores en espectro rojo-naranja-amarillo. |
| **5** | Rainbow | **[NUEVO]** Genera colores no homogéneos mediante conversión de espacio de color HSV a RGB con patrones espaciales variables. |
| **6** | Ghost | **[NUEVO]** Implementa efecto de transparencia con color cyan espectral utilizando efecto Fresnel. Valores de alpha entre 0.2 y 0.7. |
| **R** | Chromatic Aberration | **[NUEVO]** Simula aberración cromática mediante separación de canales RGB. |
| **H** | Hologram | **[ADICIONAL]** Genera efecto holográfico con scanlines procedurales horizontales y modulación de brillo. |
| **X** | X-Ray | **[ADICIONAL]** Implementa visualización tipo rayos X con resaltado de bordes mediante Fresnel inverso. |

### Vertex Shaders (Teclas numéricas superiores)

Los vertex shaders controlan la transformación geométrica del modelo.

| Tecla | Shader | Descripción |
|-------|--------|-------------|
| **7** | Standard | Sin deformación geométrica. Mantiene la geometría original del modelo. |
| **8** | Fat | Desplaza los vértices a lo largo de sus vectores normales inflando el modelo. |
| **9** | Water | Aplica deformación sinusoidal vertical para simular ondas de agua. |
| **0** | Twist | **[NUEVO]** Aplica rotación progresiva alrededor del eje Y generando una torsión helicoidal. |
| **-** | Explode | **[NUEVO]** Desplaza los triángulos individualmente a lo largo de sus normales con variación espacial. |
| **=** | Ghost Distortion | **[NUEVO]** Aplica deformación ondulatoria en múltiples ejes (X, Y, Z) con frecuencias diferenciadas. |
| **T** | Ripple | **[ADICIONAL]** Genera ondas concéntricas radiales que se propagan desde el centro del modelo. |
| **Y** | Spike | **[ADICIONAL]** Genera protuberancias basadas en vectores normales de la superficie. |

### Control de Parámetros

| Tecla | Función | Descripción |
|-------|---------|-------------|
| **Z** | Disminuir Value | Reduce la intensidad del efecto activo (decremento de 0.1). |
| **X** | Aumentar Value | Aumenta la intensidad del efecto activo (incremento de 0.1). |

El parámetro `value` controla la intensidad de los siguientes efectos:
- **Twist**: Ángulo de rotación aplicado
- **Explode**: Distancia de separación de los triángulos
- **Ghost Distortion**: Amplitud de las ondas de distorsión
- **Ripple**: Amplitud de las ondas radiales
- **Spike**: Altura de las protuberancias generadas

### Control de Iluminación

| Tecla | Función | Descripción |
|-------|---------|-------------|
| **W** | Luz Adelante | Desplaza la fuente de luz en dirección +Z. |
| **S** | Luz Atrás | Desplaza la fuente de luz en dirección -Z. |
| **A** | Luz Izquierda | Desplaza la fuente de luz en dirección -X. |
| **D** | Luz Derecha | Desplaza la fuente de luz en dirección +X. |
| **Q** | Luz Abajo | Desplaza la fuente de luz en dirección -Y. |
| **E** | Luz Arriba | Desplaza la fuente de luz en dirección +Y. |

### Control de Cámara

| Tecla | Función | Descripción |
|-------|---------|-------------|
| **↑** | Cámara Adelante | Desplaza la cámara hacia el modelo. |
| **↓** | Cámara Atrás | Desplaza la cámara alejándose del modelo. |
| **←** | Cámara Izquierda | Desplaza la cámara lateralmente hacia la izquierda. |
| **→** | Cámara Derecha | Desplaza la cámara lateralmente hacia la derecha. |

### Modo de Visualización

| Tecla | Función | Descripción |
|-------|---------|-------------|
| **F** | Toggle Wireframe | Alterna entre modo de renderizado sólido y wireframe (visualización de malla de líneas). |

---

## COMBINACIONES DE SHADERS RECOMENDADAS

### Efecto Fantasma Completo
```
Vertex Shader:   = (Ghost Distortion)
Fragment Shader: 6 (Ghost)
Parámetro Value: 0.5
```
**Resultado:** Combinación de color semi-transparente cyan con deformación ondulatoria multi-eje.

### Efecto Rainbow con Rotación
```
Vertex Shader:   0 (Twist)
Fragment Shader: 5 (Rainbow)
Parámetro Value: 0.7
```
**Resultado:** Modelo con rotación helicoidal y colores no homogéneos en espectro visible.

### Holograma con Ondas
```
Vertex Shader:   T (Ripple)
Fragment Shader: H (Hologram)
Parámetro Value: 0.4
```
**Resultado:** Efecto holográfico con scanlines combinado con ondas radiales concéntricas.

### Efecto Glitch Digital
```
Vertex Shader:   - (Explode)
Fragment Shader: R (Chromatic)
Parámetro Value: 0.3
```
**Resultado:** Aberración cromática RGB aplicada a geometría fragmentada.

### Visualización Rayos X
```
Vertex Shader:   - (Explode)
Fragment Shader: X (X-Ray)
Parámetro Value: 0.2
```
**Resultado:** Efecto de rayos X con detección de bordes aplicado a triángulos separados.

### Agua con Colores Variables
```
Vertex Shader:   9 (Water)
Fragment Shader: 5 (Rainbow)
Parámetro Value: 0.6
```
**Resultado:** Deformación ondulatoria vertical con gradiente de color no homogéneo.

---

## RECOMENDACIONES DE CONFIGURACIÓN

### Optimización de Parámetros

1. **Ghost Shader (Tecla 6):** Se recomienda utilizar valores entre 0.3 y 0.7 para mantener un balance adecuado entre transparencia y visibilidad.

2. **Rainbow (Tecla 5):** Valores superiores a 0.7 generan mayor variación cromática y patrones más contrastados.

3. **Twist (Tecla 0):** Valores inferiores a 0.5 producen rotaciones suaves. Valores superiores a 0.8 generan torsiones pronunciadas.

4. **Explode (Tecla -):** Se recomienda mantener valores inferiores a 0.3 para preservar la coherencia geométrica del modelo.

5. **Chromatic Aberration (Tecla R):** El efecto se aprecia mejor con movimiento de cámara o iluminación dinámica.

6. **Hologram (Tecla H):** La combinación con vertex shaders animados incrementa el efecto visual.

7. **Modo Wireframe (Tecla F):** Útil para visualizar las transformaciones geométricas aplicadas por los vertex shaders.

8. **Control de Iluminación:** El desplazamiento de la fuente de luz permite observar la respuesta de los shaders a diferentes ángulos de incidencia.

---

## ARQUITECTURA DEL PROYECTO

### Estructura de Directorios

```
main.py                          # Bucle principal y sistema de control de entrada
src/
  ├── gl.py                      # Configuración del renderer OpenGL
  ├── camera.py                  # Sistema de cámara
  ├── model.py                   # Carga de modelos con soporte de materiales
  ├── obj.py                     # Parser de archivos .obj y .mtl
  ├── buffer.py                  # Gestión de VBOs y VAOs
  ├── skybox.py                  # Implementación de skybox
  ├── vertexShaders.py           # Definiciones de 8 vertex shaders
  └── fragmentShaders.py         # Definiciones de 9 fragment shaders
models/                          # Modelos 3D en formato .obj
textures/                        # Archivos de textura (.jpg, .png, .bmp)
skybox/                          # Texturas del skybox (6 caras)
```

### Características Técnicas Implementadas

- **OpenGL 3.3+** con shaders GLSL versión 330 core
- **Sistema de materiales:** Carga automática de texturas desde archivos de definición de materiales (.mtl)
- **Renderizado por submeshes:** Procesamiento separado por material para soporte de múltiples texturas
- **Cache de texturas:** Sistema de caché para evitar carga redundante de texturas duplicadas
- **Soporte de transparencia:** Habilitación de blending (GL_BLEND) con función GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
- **Compatibilidad completa:** Todos los shaders implementados son mutuamente compatibles

---

## TÉCNICAS DE RENDERIZADO IMPLEMENTADAS

### Fragment Shaders - Técnicas Utilizadas

1. **Rainbow:** Conversión de espacio de color HSV a RGB, generación de patrones espaciales no homogéneos
2. **Ghost:** Implementación de efecto Fresnel, transparencia variable basada en ángulo de visión, color espectral
3. **Chromatic Aberration:** Separación de canales RGB, sampling con offset espacial
4. **Hologram:** Generación procedural de scanlines, modulación sinusoidal de intensidad
5. **X-Ray:** Efecto Fresnel inverso, detección y resaltado de bordes geométricos

### Vertex Shaders - Técnicas Utilizadas

1. **Twist:** Aplicación de matrices de rotación 3D, transformación progresiva basada en coordenada Y
2. **Explode:** Desplazamiento por vectores normales, introducción de variación basada en posición espacial
3. **Ghost Distortion:** Ondas sinusoidales en múltiples ejes, combinación de frecuencias diferenciadas
4. **Ripple:** Generación de ondas radiales desde punto central, propagación temporal
5. **Spike:** Extrusión basada en vectores normales, animación de crecimiento temporal

---

## INFORMACIÓN DEL LABORATORIO

### Distribución de Puntuación

**Shaders Requeridos (6 shaders):** 20 puntos cada uno = 120 puntos totales
- Rainbow (Fragment Shader)
- Ghost (Fragment Shader)
- Chromatic Aberration (Fragment Shader)
- Twist (Vertex Shader)
- Explode (Vertex Shader)
- Ghost Distortion (Vertex Shader)

**Shaders Adicionales (5 shaders):** 10 puntos cada uno = 50 puntos adicionales
- Hologram (Fragment Shader)
- X-Ray (Fragment Shader)
- Ripple (Vertex Shader)
- Spike (Vertex Shader)
- Water (Vertex Shader, mejorado)

### Requisitos Técnicos Cumplidos

- Compatibilidad total entre todos los shaders implementados
- Consistencia en inputs y outputs (position, normal, texCoords)
- Documentación técnica completa
- Código fuente comentado
- Sistema de control intuitivo
- Calidad visual de los efectos implementados

---

## INSTRUCCIONES DE EJECUCIÓN

### Requisitos del Sistema

```
Python 3.12 o superior
PyOpenGL 3.1.10
PyGLM 2.8.2
pygame 2.6.1
numpy 2.3.4
```

### Instalación de Dependencias

```bash
# Activar entorno virtual
source venv/bin/activate

# Instalación de paquetes necesarios
pip install PyOpenGL PyGLM pygame numpy
```

### Ejecución del Programa

```bash
python3 main.py
```

---

## DOCUMENTACIÓN ADICIONAL

La siguiente documentación complementaria está disponible:

- `LAB_SHADERS_README.md` - Documentación técnica detallada de cada shader implementado
- `QUICK_REFERENCE.md` - Guía de referencia rápida de controles y combinaciones
- `MATERIAL_LOADING.md` - Documentación del sistema de carga de materiales y texturas
- `USAGE_GUIDE.md` - Guía detallada de uso del sistema de shaders

---

## NOTAS DE IMPLEMENTACIÓN

### Características Destacadas del Sistema

1. **Sistema de materiales automático:** El modelo de ejemplo (Giant Worm Creature) carga automáticamente 2 texturas diferentes correspondientes a sus materiales definidos (Worm_Color.jpg para material 'blinn1SG', Teeth_Color.jpg para material 'blinn2SG')

2. **Compatibilidad universal de shaders:** La arquitectura permite cambiar cualquier vertex shader con cualquier fragment shader sin incompatibilidades

3. **Control en tiempo real:** Todos los parámetros de los shaders son ajustables en tiempo real sin necesidad de recargar el programa

4. **Optimización de recursos:** Implementación de cache de texturas para prevenir cargas duplicadas y sistema de submeshes para renderizado eficiente por material

---

## REFERENCIAS

Para información adicional sobre el funcionamiento interno, consulte los archivos de documentación complementaria listados anteriormente o examine el código fuente que incluye comentarios explicativos detallados.
