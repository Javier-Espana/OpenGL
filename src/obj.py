
class ObjFileParser:
    """
    Parser for Wavefront OBJ 3D model files.
    Extracts vertices, texture coordinates, normals, and face definitions.
    """
    
    def __init__(self, filepath):
        self.vertices = []
        self.texCoords = []
        self.normals = []
        self.faces = []
        
        self._parse_file(filepath)
    
    def _parse_file(self, filepath):
        """Reads and parses the OBJ file line by line."""
        with open(filepath, "r") as file:
            for line in file:
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(None, 1)
                if len(parts) < 2:
                    continue
                
                prefix, data = parts
                
                if prefix == "v":
                    self._parse_vertex(data)
                elif prefix == "vt":
                    self._parse_texcoord(data)
                elif prefix == "vn":
                    self._parse_normal(data)
                elif prefix == "f":
                    self._parse_face(data)
    
    def _parse_vertex(self, data):
        """Parses vertex position data."""
        coords = list(map(float, data.split()))
        self.vertices.append(coords)
    
    def _parse_texcoord(self, data):
        """Parses texture coordinate data."""
        coords = list(map(float, data.split()))
        self.texCoords.append([coords[0], coords[1]])
    
    def _parse_normal(self, data):
        """Parses normal vector data."""
        coords = list(map(float, data.split()))
        self.normals.append(coords)
    
    def _parse_face(self, data):
        """Parses face indices data."""
        face_vertices = []
        for vertex_str in data.split():
            indices = list(map(int, vertex_str.split("/")))
            face_vertices.append(indices)
        self.faces.append(face_vertices)                                                                                                                                                                                                                                                                                                                                                                                           