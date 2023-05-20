"""Wrapper classes for data structures. 

Handles saving and loading from file or from data.
Using Data directly requires providing a basepath for saving and loading. 
Defaults to json filetype.
"""
# pylint: disable=arguments-differ
from hanabdata.tools.io import read




class DatabaseError(Exception):
    """Raised when information is accessed that does not exist in the database"""



class Data:
    """Basic wrapper class to handle data.
    
    basepath should not end with a '/'. 
    """
    basepath = None
    extension = 'json'

    def __init__(self, data, data_id, basepath=None, extension=None):
        self.data = data
        if basepath is not None:
            self.basepath = basepath
        if extension is not None:
            self.extension = extension
        self.id = str(data_id)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, val):
        self.data[key] = val

    def __repr__(self):
        return f'{self.data}'

    def save(self, basepath=None):
        """Saves data to file at basepath folder. If none is specified, uses the class default"""
        if basepath is None:
            basepath = self.basepath
        path = f'{basepath}/{self.id}.{self.extension}'
        if self.extension == 'json':
            read.write_json(path, self.data)
        elif self.extension == 'csv':
            read.write_csv(path, self.data)
        else: 
            raise NotImplementedError('only json and csv files are supported!')
    
    @classmethod
    def load(cls, data_id, basepath=None, extension=None):
        """loads data from  system. If the data does not exist, raises a DatabaseError"""
        if basepath is None:
            parsed_path = cls.basepath
        else:
            parsed_path = basepath
        if extension is None:
            parsed_extension = cls.extension
        else:
            parsed_extension = extension
        path = f'{parsed_path}/{data_id}.{parsed_extension}'
        if parsed_extension == 'json':
            reader = read.read_json
        elif parsed_extension == 'csv':
            reader = read.read_csv
        else: 
            raise NotImplementedError('only json and csv files are supported!')
        try:
            data = reader(path) 
        except FileNotFoundError as e:
            raise DatabaseError(f'Data does not exist at {parsed_path}/{data_id}.{parsed_extension}!') from e  
        return cls(data, data_id, basepath=basepath, extension=extension)

class Chunk(Data):
    """Wrapper for groups of games."""
    basepath = './data/raw/games'
    
    @classmethod
    def load_safe(cls, data_id, basepath=None, extension=None):
        """Attempts to load chunk. If none exists, generates a chunk with empty data."""
        try:
            return cls.load(data_id, basepath=None, extension=None)
        except DatabaseError:
            return cls([None]*1000, data_id, basepath=None, extension=None)

class ChunkMeta(Data):
    """Wrapper for storing meta data"""
    basepath = './data/preprocessed/games'

class Seed(Data):
    """Wrapper for seeds."""
    basepath = './data/raw/seeds'

class User(Data):
    """Wrapper for users."""
    basepath = './data/raw/users'

class Game(Data):
    """Wrapper class for working with a single game at a time. 
    If working with multiple games, GamesIterator is preferable"""

    def save(self):
        chunk_id, index = self._get_chunk_and_index(int(self.id))
        try:
            chunk = Chunk.load(chunk_id)
        except DatabaseError:
            chunk = Chunk([None] * 1000, chunk_id)
        chunk.data[index] = self.data
        chunk.save()
    
    @classmethod
    def load(cls, data_id):
        chunk_id, index = cls._get_chunk_and_index(data_id)
        chunk = Chunk.load(chunk_id)
        game_data = chunk.data[index]
        if game_data == 'Error' or game_data is None:
            raise DatabaseError('game data does not exist!')
        return cls(game_data, data_id)

    @staticmethod
    def _get_chunk_and_index(data_id):
        """returns chunk and index for a given game"""
        return data_id // 1000, data_id % 1000

class Games(Data):
    """Games is a structure to contain a list of games. Games should be 
    sorted by ID (increasing or decreasing or random within chunk is OK) 
    for optimized filesystem access. Saving games inserts them existing 
    chunks and so will not delete any previously-saved game data but will overwrite."""
    
    def __init__(self, games, **kwargs):
        super().__init__(games, None, **kwargs)

    def save(self):
        open_chunk = None
        for game in self.data:
            chunk_id, index = Game._get_chunk_and_index(game["id"])
            if open_chunk is None:
                open_chunk = Chunk.load_safe(chunk_id)
            elif open_chunk.id != chunk_id:
                open_chunk.save()
                open_chunk = Chunk.load_safe(chunk_id)
            open_chunk[index] = game
        open_chunk.save()
    
    @classmethod
    def load(cls, game_ids):
        open_chunk = None
        games = []
        missing_ids = []
        for game_id in game_ids:
            chunk_id, index = Game._get_chunk_and_index(game_id)
            if open_chunk is None or open_chunk.id != chunk_id:
                open_chunk = Chunk.load_safe(chunk_id)
            game = open_chunk[index]
            if game is not None and game != "Error":
                games.append(game)
            else:
                missing_ids.append(game_id)
            
        return cls(games), missing_ids          

class GamesIterator:
    """Iterates over all games metadata"""
    def __init__(self, oldest_to_newest=True):
        dir_path = ChunkMeta.basepath
        files = [int(y) for y in read.get_file_names(dir_path)]
        if oldest_to_newest:
            self.chunk_list = sorted(files, reverse=True)
        else:
            self.chunk_list = sorted(files)

    def set_current(self):
        """Opens the next file and reads as JSON."""
        self.curr_chunk = chunk_num = self.chunk_list.pop()
        self.current = Chunk.load(chunk_num)
        self.index = 0

    def is_valid(self, game):
        """Returns True if a game is valid; False otherwise."""
        try:
            game["id"]
        except TypeError:
            return False
        except KeyError:
            print(f"Possible issue with JSON storage in chunk {self.curr_chunk}.")
            return False
        return True

    def __iter__(self):
        self.set_current()
        return self

    def __next__(self):
        while True:
            if self.index == 1000:
                try:
                    self.set_current()
                except IndexError as e:
                    raise StopIteration from e
            game = self.current[self.index]
            self.index += 1
            if self.is_valid(game):
                return game
            
class ScoreHuntData(Data):
    extension = 'csv'
    basepath = './data/processed/score_hunts'

