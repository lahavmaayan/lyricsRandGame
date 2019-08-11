import requests
import random
import webbrowser
from googleapiclient.discovery import build

from settings import GENIUS_KEY, YOUTUBE_API_KEY


class LyricsRandGame:
    BASE_URL = 'https://api.genius.com'
    HEADERS = {'Authorization': 'Bearer ' + GENIUS_KEY}
    MAX_SONGS_PER_PAGE = 50
    YT_BASE_URL = "https://www.youtube.com/watch?v="

    def __init__(self):
        super()
        self.prepare_the_game()

    def _base_request(self, url_addition, data):
        full_url = self.BASE_URL + url_addition
        response = requests.get(full_url, data=data, headers=self.HEADERS)
        return response.json()

    def _get_curr_player_name(self):
        return self.players[self.curr_player_id]['name']

    def request_search_info(self, search_term):
        data = {'q': search_term}
        return self._base_request('/search', data)

    def request_artist_song(self, artist_id):
        artist_url = '/artists/' + str(artist_id) + '/songs'
        data = {'sort': 'popularity', 'per_page': self.MAX_SONGS_PER_PAGE, 'page': 1}
        return self._base_request(artist_url, data)

    def request_song_lyric(self, song_id):
        song_url = '/songs/' + str(song_id)
        data = {'text_format': 'plain'}
        return self._base_request(song_url, data)

    def prepare_songs_by_artist(self):
        artist_id = self.get_artist_id()
        response = self.request_artist_song(artist_id)
        songs = response['response']['songs']
        songs_dict = {}
        for song in songs:
            title = song['title']
            song_id = song['id']
            songs_dict[title] = song_id

        self.songs_dict = songs_dict

    def get_artist_id(self):
        search_result = self.request_search_info(self.artist_name)
        artist_info = search_result['response']['hits'][0]['result']['primary_artist']
        if artist_info["name"] == self.artist_name:
            return artist_info["id"]

        raise Exception("No artist was found by this name")

    def print_plays_stats(self):
        print(" ")
        print("the current player is " + self._get_curr_player_name())
        for id, data in self.players.items():
            print(data['name'] + " has a score of " + str(data['score']))

        print(" ")

    def prepare_the_game(self):
        num_players = int(input("How many players are there? "))
        players = {}
        for i in range(num_players):
            player_name = input("give me a player's name ")
            players[i] = {'name': player_name, 'score': 0}

        self.players = players
        self.decide_first_player()
        self.print_plays_stats()
        self.artist_name = input("What's the artist name? ")

        self.youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    def get_song_lyric(self, song_id):
        response = self.request_song_lyric(song_id)
        print("Opening the lyrics")
        webbrowser.open_new_tab(response['response']['song']['url'])

    def decide_first_player(self):
        self.curr_player_id = random.choice(list(self.players.keys()))
        print(self._get_curr_player_name() + " will go first")

    def update_score(self):
        answer = input("Did the other player succeed in finding the song? Y/N ")
        while answer not in ['Y', 'N']:
            answer = input("Did the other player succeed in finding the song? Y/N ")

        if answer == 'Y':
            self.players[self.curr_player_id]['score'] += 1
            print("Well done!")
        else:
            print("Don't worry, you'll do better next time")

        self.curr_player_id = (self.curr_player_id + 1) % len(self.players)
        self.print_plays_stats()

    def _should_skip_song(self):
        should_skip = input(self._get_curr_player_name() + ", Do you wish to skip this song? Y/N ")
        while should_skip not in ['Y', 'N']:
            should_skip = input(self._get_curr_player_name() + ", Do you wish to skip this song? Y/N ")

        if should_skip == "Y":
            return True

        return False

    def play(self):
        while len(self.songs_dict) > 0:
            print("The chosen song is..")
            song_title_chosen = random.choice(list(self.songs_dict.keys()))
            song_id_chosen = self.songs_dict.pop(song_title_chosen)
            print(song_title_chosen)

            if self._should_skip_song():
                continue

            print(" ")
            self.get_song_lyric(song_id_chosen)
            self.play_the_song(song_title_chosen)
            self.update_score()

            print(" ")
            print("*******************")
            print(" ")

    def play_the_song(self, song_title_chosen):
        should_open_yt = input("Do you want to open the song on YouTube? Y/N ")
        while should_open_yt not in ['Y', 'N']:
            should_open_yt = input("Do you want to open the song on YouTube? Y/N ")

        if should_open_yt == "N":
            return

        youtube_url = self.search_youtube(song_title_chosen)
        print("Open the Youtube for the song :)")
        webbrowser.open_new_tab(youtube_url)

    def search_youtube(self, song_title):
        query = song_title + " " + self.artist_name
        response = self.youtube.search().list(q=query, part='id,snippet', maxResults=3).execute()
        results_items = response["items"]
        for item in results_items:
            if item["id"]["kind"] == "youtube#video":
                video_id = item["id"]["videoId"]
                return self.YT_BASE_URL + video_id


if __name__ == "__main__":
    game = LyricsRandGame()
    game.prepare_songs_by_artist()
    game.play()
