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

def draw_scene(values, camera_angle_x, camera_angle_y, camera_distance):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
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
    
    pygame.display.flip()

def run_visualizer():
    print("Tentando executar bubble_sort.exe...")
    
    exe_name = 'bubble_sort.exe' if sys.platform == 'win32' else './bubble_sort'
    
    try:
        if not os.path.exists(exe_name):
            print(f"ERRO: {exe_name} não encontrado!")
            return generate_test_data()
        
        proc = subprocess.Popen([exe_name], stdout=subprocess.PIPE, text=True)
        steps = []
        
        print("Lendo saída do programa C...")
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

def main():
    pygame.init()
    display = (1280, 720)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Visualizador 3D de Bubble Sort com Som")
    
    # Inicializar gerenciador de som
    sound_manager = SoundManager()
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.9, 0.9, 0.9, 1.0)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)
    
    steps = run_visualizer()
    
    if not steps:
        print("Nenhum dado para visualizar. Saindo.")
        pygame.quit()
        return
    
    camera_angle_x = 0
    camera_angle_y = 20
    camera_distance = 80
    mouse_dragging = False
    last_mouse_pos = None
    
    clock = pygame.time.Clock()
    current_step = 0
    paused = False
    running = True
    previous_step_data = None
    
    print("Iniciando visualização...")
    print("Controles:")
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
                if event.button == 1:
                    mouse_dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()
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
        
        # Detectar mudanças entre passos para tocar sons
        current_data = steps[current_step]
        if previous_step_data and current_data != previous_step_data:
            max_value = max(current_data) if current_data else 1
            
            # Encontrar diferenças entre os arrays
            for i in range(len(current_data)):
                if current_data[i] != previous_step_data[i]:
                    # Encontrar o par que foi trocado
                    for j in range(i + 1, len(current_data)):
                        if (current_data[j] != previous_step_data[j] and 
                            current_data[i] == previous_step_data[j] and 
                            current_data[j] == previous_step_data[i]):
                            # Toca som de troca
                            sound_manager.play_swap_sound(current_data[i], current_data[j], max_value)
                            break
                    break
        
        # Verificar se chegou ao final
        if current_step == len(steps) - 1 and previous_step_data != current_data:
            # Array está ordenado, tocar som de conclusão
            if current_data == sorted(current_data):
                sound_manager.play_completion_sound()
        
        draw_scene(current_data, camera_angle_x, camera_angle_y, camera_distance)
        previous_step_data = current_data.copy()
        
        if not paused and current_step < len(steps) - 1:
            current_step += 1
            pygame.time.wait(50)  # Velocidade ajustada para melhor sincronização com som
        
        clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()