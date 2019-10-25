import pygame, sys, random, math
from pygame import gfxdraw

pygame.init()


background_colour = (0,0,0)
(width, height) = (10, 10)
pixelSize = 80

#I divide mousePos by this
sensitivity = -50

#I multiply movement by this
speed = 2

minDistance = 0.5
maxSteps = 10

def pythag(x, y):
    return math.sqrt(x**2 + y**2)

def rotatePoint2d(x, y, theta):
    '''
    x′=xcosθ−ysinθ
    y′=ycosθ+xsinθ
    '''
    rotX = x * math.cos(theta) - y * math.sin(theta)
    rotY = y * math.cos(theta) + x * math.sin(theta)
    return rotX, rotY

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    #get distance from (0, 0, 0)
    def dist(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    #makes distance of Vector3 equal to 1
    def norm(self):
        try:
            dist = self.dist()
            return Vector3(self.x / dist, self.y / dist, self.z / dist)
        except ZeroDivisionError:
            return Vector3(0, 0, 0)

    #add vec3 to vec3
    def add(self, vec3):
        return Vector3(self.x + vec3.x, self.y + vec3.y, self.z + vec3.z)

    def mul(self, num):
        return Vector3(self.x * num, self.y * num, self.z * num)

    def getRot(self):
        try:
            x = math.asin(self.x/self.y)
        except ZeroDivisionError:
            x = 0
        y = math.asin(self.y)
        return Rotate2(x, y)

    #components of Vector3 for debugging
    def comp(self, rounding = 10):
        return round(self.x, rounding), round(self.y, rounding), round(self.z, rounding)

class Rotate2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    #get normalised xyz position, vec3.getRot().getPos() == vec3
    #doesn't work when self.y <= 0
    def getPos(self):
        y = math.sin(self.y)
        x = math.sin(self.x) * y
        z = math.cos(self.x) * y
        
        return Vector3(x, y, z)

    def add(self, rot2):
        return Rotate2(self.x + rot2.x, self.y + rot2.y)


    #components of Rotate2 for debugging
    def comp(self, rounding = 10):
        return round(self.x, rounding), round(self.y, rounding)

testRot = Rotate2(-0.9, 1.4)
print(testRot.comp())
print(testRot.getPos().comp())
print(testRot.getPos().getRot().comp())


class Sphere:
    pos = Vector3(0, 0, 0)
    r = 10

class Camera:
    pos = Vector3(0, 0, 10)
    rot = Rotate2(1, 0.1)
    depth = 0.25
    
class Ray:

    def __init__(self, rot2, screenX, screenY):
        self.direction = rot2.getPos()
        self.screenX = screenX
        self.screenY = screenY
        self.pos = Camera.pos

    def march(self, dis):
        self.pos = self.pos.add(self.direction.norm().mul(dis))



#make screen
screen = pygame.display.set_mode((width * pixelSize, height * pixelSize))
pygame.display.set_caption('Tutorial 1')
pygame.display.flip()

font = pygame.font.Font('freesansbold.ttf', 8)
def setPixel(x, y, color, text=""):
    pixelX = x*pixelSize
    pixelY = y*pixelSize
    pygame.draw.rect(screen, color, (pixelX, pixelY, pixelSize, pixelSize))

    if text:
        if sum(color) > 300:
            color = (0, 0, 0)
        else:
            color = (255, 255, 255)
        text = font.render(text, True, color)
        textRect = text.get_rect()
        textRect.center = (pixelX + pixelSize/2, pixelY + pixelSize/2)
        screen.blit(text, textRect) 
    

def getDistance(vec3):
    spherePos = Sphere.pos
    disToCenter = math.sqrt((spherePos.x - vec3.x)**2 + (spherePos.y - vec3.y)**2 + (spherePos.z - vec3.z)**2)
    return abs(disToCenter - Sphere.r)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
        #control depth with scroll
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                Camera.depth += 0.1
            elif event.button == 5:
                Camera.depth -= 0.1
        
    #messy movement
    movement = Vector3(0, 0, 0)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        movement = movement.add(Vector3(-1, 0, 0))
    if keys[pygame.K_s]:
        movement = movement.add(Vector3(1, 0, 0))
    if keys[pygame.K_a]:
        movement = movement.add(Vector3(0, 0, -1))
    if keys[pygame.K_d]:
        movement = movement.add(Vector3(0, 0, 1))
    if keys[pygame.K_UP]:
        movement = movement.add(Vector3(0, 1, 0))
    if keys[pygame.K_DOWN]:
        movement = movement.add(Vector3(0, -1, 0))

    print(movement.comp())    
    dist = movement.dist()
    movement = movement.getRot().add(Camera.rot).getPos().mul(dist).mul(speed)
    Camera.pos = Camera.pos.add(movement)
    print(movement.comp())

    
    #rotate camera with mouse
    (mouseX, mouseY) = pygame.mouse.get_rel()
    Camera.rot = Camera.rot.add(Rotate2(mouseX / sensitivity, mouseY / sensitivity))
    #screen.fill(background_colour)
        
    
    #make a ray for each pixel
    rays = []
    for x in range(width):
        for y in range(height):
            '''
            add a ray with the proper direction
            step 1: assume camera is pointing 0 and make ray
            ray is x, y
            rotate by camera direction
            '''
            
            thisX = (x / width - 0.5) * Camera.depth
            thisY = (y / height - 0.5) * Camera.depth
            #vec3 = Vector3(thisX, thisY, 0)
            rot2 = Rotate2(thisX, thisY).add(Camera.rot)
            thisRay = Ray(rot2, x, y)
            rays.append(thisRay)
            #print(round(rot2.y, 1), end = " ")
        #print("")

    screen.fill(background_colour)
    #march rays
    for steps in range(maxSteps):
        for ray in rays:
            distance = getDistance(ray.pos)
            x = ray.screenX
            y = ray.screenY
            if distance < minDistance:
                setPixel(x, y, (steps * 10, steps * 10, steps * 10))
                rays.remove(ray)
                
            else:
                ray.march(distance)   

        if len(rays) == 0:
            break

    for ray in rays:
        (r, g, b) = ray.direction.comp()
        r /= 100
        g /= 100
        b /= 100
        r %= 255
        g %= 255
        b %= 255
        colour = (r, g, b)
        setPixel(ray.screenX, ray.screenY, colour, str(getDistance(ray.pos)))

    rays = []

    pygame.display.update()
    #break
    #Camera.rot = Camera.rot.add(Rotate2(0.5, 0))
    #print(Camera.rot.comp())
    
    
