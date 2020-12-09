import cocos
from cocos.euclid import *

from cocos.menu import *
from GameLayer import *
from cocos.director import director


import pyglet.app

class GameScene(cocos.scene.Scene):
    def __init__(self, stages, index):
        grid_layer = cocos.layer.Layer()
        line_layer = cocos.layer.Layer()
        game_layer = GameLayer(grid_layer, line_layer, stages, index)
        super(GameScene, self).__init__(cocos.layer.ColorLayer(255, 255, 255, 255), grid_layer, line_layer, game_layer)
        self.GameLayer = game_layer

class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Reflect')
        self.font_title['font_name'] = 'Cascadia Code'
        self.font_title['font_size'] = 100
        self.font_title['bold'] = True
        self.font_title['color'] = (255, 255, 255, 255)

        self.index = 0

        self.font_item['font_name'] = 'Cascadia Code'
        self.font_item['font_size'] = 40
        self.font_item_selected['font_name'] = 'Cascadia Code'

        items = list()
        items.append(cocos.menu.MenuItem('Start from Begin', self.on_new_game))
        items.append(cocos.menu.MenuItem('Start with Selected Stage', self.on_selected_game))
        items.append(cocos.menu.MultipleMenuItem('Stage Select : ', self.on_select, ['0', '1', '2', '3'], 0))
        items.append(cocos.menu.MenuItem('Quit', pyglet.app.exit))

        self.create_menu(items, cocos.actions.ScaleTo(1.1, duration=0.25), cocos.actions.ScaleTo(1.0, duration=0.25))

    def on_new_game(self):
        director.push(stages[0])

    def on_selected_game(self):
        director.push(stages[self.index])

    def on_select(self, index):
        self.index = index

if __name__ == "__main__":
    cocos.director.director.init(caption='Reflect', width=1000, height=1000)

    stages = []

    stage_0 = GameScene(stages, 0)

    stage_0.GameLayer.grid_count = (3, 3)
    stage_0.GameLayer.init_grid()

    stage_0.GameLayer.spawn_start_node((0, 0), 0, RED, 100)
    stage_0.GameLayer.spawn_obs((1, 1))
    stage_0.GameLayer.spawn_end_node((2, 0), RED, 100)

    stage_0.GameLayer.spawn_mirror(MovableMirror, (1, 2), 1, 100)
    stage_0.GameLayer.spawn_mirror(RotatableMirror, (2, 2), 1, 100)

    stages.append(stage_0)

    # -------------------------------------------------------------------

    stage_1 = GameScene(stages, 1)
    stage_1.GameLayer.grid_count = (4, 4)
    stage_1.GameLayer.init_grid()

    stage_1.GameLayer.spawn_start_node((0, 0), 1, RED, 100)
    stage_1.GameLayer.spawn_start_node((0, 3), 1, YELLOW, 100)
    stage_1.GameLayer.spawn_obs((1, 2))
    stage_1.GameLayer.spawn_obs((0, 2))
    stage_1.GameLayer.spawn_obs((3, 2))
    stage_1.GameLayer.spawn_end_node((3, 0), RED, 100, 0)
    stage_1.GameLayer.spawn_end_node((2, 2), YELLOW, 100, 0)

    stage_1.GameLayer.spawn_mirror(MovableMirror, (0, 1), -1, 100)
    stage_1.GameLayer.spawn_mirror(MovableMirror, (2, 1), 1, 100)
    stage_1.GameLayer.spawn_mirror(RotatableMirror, (2, 3), 1, 100)

    stage_1.GameLayer.spawn_mirror(StaticMirror, (1, 0), 1, 100)

    stages.append(stage_1)

    # -------------------------------------------------------------------

    stage_2 = GameScene(stages, 2)
    stage_2.GameLayer.grid_count = (5, 5)
    stage_2.GameLayer.init_grid()

    stage_2.GameLayer.spawn_start_node((0, 0), 1, YELLOW, 100)
    stage_2.GameLayer.spawn_start_node((1, 4), 1, RED, 100)

    stage_2.GameLayer.spawn_end_node((2, 2), YELLOW, 100)
    stage_2.GameLayer.spawn_end_node((0, 1), RED, 100)

    stage_2.GameLayer.spawn_obs((1, 1))
    stage_2.GameLayer.spawn_obs((2, 1))
    stage_2.GameLayer.spawn_obs((3, 1))
    stage_2.GameLayer.spawn_obs((1, 2))
    stage_2.GameLayer.spawn_obs((3, 2))

    stage_2.GameLayer.spawn_mirror(RotatableMirror, (4, 3), 1, 100)
    stage_2.GameLayer.spawn_mirror(StaticMirror, (4, 0), 1, 100)

    stage_2.GameLayer.spawn_mirror(MovableMirror, (0, 2), 1, 100)
    stage_2.GameLayer.spawn_mirror(MovableMirror, (0, 3), -1, 100)
    stage_2.GameLayer.spawn_mirror(MovableMirror, (0, 4), 1, 100)

    stages.append(stage_2)

    # -------------------------------------------------------------------

    stage_3 = GameScene(stages, 3)
    stage_3.GameLayer.grid_count = (6, 6)
    stage_3.GameLayer.init_grid()

    stage_3.GameLayer.spawn_start_node((0, 5), 1, RED, 100)
    stage_3.GameLayer.spawn_start_node((5, 1), 3, RED, 100)
    stage_3.GameLayer.spawn_end_node((4, 0), RED, 60)
    stage_3.GameLayer.spawn_end_node((2, 2), RED, 50, 2)

    stage_3.GameLayer.spawn_obs((1, 1))
    stage_3.GameLayer.spawn_obs((1, 2))
    stage_3.GameLayer.spawn_obs((1, 3))
    stage_3.GameLayer.spawn_obs((2, 3))
    stage_3.GameLayer.spawn_obs((3, 3))
    stage_3.GameLayer.spawn_obs((4, 3))
    stage_3.GameLayer.spawn_obs((5, 3))

    stage_3.GameLayer.spawn_mirror(StaticMirror, (0, 0), -1, 100)
    stage_3.GameLayer.spawn_mirror(MovableMirror, (0, 1), -1, 100)
    stage_3.GameLayer.spawn_mirror(MovableMirror, (2, 5), 1, 100)
    stage_3.GameLayer.spawn_mirror(MovableMirror, (3, 5), 1, 100)
    stage_3.GameLayer.spawn_mirror(MovableMirror, (2, 4), -1, 90)
    stage_3.GameLayer.spawn_mirror(MovableMirror, (3, 2), -1, 100)
    stage_3.GameLayer.spawn_mirror(RotatableMirror, (4, 1), -1, 50)

    stages.append(stage_3)

    cocos.director.director.run(cocos.scene.Scene(cocos.layer.ColorLayer(111, 189, 196, 255), MainMenu()))
