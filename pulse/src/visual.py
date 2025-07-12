import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, Patch, Circle
import numpy as np
import requests
import threading
import time
import queue
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D

class HexVisualizer:
    def __init__(self, api_url, token, update_interval=1.0):
        self.api_url = api_url
        self.token = token
        self.update_interval = update_interval
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.fig.canvas.manager.set_window_title('DatsPulse Game Visualizer')
        self.data_queue = queue.Queue()
        
        # Обновленные константы типов гексов по API
        self.terrain_colors = {
            1: "#FF0000",  # Муравейник (красный)
            2: "#F5F5DC",  # Пустой (бежевый)
            3: "#8B4513",  # Грязь (коричневый)
            4: "#7FFF00",  # Кислота (ярко-зеленый)
            5: "#808080"   # Камни (серый)
        }
        
        # Цвета для юнитов
        self.unit_colors = {
            0: "#3498DB",  # рабочий - синий
            1: "#E74C3C",  # солдат - красный
            2: "#9B59B6"   # разведчик - фиолетовый
        }
        
        # Цвета для вражеских юнитов
        self.enemy_colors = {
            0: "#21618C",  # рабочий - темно-синий
            1: "#922B21",  # солдат - темно-красный
            2: "#6C3483"   # разведчик - темно-фиолетовый
        }
        
        # Цвета для ресурсов
        self.resource_colors = {
            0: "#FFD700",  # Нектар - золотой
            1: "#D2691E",  # Хлеб - коричневый
            2: "#FF4500"   # Яблоко - оранжевый
        }
        
        # Названия для легенды
        self.type_names = {
            "terrain": {
                1: "Муравейник",
                2: "Пустой",
                3: "Грязь",
                4: "Кислота",
                5: "Камни"
            },
            "units": {
                0: "Рабочий",
                1: "Солдат",
                2: "Разведчик"
            },
            "resources": {
                0: "Нектар",
                1: "Хлеб",
                2: "Яблоко"
            }
        }
        
        self.running = True
        
        # Создание потоков после объявления всех методов
        self.thread = threading.Thread(target=self.update_loop)
        self.thread.daemon = True
        self.thread.start()
        
        # Настройка анимации
        self.ani = FuncAnimation(
            self.fig, 
            self.update_visualization_from_queue, 
            interval=100,
            blit=False
        )
        
        plt.axis('equal')
        plt.axis('off')
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)  # Место для легенды
        plt.show()

    def update_loop(self):
        """Цикл обновления данных в фоновом потоке"""
        while self.running:
            state = self.fetch_game_state()
            if state:
                self.data_queue.put(state)
            time.sleep(self.update_interval)
    
    def fetch_game_state(self):
        """Получение состояния игры с сервера"""
        try:
            headers = {
                "accept": "application/json",
                "X-Auth-Token": self.token
            }
            response = requests.get(f"{self.api_url}", headers=headers)
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def axial_to_pixel(self, q, r, size=1.0):
        """Преобразование осевых координат (q, r) в пиксельные (x, y)"""
        x = size * (3/2 * q)
        y = size * (np.sqrt(3) * (r + q/2))
        return x, y

    def draw_hex(self, q, r, hex_type, size=1.0):
        """Отрисовка одного гекса"""
        x, y = self.axial_to_pixel(q, r, size)
        color = self.terrain_colors.get(hex_type, "#CCCCCC")
        hex_patch = RegularPolygon(
            (x, y), numVertices=6, radius=size, 
            orientation=np.radians(30), 
            facecolor=color, edgecolor='black', alpha=0.7
        )
        self.ax.add_patch(hex_patch)
        return x, y

    def draw_ant(self, x, y, ant_type, is_enemy=False, size=0.4, health=None, carrying=None):
        """Отрисовка муравья с характеристиками внутри"""
        # Используем разные цвета для своих и вражеских муравьев
        if is_enemy:
            color = self.enemy_colors.get(ant_type, "#000000")
        else:
            color = self.unit_colors.get(ant_type, "#000000")
            
        # Уменьшенный размер муравья
        ant_size = size * 0.4  # Уменьшили размер
        
        # Форма муравья (круг для своих, квадрат для врагов)
        if is_enemy:
            # Для врагов - квадрат
            ant_shape = RegularPolygon(
                (x, y), numVertices=4, radius=ant_size*1.2, 
                orientation=np.radians(45), 
                facecolor=color, edgecolor='black', alpha=1.0, zorder=10
            )
            self.ax.add_patch(ant_shape)
        else:
            # Для своих - круг
            circle = Circle((x, y), radius=ant_size, color=color, zorder=10)
            self.ax.add_patch(circle)
        
        # Отображение здоровья внутри фигуры
        if health is not None:
            plt.text(x, y, f"{health}", 
                     fontsize=7, 
                     ha='center', 
                     va='center',
                     color='white',
                     zorder=12)
        
        # Отображение ресурса, который несет муравей
        if carrying is not None:
            res_color = self.resource_colors.get(carrying, "#FFFFFF")
            # Маленький кружок в верхнем правом углу
            res_x = x + ant_size*0.7
            res_y = y + ant_size*0.7
            res_circle = Circle((res_x, res_y), radius=ant_size*0.3, color=res_color, zorder=12)
            self.ax.add_patch(res_circle)

    def draw_resource(self, x, y, res_type, amount, size=0.4):
        """Отрисовка ресурса в центре гекса"""
        color = self.resource_colors.get(res_type, "#000000")
        # Размер круга зависит от количества ресурса
        circle_size = size * 0.3  # Уменьшили размер
        circle = Circle((x, y), radius=circle_size, color=color, zorder=9)
        self.ax.add_patch(circle)
        
        # Текст с количеством
        plt.text(x, y, str(amount), 
                color='white', 
                fontsize=7, 
                ha='center', 
                va='center',
                zorder=12)

    def draw_anthill(self, home, spot, size=1.0):
        """Отрисовка муравейника"""
        for hex_data in home:
            q, r = hex_data['q'], hex_data['r']
            x, y = self.axial_to_pixel(q, r, size)
            
            # Основной гекс
            if q == spot['q'] and r == spot['r']:
                color = "#8B0000"  # темно-красный
            else:
                color = "#FF6347"  # томатный
                
            hex_patch = RegularPolygon(
                (x, y), numVertices=6, radius=size, 
                orientation=np.radians(30), 
                facecolor=color, edgecolor='black', alpha=0.9
            )
            self.ax.add_patch(hex_patch)
            
            # Обозначение центра
            if q == spot['q'] and r == spot['r']:
                plt.plot(x, y, 'y*', markersize=10, zorder=15)

    def draw_move_path(self, ant, size=1.0):
        """Отрисовка пути перемещения"""
        if 'move' not in ant or not ant['move']:
            return
            
        # Текущая позиция
        start_x, start_y = self.axial_to_pixel(ant['q'], ant['r'], size)
        path = ant['move']
        
        # Отрисовка пути
        for i, point in enumerate(path):
            x, y = self.axial_to_pixel(point['q'], point['r'], size)
            
            # Линия к следующей точке
            if i == 0:
                plt.plot([start_x, x], [start_y, y], 'b--', linewidth=1.0, zorder=5)
            elif i < len(path) - 1:
                next_x, next_y = self.axial_to_pixel(
                    path[i+1]['q'], path[i+1]['r'], size
                )
                plt.plot([x, next_x], [y, next_y], 'b--', linewidth=1.0, zorder=5)
            
            # Точка пути
            plt.plot(x, y, 'bo', markersize=3, zorder=6)

    def update_visualization(self, state):
        """Обновление визуализации на основе состояния игры"""
        if not state:
            return
            
        self.ax.clear()
        
        # Отрисовка всех гексов
        hex_size = 0.9
        for hex_data in state.get('map', []):
            self.draw_hex(hex_data['q'], hex_data['r'], 
                         hex_data.get('type', 2),  # По умолчанию пустой гекс
                         hex_size)
        
        # Отрисовка муравейника
        if 'home' in state and 'spot' in state:
            self.draw_anthill(state['home'], state['spot'], hex_size)
        
        # Отрисовка ресурсов В ЦЕНТРЕ ГЕКСОВ
        for food in state.get('food', []):
            x, y = self.axial_to_pixel(food['q'], food['r'], hex_size)
            self.draw_resource(x, y, food.get('type', 0), 
                              food.get('amount', 1), 
                              hex_size)
        
        # Группировка муравьев по гексам
        ants_by_hex = {}
        for ant in state.get('ants', []):
            key = (ant['q'], ant['r'])
            if key not in ants_by_hex:
                ants_by_hex[key] = []
            ants_by_hex[key].append(ant)
        
        # Отрисовка своих муравьев со смещением
        for hex_key, ants in ants_by_hex.items():
            q, r = hex_key
            base_x, base_y = self.axial_to_pixel(q, r, hex_size)
            
            # Смещения для разных типов муравьев в одном гексе
            offsets = {
                0: (-0.3, -0.3),  # Рабочий - влево вниз
                1: (0.3, -0.3),   # Солдат - вправо вниз
                2: (0, 0.3)       # Разведчик - вверх
            }
            
            for ant in ants:
                offset = offsets.get(ant.get('type', 0), (0, 0))
                x = base_x + offset[0] * hex_size
                y = base_y + offset[1] * hex_size
                
                # Получаем здоровье и несомый ресурс
                health = ant.get('health')
                carrying = ant.get('carrying')
                
                self.draw_ant(x, y, ant.get('type', 0), False, hex_size, health, carrying)
                
                # Отрисовка пути перемещения
                self.draw_move_path(ant, hex_size)
        
        # Группировка вражеских муравьев по гексам
        enemies_by_hex = {}
        for enemy in state.get('enemies', []):
            key = (enemy['q'], enemy['r'])
            if key not in enemies_by_hex:
                enemies_by_hex[key] = []
            enemies_by_hex[key].append(enemy)
        
        # Отрисовка вражеских муравьев со смещением
        for hex_key, enemies in enemies_by_hex.items():
            q, r = hex_key
            base_x, base_y = self.axial_to_pixel(q, r, hex_size)
            
            # Смещения для вражеских муравьев
            offsets = {
                0: (-0.3, -0.3),  # Рабочий - влево вниз
                1: (0.3, -0.3),   # Солдат - вправо вниз
                2: (0, 0.3)       # Разведчик - вверх
            }
            
            for enemy in enemies:
                offset = offsets.get(enemy.get('type', 1), (0, 0))
                x = base_x + offset[0] * hex_size
                y = base_y + offset[1] * hex_size
                
                health = enemy.get('health')
                attack = enemy.get('attack')
                carrying = enemy.get('carrying')
                
                self.draw_ant(x, y, enemy.get('type', 1), True, hex_size, health, carrying)
                
                # Отображение атаки для врагов
                if attack is not None:
                    plt.text(x, y+0.5, f"ATK: {attack}", 
                             fontsize=7, ha='center', color='darkred')
        
        # Информация о ходе
        turn_info = (f"Ход: {state.get('turnNo', 0)} | "
                     f"Следующий ход через: {state.get('nextTurnIn', 0):.1f} сек | "
                     f"Счет: {state.get('score', 0)}")
        plt.title(turn_info, fontsize=14, pad=20)
        
        # СОЗДАЕМ КРАСИВУЮ ЛЕГЕНДУ С ЦВЕТНЫМИ ЭЛЕМЕНТАМИ
        legend_elements = []
        
        # Территория
        for type_id, color in self.terrain_colors.items():
            name = self.type_names['terrain'].get(type_id, f"Гекс {type_id}")
            legend_elements.append(Patch(facecolor=color, edgecolor='black', label=name))
        
        # Свои юниты
        for type_id, color in self.unit_colors.items():
            name = self.type_names['units'].get(type_id, f"Свой {self.type_names['units'].get(type_id, 'Юнит')}")
            legend_elements.append(Line2D([0], [0], 
                                        marker='o', 
                                        color='w', 
                                        markerfacecolor=color,
                                        markeredgecolor='black',
                                        markersize=10,
                                        label=name))
        
        # Вражеские юниты
        for type_id, color in self.enemy_colors.items():
            name = self.type_names['units'].get(type_id, f"Враг {self.type_names['units'].get(type_id, 'Юнит')}")
            legend_elements.append(Line2D([0], [0], 
                                        marker='s', 
                                        color='w', 
                                        markerfacecolor=color,
                                        markeredgecolor='black',
                                        markersize=10,
                                        label=name))
        
        # Ресурсы
        for type_id, color in self.resource_colors.items():
            name = self.type_names['resources'].get(type_id, f"Ресурс {type_id}")
            legend_elements.append(Line2D([0], [0], 
                                        marker='o', 
                                        color='w', 
                                        markerfacecolor=color,
                                        markeredgecolor='black',
                                        markersize=10,
                                        label=name))
        
        # Добавляем легенду
        self.ax.legend(handles=legend_elements, 
                      loc='upper center', 
                      bbox_to_anchor=(0.5, -0.05),
                      ncol=4,  # 4 колонки для всех элементов
                      fontsize=8,
                      framealpha=0.7,
                      title="Легенда",
                      title_fontsize=9)
        
        self.fig.canvas.draw()

    def update_visualization_from_queue(self, frame):
        """Обновление визуализации из главного потока"""
        try:
            state = self.data_queue.get_nowait()
            self.update_visualization(state)
        except queue.Empty:
            pass
    
    def stop(self):
        """Остановка визуализатора"""
        self.running = False
        plt.close('all')

# Пример использования
if __name__ == "__main__":
    API_URL = "https://games-test.datsteam.dev/api/arena"
    TOKEN = "63bf8b86-1505-4f25-b160-27342aa20c58"
    
    visualizer = HexVisualizer(api_url=API_URL, token=TOKEN)