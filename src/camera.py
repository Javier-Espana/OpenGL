import glm
from math import sin, cos, radians, pi

class Camera(object):
	def __init__(self, width, height):

		self.screenWidth = width
		self.screenHeight = height
		
		self.position = glm.vec3(0,0,0)

		# Angulos de Euler
		self.rotation = glm.vec3(0,0,0)

		self.viewMatrix = None

		self.CreateProjectionMatrix(60, 0.1, 1000)

		self.usingLookAt = False
		
		# Sistema de cámara orbital
		self.orbitTarget = glm.vec3(0, 0, 0)  # Centro al que mira
		self.orbitRadius = 5.0  # Distancia del objetivo
		self.orbitAngleH = 0.0  # Ángulo horizontal (azimut)
		self.orbitAngleV = 0.0  # Ángulo vertical (elevación)
		self.orbitMode = False  # Si está en modo orbital
		
		# Límites de la cámara orbital
		self.minRadius = 1.0
		self.maxRadius = 50.0
		self.minElevation = -85.0  # grados
		self.maxElevation = 85.0   # grados


	def Update(self):
		# M = T * R
		# R = pitchMat * yawMat * rollMat

		if self.orbitMode:
			# Modo orbital: calcular posición basada en ángulos y radio
			self.UpdateOrbitalPosition()
			self.viewMatrix = glm.lookAt(self.position, self.orbitTarget, glm.vec3(0, 1, 0))
		elif not self.usingLookAt:
			identity = glm.mat4(1)

			translateMat = glm.translate(identity, self.position)

			pitchMat = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
			yawMat =   glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
			rollMat =  glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))

			rotationMat = pitchMat * yawMat * rollMat

			camMat = translateMat * rotationMat

			self.viewMatrix = glm.inverse(camMat)

		self.usingLookAt = False


	def CreateProjectionMatrix(self, fov, nearPlane, farPlane):
		self.projectionMatrix = glm.perspective( glm.radians(fov), self.screenWidth / self.screenHeight, nearPlane, farPlane)


	def LookAt(self, center):
		self.usingLookAt = True
		self.viewMatrix = glm.lookAt(self.position, center, glm.vec3(0,1,0) )


	def Orbit(self, center, distance, angle):
		self.position.x = center.x + sin(radians(angle) ) * distance
		self.position.z = center.z + cos(radians(angle) ) * distance


	def SetOrbitMode(self, enabled, target=None):
		"""Activa/desactiva el modo orbital de la cámara"""
		self.orbitMode = enabled
		if target is not None:
			self.orbitTarget = target
	
	
	def UpdateOrbitalPosition(self):
		"""Actualiza la posición de la cámara en modo orbital basado en ángulos"""
		# Convertir ángulos a radianes
		angleH = radians(self.orbitAngleH)
		angleV = radians(self.orbitAngleV)
		
		# Calcular posición en coordenadas esféricas
		x = self.orbitRadius * cos(angleV) * sin(angleH)
		y = self.orbitRadius * sin(angleV)
		z = self.orbitRadius * cos(angleV) * cos(angleH)
		
		# Posición final relativa al target
		self.position = self.orbitTarget + glm.vec3(x, y, z)
	
	
	def RotateOrbitHorizontal(self, delta):
		"""Rota la cámara horizontalmente alrededor del target"""
		if self.orbitMode:
			self.orbitAngleH += delta
			# Mantener entre 0-360 grados
			self.orbitAngleH = self.orbitAngleH % 360.0
	
	
	def RotateOrbitVertical(self, delta):
		"""Rota la cámara verticalmente alrededor del target con límites"""
		if self.orbitMode:
			self.orbitAngleV += delta
			# Aplicar límites de elevación
			self.orbitAngleV = max(self.minElevation, min(self.maxElevation, self.orbitAngleV))
	
	
	def ZoomOrbit(self, delta):
		"""Acerca o aleja la cámara del target con límites"""
		if self.orbitMode:
			self.orbitRadius += delta
			# Aplicar límites de distancia
			self.orbitRadius = max(self.minRadius, min(self.maxRadius, self.orbitRadius))
