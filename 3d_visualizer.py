import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import subprocess
import time
import os
import sys
import math

def draw_bar(x, height):
    w = 0.5  # largura
    d = 0.5  # profundidade
    h = height
    
    # Gradiente de roxo (0.5, 0.0, 0.5) → laranja (1.0, 0.5, 0.0)
    max_height = 40.0
    factor = min(1.0, height / max_height)

    r = 0.5 + 0.5 * factor  # vermelho: 0.5 → 1.0
    g = 0.0 + 0.5 * factor  # verde:    0.0 → 0.5
    b = 0.5 - 0.5 * factor  # azul:     0.5 → 0.0

    glColor3f(r, g, b)
    
    vertices = [
        [x - w, 0, -d],  # 0 frente-esquerda-baixo
        [x + w, 0, -d],  # 1 frente-direita-baixo
        [x + w, h, -d],  # 2 frente-direita-cima
        [x - w, h, -d],  # 3 frente-esquerda-cima
        [x - w, 0, d],   # 4 trás-esquerda-baixo
        [x + w, 0, d],   # 5 trás-direita-baixo
        [x + w, h, d],   # 6 trás-direita-cima
        [x - w, h, d]    # 7 trás-esquerda-cima
    ]
    
    faces = [
        [0, 1, 2, 3],  # frente
        [4, 5, 6, 7],  # trás
        [0, 4, 7, 3],  # esquerda
        [1, 5, 6, 2],  # direita
        [3, 2, 6, 7],  # cima
        [0, 1, 5, 4]   # baixo
    ]
    
    glBegin(GL_QUADS)
    for face in faces:
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()

def setup_lighting():
    # Configurando luz ambiente
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Posição da luz
    glLightfv(GL_LIGHT0, GL_POSITION, [10, 50, 100, 1])
    
    # Intensidade e cor da luz
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.7, 0.7, 0.7, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
    
    # Configuração do material
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

def draw_scene(values, camera_angle_x, camera_angle_y, camera_distance):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Calcular a posição da câmera usando ângulos e distância
    camera_x = camera_distance * math.sin(math.radians(camera_angle_x)) * math.cos(math.radians(camera_angle_y))
    camera_y = camera_distance * math.sin(math.radians(camera_angle_y))
    camera_z = camera_distance * math.cos(math.radians(camera_angle_x)) * math.cos(math.radians(camera_angle_y))
    
    array_center = 0  # O centro do array está na origem
    
    gluLookAt(camera_x, camera_y, camera_z,  # posição da câmera calculada
              array_center, 10, 0,           # ponto para onde a câmera olha - centro do array
              0, 1, 0)                       # vetor "para cima"
    
    # Ativando iluminação
    setup_lighting()
    
    # Desenhando barras
    spacing = 1.5  # Aumentando o espaço entre as barras para melhor visualização
    max_height = max(values) if values else 1
    offset = -len(values) * spacing / 2  # centralizar as barras
    
    for i, v in enumerate(values):
        height = (v / max_height) * 30  # Reduzindo um pouco a altura para caber melhor na tela
        draw_bar(offset + i * spacing, height)
    
    pygame.display.flip()

def run_visualizer():
    print("Tentando executar bubble_sort.exe...")
    
    # Verificar se estamos no Windows ou outro sistema
    exe_name = 'bubble_sort.exe' if sys.platform == 'win32' else './bubble_sort'
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(exe_name):
            print(f"ERRO: {exe_name} não encontrado!")
            # Gerar dados de teste
            return generate_test_data()
        
        # Executar o programa C
        proc = subprocess.Popen([exe_name], stdout=subprocess.PIPE, text=True)
        steps = []
        
        print("Lendo saída do programa C...")
        for line in proc.stdout:
            try:
                step = list(map(int, line.strip().split()))
                if step:  # Se não estiver vazio
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
    # Dados de teste para quando o programa C falha
    print("Gerando dados de teste para visualização...")
    import random
    
    # Criar array desordenado
    test_data = list(range(1, 51))
    random.shuffle(test_data)
    
    # Implementar bubble sort e gerar passos
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
    pygame.display.set_caption("Visualizador 3D de Bubble Sort")
    
    # Configuração do OpenGL
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.9, 0.9, 0.9, 1.0)  # Azul escuro quase preto
    
    # Configuração da perspectiva
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Obter os passos do algoritmo
    steps = run_visualizer()
    
    if not steps:
        print("Nenhum dado para visualizar. Saindo.")
        pygame.quit()
        return
    
    # Variáveis para controle da câmera
    camera_angle_x = 0  # ângulo horizontal (em graus)
    camera_angle_y = 20  # ângulo vertical (em graus)
    camera_distance = 80  # distância da câmera ao centro da cena
    mouse_dragging = False
    last_mouse_pos = None
    
    clock = pygame.time.Clock()
    current_step = 0
    paused = False
    running = True
    
    print("Iniciando visualização...")
    print("Controles:")
    print("- Arraste o mouse para girar a câmera")
    print("- Roda do mouse para zoom in/out")
    print("- Espaço para pausar/continuar")
    print("- Setas para avançar/retroceder passos")
    print("- R para reiniciar")
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
                elif event.key == K_r:  # Reiniciar
                    current_step = 0
                elif event.key == K_ESCAPE:
                    running = False
            # Novos eventos para controle da câmera com o mouse
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo do mouse
                    mouse_dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 4:  # Roda do mouse para cima (zoom in)
                    camera_distance = max(10, camera_distance - 5)
                elif event.button == 5:  # Roda do mouse para baixo (zoom out)
                    camera_distance = min(200, camera_distance + 5)
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:  # Botão esquerdo do mouse
                    mouse_dragging = False
            elif event.type == MOUSEMOTION and mouse_dragging:
                # Calcula o movimento do mouse
                current_mouse_pos = pygame.mouse.get_pos()
                dx = current_mouse_pos[0] - last_mouse_pos[0]
                dy = current_mouse_pos[1] - last_mouse_pos[1]
                
                # Atualiza os ângulos da câmera
                camera_angle_x -= dx * 0.5  # Sensibilidade horizontal
                camera_angle_y += dy * 0.5  # Sensibilidade vertical
                
                # Limita o ângulo vertical para evitar inversões estranhas
                camera_angle_y = max(-85, min(85, camera_angle_y))
                
                last_mouse_pos = current_mouse_pos
        
        draw_scene(steps[current_step], camera_angle_x, camera_angle_y, camera_distance)
        
        if not paused and current_step < len(steps) - 1:
            current_step += 1
            pygame.time.wait(10)  # Ajustar velocidade da animação
        
        clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()