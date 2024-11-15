Pygame is the only required dependency.

This project aims to be a complete game of some kind in the end, mainly about showcasing systems that work well together.  It is not a library and is instead a reference implementation of the said systems.  Then, this code, for your project, is meant to be cannibalized to suit your specific needs.  As a reference, you are completely free to reimplement the systems in another language or project.  If you do so then the GPL-3.0 license doesn't apply to that code.

Controls:

Left-click anywhere on the map moves the avatar to that location.  Mouse-wheel controls zooming.  Holding right-mouse-button and moving the mouse scrolls around the map.  Mouse-wheel-click toggles following the avatar.  There are two floors, left-click the numbered buttons to the right of the "Floor" label to choose them.  F1 toggles between absolute coordinates and coordinates relative to floor shown in the information panel.  The escape key or the exit button quits the application.

Winning:

The game is won by gathering the items you can pick up and putting them all down into the same square.  The items you can pick up are a blue circular graphic with a musical note inside it.  If you can pick up an item a button will appear for that when you are on the same square, and then when you have an item there will be a put down button.  You may only have one item in your inventory at a time.

Graphics:

Graphics are purposely minimal, years can be spent on them and this application isn't about graphics, it's about game systems.

What is displayed is just the moveable area of the map, that is layer 0.  Layer 0 in a more developed domain isn't displayed, it's just where you can move to.  Then with the layer 0 moveable areas, layers 1 and higher are all the art assets and those layers are as many as needed.
