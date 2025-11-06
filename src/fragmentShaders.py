# GLSL - Fragment Shaders

fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max( 0 , dot(fragNormal, lightDir)) + ambientLight;

    fragColor = texture(tex0, fragTexCoords) * intensity;
}

'''


toon_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max( 0 , dot(fragNormal, lightDir)) + ambientLight;

    if (intensity < 0.33)
        intensity = 0.2;
    else if (intensity < 0.66)
        intensity = 0.6;
    else
        intensity = 1.0;

    fragColor = texture(tex0, fragTexCoords) * intensity;
}

'''


negative_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;

void main()
{
    fragColor = 1 - texture(tex0, fragTexCoords);
}

'''


magma_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform sampler2D tex1;

uniform vec3 pointLight;
uniform float ambientLight;

uniform float time;

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max( 0 , dot(fragNormal, lightDir)) + ambientLight;

    fragColor = texture(tex0, fragTexCoords) * intensity;
    fragColor += texture(tex1, fragTexCoords) * ((sin(time) + 1) / 2);
}

'''


rainbow_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float time;

// Función para convertir HSV a RGB
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main()
{
    // Iluminación base
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(fragNormal, lightDir)) + ambientLight;
    
    // Textura base
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Crear patrón de bandas de colores usando posición del modelo
    float pattern = sin(fragPosition.x * 3.0 + time * 2.0) * 
                   cos(fragPosition.y * 2.0 + time * 1.5) * 
                   sin(fragPosition.z * 2.5 + time * 1.8);
    
    // Normalizar patrón a [0, 1]
    pattern = (pattern + 1.0) * 0.5;
    
    // Crear diferentes zonas con colores diferentes
    float hue = mod(pattern * 6.0 + time * 0.5, 1.0);
    
    // Generar color rainbow
    vec3 rainbowColor = hsv2rgb(vec3(hue, 0.8, 1.0));
    
    // Mezclar textura con color rainbow de forma no homogénea
    float mixFactor = 0.6 + 0.4 * sin(pattern * 10.0 + time);
    
    vec3 finalColor = mix(texColor.rgb, rainbowColor, mixFactor) * intensity;
    
    fragColor = vec4(finalColor, texColor.a);
}

'''


ghost_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float time;
uniform float value;

void main()
{
    // Color celeste espectral
    vec3 ghostColor = vec3(0.4, 0.8, 1.0);
    
    // Iluminación suave
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(fragNormal, lightDir)) * 0.3 + ambientLight;
    
    // Textura base con muy poca influencia
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Efecto de bordes brillantes (Fresnel)
    vec3 viewDir = normalize(-fragPosition.xyz);
    float fresnel = 1.0 - max(0.0, dot(viewDir, fragNormal));
    fresnel = pow(fresnel, 3.0);
    
    // Ondulación de transparencia
    float alphaWave = sin(fragPosition.y * 5.0 + time * 2.0) * 
                     cos(fragPosition.x * 4.0 + time * 1.5);
    alphaWave = (alphaWave + 1.0) * 0.5;
    
    // Transparencia base (semi-transparente)
    float baseAlpha = 0.3 + value * 0.3;
    float alpha = baseAlpha + alphaWave * 0.2 + fresnel * 0.3;
    alpha = clamp(alpha, 0.2, 0.7);
    
    // Mezclar textura con color espectral
    vec3 finalColor = mix(texColor.rgb, ghostColor, 0.7);
    finalColor = finalColor * (intensity + 0.5);
    
    // Añadir brillo en los bordes
    finalColor += ghostColor * fresnel * 0.5;
    
    // Pulsación de brillo
    float pulse = sin(time * 3.0) * 0.15 + 0.85;
    finalColor *= pulse;
    
    fragColor = vec4(finalColor, alpha);
}

'''


chromatic_aberration_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float time;
uniform float value;

void main()
{
    // Iluminación
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(fragNormal, lightDir)) + ambientLight;
    
    // Aberración cromática - separar los canales RGB
    vec2 center = vec2(0.5, 0.5);
    vec2 offset = fragTexCoords - center;
    float dist = length(offset);
    
    // Offset dinámico basado en distancia y tiempo
    float aberration = value * 0.01 + sin(time) * 0.005;
    
    // Muestrear cada canal con offset diferente
    float r = texture(tex0, fragTexCoords + offset * aberration * 1.0).r;
    float g = texture(tex0, fragTexCoords + offset * aberration * 0.5).g;
    float b = texture(tex0, fragTexCoords - offset * aberration * 1.0).b;
    
    vec3 finalColor = vec3(r, g, b) * intensity;
    
    // Añadir viñeta sutil
    float vignette = 1.0 - dist * 0.5;
    finalColor *= vignette;
    
    // Glitch ocasional
    float glitch = step(0.98, sin(time * 50.0 + fragPosition.x * 100.0));
    finalColor += vec3(glitch * 0.3);
    
    fragColor = vec4(finalColor, 1.0);
}

'''


hologram_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float time;
uniform float value;

void main()
{
    // Color holográfico cyan/azul
    vec3 holoColor = vec3(0.2, 0.8, 1.0);
    
    // Líneas de escaneo horizontales
    float scanline = sin(fragPosition.y * 50.0 - time * 10.0);
    scanline = smoothstep(0.3, 0.7, scanline);
    
    // Efecto Fresnel (bordes brillantes)
    vec3 viewDir = normalize(-fragPosition.xyz);
    float fresnel = 1.0 - max(0.0, dot(viewDir, fragNormal));
    fresnel = pow(fresnel, 2.0);
    
    // Textura base
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Interferencia/ruido
    float noise = fract(sin(dot(fragTexCoords * time * 0.1, vec2(12.9898, 78.233))) * 43758.5453);
    noise = noise * 0.1;
    
    // Combinar efectos
    vec3 finalColor = mix(texColor.rgb, holoColor, 0.7);
    finalColor *= scanline * 0.5 + 0.5;
    finalColor += holoColor * fresnel * 0.8;
    finalColor += noise;
    
    // Pulsación
    float pulse = sin(time * 2.0) * 0.2 + 0.8;
    finalColor *= pulse;
    
    // Transparencia variable
    float alpha = 0.4 + fresnel * 0.3 + value * 0.2;
    alpha = clamp(alpha, 0.3, 0.8);
    
    fragColor = vec4(finalColor, alpha);
}

'''


xray_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float time;
uniform float value;

void main()
{
    // Color verde/azul para rayos X
    vec3 xrayColor = vec3(0.1, 0.9, 0.7);
    
    // Detección de bordes usando normal
    vec3 viewDir = normalize(-fragPosition.xyz);
    float edge = 1.0 - abs(dot(viewDir, fragNormal));
    edge = pow(edge, 2.0);
    
    // Textura como "estructura interna"
    vec4 texColor = texture(tex0, fragTexCoords);
    float structure = (texColor.r + texColor.g + texColor.b) / 3.0;
    
    // Crear efecto de profundidad
    float depth = length(fragPosition.xyz) * 0.05;
    depth = 1.0 - clamp(depth, 0.0, 1.0);
    
    // Pulsación
    float pulse = sin(time * 3.0) * 0.3 + 0.7;
    
    // Combinar efectos
    vec3 finalColor = xrayColor * structure * depth;
    finalColor += xrayColor * edge * 2.0;
    finalColor *= pulse;
    
    // Semi-transparente
    float alpha = 0.5 + edge * 0.3 + value * 0.2;
    alpha = clamp(alpha, 0.3, 0.9);
    
    fragColor = vec4(finalColor, alpha);
}

'''




