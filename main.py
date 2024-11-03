class Entity:
    def __init__(self, entity_type):
        self.entity_type = entity_type  

    def __str__(self):
        return self.entity_type


class Spot:
    def __init__(self, spot_type, entity=None):
        self.spot_type = spot_type  
        self.entity = entity  

    def is_vacant(self):
        return self.spot_type == 'E' and self.entity is None

    def is_target(self):
        return self.spot_type in {'G', 'GI'}

    def __str__(self):
        if self.spot_type == 'GI':
            return 'GI' if self.entity else 'G'
        if self.entity:
            return str(self.entity)
        return self.spot_type


class Matrix:
    def __init__(self, structure, actions):
        self.matrix = []
        for line in structure:
            matrix_line = []
            for spot_type in line:
                entity = None
                if spot_type == 'I':
                    entity = Entity('I')
                elif spot_type == 'P':
                    entity = Entity('P')
                elif spot_type == 'R':
                    entity = Entity('R')
                elif spot_type == 'GI':
                    entity = Entity('I')  # Goal with iron initially
                matrix_line.append(Spot(spot_type, entity))
            self.matrix.append(matrix_line)
        self.remaining_actions = actions

    def display_matrix(self):
        print("\nMatrix:")
        for line in self.matrix:
            line_str = ' | '.join(str(spot) for spot in line)
            print(line_str)
            print('-' * len(line_str))

    def target_achieved(self):
        for line in self.matrix:
            for spot in line:
                if spot.spot_type == 'G' and (spot.entity is None or spot.entity.entity_type not in {'I', 'R', 'P'}):
                    return False
                if spot.spot_type == 'GI' and (spot.entity is None or spot.entity.entity_type != 'I'):
                    return False
        return True

    def relocate_entity(self, row, col, new_row, new_col):
        if not (0 <= row < len(self.matrix) and 0 <= col < len(self.matrix[0])):
            print("Invalid relocation: Out of boundaries.")
            return False
        if not (0 <= new_row < len(self.matrix) and 0 <= new_col < len(self.matrix[0])):
            print("Invalid relocation: Destination out of boundaries.")
            return False

        spot = self.matrix[row][col]
        new_spot = self.matrix[new_row][new_col]

        if spot.entity and (new_spot.is_vacant() or new_spot.spot_type in ['G', 'GI']):
            new_spot.entity = spot.entity  
            spot.entity = None  
            if spot.spot_type not in ['G', 'GI']:
                spot.spot_type = 'E'  
            self.remaining_actions -= 1

            self.trigger_iron_motion(new_row, new_col)
            return True
        else:
            print("Invalid relocation: Destination is occupied or blocked.")
            return False

    def trigger_iron_motion(self, row, col):
        irons_to_move = []

        for i, line in enumerate(self.matrix):
            for j, spot in enumerate(line):
                if spot.entity and spot.entity.entity_type == 'I':
                    nearest_red = None
                    shortest_distance = float('inf')
                    
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            if dx == 0 and dy == 0:
                                continue
                            neighbor_row, neighbor_col = i + dx, j + dy
                            if 0 <= neighbor_row < len(self.matrix) and 0 <= neighbor_col < len(self.matrix[0]):
                                neighbor_spot = self.matrix[neighbor_row][neighbor_col]
                                if neighbor_spot.entity and neighbor_spot.entity.entity_type == 'R':
                                    distance = abs(i - neighbor_row) + abs(j - neighbor_col)
                                    if distance < shortest_distance:
                                        shortest_distance = distance
                                        nearest_red = (neighbor_row, neighbor_col)
                    
                    if nearest_red:
                        target_row, target_col = nearest_red
                        dx = target_row - i
                        dy = target_col - j
                        if abs(dx) > abs(dy):  
                            new_x, new_y = i + (1 if dx > 0 else -1), j
                        else:  
                            new_x, new_y = i, j + (1 if dy > 0 else -1)
                        
                        if 0 <= new_x < len(self.matrix) and 0 <= new_y < len(self.matrix[0]):
                            target_spot = self.matrix[new_x][new_y]
                            if target_spot.is_vacant() or target_spot.is_target():
                                target_spot.entity = spot.entity
                                spot.entity = None
                                if spot.spot_type == 'GI':
                                    spot.spot_type = 'G'


class Simulation:
    def __init__(self):
        self.levels = self.setup_levels()
        self.current_stage = None

    def setup_levels(self):
        levels = []

        structure1 = [
            ['E', 'E', 'B', 'E'],
            ['E', 'G', 'I', 'G'],
            ['P', 'E', 'E', 'E']
        ]
        levels.append(Matrix(structure1, actions=5))

        structure2 = [
            ['E', 'B', 'G', 'E', 'E'],
            ['E', 'E', 'I', 'B', 'E'],
            ['G', 'I', 'G', 'I', 'G'],
            ['E', 'E', 'I', 'E', 'E'],
            ['P', 'E', 'G', 'B', 'E']
        ]
        levels.append(Matrix(structure2, actions=5))

        structure3 = [
            ['B', 'B', 'B', 'G'], 
            ['E', 'E', 'I', 'E'],
            ['P', 'E', 'E', 'G']
        ]
        levels.append(Matrix(structure3, actions=5))

        structure4 = [
            ['GI', 'E', 'G'],  
            ['B', 'I', 'E'],
            ['P', 'E', 'E'],
            ['B', 'I', 'E'],
            ['E', 'G', 'E'],  
        ]
        levels.append(Matrix(structure4, actions=5))

        structure5 = [
            ['G', 'B', 'G'],  
            ['GI', 'B', 'GI'],
            ['I', 'B', 'I'],
            ['G', 'P', 'E']
        ]
        levels.append(Matrix(structure5, actions=5))
        
        structure6 = [
            ['I', 'G', 'G', 'G', 'I'],  
            ['B', 'B', 'R', 'B', 'B'],
        ]
        levels.append(Matrix(structure6, actions=5))

        return levels

    def begin(self):
        while True:
            print("\nOptions:")
            print("1. Levels")
            print("2. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                self.choose_level()
            elif choice == "2":
                print("Exiting...")
                break
            else:
                print("Invalid choice.")

    def choose_level(self):
        print("\nChoose a level (1-6):")
        level = int(input())
        if 1 <= level <= len(self.levels):
            self.current_stage = self.levels[level - 1]
            self.run_level()
        else:
            print("Invalid level.")

    def run_level(self):
        while self.current_stage.remaining_actions > 0:
            self.current_stage.display_matrix()
            if self.current_stage.target_achieved():
                print("Stage Complete!")
                break

            print(f"Actions remaining: {self.current_stage.remaining_actions}")
            try:
                row, col = map(int, input("Select coordinates to relocate (row col): ").split())
                dest_row, dest_col = map(int, input("Specify target coordinates (row col): ").split())
                if not self.current_stage.relocate_entity(row, col, dest_row, dest_col):
                    print("Relocation failed.")
            except ValueError:
                print("Invalid input.")

        if not self.current_stage.target_achieved():
            print("Stage Failed. Out of actions.")


# Initiate the simulation
sim = Simulation()
sim.begin()
