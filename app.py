from bottle import run, route, jinja2_view, static_file, redirect, error
from functools import partial
from sys import argv
import requests
import json

view = partial(jinja2_view, template_lookup=['templates'])

url = "http://ws.audioscrobbler.com/2.0/"
LAST_FM_API_KEY = "383747abda66236dceff6fe4f90bffd8"


def load_music(type):
    params = {
        "method": "tag.getTop{}".format(type.title()),
        "tag": "rock",
        "api_key": LAST_FM_API_KEY,
        "format": 'json'
    }
    req = requests.get(url, params=params)
    return json.loads(req.text)


music = {
    "album_list": load_music('albums'),
    "artist_list": load_music('artists')
}


@route('/', method="GET")
@view("home.html")
def homepage():
    albums = music["album_list"]["albums"]["album"]
    artists = music["artist_list"]["topartists"]["artist"]
    return {"albums": albums, "artists": artists}


@route('<filename:re:.*/style\.css>', method="GET")
def css(filename):
    return static_file('style.css', root='static_files/css')


@route('<filename:re:.*/js/logic.js>', method="GET")
def js(filename):
    return static_file('logic.js', root='static_files/js')


@route('/album/<id:int>', method="GET")
@view("album.html")
def return_album(id):
    album = [album_dict for album_dict in music["album_list"]["albums"]["album"] if
             album_dict["@attr"]["rank"] == str(id)]
    if any(album):
        params = {
            "method": "album.getinfo",
            "api_key": LAST_FM_API_KEY,
            "mbid": album[0]['mbid'],
            "format": 'json'
        }
        req = requests.get(url, params)
        return json.loads(req.text)
    else:
        return redirect("/not-found")


@route('/artist/<id:int>', method="GET")
@view("artist.html")
def return_artist(id):
    artist = [artist_dict for artist_dict in music["artist_list"]["topartists"]["artist"] if
              artist_dict["@attr"]["rank"] == str(id)]
    if any(artist):
        params = {
            "method": "artist.getinfo",
            "api_key": LAST_FM_API_KEY,
            "mbid": artist[0]['mbid'],
            "format": 'json'
        }
        req = requests.get(url, params)
        return json.loads(req.text)
    else:
        return redirect('/not-found')


@route('/all-artists', method='GET')
@view("all-artists.html")
def return_all_artists():
    return {"artists": music["artist_list"]["topartists"]["artist"]}


@route('/all-albums', method="GET")
@view("all-albums.html")
def return_all_albums():
    return {"albums": music["album_list"]["albums"]["album"]}


@route('/all-songs', method="GET")
@view('all-songs.html')
def return_all_songs():
    return {}


@route('/not-found', method="GET")
@view('not-found.html')
def not_found():
    return {}


@error(404)
@view('not-found.html')
def error404(error):
    return {}


def main():
    run(host='0.0.0.0', port=argv[1])


if __name__ == "__main__":
    main()
