# GLSL - Fragment Shaders

fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;

// Lighting uniforms
uniform float ambientIntensity;
uniform vec3 ambientColor;

// Directional lights (max 4)
uniform int numDirLights;
uniform vec3 dirLightDirections[4];
uniform vec3 dirLightColors[4];
uniform float dirLightIntensities[4];

// Point lights (max 4)
uniform int numPointLights;
uniform vec3 pointLightPositions[4];
uniform vec3 pointLightColors[4];
uniform float pointLightIntensities[4];

void main()
{
    vec3 normal = normalize(fragNormal);
    vec3 finalColor = vec3(0.0);
    
    // Ambient light
    finalColor += ambientColor * ambientIntensity;
    
    // Directional lights
    for(int i = 0; i < numDirLights && i < 4; i++)
    {
        vec3 lightDir = normalize(-dirLightDirections[i]);
        float diff = max(dot(normal, lightDir), 0.0);
        finalColor += dirLightColors[i] * diff * dirLightIntensities[i];
    }
    
    // Point lights
    for(int i = 0; i < numPointLights && i < 4; i++)
    {
        vec3 lightDir = normalize(pointLightPositions[i] - fragPosition.xyz);
        float diff = max(dot(normal, lightDir), 0.0);
        
        // Attenuation
        float distance = length(pointLightPositions[i] - fragPosition.xyz);
        float attenuation = 1.0 / (1.0 + 0.09 * distance + 0.032 * distance * distance);
        
        finalColor += pointLightColors[i] * diff * pointLightIntensities[i] * attenuation;
    }
    
    // Clamp to avoid over-brightness
    finalColor = min(finalColor, vec3(1.5));
    
    fragColor = texture(tex0, fragTexCoords) * vec4(finalColor, 1.0);
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
uniform vec3 sunDirection;
uniform vec3 sunColor;
uniform float sunIntensity;

void main()
{
    // Point light calculation
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float pointIntensity = max(0.0, dot(fragNormal, lightDir));
    
    // Directional sun light calculation
    vec3 sunDir = normalize(-sunDirection);
    float sunDiffuse = max(0.0, dot(fragNormal, sunDir));
    
    // Combine lighting
    float totalIntensity = ambientLight + pointIntensity * 0.3 + sunDiffuse * sunIntensity;
    
    // Toon shading quantization
    if (totalIntensity < 0.33)
        totalIntensity = 0.2;
    else if (totalIntensity < 0.66)
        totalIntensity = 0.6;
    else
        totalIntensity = 1.0;

    fragColor = texture(tex0, fragTexCoords) * totalIntensity;
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


# Shader temático para árboles - CORTEZA OSCURA con grietas profundas
bark_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;

// Luces
uniform vec3 ambientLightColor;
uniform float ambientLightIntensity;

#define MAX_DIR_LIGHTS 4
uniform int numDirLights;
uniform vec3 dirLightDirections[MAX_DIR_LIGHTS];
uniform vec3 dirLightColors[MAX_DIR_LIGHTS];
uniform float dirLightIntensities[MAX_DIR_LIGHTS];

#define MAX_POINT_LIGHTS 4
uniform int numPointLights;
uniform vec3 pointLightPositions[MAX_POINT_LIGHTS];
uniform vec3 pointLightColors[MAX_POINT_LIGHTS];
uniform float pointLightIntensities[MAX_POINT_LIGHTS];

uniform float time;
uniform float value;

void main()
{
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Oscurecer MUCHO la corteza para que se vea dramático
    vec3 barkColor = texColor.rgb * 0.4;
    
    // Añadir grietas profundas con noise procedural
    float crack = sin(fragTexCoords.y * 80.0 + fragTexCoords.x * 50.0);
    crack = pow(abs(crack), 4.0);
    barkColor *= (0.6 + crack * 0.4);
    
    // Tonos marrones INTENSOS
    barkColor.r *= 1.3;
    barkColor.g *= 0.9;
    barkColor.b *= 0.5;
    
    // Iluminación básica
    vec3 normal = normalize(fragNormal);
    vec3 lighting = ambientLightColor * ambientLightIntensity * 0.8;
    
    // Luces direccionales con contraste ALTO
    for(int i = 0; i < numDirLights && i < MAX_DIR_LIGHTS; i++) {
        vec3 lightDir = normalize(-dirLightDirections[i]);
        float diff = max(dot(normal, lightDir), 0.0);
        diff = pow(diff, 2.0); // Contraste más fuerte
        lighting += dirLightColors[i] * diff * dirLightIntensities[i];
    }
    
    // Luces puntuales
    for(int i = 0; i < numPointLights && i < MAX_POINT_LIGHTS; i++) {
        vec3 lightDir = normalize(pointLightPositions[i] - fragPosition.xyz);
        float distance = length(pointLightPositions[i] - fragPosition.xyz);
        float attenuation = 1.0 / (1.0 + 0.09 * distance + 0.032 * distance * distance);
        float diff = max(dot(normal, lightDir), 0.0);
        lighting += pointLightColors[i] * diff * pointLightIntensities[i] * attenuation;
    }
    
    vec3 finalColor = barkColor * lighting;
    fragColor = vec4(finalColor, texColor.a);
}

'''


# Shader temático para hojas - VERDE BRILLANTE con efecto de translucidez EXTREMO
foliage_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;

// Luces
uniform vec3 ambientLightColor;
uniform float ambientLightIntensity;

#define MAX_DIR_LIGHTS 4
uniform int numDirLights;
uniform vec3 dirLightDirections[MAX_DIR_LIGHTS];
uniform vec3 dirLightColors[MAX_DIR_LIGHTS];
uniform float dirLightIntensities[MAX_DIR_LIGHTS];

#define MAX_POINT_LIGHTS 4
uniform int numPointLights;
uniform vec3 pointLightPositions[MAX_POINT_LIGHTS];
uniform vec3 pointLightColors[MAX_POINT_LIGHTS];
uniform float pointLightIntensities[MAX_POINT_LIGHTS];

uniform float time;
uniform float value;

void main()
{
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Realzar el verde de forma EXTREMA - casi fosforescente
    vec3 leafColor = texColor.rgb;
    leafColor.g = min(leafColor.g * 2.0, 1.0);
    leafColor.r *= 0.5; // Menos rojo
    leafColor.b *= 0.7; // Menos azul
    
    // Añadir brillo verde intenso
    leafColor += vec3(0.1, 0.3, 0.05);
    
    // Iluminación
    vec3 normal = normalize(fragNormal);
    vec3 lighting = ambientLightColor * ambientLightIntensity;
    
    // Luces direccionales con subsurface scattering EXTREMO
    for(int i = 0; i < numDirLights && i < MAX_DIR_LIGHTS; i++) {
        vec3 lightDir = normalize(-dirLightDirections[i]);
        float frontLight = max(dot(normal, lightDir), 0.0);
        
        // Simular luz atravesando las hojas (backlight) MUCHO MÁS FUERTE
        float backLight = max(dot(-normal, lightDir), 0.0) * 1.5;
        
        lighting += dirLightColors[i] * (frontLight + backLight) * dirLightIntensities[i] * 1.3;
    }
    
    // Luces puntuales más intensas
    for(int i = 0; i < numPointLights && i < MAX_POINT_LIGHTS; i++) {
        vec3 lightDir = normalize(pointLightPositions[i] - fragPosition.xyz);
        float distance = length(pointLightPositions[i] - fragPosition.xyz);
        float attenuation = 1.0 / (1.0 + 0.09 * distance + 0.032 * distance * distance);
        float diff = max(dot(normal, lightDir), 0.0);
        lighting += pointLightColors[i] * diff * pointLightIntensities[i] * attenuation * 1.5;
    }
    
    vec3 finalColor = leafColor * lighting;
    
    // Añadir MUCHO brillo
    finalColor += vec3(0.15, 0.25, 0.1);
    
    fragColor = vec4(finalColor, texColor.a);
}

'''


# Shader temático para la casa/cottage - NARANJA/DORADO INTENSO cálido
cottage_warm_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;

// Luces
uniform vec3 ambientLightColor;
uniform float ambientLightIntensity;

#define MAX_DIR_LIGHTS 4
uniform int numDirLights;
uniform vec3 dirLightDirections[MAX_DIR_LIGHTS];
uniform vec3 dirLightColors[MAX_DIR_LIGHTS];
uniform float dirLightIntensities[MAX_DIR_LIGHTS];

#define MAX_POINT_LIGHTS 4
uniform int numPointLights;
uniform vec3 pointLightPositions[MAX_POINT_LIGHTS];
uniform vec3 pointLightColors[MAX_POINT_LIGHTS];
uniform float pointLightIntensities[MAX_POINT_LIGHTS];

uniform float time;
uniform float value;

void main()
{
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Añadir calidez EXTREMA - tonos naranjas/dorados
    vec3 warmColor = texColor.rgb;
    warmColor.r *= 1.6;  // MUCHO más rojo
    warmColor.g *= 1.2;  // Más verde (hace amarillo/naranja)
    warmColor.b *= 0.6;  // MUCHO menos azul
    
    // Iluminación
    vec3 normal = normalize(fragNormal);
    vec3 lighting = ambientLightColor * ambientLightIntensity * 1.2;
    
    // Luces direccionales
    for(int i = 0; i < numDirLights && i < MAX_DIR_LIGHTS; i++) {
        vec3 lightDir = normalize(-dirLightDirections[i]);
        float diff = max(dot(normal, lightDir), 0.0);
        lighting += dirLightColors[i] * diff * dirLightIntensities[i] * 1.2;
    }
    
    // Luces puntuales MUCHO más intensas para la cottage
    for(int i = 0; i < numPointLights && i < MAX_POINT_LIGHTS; i++) {
        vec3 lightDir = normalize(pointLightPositions[i] - fragPosition.xyz);
        float distance = length(pointLightPositions[i] - fragPosition.xyz);
        float attenuation = 1.0 / (1.0 + 0.05 * distance + 0.01 * distance * distance);
        float diff = max(dot(normal, lightDir), 0.0);
        lighting += pointLightColors[i] * diff * pointLightIntensities[i] * attenuation * 2.0;
    }
    
    vec3 finalColor = warmColor * lighting;
    
    // Añadir brillo cálido ambiental FUERTE
    finalColor += vec3(0.15, 0.1, 0.02);
    
    fragColor = vec4(finalColor, texColor.a);
}

'''


# Shader para la grama - VERDE NEÓN brillante y saturado
grass_vibrant_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;

// Luces
uniform vec3 ambientLightColor;
uniform float ambientLightIntensity;

#define MAX_DIR_LIGHTS 4
uniform int numDirLights;
uniform vec3 dirLightDirections[MAX_DIR_LIGHTS];
uniform vec3 dirLightColors[MAX_DIR_LIGHTS];
uniform float dirLightIntensities[MAX_DIR_LIGHTS];

#define MAX_POINT_LIGHTS 4
uniform int numPointLights;
uniform vec3 pointLightPositions[MAX_POINT_LIGHTS];
uniform vec3 pointLightColors[MAX_POINT_LIGHTS];
uniform float pointLightIntensities[MAX_POINT_LIGHTS];

uniform float time;
uniform float value;

void main()
{
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Realzar verde de la grama a nivel NEÓN
    vec3 grassColor = texColor.rgb;
    grassColor.g = min(grassColor.g * 2.5, 1.0);  // MUCHO verde
    grassColor.r *= 0.6;
    grassColor.b *= 0.8;
    
    // Añadir variación dramática para textura
    float variation = sin(fragTexCoords.x * 200.0) * cos(fragTexCoords.y * 200.0) * 0.15;
    grassColor *= (1.0 + variation);
    
    // Iluminación más brillante
    vec3 normal = normalize(fragNormal);
    vec3 lighting = ambientLightColor * ambientLightIntensity * 1.3;
    
    // Luces direccionales con más intensidad
    for(int i = 0; i < numDirLights && i < MAX_DIR_LIGHTS; i++) {
        vec3 lightDir = normalize(-dirLightDirections[i]);
        float diff = max(dot(normal, lightDir), 0.0);
        lighting += dirLightColors[i] * diff * dirLightIntensities[i] * 1.4;
    }
    
    // Luces puntuales
    for(int i = 0; i < numPointLights && i < MAX_POINT_LIGHTS; i++) {
        vec3 lightDir = normalize(pointLightPositions[i] - fragPosition.xyz);
        float distance = length(pointLightPositions[i] - fragPosition.xyz);
        float attenuation = 1.0 / (1.0 + 0.09 * distance + 0.032 * distance * distance);
        float diff = max(dot(normal, lightDir), 0.0);
        lighting += pointLightColors[i] * diff * pointLightIntensities[i] * attenuation;
    }
    
    vec3 finalColor = grassColor * lighting;
    
    // Añadir brillo de frescura INTENSO
    finalColor += vec3(0.1, 0.25, 0.05);
    
    fragColor = vec4(finalColor, texColor.a);
}

'''








