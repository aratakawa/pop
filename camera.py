import math

class Camera(object) :
	def __init__(self, fov=None, aperture=None, focalLength=None) :
		self.fov = fov
		self.aperture = aperture
		self.focalLength = focalLength
		self.calculate()
	def isValid(self) :
		valid = 0
		for t in targets :
			if t != None :
				valid += 1
		if valid > 2 :
			return True
		return False
	def setFov(self, fov) :
		self.fov = fov
		self.calculate()
	def setFocalLength(self, focalLength) :
		self.focalLength = focalLength
		self.calculate()
	def setAperture(self, aperture) :
		self.aperture = aperture
		self.calculate()
	def calculate(self) :
		targets = [self.fov, self.aperture, self.focalLength]
		valid = 0
		for t in targets :
			if t != None :
				valid += 1
		if valid < 2 :
			print("Not enough attributes ready to calculate values.")
			return None
		else :
			if self.fov != None and self.aperture != None :
				self.focalLength = (0.5*self.aperture)/math.tan((0.5*self.fov)*math.pi/180)
			elif self.fov != None and self.focalLength != None :
				self.aperture = 2*math.tan((0.5*self.fov)*math.pi/180)*self.focalLength
			elif self.aperture != None and self.focalLength != None :
				self.fov = 2*(math.atan((0.5*self.aperture)/self.focalLength)*180/math.pi)
			print("Everything is ready.")
			return True