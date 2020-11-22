import cocos
from cocos.euclid import *

RED = (227, 99, 135)
PINK = (239, 187, 207)
YELLOW = (255, 211, 105)


def center_position(v1, v2):
    return (v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2


class Grid:
    def __init__(self, position, index, master_layer, layer):
        self.master_layer = master_layer
        self.layer = layer
        self.index = index

        self.position = position
        self.border = {"NW": (position[0] - self.master_layer.grid_size / 2, position[1] + self.master_layer.grid_size / 2),
                       "SE": (position[0] + self.master_layer.grid_size / 2, position[1] - self.master_layer.grid_size / 2)}

        self.box_ins = Box(position, self.master_layer.grid_scale, index, color=(111, 189, 196))
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


class Obstacle(Actor):
    def __init__(self, position, scale, index):
        super(Obstacle, self).__init__(position=position, scale=scale, image='img/grid.png', index=index)
        self.color = (255, 255, 255)


class Mirror(Actor):
    def __init__(self, position, scale, image, index, rotation, reflect):
        super(Mirror, self).__init__(position=position, scale=scale/1.1, image=image, index=index)
        self.mirror_rotation = rotation  # \ = -1, / = 1
        self.reflect_percent = reflect
        self.through_percent = 100 - reflect

        self.init_direction()

    def init_direction(self):
        if self.mirror_rotation == 1:
            self.rotation = 45
        elif self.mirror_rotation == -1:
            self.rotation = -45

    def reflect(self, from_dir):
        if self.mirror_rotation == -1:
            if from_dir == 0:
                return 3
            elif from_dir == 1:
                return 2
            elif from_dir == 2:
                return 1
            elif from_dir == 3:
                return 0
        else:
            if from_dir == 0:
                return 1
            elif from_dir == 1:
                return 0
            elif from_dir == 2:
                return 3
            elif from_dir == 3:
                return 2


class MovableMirror(Mirror):
    def __init__(self, position, scale, index, rotation, reflect):
        super(MovableMirror, self).__init__(position=position, scale=scale, image='img/movablemirror.png',
                                            index=index, rotation=rotation, reflect=reflect)


class StaticMirror(Mirror):
    def __init__(self, position, scale, index, rotation, reflect):
        super(StaticMirror, self).__init__(position=position, scale=scale, image='img/staticmirror_mint.png',
                                           index=index, rotation=rotation, reflect=reflect)


class RotatableMirror(Mirror):
    def __init__(self, position, scale, index, rotation, reflect):
        super(RotatableMirror, self).__init__(position=position, scale=scale, image='img/rotatablemirror_mint.png',
                                              index=index, rotation=rotation, reflect=reflect)

    def rotate_mirror(self):
        self.do(cocos.actions.RotateBy(90, 0.5))
        self.mirror_rotation *= -1


# direction
# -1(N) 0(↑) 1(→) 2(↓) 3(←)


class StartNode(Actor):
    def __init__(self, position, scale, index, direction, color):
        super(StartNode, self).__init__(position=position, scale=scale, index=index, image='img/startnode.png')
        self.direction = direction
        self.color = color

        self.init_direction()

    def init_direction(self):
        self.rotation = self.direction * 90


class EndNode(Actor):
    def __init__(self, position, scale, index, color, direction=-1):
        if direction == -1:
            super(EndNode, self).__init__(position=position, scale=scale/1.1, index=index, image='img/endnode_nond.png')
        else:
            super(EndNode, self).__init__(position=position, scale=scale, index=index, image='img/endnode.png')
        self.activated_color = color
        self.direction = direction

        self.init_direction()

    def init_direction(self):
        self.rotation = self.direction * 90

    def activated(self):
        self.color = self.activated_color


class Game(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, grid_layer, line_layer):
        super(Game, self).__init__()
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


if __name__ == "__main__":
    cocos.director.director.init(caption='Reflect', width=1000, height=1000)
    grid_layer = cocos.layer.Layer()
    line_layer = cocos.layer.Layer()
    scene = cocos.scene.Scene(cocos.layer.ColorLayer(255, 255, 255, 255), grid_layer, line_layer, Game(grid_layer, line_layer))
    cocos.director.director.run(scene)
