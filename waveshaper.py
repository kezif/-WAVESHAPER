from windowcapture import WindowCapture
import pyautogui
import numpy as np
import cv2
from time import time
import threading


def main():
    cords = d1,d2,d3,d4 = 0,0,960,540+30
    

    '''path = 'debug\\waveshaper1655498184.93671.png'
    img = cv2.imread(path)
    cv2.imshow('img', )#,90:130])
    cv2.waitKey()'''
    wincap = WindowCapture(capturerect=cords)
    needle_a = cv2.imread(R'needle\a.png', cv2.IMREAD_GRAYSCALE)
    needle_s = cv2.imread(R'needle\s.png', cv2.IMREAD_GRAYSCALE)
    needle_w = cv2.imread(R'needle\w.png', cv2.IMREAD_GRAYSCALE)
    needle_q = cv2.imread(R'needle\q.png', cv2.IMREAD_GRAYSCALE)
    

    while(True):
        loop_time = time()
        img = wincap.get_screenshot( capture_mouse=False)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, (img.shape[1]//2, img.shape[0]//2), interpolation = cv2.INTER_AREA)
        #img = img[18:,:]  # crop top status bar
        play_region = img[113:193,90:200] # crop so only beat line and shapes are image

        top_play_region = play_region[:play_region.shape[0]//2]
        bot_play_region = play_region[play_region.shape[0]//2:]

        threading.Thread(target=match_n_press_needle, args=(needle_a,bot_play_region, 'a') ).start()  # detect 4 diferent shapes in 4 threads
        threading.Thread(target=match_n_press_needle, args=(needle_s,bot_play_region, 's') ).start()
        threading.Thread(target=match_n_press_needle, args=(needle_w,top_play_region, 'w') ).start()
        threading.Thread(target=match_n_press_needle, args=(needle_q,top_play_region, 'q') ).start()
        


        print('FPS {}'.format(1 / (time() - loop_time)), end='\r')
        
        cv2.imshow('img', play_region)
        #cv2.imwrite(f'debug\\waveshaper{time():.5f}.png', to_save)

        k = cv2.waitKey(1)
        if k == ord('q'):
            cv2.destroyAllWindows()
            break
    
            


def match_n_press_needle(needle, region, key_to_press):
    mathing = cv2.matchTemplate(region, needle, cv2.TM_SQDIFF_NORMED)  # math shape template with what on scrennshot
    #cv2.imwrite(f'debug\\waveshaper{time():.5f}.png',region)
    if np.any(mathing < 0.9):  # if templated is found result would be lower then 1
        pyautogui.keyDown(key_to_press)
    else:
        pyautogui.keyUp(key_to_press)
    return mathing



if __name__ == '__main__':
    main()





