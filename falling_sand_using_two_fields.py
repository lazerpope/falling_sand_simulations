from colorsys import hsv_to_rgb
from copy import deepcopy, copy
import pygame as pg
from random import randint
from time import perf_counter, perf_counter_ns
from typing import Optional

pgColorOrNone = Optional[pg.Color]


def main():
    def get_empty_field(w: int, h: int) -> list[list[pgColorOrNone]]:
        return [[None for _ in range(w)] for _ in range(h)]

    def move_sand(
        x: int,
        y: int,
        field: list[list[pgColorOrNone]],
        new_field: list[list[pgColorOrNone]],
        Y_CELLS:int,
        X_CELLS:int
    ) -> None:

        if y + 1 < Y_CELLS and field[y + 1][x] is None and new_field[y + 1][x] is None:
            new_field[y + 1][x] = field[y][x]
            return
        
        sand_go_right = randint(0, 1)  == 0
        if sand_go_right:
            if (
                x + 1 < X_CELLS
                and y + 1 < Y_CELLS
                and field[y + 1][x + 1] is None
                and new_field[y + 1][x + 1] is None
            ):
                new_field[y + 1][x + 1] = field[y][x]
                return

        else:
            if (
                x - 1 >= 0
                and y + 1 < Y_CELLS
                and field[y + 1][x - 1] is None
                and new_field[y + 1][x - 1] is None
            ):
                new_field[y + 1][x - 1] = field[y][x]
                return
            
        new_field[y][x] = field[y][x]

    WIDTH = 1200
    HEIGHT = 800
    FPS = 60
    CELL_SIZE = 5
    Y_CELLS = HEIGHT // CELL_SIZE
    X_CELLS = WIDTH // CELL_SIZE
    SAND_SPAWN_RATE = 33
    SAND_SPAWN_RANGE = 5

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    pg.init()
    pg.mixer.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("My Game")
    clock = pg.time.Clock()
    font = pg.font.Font(None, 20)

    running = True
    color_hue = randint(0, 100) / 100

    field = get_empty_field(X_CELLS, Y_CELLS)

    pile = 0
    fps_index = 0
    fps_list = [FPS for _ in range(5)]

    while running:
        screen.fill(BLACK)
        start = perf_counter()

        for event in pg.event.get():
            # print(event)
            if event.type == pg.QUIT:
                running = False

        # ----------------- сыпем песочек мышкой
        if pg.mouse.get_pressed()[0]:
            color_hue += 0.001
            if color_hue > 1:
                color_hue = 0
            rgb_color_as_float = hsv_to_rgb(color_hue, 0.95, 0.96)
            rgb_color = [int(rgb_color_as_float[i] * 255) for i in range(3)]
            new_sand_color = pg.Color(*rgb_color)
            x, y = pg.mouse.get_pos()
            x = x // CELL_SIZE
            y = y // CELL_SIZE
            for _ in range(SAND_SPAWN_RATE):
                cx = x + randint(-SAND_SPAWN_RANGE, SAND_SPAWN_RANGE)
                cy = y + randint(-SAND_SPAWN_RANGE, SAND_SPAWN_RANGE)
                if (
                    cx < X_CELLS
                    and cy < Y_CELLS
                    and cx >= 0
                    and cy >= 0
                    and field[cy][cx] is None
                ):
                    pile += 1
                    field[cy][cx] = new_sand_color

        new_field = get_empty_field(X_CELLS, Y_CELLS)

        start = perf_counter_ns()

        # ----------------- двигаем песочек
        [
            [
                move_sand(x, y, field, new_field, Y_CELLS,X_CELLS)
                for x in range(X_CELLS)
                if field[y][x] is not None
            ]
            for y in range(Y_CELLS)
        ]

        end = perf_counter_ns()
        sand_fall_calc_ms = (end - start) // 1_00_000 / 10

     
        field = copy(new_field)
       

        # ----------------- рисуем песочек
        start = perf_counter_ns()
        [
            [
                pg.draw.rect(
                    screen,
                    field[y][x], #type:ignore
                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )
                for x in range(X_CELLS)
                if field[y][x] is not None
            ]
            for y in range(Y_CELLS)
        ]
        end = perf_counter_ns()

        draw_sand_ms = (end - start) // 1_00_000 / 10

        # ----------------- мерим фепас
        fps_index += 1
        if fps_index == 5:
            fps_index = 0
        fps_list[fps_index] = clock.get_fps()
        fps = sum(fps_list) / 5

        # ----------------- отладочные сообщения
        text = font.render(f"FPS: {fps:.1f}", True, WHITE)
        screen.blit(text, (10, 10))
        text = font.render(f"sand: {pile}", True, WHITE)
        screen.blit(text, (10, 40))
        # actual_sand = sum(1 for row in field for element in row if element is not None)
        # text = font.render(f"sand: {actual_sand}", True, WHITE)
        # screen.blit(text, (10, 70))
        # text = font.render(f"lost: {pile-actual_sand}", True, WHITE)
        # screen.blit(text, (10, 100))

        text = font.render(
            f"{sand_fall_calc_ms=}    {draw_sand_ms=}", True, WHITE
        )
        screen.blit(text, (10, 70))

        # print(f"{sand_fall_calc_ms=} {copy_field_ms=} {draw_sand_ms=}")
        pg.display.flip()
        clock.tick(FPS)

    pg.quit()


if __name__ == "__main__":
    main()
