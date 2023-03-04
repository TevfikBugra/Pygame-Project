import pygame
pygame.init()
import random

class GObject(pygame.sprite.Sprite):
    def __init__(self, image, coordinates) -> None:
        super().__init__()
        self.x_coordinate = coordinates[0]
        self.y_coordinate = coordinates[1]
        self.surface = pygame.image.load(image).convert_alpha()
        self.rect = self.surface.get_rect(center=coordinates)

    def display(self, screen):
        screen.blit(self.surface, self.rect)

class Skill(GObject):
    def __init__(self, planet_owned_by, coordinates) -> None:
        super().__init__('./Images/Uptime-Downtime/skill ready image.png', coordinates)
        self.cooldown = 30
        self.up_time = 7.5
        self.planet_owned_by = planet_owned_by
        self.last_given_time = None
        self.downtime_image = './Images/Uptime-Downtime/skill down image.png'
        self.surface = pygame.transform.scale(self.surface, (75, 75))

    def is_up(self):
        if self.last_given_time != None:
            is_up = pygame.time.get_ticks() / 1000 - self.last_given_time >= self.cooldown
        else:
            is_up = True
        return is_up
        
    def give_immunity(self, spaceships):
        if self.is_up():
            for spaceship in spaceships:
                spaceship.be_immune(self.up_time)
            self.last_given_time = pygame.time.get_ticks() / 1000

    def change_image(self, image):
        self.surface = pygame.image.load(image).convert()
        self.surface = pygame.transform.scale(self.surface, (75, 75))

    def display(self, screen):
        self.rect = self.surface.get_rect(center=(self.x_coordinate, self.y_coordinate))
        if not self.is_up():
            self.change_image(self.downtime_image)
        else:
            self.change_image('./Images/Uptime-Downtime/skill ready image.png')
        super().display(screen)

class Spaceship(GObject):
    def __init__(self, planet_owned_by, damage, fire_range, fire_rate, health, gold_bounty, cost, image, speed, coordinates) -> None:
        super().__init__(image, coordinates)
        self.planet_owned_by = planet_owned_by
        self.damage = damage
        self.fire_range = fire_range
        self.fire_rate = fire_rate
        self.health = health
        self.gold_bounty = gold_bounty
        self.cost = cost
        self.projectiles = []
        self.speed = speed
        self.is_immune = False
        self.immunity_end_time = None
        self.is_attacking = False
        self.last_fire_time = 0
        self.ahead_ally_distace = 10000
        if type(self.planet_owned_by) == EnemyPlanet:
            self.speed = - self.speed
        self.immune_surface = None

    def take_damage(self, damage):  #NEW FUNCTION 
        if not self.is_immune:
            self.health -= damage

    def be_immune(self, up_time):
        current_time = pygame.time.get_ticks() / 1000
        self.is_immune =  True
        self.immunity_end_time = current_time + up_time
        self.rect = self.immune_surface.get_rect(center=(self.x_coordinate, self.y_coordinate))

    def is_immunity_ended(self):
        current_time = pygame.time.get_ticks() / 1000
        if self.immunity_end_time != None:
            if self.immunity_end_time < current_time:
                self.is_immune = False
                self.immunity_end_time = None
                self.rect = self.surface.get_rect(center=(self.x_coordinate, self.y_coordinate))
    
    def fire_projectile(self, enemy):
        distance = enemy.get_distance(self.x_coordinate)
        if (distance <= self.fire_range):
            self.is_attacking = True
            if (pygame.time.get_ticks() / 1000 - self.last_fire_time > self.fire_rate):
                new_projectile = Projectile(self.damage, None, self, (self.x_coordinate, self.y_coordinate))
                self.planet_owned_by.give_target(new_projectile)
                self.projectiles.append(new_projectile)
                self.last_fire_time = pygame.time.get_ticks() / 1000
        else:
            self.is_attacking = False
    
    def update_is_attacking(self):
        self.is_attacking = False

    def special_ability(self):
        pass

    def move(self):
        if (not self.is_attacking) and (self.ahead_ally_distace > 80):
            self.x_coordinate += self.speed
            self.rect = self.surface.get_rect(center=(self.x_coordinate, self.y_coordinate))

    def is_dead(self):
        if self.health <= 0:
            return True
        else:
            return False

    def delete_projectiles(self):
        for projectile in self.projectiles:
            projectile_explosion = projectile.check_explosion()
            if projectile_explosion:
                self.projectiles.remove(projectile)


    def get_distance(self, coordinate):
        return abs(coordinate - self.x_coordinate)
    
    def update_ahead_ally_distance(self, ahead_ally):
        self.ahead_ally_distace = ahead_ally.get_distance(self.x_coordinate)
    
    def update_ahead_ally(self):
        self.ahead_ally_distace = 10000

    def check_got_hit(self, enemy_projectile, damage):
        if enemy_projectile.did_hit(self.rect):
            self.take_damage(damage)
            return True

    def give_bounty(self, opposite_planet):
        opposite_planet.gain_gold(self.gold_bounty)

    def special_ability(self):
        pass

    def display(self, screen):
        if self.is_immune:
            self.rect = self.surface.get_rect(center=(self.x_coordinate, self.y_coordinate))
            screen.blit(self.immune_surface, self.rect)
        else:
            super().display(screen)
        
    def self_turn(self, screen):
        self.delete_projectiles()
        for projectile in self.projectiles:
            projectile.self_turn(screen)
        self.move()
        self.is_immunity_ended()
        self.special_ability()
        self.display(screen)
    
    def delete_items(self):
        for projectile in self.projectiles:  #buğra
            del projectile

    def update_starting_coordinates(self, coordinates):
        self.x_coordinate = coordinates[0]
        self.y_coordinate = coordinates[1]
    
    def did_kamikaze(self, opposite_planet):
        kamikaze_succesfull = opposite_planet.got_kamikazed(self.rect, self.health)
        if kamikaze_succesfull:
            self.health = 0
        return kamikaze_succesfull



class SpaceshipTypeDamageFar(Spaceship):
    def __init__(self, planet_owned_by, damage=6, fire_range=200, fire_rate=3, health=24, gold_bounty=17, cost=15, speed=0.6, coordinates=(-100, -100)) -> None:
        super().__init__(planet_owned_by, damage, fire_range, fire_rate, health, gold_bounty, cost, './debugging_images/range_spaceship.jpeg', speed, coordinates)
        self.initial_damage = damage

        if type(planet_owned_by) == PlayerPlanet:
            self.surface = pygame.image.load('./Images/Spaceship Pictures/PlayerFar.png').convert_alpha()
            self.immune_surface = pygame.image.load('./Images/Spaceship Pictures/PlayerFar_Immune.png').convert_alpha()
            self.surface = pygame.transform.scale(self.surface, (65, 65))
            self.rect = self.surface.get_rect(center=coordinates)
        else:
            self.surface = pygame.image.load('./Images/Spaceship Pictures/EnemyFar.png').convert_alpha()
            self.immune_surface = pygame.image.load('./Images/Spaceship Pictures/EnemyFar_Immune.png').convert_alpha()
            self.surface = pygame.transform.scale(self.surface, (65, 65))
            self.rect = self.surface.get_rect(center=coordinates)

        self.immune_surface = pygame.transform.scale(self.immune_surface, (65, 65))

    def fire_projectile(self, enemy):
        distance = enemy.get_distance(self.x_coordinate)
        if (distance <= self.fire_range):
            if (pygame.time.get_ticks() / 1000 - self.last_fire_time > self.fire_rate):
                self.special_ability(distance)
                self.is_attacking = True
                new_projectile = Projectile(self.damage, None, self, (self.x_coordinate, self.y_coordinate))
                self.planet_owned_by.give_target(new_projectile)
                self.projectiles.append(new_projectile)
                self.last_fire_time = pygame.time.get_ticks() / 1000
        else:
            self.is_attacking = False
    
    def special_ability(self, distance):
        if distance > 120:
            self.damage += 2
        else:
            self.damage = self.initial_damage

    def self_turn(self, screen):
        self.delete_projectiles()
        for projectile in self.projectiles:
            projectile.self_turn(screen)
        self.move()
        self.is_immunity_ended()
        super().display(screen)

        
class SpaceshipTypeTank(Spaceship):
    def __init__(self, planet_owned_by, damage=11, fire_range=90, fire_rate=3, health=55, gold_bounty=23, cost=20, speed=0.6, coordinates=(-100, -100)) -> None:
        super().__init__(planet_owned_by, damage, fire_range, fire_rate, health, gold_bounty, cost, './debugging_images/tank_spaceship.jpeg', speed, coordinates)
        self.health_pool = health
        self.ability_used = False

        if type(planet_owned_by) == PlayerPlanet:
            self.surface = pygame.image.load('./Images/Spaceship Pictures/PlayerTank.png').convert_alpha()
            self.immune_surface = pygame.image.load('./Images/Spaceship Pictures/PlayerTank_Immune.png').convert_alpha()
            self.surface = pygame.transform.scale(self.surface, (65, 65))
            self.rect = self.surface.get_rect(center=coordinates)
        else:
            self.surface = pygame.image.load('./Images/Spaceship Pictures/EnemyTank.png').convert_alpha()
            self.immune_surface = pygame.image.load('./Images/Spaceship Pictures/EnemyTank_Immune.png').convert_alpha()
            self.surface = pygame.transform.scale(self.surface, (65, 65))
            self.rect = self.surface.get_rect(center=coordinates)

        self.immune_surface = pygame.transform.scale(self.immune_surface, (65, 65))
    
    def special_ability(self):
        if (self.health < self.health_pool / 2) and (not self.ability_used):
            self.health += self.health_pool / 5
            self.ability_used = True
        
class SpaceshipTypeDamageClose(Spaceship):
    def __init__(self, planet_owned_by, damage=5, fire_range=90, fire_rate=2, health=20, gold_bounty=12, cost=10, speed=0.9, coordinates=(-100, -100)) -> None:
        super().__init__(planet_owned_by, damage, fire_range, fire_rate, health, gold_bounty, cost, './debugging_images/damage_spaceship.jpeg', speed, coordinates)
        self.ability_used = False
        
        if type(planet_owned_by) == PlayerPlanet:
            self.surface = pygame.image.load('./Images/Spaceship Pictures/PlayerClose.png').convert_alpha()
            self.immune_surface = pygame.image.load('./Images/Spaceship Pictures/PlayerClose_Immune.png').convert_alpha()
            self.surface = pygame.transform.scale(self.surface, (65, 65))
            self.rect = self.surface.get_rect(center=coordinates)
        else:
            self.surface = pygame.image.load('./Images/Spaceship Pictures/EnemyClose.png').convert_alpha()
            self.immune_surface = pygame.image.load('./Images/Spaceship Pictures/EnemyClose_Immune.png').convert_alpha()
            self.surface = pygame.transform.scale(self.surface, (65, 65))
            self.rect = self.surface.get_rect(center=coordinates)
        
        self.immune_surface = pygame.transform.scale(self.immune_surface, (65, 65))

    def special_ability(self):
        if (self.x_coordinate > 800) and (type(self.planet_owned_by) == PlayerPlanet) and (not self.ability_used):
            self.damage += 2
            self.fire_rate -= 0.25
            self.ability_used = True
        elif (self.x_coordinate < 300) and (type(self.planet_owned_by) == EnemyPlanet) and (not self.ability_used):
            self.damage += 2
            self.fire_rate -= 0.25
            self.ability_used = True

class Projectile(GObject):
    def __init__(self, damage, opposite_planet, spaceship, coordinates) -> None:
        super().__init__('./debugging_images/projectile.jpeg', coordinates)
        self.damage = damage
        self.speed = 0.9
        self.opposite_planet = opposite_planet
        self.spaceship = spaceship
        self.is_exploded = False

    def move(self):
        self.x_coordinate += self.speed
        self.rect = self.surface.get_rect(center=(self.x_coordinate, self.y_coordinate))

    def check_explosion(self):
        self.is_exploded = self.opposite_planet.got_hit(self, self.damage)
        return self.is_exploded

    def give_damage(self, enemy):
        enemy.take_damage(self.damage)

    def did_hit(self, enemy_rectangle):
        if self.rect.colliderect(enemy_rectangle):
            return True

    def get_the_opposite_planet(self, opposite_planet):
        self.opposite_planet = opposite_planet
        if type(self.opposite_planet) == PlayerPlanet:
            self.speed = -0.9

    def self_turn(self, screen):
        self.move()
        return super().display(screen)

class Planet(GObject):
    def __init__(self, lanes, image, coordinates) -> None:
        super().__init__(image, coordinates)
        self.health = 200
        self.skill = Skill(self, (850, 57))
        self.lanes = lanes
        self.spaceships = []
        self.gold = 250
        self.selected_lane = 0
        self.opposite_planet = None
        self.spaceship_types_and_costs = {'tank':20, 'damage':10, 'ranged':15}
        self.last_spawn_time = 0

    def is_alive(self):
        if self.health <= 0:
            return False
        else:
            return True

    def take_damage(self, damage): # NEW FUNCTION
        self.health -= damage
    
    def use_skill(self):
        self.skill.give_immunity(self.spaceships)

    def select_lane(self):
        pass

    def give_target(self, projectile):
        projectile.get_the_opposite_planet(self.opposite_planet)

    def spawn_spaceships(self):
        pass

    def spaceship_kamikaze(self):
        for spaceship in self.spaceships:
            spaceship_kamikaze = spaceship.did_kamikaze(self.opposite_planet)
            if spaceship_kamikaze:
                spaceship.give_bounty(self.opposite_planet)
                self.spaceships.remove(spaceship)
    
    def got_kamikazed(self, spaceship_rect, kamikaze_damage):
        did_hit = self.rect.colliderect(spaceship_rect)
        if did_hit:
            self.take_damage(kamikaze_damage)
            return True
        else:
            return False

    def delete_spaceship(self):
        for spaceship in self.spaceships:
            spaceship_death = spaceship.is_dead()
            if spaceship_death:
                spaceship.give_bounty(self.opposite_planet)
                spaceship_index = self.spaceships.index(spaceship)
                del self.spaceships[spaceship_index]

    def got_hit(self, enemy_projectile, damage):
        if enemy_projectile.did_hit(self.rect):
            self.take_damage(damage)
            return True
        else:
            for spaceship in self.spaceships:
                did_hit_spaceship = spaceship.check_got_hit(enemy_projectile, damage)
                if did_hit_spaceship:
                    return did_hit_spaceship
        return False

    def gain_gold(self, gold_bounty):
        self.gold += gold_bounty

    def self_turn(self):
        pass

    def delete_items(self):
        for index in range(len(self.spaceships)):  #buğra
            self.spaceships[index].delete_items()
            self.spaceships[index] = None
class PlayerPlanet(Planet):
    def __init__(self, lanes, coordinates, screen) -> None:
        super().__init__(lanes, './Images/Planets-Lanes/player planet.png', coordinates)
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 25)
        self.not_able_to_spawn = pygame.image.load('./Images/Uptime-Downtime/spaceship down image.png').convert()
        self.not_able_to_spawn = pygame.transform.scale(self.not_able_to_spawn, (75, 75))
        self.able_to_spawn = pygame.image.load('./Images/Uptime-Downtime/spaceship ready image.png').convert()
        self.able_to_spawn = pygame.transform.scale(self.able_to_spawn, (75, 75))
        self.select_lane('up')

    def spawn_spaceships(self, spaceship_type):
        if (self.spaceship_types_and_costs[spaceship_type] <= self.gold) and (pygame.time.get_ticks() / 1000 - self.last_spawn_time > 2):
            if spaceship_type == 'tank':
                spaceship = SpaceshipTypeTank(self)
            elif spaceship_type == 'damage':
                spaceship = SpaceshipTypeDamageClose(self)
            elif spaceship_type == 'ranged':
                spaceship = SpaceshipTypeDamageFar(self)
            self.spaceships.append(spaceship)
            self.lanes[self.selected_lane].add_player_spaceship(spaceship)
            self.gold -= self.spaceship_types_and_costs[spaceship_type]
            self.last_spawn_time = pygame.time.get_ticks() / 1000

    def select_lane(self, key):
        self.lanes[self.selected_lane].be_deselected()

        if key == 'down':
            self.selected_lane -= 1
        elif key == 'up':
            self.selected_lane += 1

        self.selected_lane = self.selected_lane % 3

        self.lanes[self.selected_lane].be_selected()

    def enemy_appears(self, enemy_planet):
        self.opposite_planet = enemy_planet

    def display(self, screen):
        gold_label = self.font.render(f"{self.gold}", 1, (255,255,255))
        screen.blit(gold_label, (1200, 50))
        health_label = self.font.render(f"{self.health}", 1, (255,255,255))
        screen.blit(health_label, (1125, 50))
        if (pygame.time.get_ticks() / 1000 - self.last_spawn_time > 2):
            screen.blit(self.able_to_spawn, (900, 20))
        else:
            screen.blit(self.not_able_to_spawn, (900, 20))
        super().display(screen)

    def self_turn(self, screen):
        self.display(self.screen)
        self.spaceship_kamikaze()
        self.delete_spaceship()
        for spaceship in self.spaceships:
            spaceship.self_turn(screen)
        self.skill.display(screen)

class EnemyPlanet(Planet):
    def __init__(self, lanes, coordinates, player_planet) -> None:
        super().__init__(lanes, './Images/Planets-Lanes/enemy planet.png', coordinates)
        self.opposite_planet = player_planet

    def spawn_spaceships(self):
        new_spaceship = self.pick_spaceship()

        if new_spaceship != None:
            self.spaceships.append(new_spaceship)
            self.lanes[self.selected_lane].add_enemy_spaceship(new_spaceship)
            

    def pick_spaceship(self):
        spaceship_type = random.choice(('tank', 'damage', 'ranged', None))
        spaceship = None

        if (spaceship_type is not None):
            if (self.spaceship_types_and_costs[spaceship_type] <= self.gold) and (pygame.time.get_ticks() / 1000 - self.last_spawn_time > 2):
                if spaceship_type == 'tank':
                    spaceship = SpaceshipTypeTank(self)
                elif spaceship_type == 'damage':
                    spaceship = SpaceshipTypeDamageClose(self)
                elif spaceship_type == 'ranged':
                    spaceship = SpaceshipTypeDamageFar(self)

                self.gold -= self.spaceship_types_and_costs[spaceship_type]
                self.last_spawn_time = pygame.time.get_ticks() / 1000
            
        return spaceship

    def select_lane(self):
        first_lane_difference = self.lanes[0].get_difference_count()
        second_lane_difference = self.lanes[1].get_difference_count()
        third_lane_difference = self.lanes[2].get_difference_count()
        difference_list = [first_lane_difference, second_lane_difference, third_lane_difference]

        self.selected_lane = difference_list.index(max(difference_list))

    def self_turn(self, screen):
        super().display(screen)
        self.spaceship_kamikaze()
        self.delete_spaceship()
        self.select_lane()
        self.spawn_spaceships()
        for spaceship in self.spaceships:
            spaceship.self_turn(screen)
        self.skill.give_immunity(self.spaceships)
        

class Lane(GObject):
    def __init__(self, lane_number, player_spaceships, enemy_spaceships, coordinates, screen) -> None:
        super().__init__('./Images/Planets-Lanes/Normal Lane.png', coordinates)
        self.lane_number = lane_number
        self.player_spaceships = player_spaceships
        self.enemy_spaceships = enemy_spaceships
        self.is_selected = False
        self.screen = screen
        self.last_updated_time = 0

    def add_player_spaceship(self, player_spaceship):
        starting_coordinates = (self.x_coordinate - self.surface.get_width() / 2, self.y_coordinate)
        self.player_spaceships.append(player_spaceship)
        player_spaceship.update_starting_coordinates(starting_coordinates)
    
    def add_enemy_spaceship(self, enemy_spaceship):
        starting_coordinates = (self.x_coordinate + self.surface.get_width() / 2, self.y_coordinate)
        self.enemy_spaceships.append(enemy_spaceship)
        enemy_spaceship.update_starting_coordinates(starting_coordinates)

    def check_is_dead(self):
        if len(self.player_spaceships) > 0:
            if self.player_spaceships[0].is_dead():
                del self.player_spaceships[0]

        if len(self.enemy_spaceships) > 0:        
            if self.enemy_spaceships[0].is_dead():
                del self.enemy_spaceships[0]
    
    def be_selected(self):
        self.surface = pygame.image.load('./Images/Planets-Lanes/Selected Lane.png').convert()
        self.rect = self.surface.get_rect(center=(self.x_coordinate, self.y_coordinate))
        super().display(self.screen)
    
    def be_deselected(self):
        self.surface = pygame.image.load('./Images/Planets-Lanes/Normal Lane.png').convert()
        self.rect = self.surface.get_rect(center=(self.x_coordinate, self.y_coordinate))
        super().display(self.screen)

    def get_distances(self):
        if len(self.player_spaceships) >= 2:
            for index in range(len(self.player_spaceships[1:])):
                self.player_spaceships[index + 1].update_ahead_ally_distance(self.player_spaceships[index])

        if len(self.player_spaceships) >= 1:
            self.player_spaceships[0].update_ahead_ally()

        if len(self.enemy_spaceships) >= 2:
            for index in range(len(self.enemy_spaceships[1:])):
                self.enemy_spaceships[index + 1].update_ahead_ally_distance(self.enemy_spaceships[index])

        if len(self.enemy_spaceships) >= 1:
            self.enemy_spaceships[0].update_ahead_ally()

    def get_difference_count(self):
        if self.player_spaceships is None:
            if self.enemy_spaceships is None:
                return 0
            else:
                return - len(self.enemy_spaceships)
        else:
            if self.enemy_spaceships is None:
                return len(self.player_spaceships)
            else:
                return len(self.player_spaceships) - len(self.enemy_spaceships)

    def give_attack_orders(self):

        if len(self.player_spaceships) >= 3:
            if len(self.enemy_spaceships) > 0:
                for index in range(len(self.player_spaceships[:3])):
                    self.player_spaceships[index].fire_projectile(self.enemy_spaceships[0])
            else:
                for spaceship in self.player_spaceships:
                    spaceship.update_is_attacking()
        else:
            if len(self.enemy_spaceships) > 0:
                for index in range(len(self.player_spaceships)):
                    self.player_spaceships[index].fire_projectile(self.enemy_spaceships[0])
            else:
                for spaceship in self.player_spaceships:
                    spaceship.update_is_attacking()

        if len(self.enemy_spaceships) >= 3:
            if len(self.player_spaceships) > 0:
                for index in range(len(self.enemy_spaceships[:3])):
                    self.enemy_spaceships[index].fire_projectile(self.player_spaceships[0])
            else:
                for spaceship in self.enemy_spaceships:
                    spaceship.update_is_attacking()
        else:
            if len(self.player_spaceships) > 0:
                for index in range(len(self.enemy_spaceships)):
                    self.enemy_spaceships[index].fire_projectile(self.player_spaceships[0])
            else:
                for spaceship in self.enemy_spaceships:
                    spaceship.update_is_attacking()

    def self_turn(self):
        self.check_is_dead()
        self.get_distances()
        self.give_attack_orders()
        super().display(self.screen)


    
class Game:
    def __init__(self) -> None:
        self.width = 1440
        self.height = 810
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = pygame.image.load('./Images/Screens/Background.jpg').convert()
        self.lanes = [Lane(0, [], [], (720,615), self.screen), Lane(1, [], [], (720,410), self.screen), 
                        Lane(2, [], [], (720,205), self.screen)]
        self.player_planet = PlayerPlanet(self.lanes, (100,405), self.screen)
        self.enemy_planet = EnemyPlanet(self.lanes, (1340,405), self.player_planet)
        self.player_planet.enemy_appears(self.enemy_planet)
        self.clock = pygame.time.Clock()

    def exit(self): # Together with Yusuf
        does_exit = False
        for event in pygame.event.get():
            if (event.type == pygame.QUIT): 
                does_exit = True
            elif (event.type == pygame.KEYDOWN):
                if ((event.key == pygame.K_f)):
                    does_exit = True
                else:
                    self.keyboard_pressed(event)

        if does_exit:
            self.delete_items()
        return does_exit

    def tick(self):
        while True:
            self.screen.blit(self.background, (0, 0))
            end_game = self.exit()

            if end_game:
                break

            for lane in self.lanes:
                lane.self_turn()

            self.player_planet.self_turn(self.screen)
            self.enemy_planet.self_turn(self.screen)
 
            player_alive = self.player_planet.is_alive()
            enemy_alive = self.enemy_planet.is_alive()

            if not player_alive:
                self.delete_items()
                lose_screen = GObject('./Images/Screens/LoseScreen.jpg', (720, 405))
                lose_screen.display(self.screen)
                pygame.display.flip()
                pygame.time.wait(3000)
                lose_screen = None
                break
            
            if not enemy_alive:
                self.delete_items()
                win_screen = GObject('./Images/Screens/WinScreen.png', (720, 405))
                win_screen.display(self.screen)
                pygame.display.flip()
                pygame.time.wait(3000)
                win_screen = None
                break
            
            self.clock.tick(60)
            pygame.display.flip()

    def keyboard_pressed(self, event): # Together with Yusuf
        if event.key == pygame.K_DOWN:
            self.player_planet.select_lane('down')
        elif event.key == pygame.K_UP:
            self.player_planet.select_lane('up')
        elif event.key == pygame.K_SPACE:
            self.player_planet.use_skill()
        elif event.key == pygame.K_a:
            self.player_planet.spawn_spaceships('tank')
        elif event.key == pygame.K_s:
            self.player_planet.spawn_spaceships('damage')
        elif event.key == pygame.K_d:
            self.player_planet.spawn_spaceships('ranged')

    def delete_items(self):
        self.player_planet.delete_items()
        del self.player_planet
        self.enemy_planet.delete_items()
        del self.enemy_planet
        for lane in self.lanes:
            del lane

game = Game()
game.tick()
