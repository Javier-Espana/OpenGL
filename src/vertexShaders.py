

# GLSL - Vertex Shaders

vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;


void main()
{
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(inPosition, 1.0);

    fragPosition = modelMatrix * vec4(inPosition, 1.0);

    fragNormal = normalize( vec3(modelMatrix * vec4(inNormals, 0.0)));

    fragTexCoords = inTexCoords;
}

'''


fat_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float value;


void main()
{
    fragPosition = modelMatrix * vec4(inPosition + inNormals * value, 1.0);

    gl_Position = projectionMatrix * viewMatrix * fragPosition;

    fragNormal = normalize( vec3(modelMatrix * vec4(inNormals, 0.0)));

    fragTexCoords = inTexCoords;
}

'''


water_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float time;
uniform float value;


void main()
{
    float displacement = sin(time + inPosition.x + inPosition.z) * value;
    fragPosition = modelMatrix * vec4(inPosition + vec3(0,displacement, 0)  , 1.0);

    gl_Position = projectionMatrix * viewMatrix * fragPosition;

    fragNormal = normalize( vec3(modelMatrix * vec4(inNormals, 0.0)));

    fragTexCoords = inTexCoords;
}

'''


twist_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float time;
uniform float value;

void main()
{
    // Calcular ángulo de rotación basado en la altura (Y)
    float angle = inPosition.y * value * 2.0 + time * 0.5;
    
    // Matrices de rotación en Y
    float cosA = cos(angle);
    float sinA = sin(angle);
    
    // Aplicar rotación en el eje Y (twist)
    vec3 twisted = vec3(
        inPosition.x * cosA - inPosition.z * sinA,
        inPosition.y,
        inPosition.x * sinA + inPosition.z * cosA
    );
    
    // También rotar las normales
    vec3 twistedNormal = vec3(
        inNormals.x * cosA - inNormals.z * sinA,
        inNormals.y,
        inNormals.x * sinA + inNormals.z * cosA
    );
    
    fragPosition = modelMatrix * vec4(twisted, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    
    fragNormal = normalize(vec3(modelMatrix * vec4(twistedNormal, 0.0)));
    fragTexCoords = inTexCoords;
}

'''


explode_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float time;
uniform float value;

void main()
{
    // Desplazar vértices a lo largo de la normal
    float pulse = sin(time * 2.0) * 0.5 + 0.5;
    float explosion = value * pulse;
    
    // Añadir variación basada en posición
    float variation = sin(inPosition.x * 10.0) * cos(inPosition.y * 10.0) * sin(inPosition.z * 10.0);
    variation = variation * 0.3 + 0.7;
    
    vec3 exploded = inPosition + inNormals * explosion * variation;
    
    fragPosition = modelMatrix * vec4(exploded, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    
    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}

'''


ghost_distortion_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float time;
uniform float value;

void main()
{
    // Distorsión fantasmal con múltiples ondas
    float wave1 = sin(inPosition.y * 3.0 + time * 2.0) * value * 0.3;
    float wave2 = cos(inPosition.x * 4.0 + time * 1.5) * value * 0.2;
    float wave3 = sin(inPosition.z * 2.0 + time * 1.8) * value * 0.25;
    
    vec3 distortion = vec3(
        wave2 + wave3 * 0.5,
        wave1,
        wave1 * 0.5 + wave2
    );
    
    // Efecto de "flotación"
    float floating = sin(time * 1.5 + inPosition.x * 0.5) * value * 0.4;
    distortion.y += floating;
    
    // Añadir perturbación a las normales
    vec3 perturbedNormal = inNormals + vec3(
        sin(time * 3.0 + inPosition.y) * 0.1,
        cos(time * 2.5 + inPosition.x) * 0.1,
        sin(time * 2.0 + inPosition.z) * 0.1
    );
    
    vec3 ghostPos = inPosition + distortion;
    
    fragPosition = modelMatrix * vec4(ghostPos, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    
    fragNormal = normalize(vec3(modelMatrix * vec4(perturbedNormal, 0.0)));
    fragTexCoords = inTexCoords;
}

'''


ripple_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float time;
uniform float value;

void main()
{
    // Ondas concéntricas desde el centro
    vec3 center = vec3(0.0, 0.0, 0.0);
    float dist = distance(inPosition.xz, center.xz);
    
    // Crear ondas que se expanden
    float wave = sin(dist * 5.0 - time * 3.0) * value * 0.5;
    
    // Atenuación con la distancia
    float attenuation = 1.0 / (1.0 + dist * 0.5);
    wave *= attenuation;
    
    vec3 rippled = inPosition + inNormals * wave;
    
    fragPosition = modelMatrix * vec4(rippled, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    
    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}

'''


spike_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float time;
uniform float value;

void main()
{
    // Crear picos que crecen desde la superficie
    float spike = max(0.0, sin(inPosition.x * 15.0 + time) * 
                          cos(inPosition.y * 12.0 + time * 0.8) * 
                          sin(inPosition.z * 18.0 + time * 1.2));
    
    spike = pow(spike, 3.0);
    
    vec3 spiked = inPosition + inNormals * spike * value;
    
    fragPosition = modelMatrix * vec4(spiked, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    
    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}

'''