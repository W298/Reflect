import cocos
from cocos.euclid import *

# direction
# -1(N) 0(↑) 1(→) 2(↓) 3(←)


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
    def __init__(self, position, scale, image, index, rotation, reflect, GameLayer):
        super(Mirror, self).__init__(position=position, scale=scale/1.1, image=image, index=index)
        self.mirror_rotation = rotation  # \ = -1, / = 1
        self.reflect_percent = reflect
        self.through_percent = 100 - reflect
        self.GameLayer = GameLayer
        self.indi = None

        self.init_direction()
        self.draw_indi()

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

    def draw_indi(self):
        if self.indi:
            self.GameLayer.remove(self.indi)

        t = cocos.text.Label(str(int(self.reflect_percent)),
                             position=(self.position[0], self.position[1] - self.GameLayer.grid_size / 3),
                             font_size=self.GameLayer.grid_size / 8, color=(255, 255, 255, 255),
                             anchor_x="center", anchor_y="center", bold=True,
                             font_name="Cascadia Code")
        self.GameLayer.add(t)
        self.indi = t
        return t


class MovableMirror(Mirror):
    def __init__(self, position, scale, index, rotation, reflect, GameLayer):
        super(MovableMirror, self).__init__(position=position, scale=scale, image='img/movablemirror.png',
                                            index=index, rotation=rotation, reflect=reflect, GameLayer=GameLayer)


class StaticMirror(Mirror):
    def __init__(self, position, scale, index, rotation, reflect, GameLayer):
        super(StaticMirror, self).__init__(position=position, scale=scale, image='img/staticmirror_mint.png',
                                           index=index, rotation=rotation, reflect=reflect, GameLayer=GameLayer)


class RotatableMirror(Mirror):
    def __init__(self, position, scale, index, rotation, reflect, GameLayer):
        super(RotatableMirror, self).__init__(position=position, scale=scale, image='img/rotatablemirror_mint.png',
                                              index=index, rotation=rotation, reflect=reflect, GameLayer=GameLayer)

    def rotate_mirror(self):
        self.do(cocos.actions.RotateBy(90, 0.5))
        self.mirror_rotation *= -1


class StartNode(Actor):
    def __init__(self, position, scale, index, direction, color, strength, GameLayer):
        super(StartNode, self).__init__(position=position, scale=scale, index=index, image='img/startnode.png')
        self.direction = direction
        self.color = color
        self.GameLayer = GameLayer
        self.strength = strength
        self.indi = None

        self.init_direction()
        self.draw_indi()

    def init_direction(self):
        self.rotation = self.direction * 90

    def draw_indi(self):
        if self.indi:
            self.GameLayer.remove(self.indi)

        t = cocos.text.Label(str(int(self.strength)),
                             position=(self.position[0], self.position[1] - self.GameLayer.grid_size / 3),
                             font_size=self.GameLayer.grid_size / 8, color=(self.color[0], self.color[1], self.color[2], 255),
                             anchor_x="center", anchor_y="center", bold=True,
                             font_name="Cascadia Code")
        self.GameLayer.add(t)
        self.indi = t
        return t


class EndNode(Actor):
    def __init__(self, position, scale, index, color, goal_strength, GameLayer, direction=-1):
        if direction == -1:
            super(EndNode, self).__init__(position=position, scale=scale/1.1, index=index, image='img/endnode_nond.png')
        else:
            super(EndNode, self).__init__(position=position, scale=scale, index=index, image='img/endnode.png')
        self.activated_color = color
        self.isActivated = False
        self.isConnected = False
        self.index = index
        self.line_list = []
        self.direction = direction
        self.current_strength = 0
        self.goal_strength = goal_strength
        self.GameLayer = GameLayer
        self.indi = None

        self.init_direction()

    def add_strength(self, add):
        self.isConnected = True
        self.current_strength += add
        self.draw_indi()
        self.check_is_activated()
        self.current_strength -= add

    def init_direction(self):
        self.rotation = self.direction * 90

    def activated(self):
        self.color = self.activated_color
        self.isActivated = True

    def check_is_activated(self):
        if self.current_strength == self.goal_strength:
            self.activated()

    def check_connection(self):
        if self.isConnected:
            self.isConnected = False
        else:
            self.draw_indi()

    def draw_indi(self):
        if self.indi:
            self.GameLayer.remove(self.indi)

        t = cocos.text.Label(str(int(self.current_strength)) + "  " + str(self.goal_strength),
                             position=(self.position[0], self.position[1] - self.GameLayer.grid_size / 3),
                             font_size=self.GameLayer.grid_size / 8, color=(self.activated_color[0], self.activated_color[1], self.activated_color[2], 255),
                             anchor_x="center", anchor_y="center", bold=True,
                             font_name="Cascadia Code")

        self.GameLayer.add(t)
        self.indi = t


class Line(cocos.sprite.Sprite):
    def __init__(self, from_pos, to_pos, color, strength, GameLayer, from_index=(-1, -1), to_index=(-1, -1)):
        rotation = 0
        if from_pos[1] != to_pos[1]:
            rotation = 90
        super(Line, self).__init__(position=center_position(from_pos, to_pos),
                                   scale=GameLayer.grid_scale,
                                   color=color,
                                   rotation=rotation, image='img/Line.png')
        self.scale_y = min(1, max(0.4, strength / 80))
        self.GameLayer = GameLayer
        self.from_index = from_index
        self.to_index = to_index
        self.color = color
        self.strength = strength
