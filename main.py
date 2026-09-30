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
        

    def handle_vertical_boundary(self) -> None:
        if self.board_x < 0:
            self.board_x = 0
            self.precise_x = 0
            self.Angle = math.pi - self.Angle

        elif self.board_x >= width:
            self.board_x = width - 1
            self.precise_x = width - 1
            self.Angle = math.pi - self.Angle

    
    def handle_horizontal_boundary(self) -> None:
        if self.board_y < 0:
            self.board_y = 0
            self.precise_y = 0
            self.Angle = -self.Angle

        elif self.board_y >= height:
            self.board_y = height - 1
            self.precise_y = height - 1
            self.Angle = -self.Angle

    def move(self):
        self.precise_x += self.speed * math.cos(self.Angle)
        self.board_x = int(round(self.precise_x, 0))
        self.precise_y += self.speed * math.sin(self.Angle)
        self.board_y = int(round(self.precise_y, 0))

    def update_board_position(self,Board: List[List[Ray]],prev_x,prev_y)->None:
        
        Board[prev_y][prev_x] = None
        Board[self.board_y][self.board_x] = self

    def handle_boundaries(self) -> None:
        self.handle_vertical_boundary()
        self.handle_horizontal_boundary()

        self.Angle %= 2 * math.pi

    def update(self,Board: List[List[Ray]])->None:
        """Function for moving a ray."""
        
        prev_x = self.board_x
        prev_y = self.board_y
    
        # Move pixel
        self.move()

        # each code block that fixes if the ray goes outside the bounds of the screen can be a separate function
        
        self.handle_boundaries()
        
        # Edit board
        self.update_board_position(Board,prev_x,prev_y)

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

                        neighbour = Board[self.board_y + y][self.board_x + x]
                        if neighbour is not None:

                            net_distance = 1/math.sqrt(x**2 + y**2)
                            delta_x = neighbour.board_x - self.board_x
                            delta_y = neighbour.board_y - self.board_y

                            target_angle = math.atan2(delta_y, delta_x)
                            delta_angle = (target_angle - self.Angle + math.pi) % (2 * math.pi) - math.pi
                            additional_angle = angle_weight * net_distance * delta_angle
                            self.Angle += additional_angle

    def draw(self, screen: Surface) -> None:
        """Function for drawing a ray on the screen."""
        draw.rect(screen, self.colour, self._bounding_ray_rectangle())

    def _bounding_ray_rectangle(self) -> Tuple[int, int, int, int]:
        return (self.board_x*pixel_size, self.board_y*pixel_size, pixel_size, pixel_size)

def create_rays(number_of_rays: int, spawn_radius: int = 10) -> List[Ray]:
    """Function for creating a list of rays at unique random positions around the centre."""
    centre_x, centre_y = width // 2, height // 2
    cells = [(x, y)
             for x in range(centre_x - spawn_radius, centre_x + spawn_radius + 1)
             for y in range(centre_y - spawn_radius, centre_y + spawn_radius + 1)]
    positions = random.sample(cells, number_of_rays)
    return [Ray(Point(x, y), Motion(random.uniform(0, 2*math.pi), 0.75), White, "A") for x, y in positions]

def create_trace_board(width: int, height: int) -> List[List[float]]:
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


def update_trace_board(Rays: List[Ray], Trace_Board: List[List[float]], Ray_fade_speed: float) -> None:
    """Function for updating the trace board."""
    
    stamp_rays_on_trace_board(Rays, Trace_Board)
    diffuse_rays_on_trace_board(Rays, Trace_Board)
    fade_rays_on_trace_board(Trace_Board, Ray_fade_speed)

def stamp_rays_on_trace_board(Rays: List[Ray], Trace_Board: List[List[float]]) -> None:
    """Function for stamping rays on the trace board."""
    
    for ray in Rays:
        Trace_Board[ray.board_y][ray.board_x] = 1

def diffuse_rays_on_trace_board(Rays: List[Ray], Trace_Board: List[List[float]]) -> None:
    """Function for diffusing rays on the trace board."""
    
    for ray in Rays:
        ray.diffuse_ray(Trace_Board)

def fade_rays_on_trace_board(Trace_Board: List[List[float]], Ray_fade_speed: float) -> None:
    """Function for fading rays on the trace board."""
    
    for y in range(len(Trace_Board)):
        for x in range(len(Trace_Board[y])):
            if Trace_Board[y][x] > 0.0:
                Trace_Board[y][x] -= Ray_fade_speed
                if Trace_Board[y][x] < 0.0:
                    Trace_Board[y][x] = 0.0


def update_ray_board(Rays: List[Ray], Ray_Board: List[List[Ray]]) -> None:
    """Function for updating the ray board."""

    update_rays(Rays, Ray_Board)
    steer_rays_towards_nearby_rays(Rays, Ray_Board)

def update_rays(Rays: List[Ray], Ray_Board: List[List[Ray]]) -> None:
    """Function for updating rays on the ray board."""
    
    for ray in Rays:
        ray.update(Ray_Board)

def steer_rays_towards_nearby_rays(Rays: List[Ray], Ray_Board: List[List[Ray]]) -> None:
    """Function for steering rays towards nearby rays."""
    
    for ray in Rays:
        ray.attract_to_neighbour(Ray_Board)


def draw(screen: Surface, Trace_Board: List[List[float]]) -> None:
    """Function for drawing the rays and trace board on the screen."""
    screen.fill(Black)
    draw_Trace_Board(Trace_Board, screen)

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
    spawn_radius = 10
    Ray_fade_speed = 0.02
    
    Rays: List[Ray] = create_rays(number_of_rays, spawn_radius)
    Trace_Board: List[List[float]] = create_trace_board(width, height)                                   
    Ray_Board: List[List[Ray]] = create_ray_board(width, height)
    insert_rays_into_board(Rays, Ray_Board)

    while game:

        handle_events()

        update_trace_board(Rays, Trace_Board, Ray_fade_speed)
        update_ray_board(Rays, Ray_Board)
        
        draw(screen, Trace_Board)
        
        display.update()
        clock.tick(tick)

if __name__ == "__main__":
    main()