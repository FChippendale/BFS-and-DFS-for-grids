import pygame, sys, math
import numpy as np



# Necessary global variables for the interactive UI.
col, row = 80, 80
alg = "BFS"

# Necessary PyGame variables and configuration.
w,h = 1080, 720 # UI designed for w at least 160 larger than h. No issues with 640x480.

pygame.init()
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()

pygame.mouse.set_visible(True)
pygame.event.set_grab(False)


    
class Adventurer:
    def __init__(self, map_to_explore, start, goal, alg_type):
        self.map = map_to_explore
        self.col = map_to_explore.shape[0]
        self.row = map_to_explore.shape[1]
        self.pos = start
        self.start = start
        self.goal = goal
        self.to_visit = [start]
        self.alg_type = alg_type
        self.arrived = False # Tracks if the goal has been reached or not.
        self.possible = True # Tracks if there remain squares to be explored.
    
    def backtrack(self):
        """Finds which squares were travelled thorugh on the optimal route. Since each square is distance 1 from its neighbour,
        the square which has a distance of 1 less than the current square is guaranteed to be on a valid path to the current 
        square from the start. This process is started from the goal and repeated until the start is reached, while keeping
        track of the squares traversed. These are also marked on the map as -3, such that they can be added to the graphical representation.
        
        Returns:
            List of (int, int): each representing the (x, y) coordinates of one of the traversed squares.
        """
        self.pos = self.goal
        squares_travelled = [self.goal]
        x, y, = self.pos
        while (x, y) != self.start:
            for mov_x, mov_y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                if self.map[(x+mov_x + self.col) % self.col][(y+mov_y + self.row) % self.row] == self.map[x][y] - 1:
                    next_square = ((x+mov_x + self.col) % self.col, (y+mov_y + self.row) % self.row)
                    
            squares_travelled += [next_square]
            # leaves the start and goal intact, such that the distance to the goal is saved.
            if (x, y) != self.start and (x, y) != self.goal:
                self.map[x][y] = -3 
            x, y = next_square
        return squares_travelled[::-1]
            
    def step_forward(self):
        """Procedes with the path exploration until no possible square could lead to a better solution than the one already
        found, or no square can be explored. Can use both BFS or DFS algorithm, modified such that they are able to find the 
        shortest path from the start to the goal, and not just check if one exists or not.
        """
        # Was a path found or not once the map is explored.
        if not self.to_visit: 
            if self.map[self.goal[0]][self.goal[1]] == -2:
                self.possible = False
            else:
                self.arrived = True
            return [self.start]
        
        # Difference between BFS and DFS
        if self.alg_type == "DFS":
            self.pos = self.to_visit[-1]
            self.to_visit.pop(len(self.to_visit) - 1)
        if self.alg_type == "BFS":
            self.pos = self.to_visit[0]
            self.to_visit.pop(0)
        
        # Explores squares surrounding current position.
        x, y = self.pos
        new_squares = []
        for mov_x, mov_y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            # Due to it being a sphere, the map wraps horizontally, but not vertically (as that would imply travelling from one pole to the other).
            if y + mov_y >= 0 and y + mov_y < self.row:
                # Checks if the distance to the adjacent square can be improved, and if so marks it as needing to be checked.
                # Unvisited squares are treated as if their distance from the start were infinity, thus any path is an improvement.
                if self.map[(x+mov_x + self.col) % self.col][(y+mov_y + self.row) % self.row] == -2 or self.map[(x+mov_x + self.col) % self.col][(y+mov_y + self.row) % self.row] > self.map[x][y] + 1:
                    if ((x+mov_x + self.col) % self.col, (y+mov_y + self.row) % self.row) in self.to_visit:
                        self.to_visit.remove((((x+mov_x + self.col) % self.col, (y+mov_y + self.row) % self.row)))
                    
                    # Updates the map so that it now records the distance from the start to the new square via the current route.
                    self.map[(x+mov_x + self.col) % self.col][(y+mov_y + self.row) % self.row] = self.map[x][y] + 1
                    if self.map[self.goal[0]][self.goal[1]] == -2 or self.map[x][y] < self.map[self.goal[0]][self.goal[1]]: 
                        self.to_visit += [((x+mov_x + self.col) % self.col, (y+mov_y + self.row) % self.row)]
                    new_squares += [((x+mov_x + self.col) % self.col, (y+mov_y + self.row) % self.row)]
                    
        # returns all newly explored squares so that they can be updated in the graphical representation.
        return new_squares
    



class Button:
    def __init__(self, screen, x0, y0, width, height, color, text, func, text_color = (0, 0, 0)):
        """Args:
                screen: the pygame screen upon which things are drawn.
                x0 (int): the distance of the top left corner of the button from the leftmost edge of the screen.
                y0 (int): the distance of the top left corner of the button from the uppermost edge of the screen.
                width (int): width of box that acts as button.
                height (int): height of box that acts as button.
                color (int, int, int): RGB color code for backgroud color of button.
                text (String): text which the button contains.
                func (function): the function that will be called if the button in pressed.
                text_color (int, int, int): RGB code for text color, default is black (0, 0, 0).
                """
        self.screen = screen
        self.x0 = x0
        self.y0 = y0
        self.x = width
        self.y = height
        self.color = color
        self.text = text
        self.click = func
        self.text_color = text_color
        self.update()
    
    def mouse_over(self, pos):
        """Checks whether the mouse is currently over the button, needed to determine if the button was 
        clicked or not.
        Args:
            pos (int, int): x, y coordinates of the mouse on the screen, with 0 being in the topleft corner.
        
        Returns:
            Bool: if the mouse was over the box of the button or not.
        """
        if self.x0 <= pos[0] <= self.x0 + self.x and self.y0 <= pos[1] <= self.y0 + self.y:
            return True
        return False
    
    def update(self):
        pygame.draw.rect(screen, self.color, (self.x0, self.y0, self.x, self.y))
        buttonText = pygame.font.Font("freesansbold.ttf", self.y // 2)
        textSurf = buttonText.render(self.text, True, self.text_color)
        textRect = textSurf.get_rect()
        textRect.center = ((self.x0 + (self.x / 2)), (self.y0 + (self.y / 2)))
        self.screen.blit(textSurf, textRect)
        pygame.display.update()

        
        
class Map:
    def __init__(self, screen, map_side, row, col):
        self.screen = screen
        self.map_side = map_side   # Side length of the square which contains the visual representation.
        self.row = row
        self.col = col 
        self.view = "3D"
        
        # Will be assigned in reset().
        self.start = None
        self.goal = None
        self.map = None
        
        # Necessary variables for the 3D sphere view.
        self.radius = 2.5
        self.polar_ang = 0.0
        self.zenith_ang = 0.0
        self.tiles = None
        
        self.reset()
        
        
    def reset(self):
        """Resets the map in preparation for the next cycle. Creates new random start, end and walls, then procedes to call
        the appropriate function for it to be drawn.
        """
        self.map = np.random.randint(0, 3, (col, row)) # The 3 can be increased to decrease the density of walls.
        self.map = np.where(self.map > 0, -2, -1) # Squares that contain a wall are set to -1, unexplored squares are set to -2.
        np.transpose(self.map) # necessary such that x is along the columns and y is along the rows, while staying map[x][y].
        
        # Randomises start and goal positions, while ensuring neither are in the same location as a wall.
        self.start = (np.random.randint(self.col), np.random.randint(self.row))
        self.goal = (np.random.randint(self.col), np.random.randint(self.row))
        self.map[self.start[0]][self.start[1]] = 0
        self.map[self.goal[0]][self.goal[1]] = -2
        self.draw_map()
        
    
    def pol_car(self, alpha, beta):
        """Converts polar coordinates to their cartesian equivalents, while factoring in any rotation of the sphere
        and its radius.
        
        Args:
            alpha (float): the angle on the X-Z plane in radians.
            beta (float): the zenith angle of the point from the X-Z plane.
            
        Returns:
            Numpy Array [x, y, z]: cartesian coordinates.
        """
        rot_matrix = [[1, 0, 0], 
                      [0, math.cos(self.zenith_ang), -math.sin(self.zenith_ang)], 
                      [0, math.sin(self.zenith_ang), math.cos(self.zenith_ang)]]
        
        x = math.cos(alpha)*math.sin(beta)
        y = math.cos(beta)
        z = math.sin(alpha)*math.sin(beta)
        return np.matmul(np.array([x, y, z])*self.radius, rot_matrix)
        
        
    def create_tiles(self):
        """Creates the complete matrix of catesian coordinates for each face in the 3D sphere. 
        These are calculated from their associated polar coordinates before being converted.
        
        Returns:
            NumPy matrix [row, col, 4, 3] which contains the cartesian coordinates of each vertex for each
                face on the sphere. Some of these faces only have 3 vertexes, in which case the coordinates of the 
                fourth are (1, 1, 1)
        """
        np_tiles = np.ones((self.row, self.col, 4, 3))
        
        # Produces lists of polar angles that will be needed. These can be though of as latitude and longitute lines,
        # and the intersection of any two is the location of the vertex of a face.
        h_ang = [(x * 2*math.pi / self.col + self.polar_ang) % (2*math.pi) for x in range(self.col)]
        h_ang += [h_ang[0]]
        v_ang = [y*math.pi/(self.row+1) for y in range(1, self.row)]
        
        # Create faces connected with poles, these only have 3 vertexes, hence the fourth will remain (1, 1, 1).
        for i in range(self.col):
            np_tiles[0][i][0] = self.pol_car(0, 0)
            np_tiles[0][i][1] = self.pol_car(h_ang[i], v_ang[0])
            np_tiles[0][i][2] = self.pol_car(h_ang[(i+1)%self.col], v_ang[0])
            
            np_tiles[self.row-1][i][0] = self.pol_car(0, math.pi)
            np_tiles[self.row-1][i][1] = self.pol_car(h_ang[i], v_ang[-1])
            np_tiles[self.row-1][i][2] = self.pol_car(h_ang[(i+1)%col], v_ang[-1])
            
        # Creates all faces with 4 vertexes.
        for i, (x0, x1) in enumerate(zip(h_ang, h_ang[1:])):
            for ii, (y0, y1) in enumerate(zip(v_ang, v_ang[1:])):
                np_tiles[ii+1][i][0] = self.pol_car(x0, y0)
                np_tiles[ii+1][i][1] = self.pol_car(x0, y1)
                np_tiles[ii+1][i][2] = self.pol_car(x1, y1)
                np_tiles[ii+1][i][3] = self.pol_car(x1, y0)
                
        return np_tiles   
    
        
    def draw_map(self):
        """Completely resets the view of the map, redrawing every tile based on its contents and the current view style.
        """
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, self.map_side, self.map_side))
        
        # Creates the matrix of cartesian coordinates for the sphere only when they are needed.
        if self.view == "3D":
            self.tiles = self.create_tiles()
            
        for x in range(self.col):
            for y in range(self.row):
                if (x, y) == self.start: # Will always be colored green.
                    self.update_tile(x, y, (0, 255, 0))
                elif (x, y) == self.goal: # Will always be colored red.
                    self.update_tile(x, y, (255, 0, 0))
                elif self.map[x][y] == -1: # Wall colored white.
                    self.update_tile(x, y, (255, 255, 255))
                elif self.map[x][y] == -2: # Unexplored squares colored black.
                    self.update_tile(x, y, (0, 0, 0))
                elif self.map[x][y] == -3: # Squares part of the shortest path colored yellow.
                    self.update_tile(x, y, (255, 255, 0))
                else: # Explored squares colored based on their distance from the start.
                    self.update_tile(x, y, (0, 0, max(255 - self.map[x][y]*(240//self.row), 63)))
                
                
                
    def rotate_sphere(self, direction):
        """Rotates the sphere 90° in the relative direction. It then calls calls the functions so that this new rotation
        is applied immediately to the map. This only works if the current view is of the 3D sphere.
        
        Args:
            direction (String).
        """
        if self.view == "3D":
            if direction == "UP":
                self.zenith_ang += math.pi / 2.0
            if direction == "DOWN":
                self.zenith_ang = (self.zenith_ang + 3*math.pi/2.0) % (2*math.pi)
            if direction == "RIGHT":
                self.polar_ang += math.pi / 2.0
            if direction == "LEFT":
                self.polar_ang = (self.polar_ang + 3*math.pi/2.0) % (2*math.pi)

            self.create_tiles()
            self.draw_map()
            pygame.display.update()
    
    def update_tile(self, x0, y0, color):
        """Redraws the tile at (x0, y0) of the map, using the correct color. If the current view is 3D, it applies the
        conversion from 3D cartesian coordinates to 2D coordinates on the screen, simulating depth via a vanishing point
        at the center of the gamescreen.
        
        Args: 
            x0 (int): can range from 0 to self.col - 1.
            y0 (int): can range from 0 to self.row - 1.
            color (int, int, int): tuple for RGB values, each from 0 to 255.
        """
        if self.view == "3D":
            vert_2d = []
            if min(self.tiles[y0][x0][:, 2]) >= -0.15/self.radius:
                for (x, y, z) in self.tiles[y0][x0]:
                    # Doesn't include the filler vertexes for the 3 sides faces.
                    if x != 1 or y != 1 or z != 1:
                        z += 3
                        vert_2d += [(self.map_side/2 + x*self.map_side/(2*z), self.map_side/2 + y*self.map_side/(2*z))]
                pygame.draw.polygon(self.screen, color, vert_2d)
        elif self.view == "2D":
            pygame.draw.rect(self.screen, color, (x0*self.map_side/self.col, y0*self.map_side/self.row, self.map_side/self.col, self.map_side/self.row))
       
            

    
    
def mouse_released(buttons):
    """Resets the color of any clicked buttons to show that thye have been released.
    """
    for button in buttons:
        button.color = (0, 255, 255)
        button.update()
    

def mouse_pressed(buttons, mouse_pos):
    """Checks if the mouse was clicked while hovering over a valid button, and if so the button is
    activated.
    """
    for button in buttons:
        if button.mouse_over(mouse_pos):
            button.color = (0, 200, 200)
            button.click()
            button.update()

def increment_row():
    """Executed when the user clicks on the row_button, keeps track of the options for rows. 
    It then updates the button text.
    """
    global row
    global row_button
    row_options = [16, 24, 48, 60, 80, 120, 160, 240]
    row = row_options[(row_options.index(row)+1) % len(row_options)]
    row_button.text = ("Rows: " + str(row))
    
def increment_col():
    """Executed when the user clicks on the col_button, keeps track of the options for columns. 
    It then updates the button text.
    """
    global col
    global col_button
    col_options = [16, 24, 48, 60, 80, 120, 160, 240]
    col = col_options[(col_options.index(col)+1) % len(col_options)]
    col_button.text = ("Cols: " + str(col))

def swap_map_type():
    """Executed when the user clicks on the map_type button, it swaps the current view of the map.
    It then updates the button text.
    """
    global map_to_explore
    if map_to_explore.view == "2D": 
        map_to_explore.view = "3D"
    else: 
        map_to_explore.view = "2D"
   
    map_to_explore.draw_map()    
    map_type_button.text = map_to_explore.view + " Map"
    

def swap_alg_type():
    """Executed when the user clicks on the alg_type button, switching the algorithm that will be used
     for the next exploration upon reset. It then updates the button text.
     """
    global alg
    global alg_type_button
    if alg == "BFS": alg = "DFS"
    else: alg = "BFS"
    alg_type_button.text = alg
    


def wait():
    """Pauses the program, while still allowing for the user to interact with UI elements.
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: pygame.quit(), sys.exit()
                if event.key == pygame.K_SPACE:
                    return
                if map_to_explore.view == "3D":
                    if event.key == pygame.K_UP:
                        map_to_explore.rotate_sphere("UP")
                    if event.key == pygame.K_DOWN:
                        map_to_explore.rotate_sphere("DOWN")
                    if event.key == pygame.K_LEFT:
                        map_to_explore.rotate_sphere("LEFT")
                    if event.key == pygame.K_RIGHT:
                        map_to_explore.rotate_sphere("RIGHT")
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed(buttons, mouse_pos)
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_released(buttons)
        
                    

# UI configuration.
screen.fill((0, 0, 0))

status_button =   Button(screen, h + 10, h - 320, 140, 40, (180, 255, 0), "Searching", None)
row_button =      Button(screen, h + 10, h - 240, 140, 40, (0, 255, 255), ("Rows: " + str(row)), increment_row)
col_button =      Button(screen, h + 10, h - 180, 140, 40, (0, 255, 255), ("Cols: " + str(col)), increment_col)
map_type_button = Button(screen, h + 10, h - 120, 140, 40, (0, 255, 255), "3D Map", swap_map_type)
alg_type_button = Button(screen, h + 10, h - 60, 140, 40, (0, 255, 255), str(alg), swap_alg_type)

buttons = [row_button, col_button, map_type_button, alg_type_button]


# Create the first instances ready for the process to begin.
map_to_explore = Map(screen, h, row, col)
traveller = Adventurer(map_to_explore.map, map_to_explore.start, map_to_explore.goal, alg)

# Game loop, which will not be exited until the program is closed.
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: pygame.quit(), sys.exit()
            if event.key == pygame.K_SPACE:
                status_button.text = "Paused"
                status_button.color = (255, 165, 0)
                status_button.update()
                wait()
                status_button.text = "Searching"
                status_button.color = (180, 255, 0)
                status_button.update()
            if map_to_explore.view == "3D":
                if event.key == pygame.K_UP:
                    map_to_explore.rotate_sphere("UP")
                if event.key == pygame.K_DOWN:
                    map_to_explore.rotate_sphere("DOWN")
                if event.key == pygame.K_LEFT:
                    map_to_explore.rotate_sphere("LEFT")
                if event.key == pygame.K_RIGHT:
                    map_to_explore.rotate_sphere("RIGHT")
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed(buttons, mouse_pos)
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_released(buttons)
        

    if traveller.arrived == False and traveller.possible == True: # Has not yet determined if the goal can be reached.
        # Continue exploration.
        new_squares = traveller.step_forward()
        if new_squares:
            for x, y in new_squares:
                if (x, y) != map_to_explore.start and (x, y) != map_to_explore.goal:
                    map_to_explore.update_tile(x, y, (0, 0, max(255 - map_to_explore.map[x][y]*(240//row), 63)))
    else:
        # Exploration complete.
        if traveller.possible == False: # No valid route was found.
            status_button.text = "No Path"
            status_button.color = (255, 0, 0)
            status_button.update()
        else:
            # A valid route was found and will be highlighted in yellow.
            travelled_squares = traveller.backtrack()
            if travelled_squares:
                for x, y in travelled_squares:
                    if (x, y) != map_to_explore.start and (x, y) != map_to_explore.goal:
                        map_to_explore.update_tile(x, y, (255, 255, 0))
                        
            # Display distance from start to goal.
            status_button.text = ("Distance: " + str(map_to_explore.map[map_to_explore.goal[0]][map_to_explore.goal[1]]))
            status_button.color = (0, 255, 0)
            status_button.update()
            
        wait()
        
        # Reset environment and UI for next exploration.
        status_button.text = "Searching"
        status_button.color = (180, 255, 0)
        status_button.update()
        
        map_to_explore.row = row
        map_to_explore.col = col
        map_to_explore.reset()

        traveller = Adventurer(map_to_explore.map, map_to_explore.start, map_to_explore.goal, alg)
        
    pygame.display.update()
