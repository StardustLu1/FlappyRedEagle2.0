import pygame
import os
import random

pygame.init()

SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
PIPE_WIDTH = 52
PIPE_HEIGHT = 320
PIPE_GAP = 100  # 调整管道之间的左右间距
GAP = 135  # 调整上下管道之间的间隙
PIPE_VELOCITY = 3  # 管道移动速度
GROUND_HEIGHT = 112  # 地面高度
BIRD_WIDTH = 34  # 小鸟的宽度
BIRD_HEIGHT = 24  # 小鸟的高度
BIRD_X = 50  # 小鸟的初始X坐标
JUMP_VELOCITY = -9  # 小鸟跳跃的初速度
GRAVITY = 0.5  # 小鸟的重力加速度
ROTATION_SPEED = 5  # 旋转速度

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Xiaomu")

script_dir = os.path.dirname(os.path.abspath(__file__))
# 加载新背景图并进行缩放
background_img = pygame.image.load(os.path.join(script_dir, "assets", "sprites", "new-background.png"))
background_img = pygame.transform.scale(background_img, (1100, 591))  # 适应大背景图
background_width = background_img.get_width()

ground = pygame.image.load(os.path.join(script_dir, "assets", "sprites", "base.png"))
pipe_img = pygame.image.load(os.path.join(script_dir, "assets", "sprites", "pipe-green.png"))

pipe_top_img = pygame.transform.flip(pipe_img, False, True)  # 上管道是翻转的

# 加载小鸟的图片
bird_images = [
    pygame.image.load(os.path.join(script_dir, "assets", "sprites", "redbird-upflap.png")),
    pygame.image.load(os.path.join(script_dir, "assets", "sprites", "redbird-midflap.png")),
    pygame.image.load(os.path.join(script_dir, "assets", "sprites", "redbird-downflap.png"))
]
bird_index = 1  # 小鸟的初始图片（中间）

game_over_images = {
    "low": pygame.image.load(os.path.join(script_dir, "assets", "sprites", "cai.png")),
    "high": pygame.image.load(os.path.join(script_dir, "assets", "sprites", "qiang.png"))
}

# 加载数字图片（0-9）
digit_images = [pygame.image.load(os.path.join(script_dir, "assets", "sprites", f"{i}.png")) for i in range(10)]

class Ground:
    def __init__(self):
        self.x = 0
        self.width = ground.get_width()
        self.y = SCREEN_HEIGHT - ground.get_height()

    def move(self):
        self.x -= 4

        if self.x <= -self.width:
            self.x = 0

    def draw(self, screen):
        screen.blit(ground, (self.x, self.y))
        screen.blit(ground, (self.x + self.width, self.y))

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, SCREEN_HEIGHT - GAP - GROUND_HEIGHT - 100)  # 调整范围，确保下管道不接地面
        self.top = self.height - PIPE_HEIGHT  # 上管道的顶部坐标
        self.bottom = self.height + GAP  # 下管道的底部坐标

        # 缩小管道的碰撞区域（给小鸟留一点缓冲区）
        self.rect_top = pygame.Rect(self.x + 5, self.top + 5, PIPE_WIDTH - 10, PIPE_HEIGHT - 10)
        self.rect_bottom = pygame.Rect(self.x + 5, self.bottom + 5, PIPE_WIDTH - 10, SCREEN_HEIGHT - self.bottom - GROUND_HEIGHT - 10)

    def move(self):
        self.x -= PIPE_VELOCITY
        self.rect_top.x = self.x
        self.rect_bottom.x = self.x

    def draw(self, screen):
        screen.blit(pipe_top_img, self.rect_top)
        screen.blit(pipe_img, self.rect_bottom)

    def off_screen(self):
        return self.x < -PIPE_WIDTH

class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = SCREEN_HEIGHT // 2
        self.vel_y = 0  # 小鸟的垂直速度
        self.angle = 0  # 当前角度
        self.target_angle = 0  # 目标角度
        self.image = bird_images[bird_index]
        self.image_index = 1
        self.frame_counter = 1  # 用于控制小鸟动画帧的切换
        self.is_falling = False  # 新增的标记，控制小鸟下坠速度

    def update(self):
        if self.is_falling:  # 小鸟开始下坠
            self.vel_y += GRAVITY  # 应用重力
        else:  # 如果小鸟还没有开始下坠（跳跃后的缓慢下坠）
            self.vel_y = max(self.vel_y + 0.1, GRAVITY)  # 轻微下坠，防止突然下坠

        self.y += self.vel_y

        # 根据垂直速度确定目标角度
        if self.vel_y < 0:  # 向上跳跃
            self.target_angle = 30
        elif self.vel_y > 0:  # 向下下坠
            self.target_angle = -20

        # 逐渐过渡角度
        if self.angle < self.target_angle:
            self.angle = min(self.angle + ROTATION_SPEED, self.target_angle)
        elif self.angle > self.target_angle:
            self.angle = max(self.angle - ROTATION_SPEED, self.target_angle)

        # 根据小鸟的状态切换动画帧
        if self.vel_y < 0:  # 向上跳跃
            self.image_index = 2  # 使用上翅膀图片
        elif self.vel_y > 0:  # 向下下坠
            self.image_index = 0  # 使用下翅膀图片
        else:  # 处于平衡状态时
            self.image_index = 1  # 使用中间翅膀图片

        self.image = bird_images[self.image_index]

        # 限制小鸟下落不超过屏幕底部
        if self.y > SCREEN_HEIGHT - GROUND_HEIGHT - self.image.get_height():
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.image.get_height()
            self.vel_y = 0
            self.is_falling = False  # 如果触底，停止下坠

        # 限制小鸟不超出顶部
        if self.y < 0:
            self.y = 0
            self.vel_y = 0
            self.is_falling = False  # 如果碰到顶部，也停止下坠

    def jump(self):
        self.vel_y = JUMP_VELOCITY  # 设置跳跃速度
        self.is_falling = True  # 允许下坠

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, self.angle)  # 根据角度旋转小鸟
        screen.blit(rotated_image, (self.x, self.y))

    def get_rect(self):
        # 缩小小鸟的碰撞检测矩形，给小鸟周围留出一些缓冲区域
        return pygame.Rect(self.x + 2, self.y + 2, self.image.get_width() - 4, self.image.get_height() - 4)

def draw_score(score, screen):
    """绘制得分，使用数字图片"""
    score_str = str(score)
    score_width = 0
    for digit in score_str:
        score_width += digit_images[int(digit)].get_width()

    x_offset = (SCREEN_WIDTH - score_width) // 2  # 使得分居中显示

    for digit in score_str:
        screen.blit(digit_images[int(digit)], (x_offset, 20))
        x_offset += digit_images[int(digit)].get_width()

# 调整按钮大小
reset_button = pygame.image.load(os.path.join(script_dir, "assets", "sprites", "RC.png"))
reset_button = pygame.transform.scale(reset_button, (160, 100))  # 缩放按钮为适合的大小

# 游戏结束重置函数
def reset_game():
    global game_over, score, bird, pipes, ground_obj, delay_start  # 确保重置所有相关的全局变量
    game_over = False
    delay_start = None
    score = 0
    bird = Bird()  # 重新创建 Bird 实例
    pipes = [Pipe(SCREEN_WIDTH + 100)]  # 重置管道列表
    ground_obj = Ground()  # 重置地面对象

# 游戏主循环
def game_loop():
    global game_over, score, pipes, ground_obj, bird
    clock = pygame.time.Clock()
    running = True

    # 初始化游戏状态
    pipes = [Pipe(SCREEN_WIDTH + 100)]
    ground_obj = Ground()
    bird = Bird()
    score = 0
    game_over = False
    delay_start = None  # 用于记录延迟的开始时间

    background_x = 0  # 背景的初始x位置
    background_velocity = 2  # 背景滚动速度

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                if not game_over:
                    bird.jump()

        if not game_over:
            for pipe in pipes:
                pipe.move()

            pipes = [pipe for pipe in pipes if not pipe.off_screen()]

            if pipes[-1].x < SCREEN_WIDTH - PIPE_GAP:
                pipes.append(Pipe(SCREEN_WIDTH + 100))

            bird.update()

            for pipe in pipes:
                if bird.get_rect().colliderect(pipe.rect_top) or bird.get_rect().colliderect(pipe.rect_bottom):
                    game_over = True
                if bird.y >= SCREEN_HEIGHT - GROUND_HEIGHT - bird.image.get_height():
                    game_over = True

            for pipe in pipes:
                if pipe.x + PIPE_WIDTH < bird.x and not hasattr(pipe, "passed"):
                    score += 1
                    pipe.passed = True

        # 背景滚动逻辑
        screen.fill((0, 0, 0))
        background_x -= background_velocity
        if background_x <= -background_width:
            background_x = 0  # 背景滚动到左侧时复位

        # 绘制两张背景图片以避免黑块
        screen.blit(background_img, (background_x, 0))
        screen.blit(background_img, (background_x + background_width, 0))

        for pipe in pipes:
            pipe.draw(screen)

        bird.draw(screen)
        ground_obj.move()
        ground_obj.draw(screen)

        draw_score(score, screen)

        if game_over:
            if delay_start is None:
                delay_start = pygame.time.get_ticks()  # 记录延迟开始时间

            # 计算从延迟开始到现在的时间差
            elapsed_time = pygame.time.get_ticks() - delay_start

            if elapsed_time >= 2000:  # 延迟时间到达2000ms（2秒）
                # 游戏结束画面
                screen.fill((0, 0, 0))

                if score < 20:
                    game_over_image = game_over_images["low"]
                else:
                    game_over_image = game_over_images["high"]

                image_x = (SCREEN_WIDTH - game_over_image.get_width()) // 2
                image_y = (SCREEN_HEIGHT - game_over_image.get_height()) // 2
                screen.blit(game_over_image, (image_x, image_y))

                font = pygame.font.Font(None, 50)
                score_text = font.render(f"Score: {score}", True, (255, 255, 255))
                score_x = (SCREEN_WIDTH - score_text.get_width()) // 2
                score_y = image_y - 50
                screen.blit(score_text, (score_x, score_y))

                button_x = (SCREEN_WIDTH - reset_button.get_width()) // 2
                button_y = image_y + game_over_image.get_height() + 20
                screen.blit(reset_button, (button_x, button_y))

                # 检查按钮点击
                if pygame.mouse.get_pressed()[0]:  # 检测鼠标左键点击
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if button_x <= mouse_x <= button_x + reset_button.get_width() and button_y <= mouse_y <= button_y + reset_button.get_height():
                        delay_start = None
                        reset_game()  # 调用重置函数

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    game_loop()
