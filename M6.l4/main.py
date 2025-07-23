import random
from logic import Pokemon, Player, Enemy

def battle(player, enemy):
    print(f"\nPertarungan melawan {enemy.name} dengan Pokemon {enemy.pokemon.name} dimulai!")
    
    while player.pokemon.is_alive() and enemy.pokemon.is_alive():
        print(f"\nHP {player.pokemon.name}: {player.pokemon.hp}/{player.pokemon.max_hp} | Power: {player.pokemon.power}")
        print(f"HP {enemy.pokemon.name}: {enemy.pokemon.hp} | Power: {enemy.pokemon.power}")
        print("Apa yang ingin kamu lakukan?")
        print("1. Serang")
        print("2. Lari")

        action = input("Masukkan pilihan (1/2): ")

        if action == '1':
            damage = player.attack_enemy(enemy)
            print(f"Kamu menyerang dan memberikan {damage} damage!")
            
            if enemy.pokemon.is_alive():
                enemy_damage = enemy.pokemon.attack(player.pokemon)
                print(f"Musuh menyerang dan memberikan {enemy_damage} damage!")
            else:
                print("Musuh kalah!")
                # Fitur: Naikkan HP dan power setelah menang
                hp_increase = 20
                power_increase = 2
                player.pokemon.increase_stats(hp_increase, power_increase)
                player.add_win()
                print(f"Selamat! HP max bertambah {hp_increase}, Power bertambah {power_increase}.")
                print(f"Status sekarang: HP {player.pokemon.hp}/{player.pokemon.max_hp}, Power: {player.pokemon.power}")
                print(f"Total kemenangan: {player.wins}")
                return True  # Menang
        elif action == '2':
            print("Kamu melarikan diri dari pertarungan.")
            player.add_loss()
            print(f"Total kekalahan: {player.losses}")
            return False  # Kalah / lari
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")
    
    if not player.pokemon.is_alive():
        print("Pokemon kamu kalah!")
        # Fitur: Turunkan HP dan power setelah kalah
        hp_decrease = 10
        power_decrease = 1
        player.pokemon.decrease_stats(hp_decrease, power_decrease)
        player.add_loss()
        print(f"HP max berkurang {hp_decrease}, Power berkurang {power_decrease}.")
        print(f"Status sekarang: HP {player.pokemon.hp}/{player.pokemon.max_hp}, Power: {player.pokemon.power}")
        print(f"Total kekalahan: {player.losses}")
        
        # Heal sedikit setelah kalah untuk bisa lanjut bertarung
        heal_amount = player.pokemon.max_hp // 2
        player.pokemon.heal(heal_amount)
        print(f"Pokemon kamu dipulihkan sebagian. HP sekarang: {player.pokemon.hp}/{player.pokemon.max_hp}")
        
        return False
    
    return True

def start_adventure():
    print("Selamat datang di Petualangan Pokemon!")
    player_name = input("Masukkan nama pelatihmu: ")

    print("Pilih Pokemon awalmu:")
    print("1. Charmander (Power 20, HP 100)")
    print("2. Squirtle (Power 18, HP 110)")
    print("3. Bulbasaur (Power 19, HP 105)")

    choice = input("Masukkan pilihan (1/2/3): ")

    if choice == '1':
        starter = Pokemon("Charmander", 20, 100)
    elif choice == '2':
        starter = Pokemon("Squirtle", 18, 110)
    elif choice == '3':
        starter = Pokemon("Bulbasaur", 19, 105)
    else:
        print("Pilihan tidak valid, Charmander dipilih secara default.")
        starter = Pokemon("Charmander", 20, 100)

    player = Player(player_name, starter)
    print(f"Halo {player_name}, kamu memulai petualangan dengan {starter.name}!")
    print(f"Status awal: HP {player.pokemon.hp}/{player.pokemon.max_hp}, Power: {player.pokemon.power}")

    waves = [
        (("Pidgey", 15, 80), ("Rattata", 17, 70)),
        (("Zubat", 14, 75), ("Caterpie", 13, 65)),
        (("Spearow", 16, 85), ("Ekans", 18, 90)),
        (("Sandshrew", 20, 95), ("Nidoran", 19, 85)),
        (("Growlithe", 25, 110), ("Poliwag", 22, 105))
    ]
    
    current_wave = 1
    
    while current_wave <= len(waves):
        option_a, option_b = waves[current_wave - 1]
        
        print(f"\nWave {current_wave}:")
        print(f"Pilih lawan yang ingin kamu hadapi:")
        print(f"1. {option_a[0]} (Power {option_a[1]}, HP {option_a[2]})")
        print(f"2. {option_b[0]} (Power {option_b[1]}, HP {option_b[2]})")

        while True:
            pilihan = input("Masukkan pilihan musuh (1/2): ")
            if pilihan == '1':
                musuh = option_a
                break
            elif pilihan == '2':
                musuh = option_b
                break
            else:
                print("Pilihan tidak valid, silakan coba lagi.")

        enemy_pokemon = Pokemon(musuh[0], musuh[1], musuh[2])
        enemy = Enemy(f"Musuh Wave {current_wave}", enemy_pokemon)
        print(f"Kamu bertarung melawan {enemy_pokemon.name}!")

        menang = battle(player, enemy)
        
        if menang:
            print(f"Selamat! Kamu lolos wave {current_wave}.")
            current_wave += 1
            
            # Heal sebagian HP setelah menang wave
            if current_wave <= len(waves):
                heal_amount = player.pokemon.max_hp // 4
                player.pokemon.heal(heal_amount)
                print(f"Pokemon kamu pulih sebagian. HP sekarang: {player.pokemon.hp}/{player.pokemon.max_hp}")
        else:
            print(f"\nKamu gagal di wave {current_wave}.")
            retry = input("Coba lagi? (y/n): ")
            if retry.lower() != 'y':
                print("Petualangan berakhir!")
                return

    print("\nSelamat! Kamu berhasil melewati semua wave dan memenangkan petualangan!")
    print(f"Statistik akhir:")
    print(f"Pokemon: {player.pokemon.name}")
    print(f"HP: {player.pokemon.hp}/{player.pokemon.max_hp}")
    print(f"Power: {player.pokemon.power}")
    print(f"Total kemenangan: {player.wins}")
    print(f"Total kekalahan: {player.losses}")

if __name__ == '__main__':
    start_adventure()