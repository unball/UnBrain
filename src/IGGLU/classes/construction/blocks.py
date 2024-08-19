from pygame import Surface, Vector2, draw, Rect
import pygame as pg
from typing import Callable
from color_constants import *

class Screen:
    """Hold the elements in a screen of the graphic interface"""
    def __init__(self) -> None:
        self.buttons = {}
        self.blocks = {}
        self.scrollingBackgrounds = {}
        self.menuBar = None
        self.caption = None
        self.icon = None
        self.visible = True

    def setWindow(self, window) -> None:
        """Sets the window to the screen"""
        self.window = window
    
    def setCaption(self, caption: str) -> None:
        """Sets the caption to the screen"""
        self.caption = caption

    def setIcon(self, iconPath: str) -> None:
        """Sets the icon to the screen"""
        self.icon = iconPath

    def setMenuBar(self, menuBar):
        """Sets the menuBar to the screen"""
        if self.menuBar is None:
            self.menuBar = menuBar
        else:
            raise Exception("Screen already has a menu bar.")
        
    def setVisible(self, visible: bool) -> None:
        self.visible = visible
        for block in self.blocks.values():
            block.setVisible(visible)
        for scrollingBackground in self.scrollingBackgrounds.values():
            scrollingBackground.setVisible(visible)
        for button in self.buttons.values():
            if button.comboBox is None:
                button.setVisible(visible)
        if self.menuBar is not None:
            self.menuBar.setVisible(visible)

    def addButton(self, button) -> None:
        """Adds a button to the screen"""
        if button.name not in self.buttons:
            if isinstance(button, Spinner):
                self.buttons[button.decreaseButton.name] = button.decreaseButton
                button.decreaseButton.setScreen(self)
                self.buttons[button.increaseButton.name] = button.increaseButton
                button.increaseButton.setScreen(self)
            self.buttons[button.name] = button
            button.setScreen(self)
        else:
            raise Exception("Button name key already exists.")

    def addBlock(self, block) -> None:
        """Adds an element to the screen"""
        if block.name not in self.blocks:
            self.blocks[block.name] = block
            block.setScreen(self)
        else:
            raise Exception("Block name key already exists.")

    def addScrollingBackground(self, scrollingBackground):
        """Adds a scrolling background to the screen"""
        if scrollingBackground.name not in self.scrollingBackgrounds:
            self.scrollingBackgrounds[scrollingBackground.name] = scrollingBackground
            scrollingBackground.setScreen(self)
        else:
            raise Exception("Scrolling background name key already exists.")

    def draw(self) -> None:
        """Draws all the elements in the screen"""
        if self.caption is not None:
            pg.display.set_caption(self.caption)
        if self.icon is not None:
            pg.display.set_icon(pg.image.load(self.icon))
        for block in self.blocks.values():
            if not block.preference:
                block.draw()
        for scrollingBackground in self.scrollingBackgrounds.values():
            if not scrollingBackground.preference:
                scrollingBackground.draw()
        for block in self.blocks.values():
            if block.preference:
                block.draw()
        for scrollingBackground in self.scrollingBackgrounds.values():
            if scrollingBackground.preference:
                scrollingBackground.draw()
        for button in self.buttons.values():
            button.draw()
        if self.menuBar is not None:
            self.menuBar.draw()

class Block:
    """Unit of the elements of the graphic interface"""
    def __init__(self, name: str, sizeX: int, sizeY: int, posX: int, posY: int, color: Color, window, gui, border: bool=False, shape: str ="RECT", preference: bool=True) -> None:
        self.size = Vector2(sizeX, sizeY)
        self.pos = Vector2(posX, posY)
        self.name = name
        self.color = color
        self.window = window
        self.gui = gui
        self.border = border
        self.border_color = BORDER_COLOR
        self.shape = shape
        self.text = None
        self.img = None
        self.visible = True
        self.screen = None
        self.preference = preference
    
    def draw(self) -> None:
        """Draws the block unit on the screen"""
        if self.visible:
            if self.shape == "RECT":
                rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
                draw.rect(self.window, self.color, rect)
                if self.border:
                    draw.rect(self.window, self.border_color, rect, 2)
            elif self.shape == "ARROW":
                draw.line(self.window, self.color, self.pos, self.pos + self.size, 6)
                seta = pg.Surface((300, 300), pg.SRCALPHA)
                pg.draw.polygon(seta, (255,0,0), ((0, 100), (0, 200), (200, 200), (200, 300), (300, 150), (200, 0), (200, 100)))
                seta = pg.transform.scale(seta, (18, 19))
                self.window.blit(seta, self.pos+self.size-(9,9))
            elif self.shape == "CIRCLE":
                if self.border:
                    pg.draw.circle(self.window, self.border_color, self.pos, self.size.x/2+2)
                pg.draw.circle(self.window, self.color, self.pos, self.size.x/2)

            if self.text is not None:
                font = pg.font.Font(None, self.text[2])
                text = font.render(self.text[0], True, self.text[1])
                textBack = text.get_rect()
                textBack.center = (self.pos.x+self.size.x/2, self.pos.y+self.size.y/2)
                self.window.blit(text, textBack)
            if self.img is not None:
                self.window.blit(self.img, self.pos-(0,3))
    
    def setText(self, text: str, color: Color = LIGHT_GRAY_LABEL, fontSize: int =24, center: bool=False) -> None:
        """Sets a text with color and font size to the block unit"""
        self.text = (text, color, fontSize)
        if not center:
            fonte = pg.font.Font(None, fontSize)
            self.size.x = fonte.size(text)[0]

    def getText(self) -> None:
        """Returns the text of the Block"""
        return self.text[0]
    
    def setImage(self, imgPath: str) -> None:
        """Sets an image to the block unit"""
        self.img = pg.image.load(imgPath)

    def setVisible(self, visible:bool) -> None:
        """Returns whether the object is visible or not"""
        self.visible = visible

    def setScreen(self, screen) -> None:
        """Sets the screen where the block belongs to"""
        self.screen = screen

class Toggle(Block):
    """Block that holds buttons hidden until the user clicks on it"""
    def __init__(self) -> None:
        super().__init__()
        raise NotImplementedError

class Background:
    """Background properties of a block"""
    def __init__(self) -> None:
        raise NotImplementedError

class ScrollingBackground(Screen, Block):
    """Block that is able to scroll"""
    def __init__(self, name: str, sizeX: int, sizeY: int, posX: int, posY: int, color: Color, window, gui, displayVerticalSize: int, displayVerticalPos: int, border: bool=False, shape: str ="RECT", preference: bool=True) -> None:
        Block.__init__(self, name, sizeX, sizeY, posX, posY, color, window, gui, border, shape, preference)
        Screen.__init__(self)
        self.displayVerticalSize = displayVerticalSize
        self.displayVerticalPos = displayVerticalPos

    def scroll(self, direction: int) -> None:
        """Scroll the background in the area"""
        mousePos = pg.mouse.get_pos()
        if (self.pos.x < mousePos[0] < self.pos.x + self.size.x and self.displayVerticalPos < mousePos[1] < self.displayVerticalPos + self.displayVerticalSize):
            if direction == -1:
                # scrolling upwards
                if self.pos.y+self.size.y >= self.displayVerticalPos+self.displayVerticalSize+25:
                    # inside down limit
                    for block in self.blocks.values():
                        block.pos.y += direction*25
                    for button in self.buttons.values():
                        button.pos.y += direction*25
                    self.pos.y += direction*25
                    for screen in self.scrollingBackgrounds.values():
                        for block in screen.blocks.values():
                            block.pos.y += direction*25
                        for button in screen.buttons.values():
                            button.pos.y += direction*25
                        screen.pos.y += direction*25
            
            elif direction == 1:
                # scrolling downwards
                if self.pos.y <= self.displayVerticalPos-25:
                    # inside up limit
                    for block in self.blocks.values():
                        block.pos.y += direction*25
                    for button in self.buttons.values():
                        button.pos.y += direction*25
                    self.pos.y += direction*25
                    for screen in self.scrollingBackgrounds.values():
                        for block in screen.blocks.values():
                            block.pos.y += direction*25
                        for button in screen.buttons.values():
                            button.pos.y += direction*25
                        screen.pos.y += direction*25

            # if (self.displayVerticalPos <= self.pos.y-3 and direction == -1):
            #     pass
            # else:
            #     for block in self.blocks.values():
            #         block.pos.y += direction*3
            #     self.displayVerticalPos += direction*3
            # if (self.displayVerticalPos and direction == -1):
            #     pass
            # else:
            #     for block in self.blocks.values():
            #         block.pos.y += direction*3
            #     self.displayVerticalPos += direction*3

    def setVisible(self, visible: bool) -> None:
        Block.setVisible(self, visible)
        Screen.setVisible(self, visible)

    def draw(self):
        """Draws the elements in the scrolling background"""
        Block.draw(self)
        Screen.draw(self)

class MenuBar(Screen, Block):
    """Block that holds the elements in menu"""
    def __init__(self, name: str, sizeX: int, sizeY: int, posX: int, posY: int, color: Color, window, gui, border: bool=False, shape: str ="RECT", preference: bool=True) -> None:
        Block.__init__(self, name, sizeX, sizeY, posX, posY, color, window, gui, border, shape, preference)
        Screen.__init__(self)

    def draw(self):
        """Draws the elements in the menu bar"""
        Block.draw(self)
        Screen.draw(self)
        
class Button(Block):
    """Block that performs an action (event)"""
    def __init__(self, name: str, sizeX: int, sizeY: int, posX: int, posY: int, color: Color, window, gui, border: bool=True, shape="RECT", preference: bool=True) -> None:
        super().__init__(name, sizeX, sizeY, posX, posY, color, window, gui, border, shape, preference)
        self.action = None
        self.comboBox = None
        self.spinner = None

    def draw(self) -> None:
        """Draws the button on the screen"""
        super().draw()
        
    def actionAssign(self, action: Callable) -> None:
        """Assigns an action to the button"""
        self.action = action.__get__(self)
    
    def actionPerformed(self) -> None:
        """Performs the action when the button is clicked"""
        mousePos = pg.mouse.get_pos()
        if self.shape == "RECT":
            if (self.pos.x < mousePos[0] < self.pos.x + self.size.x and self.pos.y < mousePos[1] < self.pos.y + self.size.y):
                if self.action is not None and self.visible:
                    self.action()
        elif self.shape == "CIRCLE":
            if (mousePos[0] - self.pos.x) ** 2 + (mousePos[1] - self.pos.y) ** 2 <= (self.size.x/2) ** 2:
                if self.action is not None and self.visible:
                    self.action()

class ToggleButton(Button):
    """Button that alternates between two states"""
    def __init__(self, name: str, sizeX: int, sizeY: int, posX: int, posY: int, color: Color, window, gui, state: bool=False, border: bool=True, shape="RECT", preference: bool=True) -> None:
        super().__init__(name, sizeX, sizeY, posX, posY, color, window, gui, border, shape, preference)
        self.state = state
        self.imgs = ["", ""]
        self.center = False

    def setImage(self, imgPathOn: str, imgPathOff: str, center: bool=False) -> None:
        """Sets two images to the block unit, for on and off states"""
        self.imgs[0] = pg.image.load(imgPathOff)
        self.imgs[1] = pg.image.load(imgPathOn)
        self.center = center

    def changeState(self):
        """Changes the state of the button"""
        self.state = not self.state

    def isOn(self):
        """Returns whether the button is on or off"""
        return self.state
    
    def draw(self):
        """Draws the button on the screen"""
        super().draw()
        if self.visible:
            if self.center:
                self.window.blit(self.imgs[self.state], self.pos+(9,9))
            else:
                self.window.blit(self.imgs[self.state], self.pos-(0,3))


class ComboBox(Button):
    """Button that allows user to select an option over many"""
    def __init__(self, name: str, sizeX: int, sizeY: int, posX: int, posY: int, color: Color, window, gui, firstOption: str, optionsColor: Color=BACKGROUND_COLOR, border: bool=True, shape="RECT", preference: bool=True) -> None:
        super().__init__(name, sizeX, sizeY, posX, posY, color, window, gui, border, shape, preference)
        self.firstLabel = firstOption
        self.optionsColor = optionsColor
        self.setText(self.firstLabel, center=True)
        #firstOption = Button(f'{self.name}{firstOption.capitalize()}', self.size.x, self.size.y, self.pos.x, self.pos.y+self.size.y, BACKGROUND_COLOR, self.window, self.gui, border=True)
        self.options = []
        self.optionsVisibility = False
        self.idx = ""

    def addOption(self, option: str) -> None:
        """Adds an option to the option list of the ComboBox"""
        if self.options == []:
            optionButton = Button(f'{self.name}{option.capitalize()}', self.size.x, self.size.y, self.pos.x, self.pos.y+self.size.y-3, self.optionsColor, self.window, self.gui, border=True)
            optionButton.setVisible(False)
            optionButton.setText(option, center=True)
            self.options.append(optionButton)
            self.screen.addButton(optionButton)
            # if self.name in screen.buttons.keys():
            #     screen.addButton(optionButton)
            # else:
            #     for scrollingBackground in screen.scrollingBackgrounds.values():
            #         if self.name in scrollingBackground.buttons.keys():
            #             screen.scrollingBackgrounds[scrollingBackground.name].addButton(optionButton)
        else:
            optionButton = Button(f'{self.name}{option.capitalize()}', self.size.x, self.size.y, self.pos.x, self.options[-1].pos.y+self.size.y-3, self.optionsColor, self.window, self.gui, border=True)
            optionButton.setVisible(False)
            optionButton.setText(option, center=True)
            self.options.append(optionButton)
            self.screen.addButton(optionButton)
            # if self.name in screen.buttons.keys():
            #     screen.addButton(optionButton)
            # else:
            #     for scrollingBackground in screen.scrollingBackgrounds.values():
            #         if self.name in scrollingBackground.buttons.keys():
            #             screen.scrollingBackgrounds[scrollingBackground.name].addButton(optionButton)
        optionButton.comboBox = self

    def addOptions(self, listOptions: "list[str]") -> None:
        """Adds a list of options to the option list of the ComboBox"""
        for option in listOptions:
            self.addOption(option)

    def getOptionsVisibility(self) -> bool:
        """Returns whether the options are visible or not"""
        return self.optionsVisibility

    def setOptionsVisibility(self, visibility: bool) -> None:
        """Sets the visibility of the options list"""
        self.optionsVisibility = visibility
        for option in self.options:
            option.setVisible(visibility)

    def draw(self):
        """Draws the ComboBox according to its visibility"""
        super().draw()
        if self.optionsVisibility:
            for option in self.options:
                option.draw()


class TextField(Button):
    """Button that allows user to write something on it"""
    def __init__(self, name: str, sizeX: int, sizeY: int, posX: int, posY: int, color: Color, window, gui, border: bool=True, shape="RECT", preference: bool=True, downLimit: int=0, upLimit: int=100) -> None:
        super().__init__(name, sizeX, sizeY, posX, posY, color, window, gui, border, shape, preference)
        self.active = False
        self.upLimit = upLimit
        self.downLimit = downLimit

    def isActive(self) -> bool:
        """Returns whether the TextField is active to be writable or not"""
        return self.active
    
    def setActive(self, active: bool) -> None:
        """Sets if the TextField is active or not"""
        self.active = active
        if self.active:
            self.border_color = LIGHT_BLUE
        else:
            self.border_color = BORDER_COLOR

    def calcLimit(self) -> None:
        """Calculates the limits allowed in the TextField"""
        if self.getText().strip() == "":
            self.setText(str(self.downLimit), center=True)
        elif int(self.getText()) < self.downLimit:
            self.setText(str(self.downLimit), center=True)
        elif int(self.getText()) > self.upLimit:
            self.setText(str(self.upLimit), center=True)

    def draw(self) -> None:
        """Draws the TextField on the screen"""
        super().draw()
        

class Spinner(TextField):
    """Group of buttons that allow user to increase or decrease a value in a TextField"""
    def __init__(self, name: str, sizeX: int, sizeY: int, posX: int, posY: int, color: Color, window, gui, border: bool=True, shape="RECT", preference: bool=True, downLimit: int=0, upLimit: int=100) -> None:
        super().__init__(name, sizeX, sizeY, posX, posY, color, window, gui, border, shape, preference, downLimit, upLimit)
        self.decreaseButton = Button(f"decreaseButton{self.name}", self.size.x//2, self.size.y, self.pos.x+self.size.x-3, self.pos.y, self.color, self.window, self.gui)
        self.decreaseButton.setText("-", center=True)
        self.decreaseButton.spinner = self
        self.increaseButton = Button(f"increaseButton{self.name}", self.size.x//2, self.size.y, self.decreaseButton.pos.x+self.decreaseButton.size.x-3, self.pos.y, self.color, self.window, self.gui)
        self.increaseButton.setText("+", center=True)
        self.increaseButton.spinner = self

        def edit(self):
            self.setActive(not self.isActive())
            self.calcLimit()
        self.actionAssign(edit)

        def increment(self):
            self.spinner.setText(str(int(self.spinner.getText())+1), center=True)
            self.spinner.calcLimit()
        self.increaseButton.actionAssign(increment)

        def decrement(self):
            self.spinner.setText(str(int(self.spinner.getText())-1), center=True)
            self.spinner.calcLimit()
        self.decreaseButton.actionAssign(decrement)

    

class Slider(Button):
    """Button that can slide over a block"""
    def __init__(self, name: str, sizeX: int, sizeY: int, posX: int, posY: int, color: Color, window, gui, bar: Block, border: bool=True, shape="CIRCLE", preference: bool=True) -> None:
        super().__init__(name, sizeX, sizeY, posX, posY, color, window, gui, border, shape, preference)
        self.bar = bar
        self.active = False
        self.label = None
        self.originalColor = self.color

    def createLabel(self) -> None:
        """Creates a label block that shows the value of the Slider"""
        label = Block(f'{self.name}Label', self.size.x, self.size.y, self.pos.x-self.size.x/2, self.pos.y+self.size.y+5, BACKGROUND_COLOR, self.window, self.gui)
        label.setText(str(self.getValue()), LIGHT_GRAY_LABEL, center=True)
        self.label = label
        self.screen.addBlock(self.label)


    def getValue(self) -> float:
        """Returns the value according to the Slider's position"""
        return int((self.pos.x - self.bar.pos.x) / self.bar.size.x * 100)/20
    
    def isActive(self) -> bool:
        """Returns whether the Slider is being slided or not"""
        return self.active
    
    def setActive(self, active: bool) -> None:
        """Sets if the Slider is being slided or not"""
        self.active = active
        if self.active:
            self.color = self.border_color
        else:
            self.color = self.originalColor
    
    def draw(self) -> None:
        """Draws the Slider on the screen"""
        super().draw()


class LabelArea(Block):
    """Area that contains a list of labels"""
    def __init__(self, name: str, sizeX: int, sizeY: int, posX: int, posY: int, color: Color, window, gui, border: bool=True, shape="RECT", preference: bool=True) -> None:
        super().__init__(name, sizeX, sizeY, posX, posY, color, window, gui, border, shape, preference)
        self.lines = []

    def addLabel(self, labelText: str) -> None:
        """Adds a label to the lines list"""
        fonte = pg.font.Font(None, self.text[2])
        name = "".join([word.capitalize() for word in labelText.split()])
        while name in self.screen.blocks.keys():
            name += "1"
        if self.lines == []:
            newLabel = Block(name, fonte.size(labelText)[0], fonte.size(labelText)[1], self.pos.x, self.pos.y, self.color, self.window, self.gui)
            newLabel.setText(labelText, center=False)
            self.lines.append(newLabel)
            self.screen.addBlock(newLabel) # VAI DAR PROBLEMA
        else:
            newLabel = Block(name, fonte.size(labelText)[0], fonte.size(labelText)[1], self.lines[-1].pos.x, self.lines[-1].pos.y+self.lines[-1].size.y+10, self.color, self.window, self.gui)
            newLabel.setText(labelText, center=False)
            self.lines.append(newLabel)
            self.screen.addBlock(newLabel) # VAI DAR PROBLEMA
        if self.lines[-1].pos.y+self.lines[-1].size.y > self.screen.pos.y+self.screen.size.y:
            self.screen.size.y += self.lines[-1].size.y+10

    def clearAllLines(self) -> None:
        """Clears all lines"""
        for line in self.lines:
            self.screen.blocks.pop(line.name)
        self.lines = []