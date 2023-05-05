import pyautogui
import pyscreenshot as imagegrab
import PIL.Image
import cv2 as cv
import numpy as np
from random import randint
import json
import os.path


mines_count = 99
unknown_cells = 480
RGB_list = {"oneM": (), "twoM": (), "threeM": (), "fourM": (), "fiveM": (), "sixM": (), "mine": (), "flag": (),
            "empty": (), "unknown": ()}


def starter():
    """
    Click on a cell randomly
    """
    global x, y, unknown_cells
    rand1 = randint(x[0], y[0])
    rand2 = randint(x[1], y[1])
    pyautogui.click(rand1, rand2, clicks=2)
    unknown_cells -= 1


def emoji():
    """
    reset the game
    """
    global x, y
    emoji_x = x[0] + (15 * 16)
    emoji_y = x[1] - (2 * 16)
    pyautogui.click(emoji_x, emoji_y, clicks=2)


def game_location():
    """
    finds minesweeper game on screen by matching cell.jpg
    """
    game_x = 0
    game_y = 0
    imagegrab.grab().save("screen.jpg")
    img_rgb = cv.imread('screen.jpg')
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    template = cv.imread('cell.jpg', 0)
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    c = 0
    for pt in zip(
            *loc[::-1]):
        c += 1
        cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        if c == 1:
            game_x = [pt[0] + w - 16, pt[1] + h - 16]
            game_y = [pt[0] + w, pt[1] + h]
        if game_x[0] > pt[0] + w - 16:
            game_x[0] = pt[0] + w - 16
        if game_x[1] > pt[1] + h - 16:
            game_x[1] = pt[1] + h - 16
        if game_y[0] < pt[0] + w:
            game_y[0] = pt[0] + w
        if game_y[1] < pt[1] + h:
            game_y[1] = pt[1] + h
    return [game_x, game_y]


def screen_clicker():
    """
    Based on the click list, right-click or left-click on the desired cells
    """
    global x, screen_clicker_list
    for cell in screen_clicker_list:
        # left-click
        if cell[2] == "c":
            pyautogui.click(x[0] + 8 + (16 * cell[1]), x[1] + 8 + (16 * cell[0]), duration=0)
        # right-click ( flagging )
        if cell[2] == "f":
            pyautogui.click(x[0] + 8 + 16 * cell[1], x[1] + 8 + 16 * cell[0], button='right', duration=0)


def screenshot(image_counter):
    """
    1. Based on the obtained X and Y, takes a screenshot of the minefield
    2. A number is assigned to the cell based on its RGB-color and the RGB_list
    3. If the color is not in the RGB list, it shows the image of the cell and asks what it is
    4. Counts the unknown neighbors of the cell
    :return: a boolean(T > lost ,F > continue)
            and matrix of mines and unknown neighbors related to cells (mines || unknown neighbors)
    """
    global mines_count
    global unknown_cells
    global RGB_dic
    F = False
    image_name = "image" + str(image_counter) + ".jpg"
    imagegrab.grab(bbox=(x[0], x[1], y[0], y[1])).save(image_name)
    image = PIL.Image.open(image_name)
    image_rgb = image.convert("RGB")
    flag_count = 0
    unknowns = 0
    # It creates a matrix for RGB colors
    matrix = []
    for i in range(8, 256, 16):
        A = []
        for j in range(8, 480, 16):
            A.append(image_rgb.getpixel((j, i)))
        matrix.append(A)

    # create a 16*30 matrix minefield
    solver_mat = []
    for i in range(16):
        B = []
        for j in range(30):
            B.append("00")
        solver_mat.append(B)

    for i in range(16):
        for j in range(30):
            b = tuple(matrix[i][j])
            if b == tuple(RGB_list["unknown"]):
                solver_mat[i][j] = "80"
                unknowns += 1
            elif b == tuple(RGB_list["empty"]):
                continue
            elif b == tuple(RGB_list["oneM"]):
                solver_mat[i][j] = str(int(solver_mat[i][j]) + 10)
            elif b == tuple(RGB_list["twoM"]):
                solver_mat[i][j] = str(int(solver_mat[i][j]) + 20)
            elif b == tuple(RGB_list["threeM"]):
                solver_mat[i][j] = str(int(solver_mat[i][j]) + 30)
            elif b == tuple(RGB_list["fourM"]):
                solver_mat[i][j] = str(int(solver_mat[i][j]) + 40)
            elif b == tuple(RGB_list["fiveM"]):
                solver_mat[i][j] = str(int(solver_mat[i][j]) + 50)
            elif b == tuple(RGB_list["sixM"]):
                solver_mat[i][j] = str(int(solver_mat[i][j]) + 60)
            elif b == tuple(RGB_list["flag"]):
                flag_count += 1
                solver_mat[i][j] = "90"
                for k in range(-1, 2):
                    for l in range(-1, 2):
                        if abs(k) + abs(l) != 0:
                            n = i + k
                            m = j + l
                            if (16 > n > -1) and (30 > m > -1) and int(solver_mat[n][m]) != 80 and int(solver_mat[n][m]) != 90:
                                solver_mat[n][m] = str(int(solver_mat[n][m]) - 10)

            elif b == tuple(RGB_list["mine"]):
                print(" ------- Lost -------- ")
                return True, solver_mat
            else:
                img = cv.imread("image1.jpg")
                crop_img = img[(i * 16):((i + 1) * 16), (j * 16):((j + 1) * 16)]
                cv.imshow("cropped", crop_img)
                cv.waitKey(0)
                whatIsIt = input("What is it ???"
                                 " If there is a number, type the number, flag >> f, "
                                 " mine >> m, unknown >> u, empty space >> e  :")

                if whatIsIt == "1":
                    RGB_list["oneM"] = b
                elif whatIsIt == "2":
                    RGB_list["twoM"] = b
                elif whatIsIt == "3":
                    RGB_list["threeM"] = b
                elif whatIsIt == "4":
                    RGB_list["fourM"] = b
                elif whatIsIt == "5":
                    RGB_list["fiveM"] = b
                elif whatIsIt == "6":
                    RGB_list["sixM"] = b
                elif whatIsIt == "f":
                    RGB_list["flag"] = b
                elif whatIsIt == "m":
                    RGB_list["mine"] = b
                    F = True
                elif whatIsIt == "u":
                    RGB_list["unknown"] = b
                elif whatIsIt == "e":
                    RGB_list["empty"] = b
                elif whatIsIt == "7":
                    print(" Sry I can not process the 7 please reset the game ")
                    exit()
                with open('RGB.txt', 'w') as file:
                    file.write(json.dumps(RGB_list))
                    if F:
                        print(" ------- Lost -------- ")
                        return True, solver_mat
    # Counts the unknown neighbors of the cell
    for i in range(16):
        for j in range(30):
            f = int(solver_mat[i][j])
            for k in range(-1, 2):
                for l in range(-1, 2):
                    if abs(k) + abs(l) != 0:
                        n = i + k
                        m = j + l
                        if (16 > n > -1) and (30 > m > -1) and int(solver_mat[n][m]) // 10 == 8:
                            f += 1
                            solver_mat[i][j] = str(f)
    if 99 - mines_count != flag_count:
        mines_count = 99 - flag_count
    unknown_cells = unknowns
    return False, solver_mat


def unknown_neighbor(cell_i, cell_j):
    """
    :return: the index_list of its unknown neighbors
    """
    all_neighbor = []
    global minefield
    for k in range(-1, 2):
        for l in range(-1, 2):
            if abs(k) + abs(l) != 0:
                n = cell_i + k
                m = cell_j + l
                if (16 > n > -1) and (30 > m > -1) and int(minefield[n][m]) // 10 == 8:
                    all_neighbor.append([n, m])
    return all_neighbor


def joint(cell_1, cell_2):
    """
    :return: the joint neighbors of two cells
    """
    all_neighbor = cell_1 + cell_2
    joint_members = []
    for neighbor in all_neighbor:
        if joint_members.count(neighbor) == 0 and all_neighbor.count(neighbor) == 2:
            joint_members.append(neighbor)
    return joint_members


def unjoint(list1, list2):
    """
    :return: The non-shared neighbors of the first cell
    """
    for neighbor in list2:
        if list1.count(neighbor) != 0:
            list1.remove(neighbor)
    return list1


def flag(value, value_i, value_j):
    """
    1.Sets the mine counter  (mines_count)
    2.Append the index of the detected mine cell to the click list.
    3.Increases the value of mine cell by +10   >>>>>>  9x  means flag_cell and x unknown neighbors
    4.It searches in the neighbors :
        Cells that are not numbers (flag / empty / unknown) >> Minus one (one less unknown neighbor )
        Cells that are numbers (in game screen (1,...,6)) >> Minus eleven (one less mine and one less unknown neighbor)
    """
    global mines_count
    global minefield
    global screen_clicker_list
    # 1
    mines_count -= 1
    # 2
    screen_clicker_list.append([value_i, value_j, "f"])
    # 3
    minefield[value_i][value_j] = str(int(value) + 10)
    # 4
    for k in range(-1, 2):
        for l in range(-1, 2):
            if abs(k) + abs(l) != 0:
                n = value_i + k
                m = value_j + l
                if (16 > n > -1) and (30 > m > -1):
                    item = int(minefield[n][m])
                    if item == 0 or item // 10 == 7 or item // 10 == 9 or item // 10 == 8:
                        minefield[n][m] = str(item - 1)
                    elif 70 > item > 10:
                        minefield[n][m] = str(item - 11)


def clicker(value, value_i, value_j):
    """
    1.Append the index of the detected non-mine cell to the click list.
    2.It makes all the neighbors minus one (one less unknown neighbor)
    """
    global screen_clicker_list
    global minefield
    # 1
    screen_clicker_list.append([value_i, value_j, "c"])

    # minefield[value_i][value_j] = str(int(value) - 10)
    if int(value) // 10 != 7:
        # nemidoonam chera ghable if gozashte boodamesh
        # I think I did this in order not to be mistaken for an unknown neighbor in the rest of the program
        minefield[value_i][value_j] = str(int(value) - 10)
        # 2
        for clicker_k in range(-1, 2):
            for clicker_l in range(-1, 2):
                if abs(clicker_k) + abs(clicker_l) != 0:
                    n = value_i + clicker_k
                    m = value_j + clicker_l
                    if (16 > n > -1) and (30 > m > -1):
                        minefield[n][m] = str(int(minefield[n][m]) - 1)


def solver(cell_i, cell_j):
    """
    Checks the target cell for a mine or click
    """
    global minefield
    global mines_count
    global screen_clicker_list
    p = int(minefield[cell_i][cell_j])
    # To continue, the cell should not be free space or seven or flag or unknown
    if p != 0 and p // 10 != 7 and p // 10 != 9 and p // 10 != 8:

        # If the cell number is divisible by eleven, all its unknown neighbors are mines.
        if p % 11 == 0:
            # Checking neighbors
            for k in range(-1, 2):
                for l in range(-1, 2):

                    # The index should not be related to the cell we are checking.
                    if abs(k) + abs(l) != 0:
                        n = cell_i + k
                        m = cell_j + l

                        # To manage the out-of-index error and being a unknown
                        if (16 > n > -1) and (30 > m > -1) and int(minefield[n][m]) // 10 == 8:
                            flag(minefield[n][m], n, m)

        # If the cell number is between one and ten, it means there is no mine in its neighbors.
        elif 10 > p > 0:
            for k in range(-1, 2):
                for l in range(-1, 2):
                    if abs(k) + abs(l) != 0:
                        n = cell_i + k
                        m = cell_j + l

                        # To manage the out-of-index error and being a unknown and not a flag
                        if (16 > n > -1) and (30 > m > -1) and int(minefield[n][m]) // 10 == 8 and \
                                int(minefield[n][m]) // 10 != 7:
                            clicker(minefield[n][m], n, m)
        else:
            for k in range(-1, 2):
                for l in range(-1, 2):

                    # Checking the neighbors that have a joint side with the cell
                    if (k != 0) != (l != 0):
                        n = cell_i + k
                        m = cell_j + l
                        if (16 > n > -1) and (30 > m > -1):
                            q = int(minefield[n][m])

                            # the neighbor should not be a free space or seven or flag or unknown
                            # And the number of its mines should not be equal to its unknown neighbors
                            # I don't remember the wisdom for this one :)) >>>  q // 10 != 0
                            if q % 11 != 0 and q // 10 != 0 and q // 10 != 7 and q // 10 != 9 and q // 10 != 8 and q != 0:

                                # shared neighbors of cells p and q
                                join = joint(unknown_neighbor(cell_i, cell_j), unknown_neighbor(n, m))
                                minimum = min(p, q)
                                maximum = max(p, q)

                                # shared neighbors must be more than one
                                # And The number of p's mines should not be equal to q's mines Or...
                                # ...the number of shared neighbors should be equal to...
                                # ...the unknown neighbors of the smaller cell
                                if len(join) > 1 and p != q and (p // 10 != q // 10 or len(join) == (minimum % 10)):
                                    # This line was left because of a problem that I don't remember (to prevent) :???
                                    if maximum != 25 or minimum != 13:
                                        # Maximum number of mines in shared unknown neighbors
                                        # A two-digit number (mines | shared unknown neighbors)

                                        c = maximum - (minimum // 10 * 10 + len(join))
                                        # print("c = ", c, "  max = ", maximum)
                                        # If number of mines in shared unknown neighbors equal
                                        # to shared unknown neighbors, so all the shared unknown neighbors are mines
                                        # and flag them

                                        if c % 11 == 0:
                                            if p > q:
                                                unjoin = unjoint(unknown_neighbor(cell_i, cell_j),
                                                                 unknown_neighbor(n, m))
                                            else:
                                                unjoin = unjoint(unknown_neighbor(n, m),
                                                                 unknown_neighbor(cell_i, cell_j))
                                            for item in unjoin:
                                                ii = item[0]
                                                jj = item[1]
                                                flag(minefield[ii][jj], ii, jj)
                                            # If the number of mines in their shared neighbors is equal to...
                                            # ...the number of smaller cell,...
                                            # ...So all non-shared neighbors of smaller cell are NOT mines,
                                            # >>> CLICK them <<<
                                            g = minimum - ((minimum // 10) * 10 + len(join))
                                            if 10 > g > 0:
                                                if p > q:
                                                    unjoin1 = unjoint(unknown_neighbor(n, m),
                                                                      unknown_neighbor(cell_i, cell_j))
                                                else:
                                                    unjoin1 = unjoint(unknown_neighbor(cell_i, cell_j),
                                                                      unknown_neighbor(n, m))
                                                for item in unjoin1:
                                                    ii = item[0]
                                                    jj = item[1]
                                                    clicker(minefield[ii][jj], ii, jj)

                                        # If c is between 1 and 10, it means that none of the non-shared neighbors...
                                        # ...of the larger cell(the cell with bigger value) are mines >>> CLICK them <<<
                                        # With the condition that the number of remaining mines in...
                                        # ...one of the two cells must be one.
                                        elif 10 > c > 0 and (p // 10 == 1 or q // 10 == 1):
                                            if p > q:
                                                unjoin = unjoint(unknown_neighbor(cell_i, cell_j),
                                                                 unknown_neighbor(n, m))
                                            else:
                                                unjoin = unjoint(unknown_neighbor(n, m),
                                                                 unknown_neighbor(cell_i, cell_j))
                                            for item in unjoin:
                                                ii = item[0]
                                                jj = item[1]
                                                clicker(minefield[ii][jj], ii, jj)
                                        else:
                                            """
                                             In this case, the program moves away from the examined cell.
                                             If the relationship of the investigated cell with its neighbor...
                                             ...is one of several desired special cases,...
                                             ...We can deduce whether some neighbors are mines or not.
                                             I cannot scientifically solve this case, but I am sure of its existence.
                                            """
                                            # We take a copy of the indexes of the larger and smaller cells...
                                            # ...so that we don't run into problems later
                                            if p > q:
                                                p_i = cell_i
                                                p_j = cell_j
                                                q_i = n
                                                q_j = m
                                            else:
                                                p_i = n
                                                p_j = m
                                                q_i = cell_i
                                                q_j = cell_j
                                            # We check the neighboring neighbors of the cell
                                            for e in range(-1, 2):
                                                for r in range(-1, 2):
                                                    if abs(e) == 1 or abs(r) == 1:
                                                        nn = p_i + e
                                                        mm = p_j + r
                                                        # The condition that the neighbor of the neighbor...
                                                        # ...is not the same cell
                                                        if (nn != q_i) or (mm != q_j):
                                                            qq = int(minefield[nn][mm])
                                                            # Like the previous procedure
                                                            if (
                                                                    minimum // 10 < 2) and qq % 11 != 0 and qq != 0 and qq // 10 != 7 \
                                                                    and qq // 10 != 9 and qq // 10 != 8:
                                                                c_neighbors = unjoint(unknown_neighbor(p_i, p_j),
                                                                                      unknown_neighbor(q_i, q_j))
                                                                join2 = joint(c_neighbors, unknown_neighbor(nn, mm))
                                                                if len(join2) != 1 and c != qq and (
                                                                        c // 10 != qq // 10 or len(join2) == min(qq,
                                                                                                                 c) % 10):
                                                                    maximum2 = max(c, qq)
                                                                    minimum2 = min(c, qq)
                                                                    cc = maximum2 - ((minimum2 // 10) * 10 + len(join2))
                                                                    if cc % 11 == 0:
                                                                        if c > qq:
                                                                            unjoin2 = unjoint(c_neighbors,
                                                                                              unknown_neighbor(nn, mm))
                                                                        else:
                                                                            unjoin2 = unjoint(unknown_neighbor(nn, mm),
                                                                                              c_neighbors)
                                                                        for item in unjoin2:
                                                                            ii = item[0]
                                                                            jj = item[1]
                                                                            flag(minefield[ii][jj], ii, jj)
                                                                    elif 10 > cc > 0:
                                                                        if c > qq:
                                                                            unjoin2 = unjoint(c_neighbors,
                                                                                              unknown_neighbor(nn, mm))
                                                                        else:
                                                                            unjoin2 = unjoint(unknown_neighbor(nn, mm),
                                                                                              c_neighbors)
                                                                        for item in unjoin2:
                                                                            ii = item[0]
                                                                            jj = item[1]
                                                                            clicker(minefield[ii][jj], ii, jj)


def far_neighbor(cell_i, cell_j):
    global minefield
    global mines_count
    global screen_clicker_list
    p_far = int(minefield[cell_i][cell_j])
    if p_far // 10 == 1:
        for ii in range(-2, 3):
            for jj in range(-2, 3):
                if abs(ii) == 2 or abs(jj) == 2:
                    n = cell_i + ii
                    m = cell_j + jj
                    if (16 > n > -1) and (30 > m > -1):
                        q_far = int(minefield[n][m])
                        if q_far != 0 and q_far // 10 != 7 and q_far // 10 != 9 and q_far // 10 != 8 and q_far // 10 != 0:
                            join = joint(unknown_neighbor(cell_i, cell_j), unknown_neighbor(n, m))
                            minimum = min(p_far, q_far)
                            maximum = max(p_far, q_far)
                            if len(join) != 0 and len(join) != 1 and p_far != q_far and (
                                    p_far // 10 != q_far // 10 or len(join) == minimum % 10):
                                c = maximum - (minimum // 10 * 10 + len(join))
                                if c % 11 == 0:
                                    if p_far > q_far:
                                        unjoin = unjoint(unknown_neighbor(cell_i, cell_j), unknown_neighbor(n, m))
                                    else:
                                        unjoin = unjoint(unknown_neighbor(n, m), unknown_neighbor(cell_i, cell_j))
                                    for item in unjoin:
                                        item_i = item[0]
                                        item_j = item[1]
                                        flag(minefield[item_i][item_j], item_i, item_j)
                                    g = minimum - ((minimum // 10) * 10 + len(join))
                                    if 10 > g > 0:
                                        if p_far > q_far:
                                            unjoin = unjoint(unknown_neighbor(cell_i, cell_j), unknown_neighbor(n, m))
                                        else:
                                            unjoin = unjoint(unknown_neighbor(n, m), unknown_neighbor(cell_i, cell_j))
                                        for item in unjoin:
                                            item_i = item[0]
                                            item_j = item[1]
                                            clicker(minefield[item_i][item_j], item_i, item_j)
                                elif 10 > c > 0 and (p_far // 10 == 1 or q_far // 10 == 1):
                                    if p_far > q_far:
                                        unjoin = unjoint(unknown_neighbor(cell_i, cell_j), unknown_neighbor(n, m))
                                    else:
                                        unjoin = unjoint(unknown_neighbor(n, m), unknown_neighbor(cell_i, cell_j))
                                    for item in unjoin:
                                        item_i = item[0]
                                        item_j = item[1]
                                        clicker(minefield[item_i][item_j], item_i, item_j)


if __name__ == '__main__':
    img_counter = 1
    state_counter = 1
    # Read RGB file to initialize RGB_list
    if os.path.exists('RGB.txt'):
        with open('RGB.txt') as f:
            data = f.read()
            RGB_list = json.loads(data)
    # Specifying the X and Y of the game on the screen
    x, y = game_location()
    unknown_cells_temp = 480
    # Main loop
    while unknown_cells_temp - unknown_cells < 2:
        starter()
        lost, minefield = screenshot(img_counter)
        if lost:
            exit()
            # emoji()
            # unknown_cells = 480
            # continue
        elif unknown_cells_temp - unknown_cells > 2:
            unknown_cells_temp = unknown_cells
            while True:
                screen_clicker_list = []
                lost, minefield = screenshot(img_counter)
                if not lost:
                    # img_counter += 1
                    for i in range(16):
                        for j in range(30):
                            solver(i, j)
                    if len(screen_clicker_list) == 0 and mines_count != 0:
                        print("Im in far_neighbor !!!!!!!!!!!!!!")
                        for i in range(16):
                            for j in range(30):
                                far_neighbor(i, j)
                    # If it can't continue the game, it will give a new state message
                    if len(screen_clicker_list) == 0 and mines_count != 0:
                        print("a new state !!")
                        state_counter += 1
                        answer = input("Press Y to save or any key to continue ...")
                        if answer == "y" or answer == "Y":
                            image_name = "state" + str(state_counter) + "mines_count" + str(mines_count) + ".jpg"
                            imagegrab.grab(bbox=(x[0], x[1], y[0], y[1])).save(image_name)
                        exit()
                    else:
                        screen_clicker()
                        print("mines_count = ", mines_count)
                        print("unknowns =  ", unknown_cells)
                    if mines_count == 0 and unknown_cells == 0:
                        print("!!!!   WIN   !!!!")
                        exit()
        else:
            unknown_cells_temp = unknown_cells
            continue
