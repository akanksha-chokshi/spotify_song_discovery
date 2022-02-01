import streamlit as st
st.set_page_config(page_title="Song Discovery", layout="wide")

import pandas as pd
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import streamlit.components.v1 as components
import random

@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv("songs.csv")
    df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
    exploded_track_df = df.explode("genres")
    return exploded_track_df

genre_names = ['Dance Pop', 'Electronic', 'Electropop', 'Hip Hop', 'Jazz', 'K-pop', 'Latin', 'Pop', 'Pop Rap', 'R&B', 'Rock']
audio_feats = ["acousticness", "danceability", "energy", "instrumentalness", "valence", "tempo"]

exploded_track_df = load_data()

title = "Spotify Song Discovery Engine"
st.title(title)

st.sidebar.markdown("Welcome to the Spotify Song Discovery Engine. Please customise your desired genre and key audio features!")
st.sidebar.markdown("##")
st.sidebar.markdown("*Choose your genre:*")
genre = st.sidebar.radio(
    "",genre_names, index=genre_names.index("Pop"))
st.sidebar.markdown("*Choose features to customize:*")
start_year, end_year = st.sidebar.slider(
    'Select the year range',
    1990, 2019, (1990, 2019)
)
acousticness = st.sidebar.slider(
    'Acousticness',
    0.0, 1.0, 0.0)
danceability = st.sidebar.slider(
    'Danceability',
    0.0, 1.0, 0.0)
energy = st.sidebar.slider(
    'Energy',
    0.0, 1.0, 0.0)
instrumentalness = st.sidebar.slider(
    'Instrumentalness',
    0.0, 1.0, 0.0)
valence = st.sidebar.slider(
    'Valence',
    0.0, 1.0, 0.0)
tempo = st.sidebar.slider(
    'Tempo',
    0.0, 244.0, 0.0)

def ms_to_mins (ms):
    mins = (ms/1000)/60
    secs = (ms/1000)%60
    res = str(round(mins, 2)) + " min " + str(round(secs,)) + " s"
    return res

def n_neighbors_uri_audio(genre, start_year, end_year, test_feat):
    genre = genre.lower()
    genre_data = exploded_track_df[(exploded_track_df["genres"]==genre) & (exploded_track_df["release_year"]>=start_year) & (exploded_track_df["release_year"]<=end_year)]
    genre_data = genre_data.sort_values(by='popularity', ascending=False)[:500]
    neigh = NearestNeighbors()
    neigh.fit(genre_data[audio_feats].to_numpy())
    n_neighbors = neigh.kneighbors([test_feat], n_neighbors=len(genre_data), return_distance=False)[0]
    uris = genre_data.iloc[n_neighbors]["uri"].tolist()
    audios = genre_data.iloc[n_neighbors][audio_feats].to_numpy()
    lyrics = genre_data.iloc[n_neighbors]["lyrics"].tolist()
    release_date = genre_data.iloc[n_neighbors] ['release_date'].tolist()
    artists_name = genre_data.iloc[n_neighbors] ['artists_name'].tolist()
    popularity = genre_data.iloc[n_neighbors] ['popularity'].tolist()
    durationms = genre_data.iloc[n_neighbors]['duration_ms'].tolist()
    playlist = genre_data.iloc[n_neighbors]['playlist'].tolist()
    return uris, audios, lyrics, release_date, artists_name, popularity, durationms, playlist

def most_similar(test_feat):
    genre_data = exploded_track_df.copy()
    genre_data = genre_data.sort_values(by='popularity', ascending=False)[:500]
    neigh = NearestNeighbors()
    neigh.fit(genre_data[audio_feats].to_numpy())
    n_neighbors = neigh.kneighbors([test_feat], n_neighbors=50, return_distance=False)[0]
    names = genre_data.iloc[n_neighbors]["name"].tolist()
    artists = genre_data.iloc[n_neighbors]["artists_name"].tolist()
    uniquesongs = []
    uniquesongartists = []
    index = 0
    for name in names:
        if name not in uniquesongs:
            uniquesongs.append(name)
            uniquesongartists.append(artists[index])
        index += 1
    num_list = random.sample(range(0,10), 3)
    songs = []
    for i in num_list:
        songs.append(uniquesongs[i] + " by " + uniquesongartists[i])
    return songs

def same_artist (artist):
    genres_data = exploded_track_df.copy()
    songs = genres_data[genres_data['artists_name']==artist]
    songs = songs.sort_values(by="popularity", ascending=False)
    return set(songs['name'])

def same_playlist (playlist):
    genres_data = exploded_track_df.copy()
    songs = genres_data[genres_data['playlist']==playlist]
    songs = songs.sort_values(by="popularity", ascending=False)
    return set(songs['name'])

tracks_per_page = 6
test_feat = [acousticness, danceability, energy, instrumentalness, valence, tempo]
uris, audios, lyrics, date, name, popularity, durationms, playlist = n_neighbors_uri_audio(genre, start_year, end_year, test_feat)
duration = []
for d in durationms:
    duration.append(ms_to_mins(d))

tracks = []
for uri in uris:
    track = """<iframe src="https://open.spotify.com/embed/track/{}" width="260" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""".format(uri)
    tracks.append(track)

if 'previous_inputs' not in st.session_state:
    st.session_state['previous_inputs'] = [genre, start_year, end_year] + test_feat

current_inputs = [genre, start_year, end_year] + test_feat
if current_inputs != st.session_state['previous_inputs']:
    if 'start_track_i' in st.session_state:
        st.session_state['start_track_i'] = 0
    st.session_state['previous_inputs'] = current_inputs

if 'start_track_i' not in st.session_state:
    st.session_state['start_track_i'] = 0

with st.container():
    col1, col2, col3 = st.columns([2,1,2])
    if st.button("Recommend More Songs"):
        if st.session_state['start_track_i'] < len(tracks):
            st.session_state['start_track_i'] += tracks_per_page

    current_tracks = tracks[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    current_audios = audios[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    current_lyrics = lyrics[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    current_date = date[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    current_name = name[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    current_popularity = popularity[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    current_duration = duration[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    current_playlist = playlist[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]

    if st.session_state['start_track_i'] < len(tracks):
        for i, (track, audio, lyrics, date, name, popularity, duration, playlist) in enumerate(zip(current_tracks, current_audios, current_lyrics, current_date, current_name, current_popularity, current_duration, current_playlist)):
            if i%2==0:
                with col1:
                    components.html(
                        track,
                        height=400,
                    )
                    with st.expander("Visualise Audio Features"):
                        df = pd.DataFrame(dict(
                        value=audio[:5],
                        metric=audio_feats[:5]))
                        fig = px.line_polar(df, r='value', theta='metric', line_close=True)
                        fig.update_layout(height=350, width=350)
                        st.plotly_chart(fig)
                    with st.expander("Tell Me More About The Song"):
                        st.write("Release Date : " + date)
                        st.write("Artist Name : " + name)
                        st.write("Ranked Popularity on Spotify : " + str(popularity))
                        st.write("Duration : " + duration)
                    with st.expander("Suggest Similar"):
                        st.write("If you're looking for songs with similar musicality,")
                        songs = most_similar(audio)
                        for song in songs:
                            st.write("  -   " + song)
                        st.write("")
                        st.write("Here are some other popular songs by " + name +":")
                        artist_index = 0
                        for song in same_artist(name):
                            if artist_index == 3:
                                break
                            st.write("  -   " + song)
                            artist_index = artist_index + 1
                        st.write("")
                        st.write("One Spotify playlist this song has been saved in is: " + playlist)
                        st.write("")
                        st.write("Check out other popular songs in this playlist: ")
                        song_index = 0
                        for song in same_playlist(playlist):
                            if song_index == 3:
                                break
                            st.write("  -   " + song)
                            song_index = song_index + 1
                        st.write("")
                    with st.expander("View Song Lyrics"):
                        st.write(lyrics)  
            else:
                with col3:
                    components.html(
                        track,
                        height=400,
                    )
                    with st.expander("Visualise Audio Features"):
                        df = pd.DataFrame(dict(
                        value=audio[:5],
                        metric=audio_feats[:5]))
                        fig = px.line_polar(df, r='value', theta='metric', line_close=True)
                        fig.update_layout(height=350, width=350)
                        st.plotly_chart(fig)
                    with st.expander("Tell Me More About The Song"):
                        st.write("Release Date : " + date)
                        st.write("Artist Name : " + name)
                        st.write("Ranked Popularity on Spotify : " + str(popularity))
                        st.write("Duration : " + duration)
                    with st.expander("Suggest Similar"):
                        st.write("If you're looking for songs with similar musicality,")
                        songs = most_similar(audio)
                        for song in songs:
                            st.write("  -   " + song)
                        st.write("")
                        st.write("Here are some other popular songs by " + name + ":")
                        artist_index = 0
                        for song in same_artist(name):
                            if artist_index == 3:
                                break
                            st.write("  -   " + song)
                            artist_index = artist_index + 1
                        st.write("")
                        st.write("One Spotify playlist this song has been saved in is: " + playlist)
                        st.write("")
                        st.write("Check out other popular songs in this playlist: ")
                        song_index = 0
                        for song in same_playlist(playlist):
                            if song_index == 3:
                                break
                            st.write("  -   " + song)
                            song_index = song_index + 1
                        st.write("")
                    with st.expander("View Song Lyrics"):
                        st.write(lyrics)  

    else:
        st.write("No songs left to recommend")