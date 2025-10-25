
class Obj(object):
	def __init__(self, filename):
		# Asumiendo que el archivo es un formato .obj
		with open(filename, "r") as file:
			lines = file.read().splitlines()
			
		self.vertices = []
		self.texCoords = []
		self.normals = []
		self.faces = []
		# Name of the referenced material library file (mtllib)
		self.mtllib = None
		# Per-face material name (from usemtl) aligned with self.faces
		self.face_materials = []
		
		current_material = None

		for line in lines:
			# Si la linea no cuenta con un prefijo y un valor,
			# seguimos a la siguiente la linea

			line = line.rstrip()

			try:
				prefix, value = line.split(" ", 1)
			except:
				continue
			
			# Dependiendo del prefijo, parseamos y guardamos
			# la informacion en el contenedor correcto
			
			if prefix == "v": # Vertices
				vert = list(map(float,value.split(" ")))
				self.vertices.append(vert)
				
			elif prefix == "vt": # Coordenadas de textura
				vts = list(map(float,value.split(" ")))
				self.texCoords.append([vts[0],vts[1]])
				
			elif prefix == "vn": # Normales
				norm = list(map(float,value.split(" ")))
				self.normals.append(norm)
				
			elif prefix == "mtllib":
				# referenced material library filename
				# value may contain extra spaces, strip
				self.mtllib = value.strip()

			elif prefix == "usemtl":
				# the material used for subsequent faces
				current_material = value.strip()

			elif prefix == "f": # Caras
				face = []
				verts = value.split(" ")
				for vert in verts:
					vert = list(map(int, vert.split("/")))
					face.append(vert)
				self.faces.append(face)
				# record current material for this face (may be None)
				self.face_materials.append(current_material)