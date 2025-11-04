import pygame
import pygame.display
from pygame.locals import *

import glm

from src.gl import Renderer
from src.buffer import Buffer
from src.model import Model
from src.vertexShaders import *
from src.fragmentShaders import *
from src.postProcessingShaders import *

width = 960
height = 540

deltaTime = 0.0


screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()


rend = Renderer(screen)
rend.pointLight = glm.vec3(1,1,1)

currVertexShader = vertex_shader
currFragmentShader = fragment_shader

rend.SetShaders(currVertexShader, currFragmentShader)

rend.SetPostProcessingShaders(vertex_postProcess, none_postProcess)

skyboxTextures = ["skybox/right.jpg",
				  "skybox/left.jpg",
				  "skybox/top.jpg",
				  "skybox/bottom.jpg",
				  "skybox/front.jpg",
				  "skybox/back.jpg"]

rend.CreateSkybox(skyboxTextures)


# ===== CARGAR MÚLTIPLES MODELOS =====
WormModel = Model("models/Worm Models/Giant Worm Creature.obj")
WormModel.LoadMaterialsFromMtl()
WormModel.position.z = -15
WormModel.position.y = -3
WormModel.scale = glm.vec3(0.02,0.02,0.02)
WormModel.visible = True

# Cargar otros dos modelos (ajusta las rutas según tus modelos disponibles)
# Por ahora usaremos el mismo modelo pero con diferentes configuraciones
Model2 = Model("models/Worm Models/Giant Worm Creature.obj")
Model2.LoadMaterialsFromMtl()
Model2.position.z = -10
Model2.position.y = -2
Model2.scale = glm.vec3(0.015,0.015,0.015)
Model2.visible = False

Model3 = Model("models/Worm Models/Giant Worm Creature.obj")
Model3.LoadMaterialsFromMtl()
Model3.position.z = -8
Model3.position.y = -1
Model3.scale = glm.vec3(0.01,0.01,0.01)
Model3.visible = False

rend.scene.append(WormModel)
rend.scene.append(Model2)
rend.scene.append(Model3)

# Lista de modelos para facilitar el cambio
models = [WormModel, Model2, Model3]
currentModelIndex = 0

# Activar modo orbital de cámara
rend.camera.SetOrbitMode(True, glm.vec3(0, -2, -10))
rend.camera.orbitRadius = 10.0
rend.camera.orbitAngleH = 0.0
rend.camera.orbitAngleV = 20.0

postProcessIndex = 0

postProcesses = [none_postProcess,
				 grayScale_postProcess,
				 negative_postProcess,
				 hurt_postProcess,
				 depth_postProcess,
				 fog_postProcess,
				 dof_postProcess,
				 edgeDetection_postProcess,
				 outline_postProcess]

isRunning = True

while isRunning:

	deltaTime = clock.tick(60) / 1000

	rend.elapsedTime += deltaTime

	keys = pygame.key.get_pressed()
	mouseVel = pygame.mouse.get_rel()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			isRunning = False

		elif event.type == pygame.MOUSEBUTTONDOWN:
			if pygame.mouse.get_pressed()[2]:
				# Click derecho: cambiar de modelo
				currentModelIndex = (currentModelIndex + 1) % len(models)
				# Ocultar todos los modelos
				for model in models:
					model.visible = False
				# Mostrar solo el modelo actual
				models[currentModelIndex].visible = True

		elif event.type == pygame.MOUSEWHEEL:
			# Zoom con rueda del mouse
			rend.camera.ZoomOrbit(-event.y * 0.5)

		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_f:
				rend.ToggleFilledMode()

			if event.key == pygame.K_TAB:
				postProcessIndex += 1
				postProcessIndex %= len(postProcesses)
				rend.SetPostProcessingShaders(vertex_postProcess, postProcesses[postProcessIndex])

			# Cambio de modelo con teclas numéricas del pad
			if event.key == pygame.K_KP1:
				currentModelIndex = 0
				for model in models:
					model.visible = False
				models[currentModelIndex].visible = True

			if event.key == pygame.K_KP2:
				currentModelIndex = 1
				for model in models:
					model.visible = False
				models[currentModelIndex].visible = True

			if event.key == pygame.K_KP3:
				currentModelIndex = 2
				for model in models:
					model.visible = False
				models[currentModelIndex].visible = True

			# ===== FRAGMENT SHADERS (antiguos) =====
			if event.key == pygame.K_1:
				currFragmentShader = fragment_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_2:
				currFragmentShader = toon_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_3:
				currFragmentShader = negative_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_4:
				currFragmentShader = magma_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			# ===== FRAGMENT SHADERS NUEVOS =====
			if event.key == pygame.K_5:
				currFragmentShader = rainbow_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_6:
				currFragmentShader = ghost_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_r:
				currFragmentShader = chromatic_aberration_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_h:
				currFragmentShader = hologram_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			# Removemos K_x de aquí porque se usa para controlar rend.value abajo
			# if event.key == pygame.K_x:
			# 	currFragmentShader = xray_shader
			# 	rend.SetShaders(currVertexShader, currFragmentShader)


			# ===== VERTEX SHADERS (antiguos) =====
			if event.key == pygame.K_7:
				currVertexShader = vertex_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_8:
				currVertexShader = fat_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_9:
				currVertexShader = water_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			# ===== VERTEX SHADERS NUEVOS =====
			if event.key == pygame.K_0:
				currVertexShader = twist_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_MINUS:
				currVertexShader = explode_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_EQUALS:
				currVertexShader = ghost_distortion_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_t:
				currVertexShader = ripple_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_y:
				currVertexShader = spike_shader
				rend.SetShaders(currVertexShader, currFragmentShader)


	if keys[K_UP]:
		# Mover cámara orbital hacia arriba
		rend.camera.RotateOrbitVertical(50 * deltaTime)

	if keys[K_DOWN]:
		# Mover cámara orbital hacia abajo
		rend.camera.RotateOrbitVertical(-50 * deltaTime)

	if keys[K_RIGHT]:
		# Rotar cámara orbital a la derecha
		rend.camera.RotateOrbitHorizontal(50 * deltaTime)

	if keys[K_LEFT]:
		# Rotar cámara orbital a la izquierda
		rend.camera.RotateOrbitHorizontal(-50 * deltaTime)



	if keys[K_w]:
		rend.pointLight.z -= 10 * deltaTime

	if keys[K_s]:
		rend.pointLight.z += 10 * deltaTime

	if keys[K_a]:
		rend.pointLight.x -= 10 * deltaTime

	if keys[K_d]:
		rend.pointLight.x += 10 * deltaTime

	if keys[K_q]:
		rend.pointLight.y -= 10 * deltaTime

	if keys[K_e]:
		rend.pointLight.y += 10 * deltaTime


	if keys[K_z]:
		if rend.value > 0.0:
			rend.value -= 1 * deltaTime

	if keys[K_x]:
		if rend.value < 1.0:
			rend.value += 1 * deltaTime


	if pygame.mouse.get_pressed()[0]:
		# Click izquierdo: rotar cámara con el mouse
		rend.camera.RotateOrbitHorizontal(mouseVel[0] * 0.5)
		rend.camera.RotateOrbitVertical(-mouseVel[1] * 0.5)


	# Rotación automática desactivada - solo rotar con input del usuario
	# WormModel.rotation.y += 45 * deltaTime


	rend.Render()
	pygame.display.flip()

pygame.quit()
