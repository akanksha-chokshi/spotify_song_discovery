import pandas as pd

directory = "SpotGenTrack/Data Sources/"

albums = pd.read_csv(directory + "spotify_albums.csv")
artists = pd.read_csv(directory + "spotify_artists.csv")
tracks = pd.read_csv(directory + "spotify_tracks.csv")

# renaming columns and setting indexes
album = albums.rename(columns={'id':"album_id"}).set_index('album_id')
artist = artists.rename(columns={'id':"artists_id",'name':"artists_name"}).set_index('artists_id')
track = tracks.set_index('album_id').join(album['release_date'], on='album_id' )

# dropping square brackets and quotes
track.artists_id = track.artists_id.apply(lambda x: x[2:-2])

track = track.set_index('artists_id').join(artist[['artists_name','genres']], on='artists_id' )
track.reset_index(drop=False, inplace=True)

# converting to datetime
track['release_year'] = pd.to_datetime(track.release_date).dt.year

# dropping unnecessary columns
track.drop(columns = ['Unnamed: 0','country','track_name_prev','track_number','type', 'analysis_url', 'available_markets'], inplace = True)

# keeping only tracks after 1990
df = track[track.release_year >= 1990]

# listing which genres we are focusing on
genres_to_include = ['dance pop', 'electronic', 'electropop', 'hip hop', 'jazz', 'k-pop', 'latin', 'pop', 'pop rap', 'r&b', 'rock']

# removing the commas and quotes
df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])

# exploding (expanding) each row by the number of genres it has that are in the list of genres we chose
df_exploded = df.explode("genres")[df.explode("genres")["genres"].isin(genres_to_include)]

# korean pop and k-pop are the same genre
df_exploded.loc[df_exploded["genres"]=="korean pop", "genres"] = "k-pop"

# finding the list of unique genres
df_exploded_indices = list(df_exploded.index.unique())

# filtering df by those songs with the genres we want
filtered_track_df = df[df.index.isin(df_exploded_indices)]
filtered_track_df = filtered_track_df.reset_index(drop=True)

# removing "spotify:track:" from the uri
filtered_track_df["uri"] = filtered_track_df["uri"].str.replace("spotify:track:", "")

# converting to csv
filtered_track_df.to_csv("songs.csv", index=False)
