# Emilia Cocoru 342C1

import numpy as np
from PIL import Image

if __name__ == "__main__":
    # initializare culori
    white_color = (255, 255, 255)
    black_color = (0, 0, 0)
    red_color = (255, 0, 0)
    green_color = 120


    # initializare dimeniuni imagine
    width_input_image = 1920
    height_input_image = 1080

    # preluare imaginilor/fisierului txt
    input_image = np.asarray(Image.open('input.png'))
    sablon_image = np.asarray(Image.open('sablon.png'))
    sablon_text = open('sablon.txt', 'r')

    
    # aplicarea unui filtru median
    filter_image = np.array(Image.new("RGB", (width_input_image,  height_input_image), "white"))

    # se parcurge imaginea
    for i in range(1, height_input_image - 1):
        for j in range(1, width_input_image - 1):
            # ne uitam la pixelii vecini
            pixel_center_left = tuple(input_image[i][j - 1])
            pixel_center_right = tuple(input_image[i][j + 1])
            pixel_center_bottom = tuple(input_image[i - 1][j])
            pixel_center_top = tuple(input_image[i + 1][j])
            pixel_left_top = tuple(input_image[i - 1][j - 1])
            pixel_left_bottom = tuple(input_image[i + 1][j - 1])
            pixel_right_top = tuple(input_image[i - 1][j + 1])
            pixel_right_bottom = tuple(input_image[i + 1][j + 1])
            pixel_center = tuple(input_image[i][j])

            pixels = [
                pixel_center_left,
                pixel_center_right,
                pixel_center_bottom,
                pixel_center_top,
                pixel_left_top,
                pixel_left_bottom,
                pixel_right_top,
                pixel_right_bottom,
                pixel_center
            ]

            # si sortam aceeasi pixeli
            pixels.sort()

            # si il selectam pe cei din mijloc
            filter_image[i][j] = (pixels[4][0], pixels[4][1], pixels[4][2])

    Image.fromarray(filter_image).save('filter_image.png')

    # conversia din spatiul RGB in HSV
    rgb_to_hsv_image = np.array(Image.new("RGB", (width_input_image,  height_input_image), "white"))
    for i in range(height_input_image):
        for j in range(width_input_image):
            red = filter_image[i][j][0] / 255.0
            green = filter_image[i][j][1] / 255.0
            blue = filter_image[i][j][2] / 255.0

            c_max = max(red, green, blue)
            c_min = min(red, green, blue)
            delta = c_max - c_min

            if c_max == c_min:
                rgb_to_hsv_image[i][j] = (0.0, 0.0, c_max)
            else:
                s = delta / c_max
                if c_max == red:
                    h = (((green - blue) / delta) / 6) % 1.0 
                elif c_max == green:
                    h = ((2.0 + (blue - red) / delta) / 6) % 1.0
                else:
                    h = ((4.0 + (red - green) / delta) / 6) % 1.0
                rgb_to_hsv_image[i][j] = (h * 360, s * 100, c_max * 100)
    
    Image.fromarray(rgb_to_hsv_image).save('rgb_to_hsv_image.png')

    # segmentarea imaginii utilizand nuanta(Hue) pe post de criteriu de similaritate

    # trebuie sa parcurgem toata imaginea
    # daca gasim un pixel verde, vom cauta printre pixelii vecini lui pixeli de aceeasi nuanta
    # si apoi printre pixelii de aceeasi nuanta ai acelor pixeli gasiti si tot asa.
    # cu alte cuvinte vom face bfs-uri astfel incat sa ne putem defini id-urile zonelor
    pixels_id = np.zeros((height_input_image, width_input_image))
    pixels_queue = []
    min_y = [-1] * 50
    max_y = [-1] * 50
    min_x = [-1] * 50
    max_x = [-1] * 50
    id = 1

    for i in range(height_input_image):
        for j in range(width_input_image):
            if pixels_id[i][j] == 0:
                if rgb_to_hsv_image[i][j][0] != green_color:
                    pixels_id[i][j] = -1
                    rgb_to_hsv_image[i][j] = black_color
                else:
                    min_y[id] = i
                    max_x[id] = j 
                    max_y[id] = i
                    min_x[id] = j

                    pixels_queue.append((i, j))
                    pixels_id[i][j] = id
                    rgb_to_hsv_image[i][j] = white_color

                    while len(pixels_queue) > 0:
                        # cautam prin toti vecinii pixelului
                        # pixeli de nuanta verde
                        pixel = pixels_queue.pop(0) 

                        # Se calculeaza minimul și maximul
                        # pe x si pe y ale adreselor pixelilor dintr-o regiune
                        if pixel[0] < min_y[id]:
                            min_y[id] = pixel[0]
                        elif pixel[0] > max_y[id]:
                            max_y[id] = pixel[0]

                        if pixel[1] < min_x[id]:
                            min_x[id] = pixel[1]
                        elif pixel[1] > max_x[id]:
                            max_x[id] = pixel[1]

                        # pixel center left
                        if (rgb_to_hsv_image[pixel[0]][pixel[1] - 1][0] == green_color and pixels_id[pixel[0]][pixel[1] - 1] == 0):
                            pixels_id[pixel[0]][pixel[1] - 1] = id
                            rgb_to_hsv_image[pixel[0]][pixel[1] - 1] = white_color

                            pixels_queue.append((pixel[0], pixel[1] - 1))

                        #pixel center right
                        if (rgb_to_hsv_image[pixel[0]][pixel[1] + 1][0] == green_color and pixels_id[pixel[0]][pixel[1] + 1] == 0):
                            pixels_id[pixel[0]][pixel[1] + 1] = id
                            rgb_to_hsv_image[pixel[0]][pixel[1] + 1] = white_color

                            pixels_queue.append((pixel[0], pixel[1] + 1))

                        #pixel center bottom
                        if (rgb_to_hsv_image[pixel[0] - 1][pixel[1]][0] == green_color and pixels_id[pixel[0] - 1][pixel[1]] == 0):
                            pixels_id[pixel[0] - 1][pixel[1]] = id
                            rgb_to_hsv_image[pixel[0] - 1][pixel[1]] = white_color

                            pixels_queue.append((pixel[0] - 1, pixel[1]))

                        #pixel left bottom
                        if (rgb_to_hsv_image[pixel[0] + 1][pixel[1] - 1][0] == green_color and pixels_id[pixel[0] + 1][pixel[1] - 1] == 0):
                            pixels_id[pixel[0] + 1][pixel[1] - 1] = id
                            rgb_to_hsv_image[pixel[0] + 1][pixel[1] - 1] = white_color

                            pixels_queue.append((pixel[0] + 1, pixel[1] - 1))

                        #pixel left top
                        if (rgb_to_hsv_image[pixel[0] - 1][pixel[1] - 1][0] == green_color and pixels_id[pixel[0] - 1][pixel[1] - 1] == 0):
                            pixels_id[pixel[0] - 1][pixel[1] - 1] = id
                            rgb_to_hsv_image[pixel[0] - 1][pixel[1] - 1] = white_color

                            pixels_queue.append((pixel[0] - 1, pixel[1] - 1))

                        #pixel right top
                        if (rgb_to_hsv_image[pixel[0] - 1][pixel[1] + 1][0] == green_color and pixels_id[pixel[0] - 1][pixel[1] + 1] == 0):
                            pixels_id[pixel[0] - 1][pixel[1] + 1] = id
                            rgb_to_hsv_image[pixel[0] - 1][pixel[1] + 1] = white_color

                            pixels_queue.append((pixel[0] - 1, pixel[1] + 1))

                        #pixel right bottom
                        if (rgb_to_hsv_image[pixel[0] + 1][pixel[1] + 1][0] == green_color and pixels_id[pixel[0] + 1][pixel[1] + 1] == 0):
                            pixels_id[pixel[0] + 1][pixel[1] + 1] = id
                            rgb_to_hsv_image[pixel[0] + 1][pixel[1] + 1] = white_color

                            pixels_queue.append((pixel[0] + 1, pixel[1] + 1))

                    id = id + 1 # se schimba id-ul atunci cand terminam de parcus o anumita zona

    Image.fromarray(rgb_to_hsv_image).save('black_and_white_image.png')

    # identificarea dreptunghiurilor incadratoare
    # trecem prin toate id-urile si ne folosim de x si y min/max
    for id_pixel in range(1, id):
        for i in range(min_y[id_pixel], max_y[id_pixel]):
            rgb_to_hsv_image[i][min_x[id_pixel]] = red_color
            rgb_to_hsv_image[i][max_x[id_pixel]] = red_color

        for j in range(min_x[id_pixel], max_x[id_pixel]):
            rgb_to_hsv_image[min_y[id_pixel]][j] = red_color
            rgb_to_hsv_image[max_y[id_pixel]][j] = red_color
        
    Image.fromarray(rgb_to_hsv_image).save('image_with_red_square.png')


    # rearanjeaza ordinea id-urilor
    # pentru ca C-ul si S-ul sunt gasite primele 
    # pentru ca sunt putin mai mari decat celelalte caractere // cu cativa pixeli
    for this_id in range (1, id - 1): 
        for id_next in range(this_id + 1, id):
            if min_x[id_next] < min_x[this_id] and abs(min_y[id_next] - min_y[this_id]) < 25:
                temp = min_x[id_next]
                min_x[id_next] = min_x[this_id]
                min_x[this_id] = temp

                temp = max_x[id_next]
                max_x[id_next] = max_x[this_id]
                max_x[this_id] = temp

                temp = min_y[id_next]
                min_y[id_next] = min_y[this_id]
                min_y[this_id] = temp

                temp = max_y[id_next]
                max_y[id_next] = max_y[this_id]
                max_y[this_id] = temp


    # identificarea cuvintelor 

    lines = sablon_text.readlines()
    message_from_image = ""
    prev_letter = ''

    for id_pixel in range(1, id - 1):
        # se identifica lungimea si latimea dreptunghiului incadrator al regiunii
        dim_x = max_y[id_pixel] - min_y[id_pixel]
        dim_y = max_x[id_pixel] - min_x[id_pixel]

        best_matching_pixels = 0
        best_matching_letter = ""

        # se va lua fiecare litera din sablon_text
        # si se vor compara pixelii cu cei al regiunii selectate
        for line in lines:
            line = line.strip().split(" ")

            matching = 0

            for i in range(dim_y):
                for j in range(dim_x):
                    if (rgb_to_hsv_image[min_y[id_pixel] + i][min_x[id_pixel] + j] == sablon_image[int(line[2]) + i][int(line[1]) + j]).all():
                        matching += 1
            if matching > best_matching_pixels:
                best_matching_pixels = matching
                best_matching_letter = line[0]

        # se creeaza mesajul
        if best_matching_letter == '!':
            exclamation_mark = best_matching_letter
        elif best_matching_letter != "":
            if (prev_letter == 'C' and best_matching_letter == 'H'):
                message_from_image += best_matching_letter
            elif best_matching_letter == 'I':
                message_from_image += best_matching_letter
            elif abs(min_x[id_pixel] - max_x[id_pixel - 1]) >= 46:
                message_from_image += " " + best_matching_letter 
            else:
                message_from_image += best_matching_letter
            prev_letter = best_matching_letter

    final_message = message_from_image + " " + exclamation_mark
    print(final_message[1:])
