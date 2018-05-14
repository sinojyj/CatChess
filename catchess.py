#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'sinojyj'

import pygame
import os
import random

class CatChess:
    WIDTH = 600
    HEIGHT = 600
    GRID_WIDTH = WIDTH // 6
    FPS = 60
    FONT_NAME = pygame.font.get_default_font() 

    # define colors
    WHITE = (255, 255, 255)
    CAT = (255, 255, 255)
    MICE = (73, 73, 73)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # define vars
    screen = object
    clock = object
    all_sprites = object
    background = object
    back_rect = object

    cat = 0             #猫棋子
    mice = []           #老鼠棋子list
    blank = []          #空白棋子list
    click_pos = -1      #鼠标点击位置
    current_type = ''   #选中棋子类型
    current_coin = -1   #选中棋子ID
    running = True      #运行标记
    ai = False          #ai标记
    winner = None       #胜利者标记
    

    def __init__(self, first = 1):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("CAT CHESS")
        self.all_sprites = pygame.sprite.Group()
        # base_folder = os.path.dirname(__file__)
        # 加载背景图片
        # img_folder = os.path.join(base_folder, 'images')
        # background_img = pygame.image.load(os.path.join(img_folder, 'back.png')).convert()
        background_img = pygame.image.load('back.png').convert()
        self.background = pygame.transform.scale(background_img, (self.WIDTH, self.HEIGHT))
        self.back_rect = self.background.get_rect()
        self.first = first #走棋顺序 1 MICE_FIRST 0 CAT_FIRST
        self.load_coin()

    # 绘制背景
    def draw_background(self):
        self.screen.blit(self.background, self.back_rect)
        # 画网格线，棋盘为 4 个 米字格
        # 1. 画出边框
        rect_lines = [
            #外边框
            ((self.GRID_WIDTH, self.GRID_WIDTH), (self.GRID_WIDTH, self.HEIGHT - self.GRID_WIDTH)),
            ((self.GRID_WIDTH, self.GRID_WIDTH), (self.WIDTH - self.GRID_WIDTH, self.GRID_WIDTH)),
            ((self.GRID_WIDTH, self.HEIGHT - self.GRID_WIDTH),
                (self.WIDTH - self.GRID_WIDTH, self.HEIGHT - self.GRID_WIDTH)),
            ((self.WIDTH - self.GRID_WIDTH, self.GRID_WIDTH),
                (self.WIDTH - self.GRID_WIDTH, self.HEIGHT - self.GRID_WIDTH)),
            #斜线
            ((self.GRID_WIDTH, self.GRID_WIDTH),(self.WIDTH - self.GRID_WIDTH, self.HEIGHT - self.GRID_WIDTH)),
            ((self.WIDTH - self.GRID_WIDTH, self.GRID_WIDTH),(self.GRID_WIDTH, self.HEIGHT - self.GRID_WIDTH)),
            ((self.GRID_WIDTH, self.HEIGHT // 2 ),(self.WIDTH // 2,self.GRID_WIDTH)),
            ((self.WIDTH // 2,self.GRID_WIDTH),(self.WIDTH - self.GRID_WIDTH , self.HEIGHT // 2)),
            ((self.GRID_WIDTH, self.HEIGHT // 2 ),(self.WIDTH // 2,self.HEIGHT - self.GRID_WIDTH)),
            ((self.WIDTH // 2,self.HEIGHT - self.GRID_WIDTH),(self.WIDTH - self.GRID_WIDTH , self.HEIGHT // 2))      
        ]
        for line in rect_lines:
            pygame.draw.line(self.screen, self.BLACK, line[0], line[1], 2)
            #内部细线
        for i in range(3):
            pygame.draw.line(self.screen, self.BLACK,
                             (self.GRID_WIDTH * (2 + i), self.GRID_WIDTH),
                             (self.GRID_WIDTH * (2 + i), self.HEIGHT - self.GRID_WIDTH))
            pygame.draw.line(self.screen, self.BLACK,
                             (self.GRID_WIDTH, self.GRID_WIDTH * (2 + i)),
                             (self.HEIGHT - self.GRID_WIDTH, self.GRID_WIDTH * (2 + i)))

        # 2. 画出交叉点
        circle_center = [
            (self.WIDTH // 2 , self.HEIGHT // 2),
            (self.GRID_WIDTH * 4, self.GRID_WIDTH * 4),
            (self.WIDTH - self.GRID_WIDTH * 4, self.GRID_WIDTH * 4),
            (self.WIDTH - self.GRID_WIDTH * 4, self.HEIGHT - self.GRID_WIDTH * 4),
            (self.GRID_WIDTH * 4, self.HEIGHT - self.GRID_WIDTH * 4),
        ]
        for cc in circle_center:
            pygame.draw.circle(self.screen, self.BLACK, cc, 5)

    # 位置序号转坐标
    def num_2_pos(self, num):
        return ((num % 5) + 1, (num // 5) + 1)

    # 坐标转位置序号
    def pos_2_num(self, pos):
        return (pos[1] - 1) * 5 + pos[0] - 1

    # 初始化棋局
    def load_coin(self):
        self.cat = 12
        self.mice = [0,1,2,3,4,5,9,10,14,15,19,20,21,22,23,24]
        self.blank = [6,7,8,11,13,16,17,18]
        self.winner = None
        self.turn = self.first
        self.click_pos = -1
        self.current_type = ''
        self.current_coin = -1

    # 获得当前 位置序号 可以移动到的 位置列表
    def get_possible_list(self, pos_id):
        # 所有序号 最大可走范围 set
        possible_list = {
            0:[1,5,6],
            1:[0,2,6],
            2:[1,3,6,7,8],
            3:[2,4,8],
            4:[3,8,9],
            5:[0,6,10],
            6:[0,1,2,5,7,10,11,12],
            7:[2,6,8,12],
            8:[2,3,4,7,9,12,13,14],
            9:[4,8,14],
            10:[5,6,11,15,16],
            11:[6,10,12,16],
            12:[6,7,8,11,13,16,17,18],
            13:[8,12,14,18],
            14:[8,9,13,18,19],
            15:[10,16,20],
            16:[10,11,12,15,17,20,21,22],
            17:[12,16,18,22],
            18:[12,13,14,17,19,22,23,24],
            19:[14,18,24],
            20:[15,16,21],
            21:[16,20,22],
            22:[16,17,18,21,23],
            23:[18,22,24],
            24:[18,19,23]
        }
        # 入参序号合法
        if pos_id in range(0,25):
            # 取入参序号最大可走范围 与 空白棋子 交集
            result = list(set(possible_list[pos_id]).union(set(self.blank))^(set(possible_list[pos_id])^set(self.blank)))
            return (result)
        else:
            return []

    # 绘制棋子
    def draw_coin(self):
        # 判断是否被选中
        if self.cat == self.current_coin:
            cat_color = self.GREEN
        else:
            cat_color = self.CAT

        pygame.draw.circle(self.screen, cat_color, (self.num_2_pos(self.cat)[0] * 
            self.GRID_WIDTH , self.num_2_pos(self.cat)[1] * self.GRID_WIDTH), 20)

        for mice_id in self.mice:
            if mice_id == self.current_coin:
                mice_color = self.GREEN
            else:
                mice_color = self.MICE
            mice_pos = self.num_2_pos(mice_id) 
            pygame.draw.circle(self.screen, mice_color, (mice_pos[0] * 
                self.GRID_WIDTH , mice_pos[1] * self.GRID_WIDTH), 15)

    # 绘制文本
    def draw_text(self, text, size, x, y, color=WHITE):
        font = pygame.font.Font(self.FONT_NAME, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    # 显示初始屏幕
    def show_go_screen(self, winner = None):
        self.load_coin()
        note_height = 10
        if winner is not None:
            self.draw_text( 'MICE {0} !'.format('win!' if winner == 'MICE' else 'lose!'),
                      80, self.WIDTH // 2, note_height, self.RED)
        else:
            self.screen.blit(self.background, self.back_rect)

        self.draw_text( 'CAT vs MICE', 64, self.WIDTH // 2, note_height + self.HEIGHT // 4, self.BLACK)
        self.draw_text( 'Press any key to start', 22, self.WIDTH // 2, note_height + self.HEIGHT // 2,
                  self.BLUE)
        pygame.display.flip()
        waiting = True
        while waiting:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                elif (event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONDOWN):
                    waiting = False
                    # 如果猫先走并且是在AI模式 AI先走一步
                    if(self.turn == 0 and self.ai):
                        self.ai_move()
    
    # 获取位置序号的当前信息
    def get_pos_info(self, pos_id):

        if (pos_id == self.cat):
            result = 'CAT'
        elif (pos_id in self.mice):
            result = 'MICE'
        else:
            result = 'BLANK'
        self.draw_coin()
        return (result , pos_id)

    # 响应鼠标事件
    def clickd_pos(self, pos):
        # 转换坐标系
        grid = (int(round(pos[0] / (self.GRID_WIDTH + .0))),
            int(round(pos[1] / (self.GRID_WIDTH + .0))))
        pos_id = self.pos_2_num(grid)
        # 更新选中位置
        self.click_pos = pos_id
        pos_info = self.get_pos_info(pos_id)
        # 选中非空白时 更新选中棋子 否则移动棋子
        if (pos_info[0] != 'BLANK'):
            self.current_coin = pos_info[1]
            self.current_type = pos_info[0]
        else:
            self.move_coin(self.current_type,self.current_coin,self.turn,pos_id)
            

    # 移动棋子
    # coin_type 棋子类型 (CAT MICE BLANK)
    # coin_id 棋子序号  (-1 to 24，-1 表示无选中初始状态)
    # turn 当前走棋方  (1:MICE , 0:CAT)
    # pos_id 目标位置序号 (0 to 24)
    def move_coin(self , coin_type, coin_id, turn, pos_id):
        # 获取棋子能走的范围
        move_possible_list = self.get_possible_list(coin_id)
        # 判断目标位置是否合法
        if(pos_id in move_possible_list):
            # 判断 猫棋子且猫回合 
            if(coin_type == 'CAT' and turn == 0):
                self.cat = pos_id
                self.blank.remove(self.cat)
                self.blank.append(coin_id)
                self.turn = 1
                eat_list = self.check_eat(pos_id)
                if (eat_list != []):
                    self.eat_coin(eat_list)
            elif(coin_type == 'MICE' and turn == 1):
                self.mice.remove(coin_id)
                self.mice.append(pos_id)
                self.blank.remove(pos_id)
                self.blank.append(coin_id)
                self.turn = 0
                self.check_win()
                # ai 猫 走棋 
                if (self.ai and self.winner == None):
                    self.ai_move()
            # 更新棋子  
            self.current_type = ''
            self.current_coin = -1  
            self.draw_coin()

    # 检查棋局是否结束
    def check_win(self):
        cat_possible_list = self.get_possible_list(self.cat)
        mice_num = len(self.mice)
        if(cat_possible_list == [] and mice_num > 4):
            self.winner = 'MICE'
        elif(cat_possible_list and mice_num <= 4):
            self.winner = "CAT"

    # 检查吃子
    def check_eat(self, pos_id):
        # 可以吃子的位置
        check_pos_list = list(set(range(25)) ^ set([0,4,20,24]))
        # 吃掉的list
        eat_list_result = []
        # 具体位置可以吃子的范围 序列元素及对称点
        check_eat_list = {
            1:[0],
            2:[1],
            3:[2],
            5:[0],
            6:[0,1,2,5],
            7:[2,6],
            8:[2,3,4,7],
            9:[4],
            10:[5],
            11:[6,10],
            12:[6,7,8,11],
            13:[8,12],
            14:[9],
            15:[10],
            16:[10,11,12,15],
            17:[12,16],
            18:[12,13,14,17],
            19:[14],
            21:[20],
            22:[21],
            23:[22]

        }
        if(pos_id in check_pos_list):
            eat_list = check_eat_list[pos_id]
            for eat_pos in eat_list:
                # 如果两端都是老鼠 则吃掉 同时更新空白棋子位置
                if(self.get_pos_info(eat_pos)[0] == 'MICE' and self.get_pos_info(pos_id * 2 - eat_pos)[0] == 'MICE'):
                    eat_list_result.append(eat_pos)
                    eat_list_result.append(pos_id * 2 - eat_pos)
        return eat_list_result

    # 吃子
    def eat_coin(self, eat_list):
        if (eat_list != []):
            for eat_pos in eat_list:
                self.mice.remove(eat_pos)
                self.blank.append(eat_pos)
        self.check_win()

    #ai 猫 走棋
    def ai_move(self):                
        # AI
        # 1. 获取猫可走的所有范围
        possible_list = self.get_possible_list(self.cat)
        # 2. 模拟走棋
        score_dict = {} # 评分容器
        for next_step in possible_list:
            # 可能吃棋
            can_eat = self.check_eat(next_step)
            # 下一步的活动空间
            next_possible_list = self.get_possible_list(next_step)
            # 评分 吃子权重10 活动空间权重 1 离中心权重 n ** 2 * 5
            next_pos = self.num_2_pos(next_step)
            score = {next_step : len(can_eat) * 10 + len(next_possible_list) + 1 -  ((next_pos[0] -3 )** 2 + (next_pos[1] -3 )** 2) * 5}
            score_dict.update(score)
        # 3. 挑选策略 
        max_score = max(score_dict.values())
        result_list = [] # 最优列表容器
        for key in score_dict:
            if (score_dict.get(key) == max_score):
                result_list.append(key)
        # 4. 执行走棋
        # 随机获取一步  
        
        next_step_result = result_list[random.randint(0, 10000) % len(result_list)]
        self.move_coin('CAT',self.cat,self.turn,next_step_result)

    # ai方式启动游戏
    def with_ai_start(self): 
        self.ai = True
        self.start_game()

    # 启动游戏
    def start_game(self):
        game_over = True
        winner = None
        while self.running:
            if game_over:
                self.show_go_screen(self.winner)
                # 重载棋局
                
                game_over = False

            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                   # 检查是否关闭窗口
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:

                    self.clickd_pos(event.pos)
                    if (self.winner is not None):
                        game_over = True
                    continue

            # Update
            self.all_sprites.update()
            self.all_sprites.draw(self.screen)
            self.draw_background()
            self.draw_coin()
            # After drawing everything, flip the display
            pygame.display.flip()
        pygame.quit()

if __name__ == '__main__':

    # game = CatChess(0).start_game()
    game = CatChess(1).with_ai_start()
