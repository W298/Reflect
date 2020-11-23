import cocos
from cocos.euclid import *

from GameObject import *

# COLOR RGB
RED = (227, 99, 135)
PINK = (239, 187, 207)
YELLOW = (255, 211, 105)


def center_position(v1, v2):
    return (v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2


class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, grid_layer, line_layer):
        super(GameLayer, self).__init__()
        self.screen_size = cocos.director.director.get_window_size()

        self.grid_layer = grid_layer
        self.line_layer = line_layer

        self.matrix = []
        self.mirror_list = []
        self.start_node_list = []
        self.end_node_list = []
        self.line_list = []
        self.obs_list = []

        self.grid_count = (5, 5)
        self.gap_percent = (25, 1)
        self.border_gap = 10

        self.checking_grid = None

        self.gap_size = 0
        self.grid_size = 0
        self.grid_scale = 0

        self.init_grid()

        self.spawn_start_node((0, 0), 1, YELLOW)
        self.spawn_start_node((1, 4), 1, RED)

        self.spawn_end_node((2, 2), YELLOW)
        self.spawn_end_node((0, 1), RED)

        self.spawn_obs((1, 1))
        self.spawn_obs((2, 1))
        self.spawn_obs((3, 1))
        self.spawn_obs((1, 2))
        self.spawn_obs((3, 2))

        self.spawn_mirror(RotatableMirror, (4, 3), 1, 100)
        self.spawn_mirror(StaticMirror, (4, 0), 1, 100)

        self.spawn_mirror(MovableMirror, (0, 2), 1, 100)
        self.spawn_mirror(MovableMirror, (0, 3), -1, 100)
        self.spawn_mirror(MovableMirror, (0, 4), 1, 100)

        self.schedule(self.update)

    # direction
    # -1(N) 0(↑) 1(→) 2(↓) 3(←)

    def update_line(self):
        for l in self.line_list:
            self.line_layer.remove(l)
        self.line_list.clear()
        for e in self.end_node_list:
            e.color = (255, 255, 255)

        for s in self.start_node_list:
            self.search_next(s.index, s.direction, s.color)

    def search_next(self, origin_index, direction, color):
        next_index = (-1, -1)
        if direction == 0:
            next_index = (origin_index[0], origin_index[1] + 1)
        elif direction == 1:
            next_index = (origin_index[0] + 1, origin_index[1])
        elif direction == 2:
            next_index = (origin_index[0], origin_index[1] - 1)
        elif direction == 3:
            next_index = (origin_index[0] - 1, origin_index[1])

        if 0 <= next_index[0] < self.grid_count[0] and 0 <= next_index[1] < self.grid_count[1]:
            next_grid = self.matrix[next_index[0]][next_index[1]]
            self.spawn_line(origin_index, next_index, color)

            if next_grid.item_ins is not None:
                if isinstance(next_grid.item_ins, Mirror):
                    self.search_next(next_index, next_grid.item_ins.reflect(direction), color)
                elif isinstance(next_grid.item_ins, EndNode):
                    if next_grid.item_ins.direction == -1 or abs(direction - next_grid.item_ins.direction) == 2:
                        if tuple(next_grid.item_ins.activated_color) == tuple(color):
                            next_grid.item_ins.activated()
                    return
            else:
                self.search_next(next_index, direction, color)
        else:
            origin_pos = self.matrix[origin_index[0]][origin_index[1]].position
            next_pos = (-1, -1)
            adder = self.grid_size + self.gap_size
            if direction == 0:
                next_pos = (origin_pos[0], origin_pos[1] + adder)
            elif direction == 1:
                next_pos = (origin_pos[0] + adder, origin_pos[1])
            elif direction == 2:
                next_pos = (origin_pos[0], origin_pos[1] - adder)
            elif direction == 3:
                next_pos = (origin_pos[0] - adder, origin_pos[1])

            self.spawn_line_pos(origin_pos, next_pos, color)
            return

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

                grid = Grid((x_pos, y_pos), (x, y), self, self.grid_layer)
                t_list.append(grid)
            self.matrix.append(t_list)

    def spawn_line(self, from_index, to_index, color):
        rotation = 0
        if from_index[1] != to_index[1]:
            rotation = 90

        l = cocos.sprite.Sprite(image='img/Line.png',
                                position=center_position(self.matrix[from_index[0]][from_index[1]].position,
                                                         self.matrix[to_index[0]][to_index[1]].position),
                                scale=self.grid_scale / 1,
                                color=color,
                                rotation=rotation)

        self.line_list.append(l)
        self.line_layer.add(l)

    def spawn_line_pos(self, from_pos, to_pos, color):
        rotation = 0
        if from_pos[1] != to_pos[1]:
            rotation = 90

        l = cocos.sprite.Sprite(image='img/Line.png',
                                position=center_position(from_pos, to_pos),
                                scale=self.grid_scale / 1,
                                color=color,
                                rotation=rotation)

        self.line_list.append(l)
        self.line_layer.add(l)

    def spawn_obs(self, index):
        o = Obstacle(self.matrix[index[0]][index[1]].position, self.grid_scale, index)
        self.matrix[index[0]][index[1]].item_ins = o
        self.obs_list.append(o)
        self.add(o)

    def spawn_mirror(self, c, index, direction, reflect):
        m = c(self.matrix[index[0]][index[1]].position, self.grid_scale / 1.3, index, direction, reflect)
        self.matrix[index[0]][index[1]].item_ins = m
        self.mirror_list.append(m)
        self.add(m)

    def spawn_start_node(self, index, direction, color):
        s = StartNode(self.matrix[index[0]][index[1]].position, self.grid_scale / 1.3, index, direction, color)
        self.matrix[index[0]][index[1]].item_ins = s
        self.start_node_list.append(s)
        self.add(s)

    def spawn_end_node(self, index, color, direction=-1):
        e = EndNode(self.matrix[index[0]][index[1]].position, self.grid_scale / 1.3, index, color, direction)
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
        self.update_line()
        return
