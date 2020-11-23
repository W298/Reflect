import cocos
from cocos.euclid import *

from GameLayer import *

if __name__ == "__main__":
    cocos.director.director.init(caption='Reflect', width=1000, height=1000)
    grid_layer = cocos.layer.Layer()
    line_layer = cocos.layer.Layer()
    scene = cocos.scene.Scene(cocos.layer.ColorLayer(255, 255, 255, 255), grid_layer, line_layer, GameLayer(grid_layer, line_layer))
    cocos.director.director.run(scene)
