


vertex_postProcess = '''
#version 430

out vec2 fragTexCoords;

const vec2 pos[4] = vec2[](
	vec2(-1.0, -1.0),
	vec2( 1.0, -1.0),
	vec2( 1.0,  1.0),
	vec2(-1.0,  1.0)
);

void main()
{
	gl_Position = vec4( pos[gl_VertexID], 0.0, 1.0);
	fragTexCoords = ( pos[gl_VertexID] + 1 ) / 2;
}

'''

none_postProcess = '''
#version 430

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;

out vec4 fragColor;

void main(){
	fragColor = texture(frameBuffer, fragTexCoords);
}

'''

grayScale_postProcess = '''
#version 430

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;

out vec4 fragColor;

void main(){
	vec4 color = texture(frameBuffer, fragTexCoords);
	float gray = dot(color.rgb, vec3(0.3, 0.6, 0.1) );
	fragColor = vec4(gray, gray, gray, 1.0);
}

'''

negative_postProcess = '''
#version 430

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;

out vec4 fragColor;

void main(){
	fragColor = 1 - texture(frameBuffer, fragTexCoords);
}

'''

hurt_postProcess = '''
#version 430

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform float time;

out vec4 fragColor;

void main(){
	vec3 color = texture(frameBuffer, fragTexCoords).rgb;

	vec2 centered = fragTexCoords * 2.0 - 1.0;
	float dist = length(centered);
	float vignetteStrength = smoothstep(sin(time * 5) * 0.1 + 0.6, 1.0, dist) * 0.5;
	vec3 redTint = vec3(1.0, 0.0, 0.0);

	color = mix(color, redTint, vignetteStrength);

	fragColor = vec4(color, 1.0);

}

'''

depth_postProcess = '''
#version 430

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform sampler2D depthTexture;

out vec4 fragColor;

void main(){
	float depth = texture(depthTexture, fragTexCoords).r;

	depth = 1 - depth;
	depth = clamp(depth, 0.0, 0.1) * 10;

	fragColor = vec4(vec3(depth), 1.0);
}

'''

fog_postProcess = '''
#version 430

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform sampler2D depthTexture;

out vec4 fragColor;

void main(){
	vec3 color = texture(frameBuffer, fragTexCoords).rgb;
	float depth = texture(depthTexture, fragTexCoords).r;

	depth = 1 - depth;
	depth = clamp(depth, 0.0, 0.1) * 10;

	vec3 fogColor = vec3(0.5,0.5,0.5);
	color = mix(fogColor, color, depth);

	fragColor = vec4(color, 1.0);
}

'''

dof_postProcess = '''
#version 430 core

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform sampler2D depthTexture;

out vec4 fragColor;

void main() {
    vec2 texelSize = 1.0 / vec2(textureSize(frameBuffer,0));
    float depth = texture(depthTexture, fragTexCoords).r;
    depth = clamp(depth,0.0, 0.1) * 10;

    vec3 color = vec3(0.0);
    int samples = 0;
    for(int x=-1;x<=1;x++){
        for(int y=-1;y<=1;y++){
            vec2 offset = vec2(x,y) * texelSize * depth * 2;
            color += texture(frameBuffer, fragTexCoords+offset).rgb;
            samples++;
        }
    }
    color /= float(samples);

    fragColor = vec4(color, 1.0);
}
'''

edgeDetection_postProcess = '''
#version 430 core

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform sampler2D depthTexture;

out vec4 fragColor;

float depthAt(vec2 uv) { return texture(depthTexture, uv).r; }

void main()
{
    vec2 texelSize = 5 / vec2(textureSize(depthTexture,0));
    float depthC = texture(depthTexture, fragTexCoords).r;
    float depthL = texture(depthTexture, fragTexCoords + vec2(-texelSize.x,0)).r;
    float depthR = texture(depthTexture, fragTexCoords + vec2(texelSize.x,0)).r;
    float depthU = texture(depthTexture, fragTexCoords + vec2(0,texelSize.y)).r;
    float depthD = texture(depthTexture, fragTexCoords + vec2(0,-texelSize.y)).r;

    float edge = abs(depthL-depthR) + abs(depthU-depthD);
    edge *= 5.0;
    fragColor = vec4(vec3(edge),1.0);
}
'''

outline_postProcess = '''
#version 430 core

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform sampler2D depthTexture;

out vec4 fragColor;

void main() {
    vec2 texelSize = 3.0 / vec2(textureSize(depthTexture,0));
    float depthC = texture(depthTexture, fragTexCoords).r;
    float depthL = texture(depthTexture, fragTexCoords + vec2(-texelSize.x,0)).r;
    float depthR = texture(depthTexture, fragTexCoords + vec2(texelSize.x,0)).r;
    float depthU = texture(depthTexture, fragTexCoords + vec2(0,texelSize.y)).r;
    float depthD = texture(depthTexture, fragTexCoords + vec2(0,-texelSize.y)).r;

    float edge = abs(depthL-depthR) + abs(depthU-depthD);
    edge *= 5.0;
    if(edge > 0.01)
    {
        fragColor = vec4(0.0,0.0,0.0,1.0);
    }
    else
    {
        fragColor = texture(frameBuffer, fragTexCoords);
    }
}
'''


# Post-procesamiento de ambiente natural - TINTE VERDE MÁGICO dramático
nature_ambient_postProcess = '''
#version 430

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform float time;

out vec4 fragColor;

void main() {
    vec4 color = texture(frameBuffer, fragTexCoords);
    
    // Añadir tinte verde INTENSO para ambiente mágico/fantástico
    color.g *= 1.4;
    color.r *= 0.85;
    color.b *= 0.9;
    
    // Viñeta FUERTE
    vec2 uv = fragTexCoords * 2.0 - 1.0;
    float vignette = 1.0 - dot(uv, uv) * 0.5;
    vignette = pow(vignette, 0.8);
    color.rgb *= vignette;
    
    // Bloom EXTREMO en áreas brillantes
    float brightness = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    if(brightness > 0.5) {
        color.rgb *= (1.0 + (brightness - 0.5) * 1.0);
    }
    
    // Añadir brillo ambiental verde
    color.rgb += vec3(0.05, 0.15, 0.02);
    
    fragColor = color;
}
'''


# Post-procesamiento de bruma - NIEBLA AZUL DENSA
depth_fog_postProcess = '''
#version 430

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform sampler2D depthTexture;
uniform float time;

out vec4 fragColor;

void main() {
    vec4 color = texture(frameBuffer, fragTexCoords);
    float depth = texture(depthTexture, fragTexCoords).r;
    
    // Convertir profundidad a distancia - MÁS AGRESIVO
    depth = pow(depth, 4.0);
    
    // Color de la bruma AZUL INTENSO
    vec3 fogColor = vec3(0.4, 0.5, 0.8);
    
    // Mezclar con fog MUCHO más fuerte
    float fogAmount = clamp(depth * 1.5, 0.0, 0.9);
    color.rgb = mix(color.rgb, fogColor, fogAmount);
    
    // Añadir tinte azul general
    color.b *= 1.2;
    
    fragColor = color;
}
'''


# Post-procesamiento de día soleado - SATURACIÓN EXTREMA y BRILLO
sunny_day_postProcess = '''
#version 430

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform float time;

out vec4 fragColor;

void main() {
    vec4 color = texture(frameBuffer, fragTexCoords);
    
    // Aumentar brillo DRAMÁTICO
    color.rgb *= 1.5;
    
    // Aumentar saturación EXTREMA
    float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    color.rgb = mix(vec3(gray), color.rgb, 2.0);
    
    // Aumentar contraste FUERTE
    color.rgb = (color.rgb - 0.5) * 1.6 + 0.5;
    
    // Tinte amarillo cálido INTENSO
    color.r *= 1.2;
    color.g *= 1.15;
    color.b *= 0.85;
    
    // Brillo adicional en el centro
    vec2 center = fragTexCoords - 0.5;
    float centerGlow = 1.0 - length(center) * 0.8;
    color.rgb *= (0.8 + centerGlow * 0.4);
    
    fragColor = color;
}
'''


# Post-procesamiento de atardecer - NARANJA/ROJO ARDIENTE dramático
sunset_postProcess = '''
#version 430

in vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform float time;

out vec4 fragColor;

void main() {
    vec4 color = texture(frameBuffer, fragTexCoords);
    
    // Añadir tonos naranjas/rojos EXTREMOS
    color.r *= 1.8;
    color.g *= 1.1;
    color.b *= 0.5;
    
    // Viñeta MUY pronunciada - casi negra en los bordes
    vec2 uv = fragTexCoords * 2.0 - 1.0;
    float vignette = 1.0 - dot(uv, uv) * 0.7;
    vignette = pow(vignette, 0.5);
    color.rgb *= vignette;
    
    // Aumentar calidez EXTREMA en áreas brillantes
    float brightness = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    if(brightness > 0.3) {
        color.r *= (1.0 + (brightness - 0.3) * 0.8);
        color.g *= (1.0 + (brightness - 0.3) * 0.4);
    }
    
    // Añadir brillo dorado
    color.rgb += vec3(0.15, 0.08, 0.0) * brightness;
    
    fragColor = color;
}
'''
