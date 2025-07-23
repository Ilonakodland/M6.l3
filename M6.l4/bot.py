import discord
from discord.ext import commands
import os
import random
from logic import Pokemon, Player, Enemy

# Cek keberadaan config.py, jika tidak ada, gunakan environment variable
try:
    from config import TOKEN
except ImportError:
    TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Menyimpan data pemain
players = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    print("Bot siap digunakan!")

@bot.command()
async def start(ctx):
    await ctx.send(f'Selamat datang di Pokemon Adventure Bot! Ini adalah game petualangan Pokemon. '
                  f'Mulai dengan mendapatkan Pokemon pertamamu dengan perintah `!claim`')

@bot.command()
async def claim(ctx, choice: str = None):
    user_id = str(ctx.author.id)

    if user_id in players:
        await ctx.send(f"{ctx.author.mention}, kamu sudah memiliki Pokemon: {players[user_id].pokemon.name}!")
        return

    starters = {
        "charmander": ("Charmander", 20, 100),
        "squirtle": ("Squirtle", 18, 110),
        "bulbasaur": ("Bulbasaur", 19, 105)
    }

    if choice is None or choice.lower() not in starters:
        options = ", ".join(starters.keys())
        await ctx.send(f"{ctx.author.mention}, pilih Pokemon dengan `!claim <nama>`\nContoh: `!claim charmander`\nPilihan: {options}")
        return

    selected = starters[choice.lower()]
    pokemon = Pokemon(selected[0], selected[1], selected[2])
    player = Player(ctx.author.name, pokemon)
    players[user_id] = player

    await ctx.send(f"{ctx.author.mention}, kamu memilih {pokemon.name}!\n"
                   f"Status: HP {pokemon.hp}/{pokemon.max_hp}, Power: {pokemon.power}\n"
                   f"Gunakan `!stats` untuk melihat status dan `!battle` untuk bertarung.")

@bot.command()
async def stats(ctx):
    user_id = str(ctx.author.id)
    
    # Periksa apakah pemain memiliki Pokemon
    if user_id not in players:
        await ctx.send(f"{ctx.author.mention}, kamu belum memiliki Pokemon! Gunakan `!claim` untuk mendapatkan Pokemon.")
        return
    
    player = players[user_id]
    pokemon = player.pokemon
    
    embed = discord.Embed(title=f"Pokemon {pokemon.name}", color=0x00ff00)
    embed.set_author(name=f"Trainer: {ctx.author.name}")
    embed.add_field(name="HP", value=f"{pokemon.hp}/{pokemon.max_hp}", inline=True)
    embed.add_field(name="Power", value=str(pokemon.power), inline=True)
    embed.add_field(name="Stats", value=f"Kemenangan: {player.wins}\nKekalahan: {player.losses}", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def battle(ctx):
    user_id = str(ctx.author.id)
    
    # Periksa apakah pemain memiliki Pokemon
    if user_id not in players:
        await ctx.send(f"{ctx.author.mention}, kamu belum memiliki Pokemon! Gunakan `!claim` untuk mendapatkan Pokemon.")
        return
    
    player = players[user_id]
    
    # Daftar musuh dengan tingkat kesulitan yang bervariasi
    enemies = [
        ("Pidgey", 15, 80),
        ("Rattata", 17, 70),
        ("Zubat", 14, 75),
        ("Caterpie", 13, 65),
        ("Spearow", 16, 85),
        ("Ekans", 18, 90),
        ("Sandshrew", 20, 95),
        ("Nidoran", 19, 85),
        ("Growlithe", 25, 110),
        ("Poliwag", 22, 105)
    ]
    
    # Pilih musuh secara acak dengan kekuatan yang sesuai
    enemy_power_factor = min(1.5, 0.8 + (player.wins * 0.1))  # Tingkat kesulitan meningkat seiring kemenangan
    
    enemy_data = random.choice(enemies)
    enemy_name = enemy_data[0]
    enemy_power = int(enemy_data[1] * enemy_power_factor)
    enemy_hp = int(enemy_data[2] * enemy_power_factor)
    
    enemy_pokemon = Pokemon(enemy_name, enemy_power, enemy_hp)
    enemy = Enemy(f"Lawan {ctx.author.name}", enemy_pokemon)
    
    # Mulai pertarungan
    await ctx.send(f"{ctx.author.mention}, kamu bertemu dengan {enemy_pokemon.name} liar!\n"
                  f"Status musuh: HP {enemy_pokemon.hp}, Power {enemy_pokemon.power}\n"
                  f"Status Pokemon-mu: HP {player.pokemon.hp}/{player.pokemon.max_hp}, Power {player.pokemon.power}\n"
                  f"Gunakan `!attack` untuk menyerang atau `!run` untuk kabur!")
    
    # Simpan data musuh untuk pertarungan
    players[user_id].current_enemy = enemy

@bot.command()
async def attack(ctx):
    user_id = str(ctx.author.id)
    
    # Periksa apakah pemain memiliki Pokemon dan sedang bertarung
    if user_id not in players:
        await ctx.send(f"{ctx.author.mention}, kamu belum memiliki Pokemon! Gunakan `!claim` untuk mendapatkan Pokemon.")
        return
    
    player = players[user_id]
    
    if not hasattr(player, 'current_enemy') or player.current_enemy is None:
        await ctx.send(f"{ctx.author.mention}, kamu tidak sedang bertarung! Gunakan `!battle` untuk mencari lawan.")
        return
    
    enemy = player.current_enemy
    
    # Player menyerang
    damage = player.attack_enemy(enemy)
    response = [f"{ctx.author.mention}, {player.pokemon.name} menyerang {enemy.pokemon.name} dan memberikan {damage} damage!"]

    

    
    # Cek apakah musuh kalah
    if not enemy.pokemon.is_alive():
        # Pemain menang
        hp_increase = 10 + random.randint(5, 15)
        power_increase = 1 + random.randint(0, 2)
        player.pokemon.increase_stats(hp_increase, power_increase)
        player.add_win()
        
        response.append(f"Selamat! Kamu mengalahkan {enemy.pokemon.name}!")
        response.append(f"HP max bertambah {hp_increase}, Power bertambah {power_increase}.")
        response.append(f"Status sekarang: HP {player.pokemon.hp}/{player.pokemon.max_hp}, Power: {player.pokemon.power}")
        response.append(f"Total kemenangan: {player.wins}")
        if player.wins % 5 == 0:
            response.append("Bonus! Karena total kemenanganmu mencapai kelipatan 5, Pokemonmu mendapat +10 HP dan +5 Power!")
        
        # Reset current_enemy
        player.current_enemy = None
    else:
        # Musuh membalas
        enemy_damage = enemy.pokemon.attack(player.pokemon)
        response.append(f"{enemy.pokemon.name} menyerang balik dan memberikan {enemy_damage} damage!")
        
        # Cek apakah pemain kalah
        if not player.pokemon.is_alive():
            # Pemain kalah
            hp_decrease = 5 + random.randint(0, 5)
            power_decrease = random.randint(0, 1)
            player.pokemon.decrease_stats(hp_decrease, power_decrease)
            player.add_loss()
            
            response.append(f"Pokemon kamu kalah melawan {enemy.pokemon.name}!")
            response.append(f"HP max berkurang {hp_decrease}, Power berkurang {power_decrease}.")
            
            # Heal Pokemon
            heal_amount = player.pokemon.max_hp // 2
            player.pokemon.heal(heal_amount)
            
            response.append(f"Pokemon kamu dipulihkan sebagian. HP sekarang: {player.pokemon.hp}/{player.pokemon.max_hp}")
            response.append(f"Total kekalahan: {player.losses}")
            
            # Reset current_enemy
            player.current_enemy = None
        else:
            response.append(f"Status Pokemon-mu: HP {player.pokemon.hp}/{player.pokemon.max_hp}")
            response.append(f"Status musuh: HP {enemy.pokemon.hp}")
    
    await ctx.send("\n".join(response))

@bot.command()
async def run(ctx):
    user_id = str(ctx.author.id)
    
    # Periksa apakah pemain memiliki Pokemon dan sedang bertarung
    if user_id not in players:
        await ctx.send(f"{ctx.author.mention}, kamu belum memiliki Pokemon! Gunakan `!claim` untuk mendapatkan Pokemon.")
        return
    
    player = players[user_id]
    
    if not hasattr(player, 'current_enemy') or player.current_enemy is None:
        await ctx.send(f"{ctx.author.mention}, kamu tidak sedang bertarung! Gunakan `!battle` untuk mencari lawan.")
        return
    
    # Melarikan diri dari pertarungan
    player.add_loss()
    player.current_enemy = None
    
    await ctx.send(f"{ctx.author.mention}, kamu melarikan diri dari pertarungan!\n"
                  f"Total kekalahan: {player.losses}")

@bot.command()
async def heal(ctx):
    user_id = str(ctx.author.id)
    
    # Periksa apakah pemain memiliki Pokemon
    if user_id not in players:
        await ctx.send(f"{ctx.author.mention}, kamu belum memiliki Pokemon! Gunakan `!claim` untuk mendapatkan Pokemon.")
        return
    
    player = players[user_id]
    
    if hasattr(player, 'current_enemy') and player.current_enemy is not None:
        await ctx.send(f"{ctx.author.mention}, kamu tidak bisa menyembuhkan Pokemon saat sedang bertarung!")
        return
    
    # Hanya bisa heal jika HP kurang dari max
    if player.pokemon.hp >= player.pokemon.max_hp:
        await ctx.send(f"{ctx.author.mention}, Pokemon kamu sudah memiliki HP penuh!")
        return
    
    # Menyembuhkan Pokemon
    heal_amount = player.pokemon.max_hp // 2
    old_hp = player.pokemon.hp
    player.pokemon.heal(heal_amount)
    
    await ctx.send(f"{ctx.author.mention}, Pokemon kamu disembuhkan!\n"
                  f"HP sebelum: {old_hp}/{player.pokemon.max_hp}\n"
                  f"HP sekarang: {player.pokemon.hp}/{player.pokemon.max_hp}")

@bot.command()
async def bantu(ctx):
    commands = [
        "**!start** - Informasi tentang bot",
        "**!claim** - Klaim Pokemon pertamamu",
        "**!select <nomor>** - Pilih Pokemon starter",
        "**!stats** - Lihat status Pokemon-mu",
        "**!battle** - Cari lawan untuk bertarung",
        "**!attack** - Serang lawan saat bertarung",
        "**!run** - Melarikan diri dari pertarungan",
        "**!heal** - Pulihkan HP Pokemon-mu (saat tidak bertarung)"
    ]
    
    embed = discord.Embed(title="Pokemon Adventure Bot - Bantuan", color=0x3498db)
    embed.description = "Daftar perintah yang tersedia:"
    embed.add_field(name="Perintah", value="\n".join(commands), inline=False)
    
    await ctx.send(embed=embed)



#admin
@bot.command()
@commands.has_permissions(administrator=True)
async def setwins(ctx, jumlah: int):
    user_id = str(ctx.author.id)

    if user_id not in players:
        await ctx.send(f"{ctx.author.mention}, kamu belum memiliki Pokemon.")
        return

    player = players[user_id]
    previous_wins = player.wins
    player.wins = jumlah

    # Hitung total kelipatan 5 yang baru dibanding sebelumnya
    prev_bonus = previous_wins // 5
    new_bonus = jumlah // 5
    delta = new_bonus - prev_bonus

    if delta > 0:
        for _ in range(delta):
            player.pokemon.increase_stats(10, 5)

    await ctx.send(f"{ctx.author.mention}, total win kamu diatur menjadi {jumlah}. "
                   f"{'Bonus stats diberikan: +' + str(10*delta) + ' HP dan +' + str(5*delta) + ' Power.' if delta > 0 else 'Tidak ada bonus stats diberikan.'}")

@bot.command()
@commands.has_permissions(administrator=True)
async def claimpluh(ctx):
    user_id = str(ctx.author.id)

    if user_id in players:
        await ctx.send(f"{ctx.author.mention}, kamu sudah memiliki Pokemon: {players[user_id].pokemon.name}!")
        return

    pokemon = Pokemon("Pluh", 500, 500)
    player = Player(ctx.author.name, pokemon)
    players[user_id] = player

    await ctx.send(f"{ctx.author.mention}, kamu telah mendapatkan Pokemon spesial **Pluh**!\n"
                   f"Status: HP {pokemon.hp}/{pokemon.max_hp}, Power: {pokemon.power}")

if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: Token Discord tidak ditemukan. Pastikan ada file config.py dengan TOKEN atau environment variable DISCORD_TOKEN.")