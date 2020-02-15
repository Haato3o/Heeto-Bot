from PIL import Image
import random
import os

class ActWin(object):
    '''
        Activate Windows library :)
    '''
    def __init__(self, img_path: str):
        self.img_path: str = img_path
        self.img_bytes: Image.Image = None
        self.steppin_watermark: Image.Image = Image.open(os.path.join(os.path.abspath(""), "Libs", "Steppin", "images", "activate_windows.png"))

    def OpenImage(self):
        '''
            Opens the background image
        '''
        self.img_bytes = Image.open(self.img_path)

    def ResizeImage(self):
        '''
            Resize to the same width and height as the steppin watermark
        '''
        self.img_bytes = self.img_bytes.resize(self.steppin_watermark.size)

    def StepOnImage(self):
        '''
            :steppin:
        '''
        self.img_bytes.paste(self.steppin_watermark, (0, 0), self.steppin_watermark)
    
    def SaveImage(self) -> str:
        '''
            Saves the output
        '''
        # TODO: Enhance the way to save the output, so Heeto Bot doesn't have to remake the image if there's already one made
        outputName = f"{hex(random.randint(1, 2**32))}.png"
        outputPath = os.path.join(os.path.abspath('temp'), f"{outputName}")
        self.img_bytes.save(outputPath)
        return outputPath
    
    def ManipulateImage(self) -> str:
        self.OpenImage()
        self.ResizeImage()
        self.StepOnImage()
        fileOutput: str = self.SaveImage()
        return fileOutput
