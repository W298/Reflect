import cocos
from cocos.euclid import *

# direction
# -1(N) 0(↑) 1(→) 2(↓) 3(←)


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
