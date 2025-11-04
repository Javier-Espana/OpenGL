import glm # pip install PyGLM
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from src.camera import Camera
from src.skybox import Skybox

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _,_, self.width, self.height = screen.get_rect()
        
        glClearColor(0.2, 0.2, 0.2, 1.0)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)  # Habilitar transparencia para shaders ghost/hologram
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glViewport(0,0, self.width, self.height)

        self.camera = Camera(self.width, self.height)

        self.scene = []
        

        self.filledMode = False
        self.ToggleFilledMode()

        self.activeShader = None
        self.active_postProcessing_Shader = None

        self.skybox = None

        self.pointLight = glm.vec3(0,0,0)
        self.ambientLight = 0.1


        self.value = 0.0;
        self.elapsedTime = 0.0;

        self.CreateFrameBuffer()



    def CreateSkybox(self, textureList):
        self.skybox = Skybox(textureList)
        self.skybox.cameraRef = self.camera


    def CreateFrameBuffer(self):
        # Crear frameBuffer
        self.FBO = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

        # Crear la textura del framebuffer
        self.FBOTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.FBOTexture)
        glTexImage2D(GL_TEXTURE_2D,0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE,None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.FBOTexture, 0)

        # Create depthTexture/Z buffer
        self.depthTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depthTexture)
        glTexImage2D(GL_TEXTURE_2D,0, GL_DEPTH_COMPONENT24, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT ,None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depthTexture, 0)

        # Unbind
        glBindFramebuffer(GL_FRAMEBUFFER, 0)


    def ToggleFilledMode(self):
        self.filledMode = not self.filledMode

        if self.filledMode:
            glEnable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT, GL_FILL)
        else:
            glDisable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


    def SetShaders(self, vertexShader, fragmentShader):
        if vertexShader is not None and fragmentShader is not None:
            self.activeShader = compileProgram( compileShader(vertexShader, GL_VERTEX_SHADER),
                                                compileShader(fragmentShader, GL_FRAGMENT_SHADER) )
        else:
            self.activeShader = None


    def SetPostProcessingShaders(self, vertexShader, fragmentShader):
        if vertexShader is not None and fragmentShader is not None:
            self.active_postProcessing_Shader = compileProgram( compileShader(vertexShader, GL_VERTEX_SHADER),
                                                compileShader(fragmentShader, GL_FRAGMENT_SHADER) )
        else:
            self.active_postProcessing_Shader = None


    def Render(self):
        if self.active_postProcessing_Shader is not None:
            glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        self.camera.Update()

        if self.skybox is not None:
            self.skybox.Render()


        if self.activeShader is not None:
            glUseProgram(self.activeShader)

            glUniformMatrix4fv( glGetUniformLocation(self.activeShader, "viewMatrix"),
                                1, GL_FALSE, glm.value_ptr(self.camera.viewMatrix) )

            glUniformMatrix4fv( glGetUniformLocation(self.activeShader, "projectionMatrix"),
                                1, GL_FALSE, glm.value_ptr(self.camera.projectionMatrix) )

            glUniform3fv( glGetUniformLocation(self.activeShader, "pointLight"), 1, glm.value_ptr(self.pointLight) )
            glUniform1f( glGetUniformLocation(self.activeShader, "ambientLight"), self.ambientLight )

            glUniform1f( glGetUniformLocation(self.activeShader, "value"), self.value )
            glUniform1f( glGetUniformLocation(self.activeShader, "time"), self.elapsedTime )


            glUniform1i( glGetUniformLocation(self.activeShader, "tex0"), 0)
            glUniform1i( glGetUniformLocation(self.activeShader, "tex1"), 1)



        for obj in self.scene:

            if self.activeShader is not None:
                glUniformMatrix4fv( glGetUniformLocation(self.activeShader, "modelMatrix"),
                                1, GL_FALSE, glm.value_ptr( obj.GetModelMatrix() ) )

            obj.Render()


        if self.active_postProcessing_Shader is not None:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glClear(GL_COLOR_BUFFER_BIT)

            glDisable(GL_DEPTH_TEST)

            glUseProgram(self.active_postProcessing_Shader)

            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.FBOTexture)

            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.depthTexture)

            glUniform1i( glGetUniformLocation(self.active_postProcessing_Shader, "frameBuffer"), 0)
            glUniform1i( glGetUniformLocation(self.active_postProcessing_Shader, "depthTexture"), 1)

            glUniform1f( glGetUniformLocation(self.active_postProcessing_Shader, "time"), self.elapsedTime )

            glDrawArrays(GL_QUADS, 0, 4)

            glEnable(GL_DEPTH_TEST)
