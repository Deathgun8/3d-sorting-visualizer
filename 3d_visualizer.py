import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import subprocess
import time
import os
import sys
import math
import numpy as np

class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=11025, size=-16, channels=2, buffer=512)
        self.enabled = True
        self.volume = 0.3
    
    def create_tone(self, frequency, duration=0.1):
        """Cria um tom com a frequência especificada"""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Gerar onda senoidal
        wave_array = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
        
        # Aplicar envelope para suavizar o som (fade in/out)
        fade_frames = frames // 10
        wave_array[:fade_frames] *= np.linspace(0, 1, fade_frames)
        wave_array[-fade_frames:] *= np.linspace(1, 0, fade_frames)
        
        # Ajustar volume e converter para int16
        wave_array = (wave_array * self.volume * 32767).astype(np.int16)
        
        # Converter para stereo e garantir que seja C-contiguous
        stereo_wave = np.array([wave_array, wave_array]).T
        stereo_wave = np.ascontiguousarray(stereo_wave)
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def play_comparison_sound(self, value1, value2, max_value):
        """Toca som baseado na comparação de dois valores"""
        if not self.enabled:
            return
        
        # Frequência baseada na média dos valores sendo comparados
        avg_value = (value1 + value2) / 2
        # Mapear para frequência entre 200Hz e 800Hz
        frequency = 200 + (avg_value / max_value) * 400
        
        sound = self.create_tone(frequency, 0.05)  # Som mais curto para comparações
        sound.play()
    
    def play_swap_sound(self, value1, value2, max_value):
        """Toca som especial quando há troca"""
        if not self.enabled:
            return
        
        # Som mais grave para indicar troca
        avg_value = (value1 + value2) / 2
        frequency = 150 + (avg_value / max_value) * 100
        
        sound = self.create_tone(frequency, 0.15)  # Som mais longo para trocas
        sound.play()
    
    def play_quicksort_pivot_sound(self, pivot_value, max_value):
        """Toca som especial para o pivot do quicksort"""
        if not self.enabled:
            return
        
        # Som distintivo para o pivot - frequência mais alta e duração curta
        frequency = 400 + (pivot_value / max_value) * 300
        
        # Tom com modulação para se destacar
        sample_rate = 22050
        duration = 0.08
        frames = int(duration * sample_rate)
        
        # Criar onda com modulação para som mais interessante
        t = np.linspace(0, duration, frames)
        wave_array = np.sin(2 * np.pi * frequency * t) * np.sin(10 * np.pi * t)
        
        # Aplicar envelope
        fade_frames = frames // 8
        wave_array[:fade_frames] *= np.linspace(0, 1, fade_frames)
        wave_array[-fade_frames:] *= np.linspace(1, 0, fade_frames)
        
        # Ajustar volume
        wave_array = (wave_array * self.volume * 0.8 * 32767).astype(np.int16)
        
        # Converter para stereo
        stereo_wave = np.array([wave_array, wave_array]).T
        stereo_wave = np.ascontiguousarray(stereo_wave)
        
        sound = pygame.sndarray.make_sound(stereo_wave)
        sound.play()
    
    def play_quicksort_partition_sound(self, left_idx, right_idx, array_length):
        """Toca som para indicar particionamento no quicksort"""
        if not self.enabled:
            return
        
        # Som baseado na posição da partição
        position_ratio = (left_idx + right_idx) / (2 * array_length)
        frequency = 250 + position_ratio * 200
        
        sound = self.create_tone(frequency, 0.06)
        sound.play()
    
    def play_completion_sound(self):
        """Toca som de conclusão quando a ordenação termina"""
        if not self.enabled:
            return
        
        # Sequência de tons ascendentes
        frequencies = [131, 165, 196, 262]  # C3, E3, G3, C4
        for i, freq in enumerate(frequencies):
            pygame.time.wait(i * 50)  # Pequeno delay entre notas
            sound = self.create_tone(freq, 0.3)
            sound.play()
    
    def toggle(self):
        """Liga/desliga o som"""
        self.enabled = not self.enabled
        return self.enabled
    
    def set_volume(self, volume):
        """Ajusta o volume (0.0 a 1.0)"""
        self.volume = max(0.0, min(1.0, volume))

    def play_merge_sound(self, value, index, max_value):
        if not self.enabled:
            return
        frequency = 180 + (value / max_value) * 250
        sound = self.create_tone(frequency, 0.05)
        sound.play()

def draw_bar(x, height):
    w = 0.5  # largura
    d = 0.5  # profundidade
    h = height

    # Gradiente de roxo → laranja
    max_height = 40.0
    factor = min(1.0, height / max_height)
    r = 0.5 + 0.5 * factor
    g = 0.0 + 0.5 * factor
    b = 0.5 - 0.5 * factor

    vertices = [
        [x - w, 0, -d],  # 0
        [x + w, 0, -d],  # 1
        [x + w, h, -d],  # 2
        [x - w, h, -d],  # 3
        [x - w, 0,  d],  # 4
        [x + w, 0,  d],  # 5
        [x + w, h,  d],  # 6
        [x - w, h,  d]   # 7
    ]

    faces = [
        [0, 1, 2, 3],  # frente
        [4, 5, 6, 7],  # trás
        [0, 4, 7, 3],  # esquerda
        [1, 5, 6, 2],  # direita
        [3, 2, 6, 7],  # cima
        [0, 1, 5, 4]   # baixo
    ]

    # Face sólida colorida
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    for face in faces:
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()

    # Desenhar bordas pretas
    glColor3f(0, 0, 0)
    glLineWidth(1.5)
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # frente
        (4, 5), (5, 6), (6, 7), (7, 4),  # trás
        (0, 4), (1, 5), (2, 6), (3, 7)   # conexões frente-trás
    ]
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    glLightfv(GL_LIGHT0, GL_POSITION, [10, 50, 100, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.7, 0.7, 0.7, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
    
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

def draw_text_bitmap(text, x, y, color=(1.0, 1.0, 1.0)):
    """Desenha texto usando caracteres bitmap simples"""
    # Implementação básica de bitmap para letras essenciais
    # Cada caractere é definido em uma grade 8x12
    
    char_width = 12
    char_height = 16
    spacing = 2
    
    glColor3f(color[0], color[1], color[2])
    glPointSize(2.0)
    
    current_x = x
    
    # Dicionário com padrões de bitmap para caracteres necessários
    char_patterns = {
        'B': [
            "████████",
            "█      █",
            "█      █", 
            "█      █",
            "████████",
            "█      █",
            "█      █",
            "█      █",
            "████████"
        ],
        'U': [
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            "████████"
        ],
        'L': [
            "█       ",
            "█       ",
            "█       ",
            "█       ",
            "█       ",
            "█       ",
            "█       ",
            "█       ",
            "████████"
        ],
        'E': [
            "████████",
            "█       ",
            "█       ",
            "█       ",
            "████████",
            "█       ",
            "█       ",
            "█       ",
            "████████"
        ],
        'S': [
            "████████",
            "█       ",
            "█       ",
            "█       ",
            "████████",
            "       █",
            "       █",
            "       █",
            "████████"
        ],
        'O': [
            "████████",
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            "████████"
        ],
        'R': [
            "████████",
            "█      █",
            "█      █",
            "█      █",
            "████████",
            "█   █   ",
            "█    █  ",
            "█     █ ",
            "█      █"
        ],
        'T': [
            "████████",
            "   █    ",
            "   █    ",
            "   █    ",
            "   █    ",
            "   █    ",
            "   █    ",
            "   █    ",
            "   █    "
        ],
        'M': [
            "█      █",
            "██    ██",
            "█ █  █ █",
            "█  ██  █",
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            "█      █"
        ],
        'G': [
            "████████",
            "█       ",
            "█       ",
            "█       ",
            "█   ████",
            "█      █",
            "█      █",
            "█      █",
            "████████"
        ],
        'Q': [
            "████████",
            "█      █",
            "█      █",
            "█      █",
            "█      █",
            "█   █  █",
            "█    █ █",
            "█      █",
            "████████"
        ],
        'I': [
            "████████",
            "   █    ",
            "   █    ",
            "   █    ",
            "   █    ",
            "   █    ",
            "   █    ",
            "   █    ",
            "████████"
        ],
        'C': [
            "████████",
            "█       ",
            "█       ",
            "█       ",
            "█       ",
            "█       ",
            "█       ",
            "█       ",
            "████████"
        ],
        'K': [
            "█      █",
            "█     █ ",
            "█    █  ",
            "█   █   ",
            "████    ",
            "█   █   ",
            "█    █  ",
            "█     █ ",
            "█      █"
        ],
        ' ': [
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "        "
        ]
    }
    
    for char in text.upper():
        if char in char_patterns:
            pattern = char_patterns[char]
            for row, line in enumerate(pattern):
                for col, pixel in enumerate(line):
                    if pixel == '█':
                        glBegin(GL_POINTS)
                        glVertex2f(current_x + col, y + row * 2)
                        glEnd()
        current_x += char_width + spacing

def get_text_bounds(text, x, y):
    """Retorna os limites (bounds) de um texto para detecção de clique"""
    char_width = 12
    spacing = 2
    char_height = 18
    
    text_width = len(text) * (char_width + spacing)
    return {
        'x': x,
        'y': y,
        'width': text_width,
        'height': char_height
    }

def is_point_in_bounds(point_x, point_y, bounds):
    """Verifica se um ponto está dentro dos limites especificados"""
    return (bounds['x'] <= point_x <= bounds['x'] + bounds['width'] and
            bounds['y'] <= point_y <= bounds['y'] + bounds['height'])

def draw_menu_bar(display_width, display_height, active_algorithm):
    """Desenha a barra de menu estática no topo da tela"""
    # Salvar o estado atual da matriz
    glPushMatrix()
    
    # Configurar projeção ortográfica para desenho 2D
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, display_width, display_height, 0, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Desabilitar iluminação e teste de profundidade para o menu
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Habilitar blending para transparência
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Desenhar fundo da barra de menu (cinza claro translúcido)
    menu_height = 100
    glColor4f(0.8, 0.8, 0.8, 0.85)  # Cinza claro com 85% de opacidade
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(display_width, 0)
    glVertex2f(display_width, menu_height)
    glVertex2f(0, menu_height)
    glEnd()
    
    # Desenhar linha de separação na parte inferior
    glColor4f(0.5, 0.5, 0.5, 1.0)  # Cinza mais escuro
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glVertex2f(0, menu_height)
    glVertex2f(display_width, menu_height)
    glEnd()
    
    # Posições dos textos - reorganizadas para incluir Quick Sort
    bubble_text_x = 50
    bubble_text_y = 30
    merge_text_x = 280
    merge_text_y = 30
    quick_text_x = 500
    quick_text_y = 30
    
    # Desenhar fundo de destaque para o algoritmo ativo
    if active_algorithm == "bubble":
        bounds = get_text_bounds("BUBBLE SORT", bubble_text_x, bubble_text_y)
        glColor4f(0.9, 0.8, 1.0, 0.6)  # Roxo muito claro para destaque
        glBegin(GL_QUADS)
        glVertex2f(bounds['x'] - 5, bounds['y'] - 5)
        glVertex2f(bounds['x'] + bounds['width'] + 5, bounds['y'] - 5)
        glVertex2f(bounds['x'] + bounds['width'] + 5, bounds['y'] + bounds['height'] + 5)
        glVertex2f(bounds['x'] - 5, bounds['y'] + bounds['height'] + 5)
        glEnd()
    elif active_algorithm == "merge":
        bounds = get_text_bounds("MERGE SORT", merge_text_x, merge_text_y)
        glColor4f(0.9, 0.8, 1.0, 0.6)  # Roxo muito claro para destaque
        glBegin(GL_QUADS)
        glVertex2f(bounds['x'] - 5, bounds['y'] - 5)
        glVertex2f(bounds['x'] + bounds['width'] + 5, bounds['y'] - 5)
        glVertex2f(bounds['x'] + bounds['width'] + 5, bounds['y'] + bounds['height'] + 5)
        glVertex2f(bounds['x'] - 5, bounds['y'] + bounds['height'] + 5)
        glEnd()
    elif active_algorithm == "quick":
        bounds = get_text_bounds("QUICK SORT", quick_text_x, quick_text_y)
        glColor4f(0.9, 0.8, 1.0, 0.6)  # Roxo muito claro para destaque
        glBegin(GL_QUADS)
        glVertex2f(bounds['x'] - 5, bounds['y'] - 5)
        glVertex2f(bounds['x'] + bounds['width'] + 5, bounds['y'] - 5)
        glVertex2f(bounds['x'] + bounds['width'] + 5, bounds['y'] + bounds['height'] + 5)
        glVertex2f(bounds['x'] - 5, bounds['y'] + bounds['height'] + 5)
        glEnd()
    
    # Desenhar texto "BUBBLE SORT" 
    bubble_color = (0.4, 0.2, 0.6) if active_algorithm == "bubble" else (0.6, 0.4, 0.8)
    draw_text_bitmap("BUBBLE SORT", bubble_text_x, bubble_text_y, bubble_color)
    
    # Desenhar texto "MERGE SORT"
    merge_color = (0.4, 0.2, 0.6) if active_algorithm == "merge" else (0.6, 0.4, 0.8)
    draw_text_bitmap("MERGE SORT", merge_text_x, merge_text_y, merge_color)
    
    # Desenhar texto "QUICK SORT"
    quick_color = (0.4, 0.2, 0.6) if active_algorithm == "quick" else (0.6, 0.4, 0.8)
    draw_text_bitmap("QUICK SORT", quick_text_x, quick_text_y, quick_color)
    
    # Restaurar configurações
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    
    # Restaurar matrizes
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    # Retornar os bounds para detecção de clique
    return {
        'bubble': get_text_bounds("BUBBLE SORT", bubble_text_x, bubble_text_y),
        'merge': get_text_bounds("MERGE SORT", merge_text_x, merge_text_y),
        'quick': get_text_bounds("QUICK SORT", quick_text_x, quick_text_y)
    }

def draw_scene(values, camera_angle_x, camera_angle_y, camera_distance, display_size, active_algorithm):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Desenhar a visualização 3D
    glLoadIdentity()
    
    camera_x = camera_distance * math.sin(math.radians(camera_angle_x)) * math.cos(math.radians(camera_angle_y))
    camera_y = camera_distance * math.sin(math.radians(camera_angle_y))
    camera_z = camera_distance * math.cos(math.radians(camera_angle_x)) * math.cos(math.radians(camera_angle_y))
    
    array_center = 0
    
    gluLookAt(camera_x, camera_y, camera_z,
              array_center, 10, 0,
              0, 1, 0)
    
    setup_lighting()
    
    spacing = 1.5
    max_height = max(values) if values else 1
    offset = -len(values) * spacing / 2
    
    for i, v in enumerate(values):
        height = (v / max_height) * 30
        draw_bar(offset + i * spacing, height)
    
    # Desenhar a barra de menu por último (sobreposta) e retornar bounds
    menu_bounds = draw_menu_bar(display_size[0], display_size[1], active_algorithm)
    
    pygame.display.flip()
    
    return menu_bounds

def run_visualizer(algorithm="bubble"):
    print(f"Tentando executar {algorithm}_sort.exe...")
    
    if algorithm == "bubble":
        exe_name = 'bubble_sort.exe' if sys.platform == 'win32' else './bubble_sort'
    elif algorithm == "merge":
        exe_name = 'merge_sort.exe' if sys.platform == 'win32' else './merge_sort'
    elif algorithm == "quick":
        exe_name = 'quick_sort.exe' if sys.platform == 'win32' else './quick_sort'
    else:
        print(f"Algoritmo '{algorithm}' não reconhecido!")
        return generate_test_data()
    
    try:
        if not os.path.exists(exe_name):
            print(f"ERRO: {exe_name} não encontrado!")
            return generate_test_data()
        
        proc = subprocess.Popen([exe_name], stdout=subprocess.PIPE, text=True)
        steps = []
        
        print(f"Lendo saída do programa {algorithm} sort...")
        for line in proc.stdout:
            try:
                step = list(map(int, line.strip().split()))
                if step:
                    steps.append(step)
                    print(f"Passo lido: {step[:5]}{'...' if len(step) > 5 else ''}")
            except ValueError as e:
                print(f"Erro ao ler linha: {line.strip()} - {e}")
                continue
        
        print(f"Total de passos lidos: {len(steps)}")
        
        if not steps:
            print("Nenhum passo recebido. Gerando dados de teste...")
            return generate_test_data()
            
        return steps
    
    except Exception as e:
        print(f"Erro ao executar {exe_name}: {e}")
        return generate_test_data()

def generate_test_data():
    print("Gerando dados de teste para visualização...")
    import random
    
    test_data = list(range(1, 31))  # Array menor para melhor visualização sonora
    random.shuffle(test_data)
    
    steps = [test_data.copy()]
    
    for i in range(len(test_data)):
        for j in range(len(test_data) - i - 1):
            if test_data[j] > test_data[j + 1]:
                test_data[j], test_data[j + 1] = test_data[j + 1], test_data[j]
                steps.append(test_data.copy())
    
    print(f"Gerados {len(steps)} passos de teste")
    return steps

def detect_quicksort_changes(current_data, previous_data, sound_manager):
    """Detecta mudanças específicas do quicksort e toca sons apropriados"""
    if not previous_data or len(current_data) != len(previous_data):
        return
    
    max_value = max(current_data) if current_data else 1
    changes = []
    
    # Encontrar todas as posições que mudaram
    for i in range(len(current_data)):
        if current_data[i] != previous_data[i]:
            changes.append(i)
    
    # Se há exatamente 2 mudanças, provavelmente é uma troca (swap)
    if len(changes) == 2:
        i, j = changes
        # Verificar se é realmente uma troca
        if (current_data[i] == previous_data[j] and 
            current_data[j] == previous_data[i]):
            sound_manager.play_swap_sound(current_data[i], current_data[j], max_value)
            return
    
    # Se há mudanças mais complexas, pode ser particionamento
    if len(changes) > 2:
        # Tocar som de particionamento baseado na extensão das mudanças
        left_change = min(changes)
        right_change = max(changes)
        sound_manager.play_quicksort_partition_sound(left_change, right_change, len(current_data))
        
        # Identificar possível pivot (elemento que pode ter mudado de posição significativamente)
        for i in changes:
            # Se um elemento se moveu muito, pode ser o pivot sendo posicionado
            old_pos = previous_data.index(current_data[i]) if current_data[i] in previous_data else -1
            if old_pos != -1 and abs(i - old_pos) > 1:
                sound_manager.play_quicksort_pivot_sound(current_data[i], max_value)
                break

def main():
    pygame.init()
    display = (1280, 720)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Visualizador 3D de Algoritmos de Ordenação")
    
    # Inicializar gerenciador de som
    sound_manager = SoundManager()
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.9, 0.9, 0.9, 1.0)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Algoritmo ativo (padrão: bubble)
    active_algorithm = "bubble"
    
    steps = run_visualizer(active_algorithm)
    
    if not steps:
        print("Nenhum dado para visualizar. Saindo.")
        pygame.quit()
        return
    
    camera_angle_x = 0
    camera_angle_y = 20
    camera_distance = 80
    mouse_dragging = False
    last_mouse_pos = None
    menu_bounds = None
    
    clock = pygame.time.Clock()
    current_step = 0
    paused = False
    running = True
    previous_step_data = None
    
    print("Iniciando visualização...")
    print("Controles:")
    print("- Clique nos nomes dos algoritmos para trocar")
    print("- Arraste o mouse para girar a câmera")
    print("- Roda do mouse para zoom in/out")
    print("- Espaço para pausar/continuar")
    print("- Setas para avançar/retroceder passos")
    print("- R para reiniciar")
    print("- M para ligar/desligar som")
    print("- +/- para ajustar volume")
    print("- ESC para sair")
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    paused = not paused
                elif event.key == K_LEFT and current_step > 0:
                    current_step -= 1
                elif event.key == K_RIGHT and current_step < len(steps) - 1:
                    current_step += 1
                elif event.key == K_r:
                    current_step = 0
                elif event.key == K_m:
                    enabled = sound_manager.toggle()
                    print(f"Som {'ligado' if enabled else 'desligado'}")
                elif event.key == K_PLUS or event.key == K_EQUALS:
                    sound_manager.set_volume(sound_manager.volume + 0.1)
                    print(f"Volume: {sound_manager.volume:.1f}")
                elif event.key == K_MINUS:
                    sound_manager.set_volume(sound_manager.volume - 0.1)
                    print(f"Volume: {sound_manager.volume:.1f}")
                elif event.key == K_ESCAPE:
                    running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Clique esquerdo
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Verificar clique nos algoritmos
                    if menu_bounds:
                        if is_point_in_bounds(mouse_pos[0], mouse_pos[1], menu_bounds['bubble']):
                            if active_algorithm != "bubble":
                                print("Trocando para Bubble Sort...")
                                active_algorithm = "bubble"
                                steps = run_visualizer(active_algorithm)
                                current_step = 0
                                previous_step_data = None
                        elif is_point_in_bounds(mouse_pos[0], mouse_pos[1], menu_bounds['merge']):
                            if active_algorithm != "merge":
                                print("Trocando para Merge Sort...")
                                active_algorithm = "merge"
                                steps = run_visualizer(active_algorithm)
                                current_step = 0
                                previous_step_data = None
                        elif is_point_in_bounds(mouse_pos[0], mouse_pos[1], menu_bounds['quick']):
                            if active_algorithm != "quick":
                                print("Trocando para Quick Sort...")
                                active_algorithm = "quick"
                                steps = run_visualizer(active_algorithm)
                                current_step = 0
                                previous_step_data = None
                        else:
                            # Clique fora do menu - iniciar arrastar câmera
                            if mouse_pos[1] > 100:  # Abaixo da barra de menu
                                mouse_dragging = True
                                last_mouse_pos = mouse_pos
                    else:
                        mouse_dragging = True
                        last_mouse_pos = mouse_pos
                elif event.button == 4:
                    camera_distance = max(10, camera_distance - 5)
                elif event.button == 5:
                    camera_distance = min(200, camera_distance + 5)
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_dragging = False
            elif event.type == MOUSEMOTION and mouse_dragging:
                current_mouse_pos = pygame.mouse.get_pos()
                dx = current_mouse_pos[0] - last_mouse_pos[0]
                dy = current_mouse_pos[1] - last_mouse_pos[1]
                
                camera_angle_x -= dx * 0.5
                camera_angle_y += dy * 0.5
                camera_angle_y = max(-85, min(85, camera_angle_y))
                
                last_mouse_pos = current_mouse_pos
        
        # Verificar se ainda temos dados válidos
        if not steps:
            continue
            
        # Detectar mudanças entre passos para tocar sons
        current_data = steps[current_step]
        if previous_step_data and current_data != previous_step_data:
            max_value = max(current_data) if current_data else 1
            
            # Detectar mudanças específicas para cada algoritmo
            if active_algorithm == "bubble":
                # Lógica original para bubble sort
                for i in range(len(current_data)):
                    if current_data[i] != previous_step_data[i]:
                        for j in range(i + 1, len(current_data)):
                            if (current_data[j] != previous_step_data[j] and 
                                current_data[i] == previous_step_data[j] and 
                                current_data[j] == previous_step_data[i]):
                                sound_manager.play_swap_sound(current_data[i], current_data[j], max_value)
                                break
                        break
            elif active_algorithm == "merge":
                # Lógica original para merge sort
                for i in range(len(current_data)):
                    if current_data[i] != previous_step_data[i]:
                        sound_manager.play_merge_sound(current_data[i], i, max_value)
            elif active_algorithm == "quick":
                # Nova lógica específica para quick sort
                detect_quicksort_changes(current_data, previous_step_data, sound_manager)

        # Verificar se chegou ao final - CORREÇÃO AQUI
        if current_step == len(steps) - 1:
            # Verificar se é a primeira vez que chegamos ao final
            if not hasattr(main, 'completion_played'):
                main.completion_played = {}
            
            # Criar uma chave única para este processo de ordenação
            array_key = f"{active_algorithm}_{str(current_data)}"
            
            # Se ainda não tocamos o som de conclusão para este array
            if array_key not in main.completion_played:
                # Verificar se o array está realmente ordenado
                if current_data == sorted(current_data):
                    sound_manager.play_completion_sound()
                    main.completion_played[array_key] = True
                    print(f"Som de conclusão tocado para {active_algorithm}")  # Debug

        menu_bounds = draw_scene(current_data, camera_angle_x, camera_angle_y, camera_distance, display, active_algorithm)

        # IMPORTANTE: Só atualizar previous_step_data depois de todas as verificações
        if previous_step_data != current_data:
            previous_step_data = current_data.copy()

        if not paused and current_step < len(steps) - 1:
            current_step += 1
            # Velocidade ajustada baseada no algoritmo
            if active_algorithm == "quick":
                pygame.time.wait(80)  # Um pouco mais lento para quick sort devido à complexidade sonora
            else:
                pygame.time.wait(60)  # Velocidade padrão

        clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()