"""
飛機遊戲
"""
import random
from pathlib import Path
from time import sleep

import pygame

p = Path(__file__).parent  # 檔案位置
img_dir = p.joinpath("images")  # 圖片資料夾

INVINCIBLE_MODE = True  # 無敵模式

pygame.init()  # 初始化

WIDTH = 800  # 視窗寬度
HEIGHT = 600  # 視窗高度
BAR_LENGTH = 150  # 生命值長度
BAR_HEIGHT = 20  # 生命值高度

WHITE = pygame.Color("white")
GREEN = pygame.Color("green")
BLACK = pygame.Color("black")

size = WIDTH, HEIGHT  # 視窗大小
screen = pygame.display.set_mode(size)  # 設定視窗大小
pygame.display.set_caption("太空射擊")  # 設定視窗標題

clock = pygame.time.Clock()  # 遊戲刷新間隔計時

background_color = pygame.Surface(screen.get_size())
background_color.fill(WHITE)

background = pygame.image.load(
    img_dir.joinpath("background.jpg")
).convert_alpha()  # 匯入背景
background = pygame.transform.scale(background, (WIDTH, HEIGHT))  # 背景大小
background.set_alpha(225)

# background = pygame.Surface(screen.get_size()).convert()
# background.fill((0,0,0))    #黑色


# 設定遊玩圖片
player_image = pygame.image.load(img_dir.joinpath("airplane.png")).convert_alpha()
bullet_image = pygame.image.load(img_dir.joinpath("bullet.png")).convert_alpha()
enemy_image = pygame.image.load(img_dir.joinpath("enemy.png")).convert_alpha()


class Player(pygame.sprite.Sprite):
    """
    玩家
    """

    def __init__(self):
        super().__init__()  # pygame物件繼承init
        self.image = pygame.transform.scale(player_image, (80, 80))  # 飛機圖片大小
        self.rect = self.image.get_rect()  # 玩家碰撞範圍
        self.radius = 35  # 判定玩家範圍半徑

        # 飛機初始位置
        self.rect.centerx = WIDTH / 2  # 寬度
        self.rect.bottom = HEIGHT - 10  # 高度
        self.hp = 100

    def update(self) -> None:  # 更新xy位置
        x, y = pygame.mouse.get_pos()
        self.rect.centerx = x
        self.rect.centery = y

        # 檢查飛機是否超出範圍
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):  # 射擊
        bullet = Bullet(self.rect.centerx, self.rect.top)  # 飛機中間上面射出子彈
        all_sprites.add(bullet)  # 子彈群組加入所有物件群組
        bullets.add(bullet)  # 子彈群組加入所有子彈群組


class Enemy(pygame.sprite.Sprite):
    """
    敵人
    """

    MIN_SPEED_CHANGE_ITV = 500  # 最小速度更新間隔
    MAX_SPEED_CHANGE_ITV = 2000  # 最大速度更新間隔

    def __init__(self, x=None, y=None, speedx=None, speedy=None):  # 敵人初始座標速度
        super().__init__()  # pygame物件繼承init
        self.next_speed_time = 0  # 下一次速度更新時間
        self.image = pygame.transform.scale(enemy_image, (80, 80))  # 敵人圖片大小
        self.image = pygame.transform.rotate(self.image, 180)  # 敵人旋轉180度
        self.rect = self.image.get_rect()  # 敵人碰撞範圍
        self.radius = self.rect.width * 0.85 / 2  # 判定敵人範圍半徑

        # 亂數生成敵人位置
        self.rect.x = random.randint(0, WIDTH - self.rect.width) if not x else x
        self.rect.y = 0 if not y else y

        # 亂數生成敵人速度
        self.speedx = random.randint(-3, 3) if not speedx else speedx
        self.speedy = random.randint(2, 6) if not speedy else speedy

    def update(self):  # 更新xy位置
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # 如果敵人跑出窗口，重新生成敵人的位置和速度
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-50, -20)

        # 撞牆反彈
        if self.rect.left < 0 or self.rect.right > WIDTH:  # 左右反彈
            self.speedx = -self.speedx

    # 敵人方向變化
    def random_speed(self):
        random_delay = random.randint(
            self.MIN_SPEED_CHANGE_ITV, self.MAX_SPEED_CHANGE_ITV
        )
        self.next_speed_time = pygame.time.get_ticks() + random_delay
        self.speedx = random.randint(-10, 10)
        self.speedy = random.randint(2, 10)


class Bullet(pygame.sprite.Sprite):
    """
    子彈
    """

    def __init__(self, x, y):  # 子彈初始射出位置
        super().__init__()  # pygame物件init
        self.image = pygame.transform.scale(bullet_image, (25, 50))  # 子彈圖片大小
        self.rect = self.image.get_rect()  # 子彈碰撞範圍
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10  # 子彈y軸速度

    def update(self):  # 更新xy位置
        self.rect.y += self.speedy
        if self.rect.bottom < 0:  # 如果子彈超出螢幕範圍
            self.kill()  # 刪除子彈


def draw_hp_bar(hp, screen, x, y):
    """
    畫出生命值

    screen: 螢幕
    x: x座標
    y: y座標
    hp: 生命值
    """
    hp = max(hp, 0)

    # 生命值長度
    width = (hp / 100) * BAR_LENGTH

    # 外框
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)

    # 生命值
    hp_rect = pygame.Rect(x, y, width, BAR_HEIGHT)
    un_hp_rect = pygame.Rect(x + width, y, BAR_LENGTH - width, BAR_HEIGHT)

    pygame.draw.rect(screen, BLACK, un_hp_rect)
    pygame.draw.rect(screen, GREEN, hp_rect)  # 血量
    pygame.draw.rect(screen, WHITE, outline_rect, 2)  # 外框


if __name__ == "__main__":

    all_sprites = pygame.sprite.Group()  # 所有物件群組
    player = Player()  # 玩家
    all_sprites.add(player)  # 玩家群組加入所有物件群組

    enemies = pygame.sprite.Group()  # 敵人群組
    bullets = pygame.sprite.Group()  # 子彈群組

    enemies_num = 5  # 敵人數量
    for i in range(enemies_num):  # 生成五個敵人
        enemy = Enemy()
        all_sprites.add(enemy)  # 敵人加入所有物件群組
        enemies.add(enemy)  # 敵人加入所有敵人群組

    # 子彈發射間隔
    bullets_timer = pygame.USEREVENT
    pygame.time.set_timer(bullets_timer, 500)  # 每0.5跑一顆子彈

    # 分數
    score = 0  # 從0分開始計算
    font = pygame.font.SysFont("Calibri", 50)  # 分數字型字體

    running = True  # 執行
    is_pause = False
    while running:
        clock.tick(30)  # 一秒刷新30次
        if not is_pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # 關閉遊戲視窗
                    running = False

                if event.type == bullets_timer:
                    player.shoot()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        is_pause = True

                    if event.key == pygame.K_ESCAPE:
                        running = False

            # 敵人方向和速度變化
            for e in enemies:
                if e.next_speed_time < pygame.time.get_ticks():
                    e.random_speed()

            all_sprites.update()  # 每執行一次所有物件群組更新

            # 生成新的敵人
            hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
            for hit in hits:
                score += 1  # 每次擊中家+1分
                e = Enemy()  # 生成敵人位置
                all_sprites.add(e)  # e加入所有物件群組
                enemies.add(e)  # e加入所有敵人群組

            # 碰撞理處
            hits = pygame.sprite.spritecollide(
                player, enemies, False, pygame.sprite.collide_circle
            )  # 圓形碰撞處理
            if hits:
                if player.hp > 0:
                    if not INVINCIBLE_MODE:
                        player.hp -= 20
                    for e in hits:
                        e.kill()
                        enemy = Enemy()
                        all_sprites.add(enemy)  # 敵人加入所有物件群組
                        enemies.add(enemy)  # 敵人加入所有敵人群組

                if player.hp <= 0:
                    text = font.render("Game Over", True, (WHITE))  # 遊戲結束的字幕
                    textW = text.get_rect().width
                    textH = text.get_rect().height
                    screen.blit(
                        text, ((WIDTH - textW) / 2, (HEIGHT - textH) / 2)
                    )  # 顯示結束字幕至中
                    pygame.display.update()  # 更新
                    sleep(1)  # 等待一秒結束
                    running = False

            screen.blit(background_color, (0, 0))
            screen.blit(background, (0, 0))  # 背景位置

            # 打印分數
            screen.blit(font.render(str(score), True, (WHITE)), (WIDTH / 2, 48))

            # 印出血條
            all_sprites.draw(screen)  # 顯示所有物件群組
            draw_hp_bar(player.hp, screen, 50, 50)

            pygame.display.update()  # 更新

        # 暫停
        if is_pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # 關閉遊戲視窗
                    running = False

                if event.type == pygame.KEYDOWN:  # 如果暫停時按了p則繼續遊戲
                    if event.key == pygame.K_p:
                        is_pause = False

                    if event.key == pygame.K_ESCAPE:
                        running = False

    pygame.quit()  # 結束
