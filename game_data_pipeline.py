import json
import os
import pandas as pd

class Game_Data_Pipeline(object):

    def __init__(self, folder):
        self.folder = folder
        self.total_dict = {}

    def parse_data(j_dict, field):
        """Takes in dict chunks parses out only the field 
        to save space and time.

        Keyword arguments:
        j_dict - json dictionary of game data
        field - the field to return

        Returns:
        game_dict - dictgame_id
        """
        if field == 'all':
            return {int(key): j_dict[key] for key in j_dict.keys()}
        elif field == 'combine':
            return {int(key):
                    set(j_dict[key]['mechanics']+j_dict[key]['categories']) for key in j_dict.keys()}
        else:
            return {int(key): j_dict[key][field] for key in j_dict.keys()}

    def merge_dicts(*dict_args):
        """
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts.
        """
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    def load_data(location_str):
        f = open(location_str, 'r')
        json_to_dict = json.load(f)
        f.close()
        return(json_to_dict)

    def gather_files(self):
        files = os.listdir(self.folder)
        list_of_game_dicts = []
        for f in files:
            if f[:5] == 'games':
                f = self.folder + "/" + f
                game_dict = self.load_data(f)
                parsed_dict = {int(key): game_dict[key] for key in game_dict.keys()}
                list_of_game_dicts.append(parsed_dict)
        
        return list_of_game_dicts

    def create_total_dict(self):
        game_list = self.gather_files()
        self.total_dict = self.merge_dicts(*game_list)

    def get_total_dict(self):
        return self.total_dict

    def unravel_dict(d):
        games = []
        categories = []
        for game, keywords in d.iteritems():
            for word in keywords:
                games.append(game)
                categories.append(word)
        ones = [1]*len(games)
        return games, categories, ones

    def create_set_matrix(ids_, features, ones):
        df = pd.DataFrame({'ids': ids_, 'features': features, 'ones':ones})
        feature_matrix = df.pivot(index='ids', columns='features', values='ones')
        return feature_matrix

    def add_player_counts(feature_matrix):
        pass

    def data_pipeline(folder, field, set=False):
        list_of_game_dicts = gather_files(folder, field)
        merged_dicts = merge_dicts(*list_of_game_dicts)
        if set: 
            feature_matrix = create_set_matrix(*unravel_dict(merged_dicts))
            minplayer_dict = merge_dicts(*gather_files(folder, 'minplayers'))
            feature_matrix['minplayers'] = pd.Series(minplayer_dict)
            maxplayer_dict = merge_dicts(*gather_files(folder, 'maxplayers'))
            feature_matrix['maxplayers'] = pd.Series(maxplayer_dict)
            feature_matrix.fillna(0, inplace=True)
            return feature_matrix
        else: 
            return merged_dicts