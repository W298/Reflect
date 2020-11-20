import cocos
from cocos.euclid import *


def center_position(v1, v2):
    return (v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2


class Grid:
    def __init__(self, position, index, layer):
        self.layer = layer
        self.index = index

        self.position = position
        self.border = {"NW": (position[0] - self.layer.grid_size / 2, position[1] + self.layer.grid_size / 2),
                       "SE": (position[0] + self.layer.grid_size / 2, position[1] - self.layer.grid_size / 2)}

        self.box_ins = Box(position, self.layer.grid_scale, index, color=(111, 189, 196))
        self.layer.add(self.box_ins)

        self.item_ins = None

    def check_clicked(self, check_pos):
        return self.border["NW"][0] <= check_pos[0] <= self.border["SE"][0] and self.border["SE"][1] <= check_pos[1] <= \
               self.border["NW"][1]

    def move_item(self, target_grid):
        target_grid.item_ins = self.item_ins
        target_grid.item_ins.position = target_grid.position
        target_grid.item_ins.index = target_grid.index
        self.item_ins = None


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


# direction
# -1(N) 0(↑) 1(→) 2(↓) 3(←)


class StartNode(Actor):
    def __init__(self, position, scale, index, direction):
        super(StartNode, self).__init__(position=position, scale=scale, index=index, image='img/startnode.png')
        self.direction = direction

        self.init_direction()

    def init_direction(self):
        self.rotation = self.direction * 90


class EndNode(Actor):
    def __init__(self, position, scale, index, direction=-1):
        super(EndNode, self).__init__(position=position, scale=scale, index=index, image='img/endnode.png')
        self.direction = direction

        self.init_direction()

    def init_direction(self):
        self.rotation = self.direction * 90


class Game(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(Game, self).__init__()
        self.screen_size = cocos.director.director.get_window_size()

        self.matrix = []
        self.mirror_list = []
        self.start_node = None
        self.end_node_list = []
        self.line_list = []

        self.grid_count = (5, 5)
        self.gap_percent = (25, 1)
        self.border_gap = 10

        self.checking_grid = None

        self.gap_size = 0
        self.grid_size = 0
        self.grid_scale = 0

        self.init_grid()

        self.spawn_line((0, 1), (1, 1))
        self.spawn_line((1, 1), (1, 2))
        self.spawn_line((1, 2), (2, 2))

        self.spawn_start_node((0, 1), 1)
        self.spawn_end_node((4, 4))

        self.spawn_mirror(RotatableMirror, (3, 3), -1, 100)
        self.spawn_mirror(StaticMirror, (1, 1), 1, 100)
        self.spawn_mirror(MovableMirror, (2, 2), 1, 100)
        self.spawn_mirror(MovableMirror, (0, 0), -1, 100)

        self.schedule(self.update)

    def init_grid(self):
        grid_count_max = max(self.grid_count[0], self.grid_count[1])
        self.gap_size = (self.screen_size[0] - self.border_gap * 2) / (
                grid_count_max * self.gap_percent[0] + (grid_count_max - 1) * self.gap_percent[1])
        self.grid_size = self.gap_size * self.gap_percent[0]
        self.grid_scale = self.grid_size / 2000

        first = self.border_gap + self.grid_size / 2

        for x in range(self.grid_count[0]):
            t_list = []
            for y in range(self.grid_count[1]):
                x_pos = first + x * (self.grid_size + self.gap_size)
                y_pos = first + y * (self.grid_size + self.gap_size)

                grid = Grid((x_pos, y_pos), (x, y), self)
                t_list.append(grid)
            self.matrix.append(t_list)

    def spawn_line(self, from_index, to_index):
        rotation = 0
        if from_index[1] != to_index[1]:
            rotation = 90

        l = cocos.sprite.Sprite(image='img/Line.png',
                                position=center_position(self.matrix[from_index[0]][from_index[1]].position,
                                                         self.matrix[to_index[0]][to_index[1]].position),
                                scale=self.grid_scale / 1,
                                color=(181, 178, 255),
                                rotation=rotation)

        self.line_list.append(l)
        self.add(l)

    def spawn_mirror(self, c, index, direction, reflex):
        m = c(self.matrix[index[0]][index[1]].position, self.grid_scale / 1.3, index, direction, reflex)
        self.matrix[index[0]][index[1]].item_ins = m
        self.mirror_list.append(m)
        self.add(m)

    def spawn_start_node(self, index, direction):
        s = StartNode(self.matrix[index[0]][index[1]].position, self.grid_scale / 1.3, index, direction)
        self.matrix[index[0]][index[1]].item_ins = s
        self.start_node = s
        self.add(s)

    def spawn_end_node(self, index, direction=-1):
        e = EndNode(self.matrix[index[0]][index[1]].position, self.grid_scale / 1.3, index, direction)
        self.matrix[index[0]][index[1]].item_ins = e
        self.end_node_list.append(e)
        self.add(e)

    def get_grid(self, position):
        for x_i in range(self.grid_count[0]):
            for y_i in range(self.grid_count[1]):
                if self.matrix[x_i][y_i].check_clicked((position[0], position[1])):
                    return self.matrix[x_i][y_i]
        return None

    def on_mouse_press(self, x, y, buttons, modifiers):
        grid = self.get_grid((x, y))
        if grid is None:
            return
        self.checking_grid = grid

        if self.checking_grid.item_ins is not None:
            if isinstance(self.checking_grid.item_ins, RotatableMirror):
                self.checking_grid.item_ins.rotate_mirror()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        grid = self.get_grid((x + dx, y + dy))
        if grid is None:
            return

        if self.checking_grid is not None:
            if self.checking_grid != grid:
                if grid.item_ins is None and self.checking_grid.item_ins is not None and isinstance(
                        self.checking_grid.item_ins, MovableMirror):
                    self.checking_grid.move_item(grid)

                self.checking_grid = grid

    def update(self, dt):
        return


if __name__ == "__main__":
    cocos.director.director.init(caption='Reflect', width=1000, height=1000)
    scene = cocos.scene.Scene(cocos.layer.ColorLayer(255, 255, 255, 255), Game())
    cocos.director.director.run(scene)
