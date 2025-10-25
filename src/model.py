from OpenGL.GL import *
from src.obj import Obj
from src.buffer import Buffer

import glm

import pygame
import os

class Model(object):
	def __init__(self, filename, autoLoadMaterials=False):
		self.objFile = Obj(filename)
		self.objFilename = filename

		self.position = glm.vec3(0,0,0)
		self.rotation = glm.vec3(0,0,0)
		self.scale = glm.vec3(1,1,1)

		self.textures = []

		# mapping material name -> OpenGL texture id
		self.material_textures = {}

		# submeshes: list of dicts { material, posBuffer, texCoordsBuffer, normalsBuffer, vertexCount }
		self.submeshes = []

		# cache: texture file path -> OpenGL texture id (avoid loading duplicates)
		self.texture_cache = {}

		# If autoLoadMaterials is True, load textures automatically
		# Otherwise, user must call LoadMaterialsFromMtl() manually
		if autoLoadMaterials:
			try:
				self.LoadMaterialsFromMtl()
			except Exception as e:
				print(f"Warning: failed to load .mtl textures for {filename}: {e}")
				self.BuildBuffers()
		else:
			# Build buffers without materials (will have single default submesh)
			self.BuildBuffers()

	def GetModelMatrix(self):

		identity = glm.mat4(1)

		translateMat = glm.translate(identity, self.position)

		pitchMat = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
		yawMat =   glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
		rollMat =  glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))

		rotationMat = pitchMat * yawMat * rollMat

		scaleMat = glm.scale(identity, self.scale)

		return translateMat * rotationMat * scaleMat


	def BuildBuffers(self):
		# Group faces by material so we can create submeshes per material
		faces = self.objFile.faces
		face_materials = getattr(self.objFile, 'face_materials', [None] * len(faces))

		# dict material -> accumulators
		acc = {}

		for idx, face in enumerate(faces):
			mat = face_materials[idx] if idx < len(face_materials) else None
			if mat is None:
				mat = 'default'
			if mat not in acc:
				acc[mat] = { 'positions': [], 'texcoords': [], 'normals': [], 'vertexCount': 0 }

			facePositions = []
			faceTexCoords = []
			faceNormals = []

			for i in range(len(face)):
				facePositions.append( self.objFile.vertices [ face[i][0] - 1 ] )
				faceTexCoords.append( self.objFile.texCoords[ face[i][1] - 1 ] )
				faceNormals.append( self.objFile.normals[ face[i][2] - 1 ] )

			# triangle 0,1,2
			for value in facePositions[0]: acc[mat]['positions'].append(value)
			for value in facePositions[1]: acc[mat]['positions'].append(value)
			for value in facePositions[2]: acc[mat]['positions'].append(value)

			for value in faceTexCoords[0]: acc[mat]['texcoords'].append(value)
			for value in faceTexCoords[1]: acc[mat]['texcoords'].append(value)
			for value in faceTexCoords[2]: acc[mat]['texcoords'].append(value)

			for value in faceNormals[0]: acc[mat]['normals'].append(value)
			for value in faceNormals[1]: acc[mat]['normals'].append(value)
			for value in faceNormals[2]: acc[mat]['normals'].append(value)

			acc[mat]['vertexCount'] += 3

			if len(face) == 4:
				# quad -> second triangle 0,2,3
				for value in facePositions[0]: acc[mat]['positions'].append(value)
				for value in facePositions[2]: acc[mat]['positions'].append(value)
				for value in facePositions[3]: acc[mat]['positions'].append(value)

				for value in faceTexCoords[0]: acc[mat]['texcoords'].append(value)
				for value in faceTexCoords[2]: acc[mat]['texcoords'].append(value)
				for value in faceTexCoords[3]: acc[mat]['texcoords'].append(value)

				for value in faceNormals[0]: acc[mat]['normals'].append(value)
				for value in faceNormals[2]: acc[mat]['normals'].append(value)
				for value in faceNormals[3]: acc[mat]['normals'].append(value)

				acc[mat]['vertexCount'] += 3

		# Create Buffer objects for each material submesh
		self.submeshes = []
		for mat, data in acc.items():
			posBuf = Buffer(data['positions'])
			texBuf = Buffer(data['texcoords'])
			normBuf = Buffer(data['normals'])
			texture_id = self.material_textures.get(mat)
			self.submeshes.append({
				'material': mat,
				'posBuffer': posBuf,
				'texCoordsBuffer': texBuf,
				'normalsBuffer': normBuf,
				'vertexCount': data['vertexCount'],
				'texture': texture_id
			})


	def AddTexture(self, filename):
		textureSurface = pygame.image.load(filename)
		textureData = pygame.image.tostring(textureSurface, "RGB", True)

		texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, texture)

		glTexImage2D(GL_TEXTURE_2D,
					 0,
					 GL_RGB,
					 textureSurface.get_width(),
					 textureSurface.get_height(),
					 0,
					 GL_RGB,
					 GL_UNSIGNED_BYTE,
					 textureData)

		glGenerateMipmap(GL_TEXTURE_2D)

		self.textures.append(texture)
		return texture


	def LoadMaterialsFromMtl(self, customTexturePaths=None):
		"""
		Load materials and textures from the .mtl file referenced by the .obj.
		
		Args:
			customTexturePaths: Optional dict mapping material names to texture file paths.
			                   If provided, these paths override the ones in the .mtl file.
			                   Example: {'phong1SG': 'textures/custom.jpg'}
		
		Returns:
			Number of textures loaded
		"""
		return self.LoadMtlTextures(self.objFilename, customTexturePaths)


	def LoadMtlTextures(self, objFilename, customTexturePaths=None):
		"""
		Read the .mtl referenced by the .obj and load any `map_Kd` textures.
		objFilename: path to the .obj file used to resolve relative paths.
		"""

		mtl_name = self.objFile.mtllib
		if not mtl_name:
			print(f"[Model] No .mtl file referenced by {objFilename}")
			return

		# Resolve path relative to the .obj file
		obj_dir = os.path.dirname(objFilename)
		mtl_path = os.path.join(obj_dir, mtl_name)

		if not os.path.exists(mtl_path):
			print(f"[Model] Warning: .mtl file not found: {mtl_path}")
			return

		print(f"\n[Model] Loading materials from: {mtl_path}")

		materials = {}
		current_mat = None
		with open(mtl_path, 'r', encoding='utf-8', errors='ignore') as f:
			for line in f:
				line = line.strip()
				if not line or line.startswith('#'):
					continue
				parts = line.split(' ', 1)
				if len(parts) == 1:
					key = parts[0]
					val = ''
				else:
					key, val = parts[0], parts[1].strip()
				if key == 'newmtl':
					current_mat = val
					materials[current_mat] = {}
					print(f"  - Found material: {current_mat}")
				elif key == 'map_Kd' and current_mat is not None:
					# diffuse texture map
					materials[current_mat]['map_Kd'] = val
					print(f"    -> map_Kd: {val}")

		# Load and map textures to materials
		textures_loaded = 0
		for mat, props in materials.items():
			# Check if custom texture path is provided for this material
			if customTexturePaths and mat in customTexturePaths:
				tex_path = customTexturePaths[mat]
				print(f"  [Custom] Using custom texture for material '{mat}': {tex_path}")
			else:
				tex = props.get('map_Kd')
				if not tex:
					continue
				tex_path = tex
				if not os.path.isabs(tex_path):
					tex_path = os.path.join(obj_dir, tex_path)
				tex_path = os.path.normpath(tex_path)

				# If not found in the obj directory, try common texture directories
				if not os.path.exists(tex_path):
					# Try multiple common texture directories
					search_dirs = [
						os.path.join(obj_dir, "..", "..", "textures", "Eye Textures"),
						os.path.join(obj_dir, "..", "..", "textures", "Worm Textures"),
						os.path.join(obj_dir, "..", "..", "textures", "Creature Textures"),
						os.path.join(obj_dir, "..", "..", "textures"),
					]
					
					found = False
					for search_dir in search_dirs:
						alt_path = os.path.join(search_dir, os.path.basename(tex))
						alt_path = os.path.normpath(alt_path)
						if os.path.exists(alt_path):
							tex_path = alt_path
							found = True
							break
					
					if not found and not os.path.exists(tex_path):
						print(f"  [Error] Texture file not found for material '{mat}': {tex}")
						continue

			# Use cache to avoid loading same texture multiple times
			if tex_path in self.texture_cache:
				tex_id = self.texture_cache[tex_path]
				self.material_textures[mat] = tex_id
				print(f"  [Cache] Reusing texture for material '{mat}': {tex_path}")
			elif os.path.exists(tex_path):
				tex_id = self.AddTexture(tex_path)
				self.texture_cache[tex_path] = tex_id
				self.material_textures[mat] = tex_id
				textures_loaded += 1
				print(f"  [Loaded] Texture for material '{mat}': {tex_path}")
			else:
				print(f"  [Error] Texture file not found for material '{mat}': {tex_path}")

		print(f"[Model] Loaded {textures_loaded} unique texture(s) from .mtl\n")

		# After loading textures, rebuild buffers so submeshes pick up material mappings
		# (Buffers will be created even if textures missing)
		self.BuildBuffers()

		# Report submeshes created
		print(f"[Model] Created {len(self.submeshes)} submesh(es):")
		for idx, sub in enumerate(self.submeshes):
			mat_name = sub['material']
			vert_count = sub['vertexCount']
			has_tex = "✓" if sub.get('texture') is not None else "✗"
			print(f"  [{idx}] Material: '{mat_name}' | Vertices: {vert_count} | Texture: {has_tex}")
		print()

		return textures_loaded

	def Render(self):

		# Render each submesh: bind its texture (if any) to texture unit 0 and draw
		for sub in self.submeshes:
			tex = sub.get('texture')
			if tex is not None:
				glActiveTexture(GL_TEXTURE0)
				glBindTexture(GL_TEXTURE_2D, tex)

			# bind buffers for this submesh
			sub['posBuffer'].Use(0, 3)
			sub['texCoordsBuffer'].Use(1, 2)
			sub['normalsBuffer'].Use(2, 3)

			glDrawArrays(GL_TRIANGLES, 0, sub['vertexCount'])

			glDisableVertexAttribArray(0)
			glDisableVertexAttribArray(1)
			glDisableVertexAttribArray(2)




