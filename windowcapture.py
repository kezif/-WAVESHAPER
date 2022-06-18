import numpy as np
import win32gui, win32ui, win32con
#slightly modified code snippet from https://www.youtube.com/c/LearnCodeByGaming



class WindowCapture:

    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    # constructor
    def __init__(self, window_name=None, capturerect=None):
        # find the handle for the window we want to capture.
        # if no window name is given, capture the entire screen
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception('Window not found: {}'.format(window_name))

        self.capturerect = capturerect
        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)

        if capturerect is None:
            self.w = window_rect[2] - window_rect[0]
            self.h = window_rect[3] - window_rect[1]
        else:
            self.w = capturerect[2] - capturerect[0]
            self.h = capturerect[3] - capturerect[1]

        # account for the window border and titlebar and cut them off
        border_pixels = 0
        titlebar_pixels = 0
        self.w = self.w - border_pixels #(border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels + capturerect[1]
        self.cropped_y = titlebar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

        self.wDC = win32gui.GetWindowDC(self.hwnd)
        self.dcObj = win32ui.CreateDCFromHandle(self.wDC)
        self.cDC = self.dcObj.CreateCompatibleDC()
        self.dataBitMap = win32ui.CreateBitmap()
        self.dataBitMap.CreateCompatibleBitmap(self.dcObj, self.w, self.h)
        self.cDC.SelectObject(self.dataBitMap)

    def get_screenshot(self, capture_mouse=True):

       
        # get screenshot
        self.cDC.BitBlt((self.capturerect[1], self.capturerect[0]), (self.w, self.h), self.dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)
        
        if capture_mouse:
             ## get cursor in screentshot: https://www.codestudyblog.com/cnb11/1124220434.html
            ci = win32gui.GetCursorInfo()
            if(ci [1]!=0):# at some point the cursor will be hidden by the game or program, thus reporting an error 
                cursorX, cursorY = ci[2]
                win32gui.DrawIconEx(self.cDC.GetHandleOutput(), cursorX, cursorY, ci[1], 0, 0, 0, None, win32con.DI_NORMAL)#2 size of the icon 
                #DrawIconEx  draws a bitmap into the specified context 
                #hdc.GetHandleOutput() returns the context handle 
                # parameter （ the context handle to put in, x coordinates, y coordinates, need to put the cursor handle ， the height of the cursor and the width of the cursor ， animation cursor to take the first frame, the background brush （ can be empty ）， drawing type int ）

        # convert the raw data into a format opencv can read
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = self.dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

       

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() 
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[...,:3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = np.ascontiguousarray(img)

        return img

    def __del__(self):
         # free resources
        self.dcObj.DeleteDC()
        self.cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.wDC)
        win32gui.DeleteObject(self.dataBitMap.GetHandle())


    # find the name of the window you're interested in.
    # once you have it, update window_capture()
    # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)
