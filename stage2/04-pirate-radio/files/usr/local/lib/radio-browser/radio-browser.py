from flask import Flask, request
from flask_cors import CORS, cross_origin
from mpd import MPDClient
from pyradios import RadioBrowser

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

rb = RadioBrowser()


@app.route("/add_radio")
@cross_origin()
def add_stream():
    stream_name = request.args.get("name")
    stream_details = rb.search(name=stream_name)
    try:
        stream_uri = stream_details[0].get("url")
        mpd_client = MPDClient()
        mpd_client.timeout = 10
        mpd_client.idletimeout = None
        mpd_client.connect("localhost", 6600)
        mpd_client.add(stream_uri)
        mpd_client.close()
        mpd_client.disconnect()
        return ""
    except IndexError:
        return "No stream found"
