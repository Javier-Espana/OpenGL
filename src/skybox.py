import numpy as np
import glm
from OpenGL.GL import * 
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame


# Skybox vertex shader - version 330 para compatibilidad
skybox_vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 position;

uniform mat4 view;
uniform mat4 projection;

out vec3 cubeTexCoords;

void main()
{
    cubeTexCoords = position;
    // Remover la translación de la view matrix
    mat4 rotView = mat4(mat3(view));
    vec4 pos = projection * rotView * vec4(position, 1.0);
    // Forzar z=w para que el skybox esté siempre en el far plane
    gl_Position = pos.xyww;
}

'''


skybox_fragment_shader = '''
#version 330 core

in vec3 cubeTexCoords;

uniform samplerCube cubemapTexture;

out vec4 outColor;

void main()
{
    outColor = texture(cubemapTexture, cubeTexCoords);
}

'''


class Skybox(object):
	def __init__(self, textureList):
		self.cameraRef = None
		
		# Vértices del cubo para el skybox (optimizado con un solo cubo)
		skyboxVertices = [
			# Posiciones (x, y, z)
			-1.0,  1.0, -1.0,
			-1.0, -1.0, -1.0,
			 1.0, -1.0, -1.0,
			 1.0, -1.0, -1.0,
			 1.0,  1.0, -1.0,
			-1.0,  1.0, -1.0,

			-1.0, -1.0,  1.0,
			-1.0, -1.0, -1.0,
			-1.0,  1.0, -1.0,
			-1.0,  1.0, -1.0,
			-1.0,  1.0,  1.0,
			-1.0, -1.0,  1.0,

			 1.0, -1.0, -1.0,
			 1.0, -1.0,  1.0,
			 1.0,  1.0,  1.0,
			 1.0,  1.0,  1.0,
			 1.0,  1.0, -1.0,
			 1.0, -1.0, -1.0,

			-1.0, -1.0,  1.0,
			-1.0,  1.0,  1.0,
			 1.0,  1.0,  1.0,
			 1.0,  1.0,  1.0,
			 1.0, -1.0,  1.0,
			-1.0, -1.0,  1.0,

			-1.0,  1.0, -1.0,
			 1.0,  1.0, -1.0,
			 1.0,  1.0,  1.0,
			 1.0,  1.0,  1.0,
			-1.0,  1.0,  1.0,
			-1.0,  1.0, -1.0,

			-1.0, -1.0, -1.0,
			-1.0, -1.0,  1.0,
			 1.0, -1.0, -1.0,
			 1.0, -1.0, -1.0,
			-1.0, -1.0,  1.0,
			 1.0, -1.0,  1.0
		]
		
		# Convertir a numpy array
		self.vertexData = np.array(skyboxVertices, dtype=np.float32)
		self.vertexCount = 36
		
		# Crear VAO y VBO
		self.VAO = glGenVertexArrays(1)
		self.VBO = glGenBuffers(1)
		
		glBindVertexArray(self.VAO)
		glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
		glBufferData(GL_ARRAY_BUFFER, self.vertexData.nbytes, self.vertexData, GL_STATIC_DRAW)
		
		# Configurar atributos de vértices
		glEnableVertexAttribArray(0)
		glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))
		
		glBindVertexArray(0)
		
		# Compilar shaders
		self.shaderProgram = compileProgram(
			compileShader(skybox_vertex_shader, GL_VERTEX_SHADER),
			compileShader(skybox_fragment_shader, GL_FRAGMENT_SHADER)
		)
		
		# Crear y cargar cubemap texture
		self.cubemapTexture = self._loadCubemap(textureList)
		

	def _loadCubemap(self, faces):
		"""Carga las 6 caras del cubemap"""
		textureID = glGenTextures(1)
		glBindTexture(GL_TEXTURE_CUBE_MAP, textureID)
		
		# Cargar cada cara del cubemap
		for i, facePath in enumerate(faces):
			try:
				image = pygame.image.load(facePath)
				imageData = pygame.image.tostring(image, "RGB", False)
				width = image.get_width()
				height = image.get_height()
				
				glTexImage2D(
					GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
					0,
					GL_RGB,
					width,
					height,
					0,
					GL_RGB,
					GL_UNSIGNED_BYTE,
					imageData
				)
			except Exception as e:
				print(f"Error loading skybox texture {facePath}: {e}")
		
		# Configurar parámetros del cubemap
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
		
		return textureID
		

	def Render(self):
		"""Renderiza el skybox"""
		# Deshabilitar escritura en depth buffer
		glDepthFunc(GL_LEQUAL)
		glDepthMask(GL_FALSE)
		
		glUseProgram(self.shaderProgram)
		
		# Pasar matrices de cámara
		if self.cameraRef is not None:
			glUniformMatrix4fv(
				glGetUniformLocation(self.shaderProgram, "view"),
				1, GL_FALSE, glm.value_ptr(self.cameraRef.viewMatrix)
			)
			glUniformMatrix4fv(
				glGetUniformLocation(self.shaderProgram, "projection"),
				1, GL_FALSE, glm.value_ptr(self.cameraRef.projectionMatrix)
			)
		
		# Bind VAO y texture
		glBindVertexArray(self.VAO)
		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubemapTexture)
		glUniform1i(glGetUniformLocation(self.shaderProgram, "cubemapTexture"), 0)
		
		# Dibujar skybox
		glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)
		
		# Restaurar estado
		glBindVertexArray(0)
		glDepthMask(GL_TRUE)
		glDepthFunc(GL_LESS)
