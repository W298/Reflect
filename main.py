import cocos
from cocos.euclid import *


class Grid:
    def __init__(self, position, index, layer):
        self.layer = layer
        self.index = index

        self.position = position
        self.border = {"NW": (position[0] - self.layer.grid_size/2, position[1] + self.layer.grid_size/2),
                       "SE": (position[0] + self.layer.grid_size/2, position[1] - self.layer.grid_size/2)}

        self.box_ins = Box(position, self.layer.grid_scale, index, color=(111, 189, 196))
        self.layer.add(self.box_ins)

        self.item_ins = None

    def check_clicked(self, check_pos):
        return self.border["NW"][0] <= check_pos[0] <= self.border["SE"][0] and self.border["SE"][1] <= check_pos[1] <= self.border["NW"][1]


class Actor(cocos.sprite.Sprite):
    def __init__(self, position, scale, image, index):
        super(Actor, self).__init__(position=position, scale=scale, image=image)
        self.index = index


class Box(Actor):
    def __init__(self, position, scale, index, color):
        super(Box, self).__init__(position=position, scale=scale, image='img/grid.png', index=index)
        self.color = color


class Mirror(Actor):
    def __init__(self, position, scale, image, index, direction, reflex):
        super(Mirror, self).__init__(position=position, scale=scale, image=image, index=index)
        self.direction = direction  # \ = -1, / = 1
        self.reflex_percent = reflex
        self.through_percent = 100 - reflex

        self.init_direction()

    def init_direction(self):
        if self.direction == 1:
            self.rotation = 45
        elif self.direction == -1:
            self.rotation = -45

    def move_mirror(self, position):
        self.position = position
        self.update_index()

    def update_index(self):
        print("Updated")


class MovableMirror(Mirror):
    def __init__(self, position, scale, index, direction, reflex):
        super(MovableMirror, self).__init__(position=position, scale=scale, image='img/movablemirror.png',
                                            index=index, direction=direction, reflex=reflex)


class StaticMirror(Mirror):
    def __init__(self, position, scale, index, direction, reflex):
        super(StaticMirror, self).__init__(position=position, scale=scale, image='img/staticmirror.png',
                                           index=index, direction=direction, reflex=reflex)


class RotatableMirror(Mirror):
    def __init__(self, position, scale, index, direction, reflex):
        super(RotatableMirror, self).__init__(position=position, scale=scale, image='img/rotatablemirror.png',
                                              index=index, direction=direction, reflex=reflex)

    def rotate_mirror(self):
        self.do(cocos.actions.RotateBy(90, 0.5))
        self.direction *= -1


class Game(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(Game, self).__init__()
        self.screen_size = cocos.director.director.get_window_size()

        self.matrix = []
        self.mirror_list = []

        self.grid_count = (5, 5)
        self.gap_percent = (25, 1)
        self.border_gap = 10

        self.checking_grid = None

        grid_count_max = max(self.grid_count[0], self.grid_count[1])
        self.gap_size = (self.screen_size[0] - self.border_gap * 2) / (grid_count_max * self.gap_percent[0] + (grid_count_max - 1) * self.gap_percent[1])
        self.grid_size = self.gap_size * self.gap_percent[0]
        self.grid_scale = self.grid_size/2000

        first = self.border_gap + self.grid_size/2

        for x in range(self.grid_count[0]):
            t_list = []
            for y in range(self.grid_count[1]):
                x_pos = first + x * (self.grid_size + self.gap_size)
                y_pos = first + y * (self.grid_size + self.gap_size)

                grid = Grid((x_pos, y_pos), (x, y), self)
                t_list.append(grid)
            self.matrix.append(t_list)

        self.m = RotatableMirror(self.matrix[3][3].position, self.grid_scale/1.3, (3, 3), -1, 100)
        self.matrix[3][3].item_ins = self.m
        self.mirror_list.append(self.m)
        self.add(self.m)

        self.m2 = StaticMirror(self.matrix[1][1].position, self.grid_scale/1.3, (1, 1), 1, 100)
        self.matrix[1][1].item_ins = self.m2
        self.mirror_list.append(self.m2)
        self.add(self.m2)

        self.schedule(self.update)

    def get_grid(self, position):
        for x_i in range(self.grid_count[0]):
            for y_i in range(self.grid_count[1]):
                if self.matrix[x_i][y_i].check_clicked((position[0], position[1])):
                    return self.matrix[x_i][y_i]

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.checking_grid = self.get_grid((x, y))

        if self.checking_grid.item_ins is not None:
            if isinstance(self.checking_grid.item_ins, RotatableMirror):
                self.checking_grid.item_ins.rotate_mirror()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        grid = self.get_grid((x + dx, y + dy))

        if self.checking_grid is not None:
            if self.checking_grid != grid:
                if self.checking_grid.item_ins is not None and isinstance(self.checking_grid.item_ins, MovableMirror):
                    grid.item_ins = self.checking_grid.item_ins
                    grid.item_ins.position = grid.position
                    grid.item_ins.index = grid.index
                    self.checking_grid.item_ins = None

                self.checking_grid = grid

    def update(self, dt):
        return


if __name__ == "__main__":
    cocos.director.director.init(caption='Reflect', width=1000, height=1000)
    scene = cocos.scene.Scene(cocos.layer.ColorLayer(255, 255, 255, 255), Game())
    cocos.director.director.run(scene)
