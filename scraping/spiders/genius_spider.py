import re

import dateparser
import scrapy
from bs4 import BeautifulSoup

from lyric_pro_etls.models import Song;
from lyric_pro_etls.mongo import insert_song, get_song_by_slug


class GeniusSpider(scrapy.Spider):
    name = "genius"

    def start_requests(self):
        urls = [
            "https://genius.com/Radiohead-creep-lyrics",
            "https://genius.com/King-gizzard-and-the-lizard-wizard-robot-stop-lyrics",
            "https://genius.com/The-beatles-here-comes-the-sun-lyrics",
            "https://genius.com/Radiohead-fake-plastic-trees-lyrics",
            "https://genius.com/Dogs-in-a-pile-fenway-lyrics",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # get the url slug
        slug = response.url.split("/")[-1]

        if get_song_by_slug(slug) is not None:
            return

        # get the song title
        selectors = response.css("h1").css("span")
        titles = [
            s.css("::text").get() 
            for s in selectors 
            if s.css("::attr(class)").get(default="").startswith("SongHeader-")
        ]
        title = titles[0] if len(titles) == 1 else None

        # get the artist
        artist = response.css("div[class^=HeaderArtistAndTracklist-]:first-of-type").css("a[class^=StyledLink-]::text").get()

        # get the song lyrics
        lyrics = ""
        selectors = response.css("div[class^=Lyrics-]")
        for selector in selectors:
            soup = BeautifulSoup(selector.get(), features="lxml")
            lyrics += soup.get_text()
        
        # remove double quotes
        lyrics = lyrics.replace("\"", "")
        # insert newline between lower-case letter followed by upper-case letter 
        lyrics = re.sub(r'([a-z])([A-Z])', lambda m: m.group(1) + "\n" + m.group(2), lyrics)
        # insert newline between closing brace and letter
        lyrics = re.sub(r'([\]\)])([a-zA-Z])', lambda m: m.group(1) + "\n" + m.group(2), lyrics)
        # insert newline bewteen letter and opening brace
        lyrics = re.sub(r'([a-zA-Z])([\[\(])', lambda m: m.group(1) + "\n" + m.group(2), lyrics)


        # get the song release date
        release_date = response.css("div[class^=MetadataStats-]").css("span[class^=LabelWithIcon-]:first-of-type::text").get()
        release_date = dateparser.parse(release_date)

        # TODO: get the song about section

        song = Song(
            slug=slug,
            title=title,
            artist=artist,
            lyrics=lyrics,
            release_date=release_date,
        )

        insert_song(song)