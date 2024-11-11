"""Change name in downloaded games."""

from tqdm import tqdm
from hanabdata.tools.io import read
from hanabdata.tools import structures
from hanabdata.tools.io.update import update_chunk

def change_name(old_name, new_name):
    """Change name in downloaded games."""
    # chunk_list = sorted([int(y) for y in read.get_file_names("./data/raw/games")])
    # for chunk in tqdm(chunk_list):
    #     try:
    #         data = structures.Chunk.load(chunk)
    #     except ValueError:
    #         update_chunk(chunk)
    #         data = structures.Chunk.load(chunk)
    #     for game in data:
    #         if game is None or game == "Error":
    #             continue
    #         players = game["players"]
    #         if old_name in players:
    #             i = players.index(old_name)
    #             players[i] = new_name
    #     data.save()

    chunk_list = sorted([int(y) for y in read.get_file_names("./data/preprocessed/games")])
    for chunk in tqdm(chunk_list):
        try:
            data = structures.ChunkMeta.load(chunk)
        except ValueError:
            update_chunk(chunk)
            data = structures.ChunkMeta.load(chunk)
        for game in data:
            if game is None or game == "Error" or game == []:
                continue
            try:
                players = game["playerNames"]
            except TypeError: # lol, gotta fix this sooner or later
                try:
                    players = game[0]["playerNames"]
                except IndexError:
                    print(game)
                    break
            if old_name in players:
                i = players.index(old_name)
                players[i] = new_name
        data.save()

if __name__ == "__main__":
    change_name("purplejoe2", "purplejoe")
    print("success")
