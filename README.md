# SFGL
Simple Furry Graphics Library (For K210 - Micropython)

# Example
    from sfgl import * #import SFGL library
    import image
    
    # basic
    background = image.Image("/sd/img/welcome/home.jpg")
    renderer = FurryRenderer(background) #Set Renderer

    Logo = image.Image("/sd/img/welcome/LOGO.jpg")
    Logo = FurryController.Button(Logo, x=0,y=0, alpha=100) #Use Button
    Logo.setbind(enter) # set Bind Function
    renderer.addcontroller(Logo, name="Furry", zindex=0)
    
    # animation
    renderer.setanimate("Furry",2,alpha=100,x=15,y=103,scale=1.2)

    #loop
    while True:
        renderer.render()

# Constrcut
- FurryRenderer 
  - 
- FurryController
  - 
  -  Pic  
  - Button
  - Camera
    
    

