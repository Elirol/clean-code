from __future__ import annotations

from pygame import Surface, display, event, font, draw, time as tm
from pygame.locals import *

import sys, os, random, math, pygame as p
from typing import List, Tuple
from dataclasses import dataclass

### Window settings ###
#ctypes.windll.user32.SetProcessDPIAware()
os.environ["SDL_VIDEO_CENTERED"] = "1"
p.init()
font.init()


### Create Screen ###
pixel_size = 2
window_width = 650
window_height = 650
width = window_width // pixel_size
height = window_height // pixel_size
screen = display.set_mode((window_width, window_height))
display.set_caption("Pixel Chaos!")


### Colours ###
Black = (0, 0, 0)
White = (255, 255, 255)
Red = (255, 0, 0)
Green = (0, 255, 0)
Blue = (0, 0, 255)


@dataclass
class Point:
    x: int
    y: int

@dataclass
class Motion:
    angle: float
    speed: float

class Ray:
    # I main där rays skapas krävs en Point och Motion class i.e byt till nedanför funktionsanrop
    # Rays: List[Ray] = [Ray(width//2, height//2, random.uniform(0, 2*math.pi), 0.75, White, "A") for _ in range(number_of_rays)]
    # Rays: List[Ray] = [Ray(Point(width//2, height//2), Motion(random.uniform(0, 2*math.pi), 0.75, White), "A") for _ in range(number_of_rays)]
    def __init__(self, ray_origin: Point, motion: Motion, colour: Tuple[int, int, int], type: str) -> None:
        self.board_x: int = ray_origin.x
        self.board_y: int = ray_origin.y
        self.precise_x: float = ray_origin.x
        self.precise_y: float = ray_origin.y
        self.Angle: float = motion.angle
        self.speed: float = motion.speed
        self.colour: Tuple[int, int, int] = colour
        self.type: str = type
        

    def update(self, Board: List[List[Ray]]) -> None: 
        """Function for moving a ray."""

        # Move pixel
        prev_x = self.board_x
        prev_y = self.board_y
        self.precise_x += self.speed * math.cos(self.Angle)
        self.board_x = int(round(self.precise_x, 0))
        self.precise_y += self.speed * math.sin(self.Angle)
        self.board_y = int(round(self.precise_y, 0))
        

        # each code block that fixes if the ray goes outside the bounds of the screen can be a separate function

        if self.board_x < 0:                # If outside to the left
            self.board_x = 0
            self.precise_x = 0

            if self.Angle < math.pi:
                self.Angle -= 2 * (math.pi/2 - (math.pi - self.Angle))
            else:
                self.Angle += 2 * (math.pi/2 - (self.Angle - math.pi))
        
        elif self.board_x >= width:         # If outside to the right
            self.board_x = width-1
            self.precise_x = width-1
            
            if self.Angle < math.pi/2:
                self.Angle += 2 * (math.pi/2 - self.Angle)
            else:
                self.Angle -= 2 * (math.pi/2 - (2 * math.pi - self.Angle))

        if self.board_y < 0:                # If outside to the top
            self.board_y = 0
            self.precise_y = 0

            if self.Angle < math.pi/2:
                self.Angle -= 2 * (math.pi/2 - (math.pi/2 - self.Angle))
            else:
                self.Angle += 2 * (math.pi/2 - (self.Angle - math.pi/2)) 

        elif self.board_y >= height:        # If outside to the bottom
            self.board_y = height-1
            self.precise_y = height-1

            if self.Angle < 3 * math.pi/2:
                self.Angle -= 2 * (math.pi/2 - (3*math.pi/2 - self.Angle))
            else:
                self.Angle += 2 * (math.pi/2 - (self.Angle - 3*math.pi/2))

        self.Angle %= 2*math.pi     # Get angle between 0.0 - 2*pi
        
        # Edit board
        Board[prev_y][prev_x] = None
        Board[self.board_y][self.board_x] = self

    def diffuse_ray(self, Board: List[List[float]]) -> None:
        for x, y, dx, dy in self._near_raycell_diffuse_values():
            Board[y][x] = self._diffuse_intensity(dx, dy)

    def _near_raycell_diffuse_values(self):
        for dy in range(-1, 2): #no hardcoded ranges :P
            if 0 <= self.board_y + dy < height:
                for dx in range(-1, 2):
                    if dy == 0 and dx == 0:
                        continue
                    x, y = self.board_x + dx, self.board_y + dy
                    if 0 <= x < width and 0 <= y < height:
                        yield x, y, dx, dy
                      
    def _diffuse_intensity(self, x: int, y: int) -> float:
        return 0.85 / math.sqrt(x**2 + y**2)
    
    def attract_to_neighbour(self, Board: List[List[Ray]]) -> None:
        """Function that attracts the pixel to nearby neighbours."""

        # * New search function starts the search with the "self" objects position in the top left corner. 
        # * The offset variables can be adjusted so that the "self" object is moved around, including outside of the search view.
        angle_weight = 0.15
        search_x = 5
        search_y = 3
        offset_x = 0
        offset_y = 1

        # New search function #

        #make angle calculation into function
        for y in range(search_y):
            if 0 <= y + offset_y + self.board_y < height:
                for x in range(search_x):
                    if 0 <= x + offset_x + self.board_x < width and not Board[y + offset_y + self.board_y][x + offset_x + self.board_x] is None:
                        pass
                        # Calculate angle between

        # fix range so its not hardocded
        for y in range(-2, 3):
            if 0 <= self.board_y + y < height:
                for x in range(-2, 3):
                    if y == 0 and x == 0:
                        continue
                    if 0 <= self.board_x + x < width:
                        if not Board[self.board_y + y][self.board_x + x] is None:
                            try: # move try catch into separate function
                                net_distance = 1/math.sqrt(x**2 + y**2)
                                delta_x = abs(self.board_x - Board[self.board_y + y][self.board_x + x].board_x) * (-1 if True else 1)
                                delta_y = abs(self.board_y - Board[self.board_y + y][self.board_x + x].board_y) * (-1 if True else 1)
                                
                                delta_angle = self.Angle - math.tan(delta_y/delta_x)
                                additional_angle = angle_weight * net_distance * delta_angle
                                self.Angle += additional_angle
                            except ZeroDivisionError:
                                continue

    def draw(self, screen: Surface) -> None:
        """Function for drawing a ray on the screen."""
        draw.rect(screen, self.colour, self._bounding_ray_rectangle())

    def _bounding_ray_rectangle(self) -> Tuple[int, int, int, int]:
        return (self.board_x*pixel_size, self.board_y*pixel_size, pixel_size, pixel_size)

def create_rays(number_of_rays: int) -> List[Ray]:
    """Function for creating a list of rays."""
    return [Ray(Point(width//2, height//2), Motion(random.uniform(0, 2*math.pi), 0.75), White, "A") for _ in range(number_of_rays)]

def create_pixel_data_board(width: int, height: int) -> List[List[float]]:
    """Function for creating a 2D board."""
    return [[0.0 for _ in range(width)] for _ in range(height)]

def create_ray_board(width: int, height: int) -> List[List[Ray]]:
    """Function for creating a 2D board for rays."""
    return [[None for _ in range(width)] for _ in range(height)]

def insert_rays_into_board(rays: List[Ray], Board: List[List[Ray]]) -> None:
    """Function for inserting rays into a board."""
    for ray in rays:
        Board[ray.board_y][ray.board_x] = ray

def handle_events() -> None:
    """Function for handling events."""

    for ev in event.get():
        quit_game(ev)

def quit_game(event: event.Event) -> None:
    """Function for quitting the game."""
    
    if event.type == QUIT:
        sys.exit()

def update_Trace_Board(Trace_Board: List[List[float]], Ray_fade_speed: float) -> None:
    """Function for updating each cell in the trace board."""
    
    for y in range(len(Trace_Board)):
        for x in range(len(Trace_Board[y])):
            
            update_Trace_Board_Cell(Trace_Board, x, y, Ray_fade_speed)

def update_Trace_Board_Cell(Trace_Board: List[List[float]], x: int, y: int, Ray_fade_speed: float) -> None:
    """Function for updating a single cell in the trace board."""
    
    if Trace_Board[y][x] > 0.0:
        Trace_Board[y][x] -= Ray_fade_speed

def update_Ray_Board(Ray_Board: List[List[Ray]], Trace_Board: List[List[float]], Rays: List[Ray]) -> None:
    """Function for updating each cell in the ray board."""
    for ray in Rays:
        Trace_Board[ray.board_y][ray.board_x] = 1
        ray.diffuse_ray(Trace_Board)
        ray.update(Ray_Board)
        ray.attract_to_neighbour(Ray_Board)

def update_Ray_Board_Cell(Ray_Board: List[List[Ray]], x: int, y: int) -> None:
    """Function for updating a single cell in the ray board."""

    if Ray_Board[y][x] is not None:
        Ray_Board[y][x].diffuse_ray(Ray_Board)
        Ray_Board[y][x].update(Ray_Board)
        Ray_Board[y][x].attract_to_neighbour(Ray_Board)

def draw_Trace_Board(Trace_Board: List[List[float]], screen: Surface) -> None:
    """Function for drawing the trace board on the screen."""
    
    for y in range(len(Trace_Board)):
        for x in range(len(Trace_Board[y])):
            if Trace_Board[y][x] > 0.0:
                draw.rect(screen, (int(Trace_Board[y][x]*255), int(Trace_Board[y][x]*255), int(Trace_Board[y][x]*255)), (x*pixel_size, y*pixel_size, pixel_size, pixel_size))

def main() -> None: 
    """Main function for running the program."""
    
    tick = 60                   
    clock = tm.Clock()          
    game = True

    # Ray settings # 
    number_of_rays = 100
    Ray_fade_speed = 0.02
    
    Rays: List[Ray] = create_rays(number_of_rays)
    Trace_Board: List[List[float]] = create_pixel_data_board(width, height)                                   
    Ray_Board: List[List[Ray]] = create_ray_board(width, height)
    insert_rays_into_board(Rays, Ray_Board)

    while game:

        handle_events()

        update_Trace_Board(Trace_Board, Ray_fade_speed)
        update_Ray_Board(Ray_Board, Trace_Board, Rays)  

        screen.fill(Black)
        draw_Trace_Board(Trace_Board, screen)
        display.update()
        
        clock.tick(tick)

if __name__ == "__main__":
    main()