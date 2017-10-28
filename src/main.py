from sense_hat import SenseHat
from time import sleep
from random import randint


sense = SenseHat()

#clear all LEDs before we begin
sense.clear()

#for better photos, set light to low
sense.low_light = True

#set colors for red, blank, yellow, and white points
r = (255,0,0)
b = (0,0,0)
l = (255,255,0)
w = (255,255,255)

#set all vertical, horizontal, termination, and origin points to same color
v = (0,255,0)
h = (0,255,0)
t = (0,255,0)
o = (0,255,0)

#Initiate variables
x = 2
y = 4

time = 0
limit = 10
timer = 0
jump = 0
prev_z = sense.accel_raw['z']

#Basic start screen
maze = [[b,b,b,v,b,v,b,b],
		[h,h,h,t,h,o,h,h],
		[b,b,b,v,b,b,b,b],
		[b,b,b,v,b,b,b,b],
		[b,b,b,t,h,h,t,h],
		[b,b,b,v,b,b,v,b],
		[b,b,b,v,b,b,v,b],
		[b,b,b,v,b,b,v,b]]

#Animations for crash
explode1 = [[w,w,w,r,w,w,w,w],
			[w,w,r,r,r,w,w,w],
			[w,r,r,r,l,r,w,w],
			[w,r,l,l,l,l,r,r],
			[r,r,l,r,r,l,r,r],
			[r,r,l,l,r,l,r,r],
			[w,r,r,l,l,r,r,w],
			[w,w,r,r,r,r,r,w]]

explode2 = [[w,w,w,w,w,r,w,w],
			[w,w,w,r,r,r,w,w],
			[w,w,r,r,l,l,r,w],
			[w,r,r,l,l,l,r,r],
			[r,r,r,l,r,l,r,r],
			[r,r,r,l,r,l,r,r],
			[w,r,r,r,l,r,r,w],
			[w,w,r,r,r,r,r,w]]

#function to handle basic marble movements
def move_marble(pitch,roll,x,y,jump):
	#make temporary copies of x and y as we update values and run some checks
	new_x = x
	new_y = y
	#move marble based on pitch and roll, checking for display borders before making changes
	if 2 < pitch < 179 and x != 0:
		new_x -= 1
		#if we are far enough away from the edge, we will allow jumping,
		#which moves the marble two spaces instead of one without checking for a wall in between
		if x != 1:
			new_x -= jump
	elif 358 > pitch > 179 and x != 7 :
		new_x +=1
		if x != 6:
			new_x += jump
	if 2 < roll < 179 and y != 7:
		new_y += 1
		if y != 6:
			new_y += jump
	elif 358 > roll > 179 and y != 0 :
		new_y -= 1
		if y != 1:
			new_y -= jump
	x,y = check_wall(x,y,new_x,new_y)
	return x,y

#check to see if there is a wall where we want to put the marble
#changes made by user movement won't go through if there is a wall in the new location
def check_wall(x,y,new_x,new_y):
	#we check h here, but because we use '!='' instead of 'is not' it will check 
	#based on the value and not the variable name
	if maze[new_y][new_x] != h:
		return new_x, new_y
	elif maze[new_y][x] != h:
		return x, new_y
	elif maze[y][new_x] != h:
		return new_x, y
	return x,y

def lose(x, y):
	#crash animation
	sense.set_pixels(sum(explode1,[]))
	sleep(.75)
	sense.set_pixels(sum(explode2,[]))
	sleep(.75)
	#show final score based on total time before crash
	sense.show_message(str(time/10), scroll_speed=0.2, text_colour=[0,0,255])
	#wait for joystick input before starting new game
	sense.stick.wait_for_event()
	x,y = reset(x, y)
	return x, y

def reset(x, y):
	global timer, jump, time, limit, maze, prev_color, prev_z
	x = 2
	y = 4
	timer = 0
	jump = 0
	time = 0
	limit = 10
	maze = [[b,b,b,v,b,v,b,b],
			[h,h,h,t,h,o,h,h],
			[b,b,b,v,b,b,b,b],
			[b,b,b,v,b,b,b,b],
			[b,b,b,t,h,h,t,h],
			[b,b,b,v,b,b,v,b],
			[b,b,b,v,b,b,v,b],
			[b,b,b,v,b,b,v,b]]
	prev_z = sense.accel_raw['z']
	return x,y

def draw_hor(direction, end_point, new_row):
	if direction == 1:
		mod = -1
	else:
		mod = 1
	loc = end_point + mod
	
	while True:
		if loc not in range(8): 
			break
		if new_row[loc] is b:
			if randint(1,2) == 1 and abs(loc - end_point) > 1: 
				if loc + mod not in range(8):
					new_row[loc] = o
					break
				else:
					if new_row[loc + mod] == b:
						new_row[loc] = o
						if randint(1,4) == 1:
							break
			else:
				new_row[loc] = h
				loc = loc + mod
		else:
			break
	return new_row


def add_row(maze): 
	#new row goes at top
	end_list = []
	new_row = [b,b,b,b,b,b,b,b]
	for i, e in enumerate(maze[0]):
		if e is o:
			new_row[i] = v
		if e is t:
			if randint(1,2) == 1:
				new_row[i] = v
		if e is v:
			if randint(1,2) == 1:
					new_row[i] = t
					end_list.append(i)
			else:
				new_row[i] = v
	if end_list:
		new_row = [o if j is v else j for j in new_row]	
	for end_point in end_list:
		direction = randint(1,6)
		if direction == 1:
			new_row = draw_hor(1, end_point, new_row)
		elif direction == 2:
			new_row = draw_hor(2, end_point, new_row)
		else:
			new_row = draw_hor(1, end_point, new_row)
			new_row = draw_hor(2, end_point, new_row)
	if new_row == [b,b,b,b,b,b,b,b]:
		new_row = [v if k is t else b for k in maze[0]]
	for k, column in enumerate(new_row):
		if column != h:
			if randint(1,8) == 1:
				new_row[k] = r 
	maze.insert(0, new_row)
	#remove last row
	maze.pop()
	return maze


while True:
	if time % limit == 0:
		maze = add_row(maze)
		if maze[y][x] == h:
			y += 1
			if y == 8:
				x,y = lose(x, y)
	if time % 100 == 0:
		limit = max (1, limit - 1)
	
	pitch = sense.get_orientation()['pitch']
	roll = sense.get_orientation()['roll']
	diff_z = sense.accel_raw['z'] - prev_z
	if abs(diff_z) > .5 and timer == 0:
		jump = 1
		timer += 1
	x,y = move_marble(pitch, roll, x, y, jump)
	if maze[y][x] == r:
		x,y = lose(x, y)

	maze[y][x] = w
	sense.set_pixels(sum(maze,[]))

	sleep(.01)
	maze[y][x] = b
	prev_z = sense.accel_raw['z']
	if timer == 3:
		timer = 0
	elif timer > 0 or jump == 1:
		timer +=1
	jump = 0
	time += 1
	