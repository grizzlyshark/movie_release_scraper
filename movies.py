import requests
import bs4
import csv
import os
import smtplib
import configs
from email.message import EmailMessage


class Movie(object):
    movieList = []

    def __init__(self, imdbID, url, title, genre, plot, score, image):
        self.imdbID = imdbID
        self.url = url
        self.title = title
        self.genre = genre
        self.plot = plot
        self.score = score
        self.image = image
        Movie.movieList.append(self)


def makeSoup(source):
    res = requests.get(source)
    res.raise_for_status()
    return bs4.BeautifulSoup(res.text, 'lxml')


def buildTable():
    # opens csv to append new movies into after table entry is build
    with open('pastReleases.csv', 'a') as writer:
        newReleaseWriter = csv.writer(writer)
        # opens csv to read existing entries
        with open('pastReleases.csv', 'r') as reader:
            pastReleaseReader = csv.reader(reader)
            pastReleases = []
            for row in pastReleaseReader:
                pastReleases.append(row)
            # builds table by checking if movie has already been scraped
            table = ''
            for movie in Movie.movieList:
                if ([movie.title]) not in pastReleases:
                    tableEntry = f"""\
<table class="table" style="width: 100%">
    <tr>
        <td rowspan="4" style="width: 175px"><a href="{movie.url}">
        <img height="209" src="{movie.image}" width="140"></a>&nbsp;</td>
        <td class="title"><a href="{movie.url}"><strong>{movie.title}</strong></a></td>
    </tr>
    <tr>
        <td>{movie.genre}</td>
    </tr>
    <tr>
        <td>IMDB Score: {movie.score}</td>
    </tr>
    <tr>
        <td>{movie.plot}</td>
    </tr>
</table>

                    """
                    table += tableEntry
                    newReleaseWriter.writerow([movie.title])
            return table


def scrape():
    # scrapes info and creates Movie object for each movie
    for movie in imdbSoup.find_all('div', class_="lister-item mode-detail"):
        imdbID = movie.div['data-tconst']  # access tags like dicts
        url = f'https://www.imdb.com/title/{imdbID}'
        title = movie.h3.a.text.strip()
        genre = movie.find('span', class_="genre").text.strip()
        plot = movie.find('p', class_="").text.strip()
        score = movie.find(
            'span', class_="ipl-rating-star__rating").text.strip()
        image = movie.find('img', class_="loadlate")['loadlate']
        # create a movie object for each movie, accessible in Movie.movieList
        Movie(imdbID, url, title, genre, plot, score, image)
        # print(title)


def sendEmail(movies):
    msg = EmailMessage()
    msg['Subject'] = f"Recent Movie Releases"
    msg['From'] = configs.sender
    msg['To'] = configs.recipients
    msg.add_alternative(f"""\
<!DOCTYPE html>
<html>
    <body>
<head>
<meta content="en-us" http-equiv="Content-Language">
<style type="text/css">
.table {{
    border-style: solid;
    border-width: 1px;
}}
.title {{
    font-size: large;
}}
</style>
</head>


        <h1 style="color:SlateGray;">Recent Releases:</h1>
        {moviesTable}
    </body>
</html>
""", subtype='html')

    if moviesTable:  # if movie table is empty, email does not send
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(configs.sender, configs.password)
            smtp.send_message(msg)


# main
# makes beautiful soup using IMDB New Releases page
imdbSoup = makeSoup(
    'https://www.imdb.com/list/ls016522954/?ref_=ttls_ref_typ&sort=release_date,desc&st_dt=&mode=detail&page=1&title_type=movie')

scrape()
moviesTable = buildTable()
sendEmail(moviesTable)
