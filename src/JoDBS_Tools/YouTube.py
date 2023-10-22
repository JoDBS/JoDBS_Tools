import json, requests


def v3GetLatestVideo(ChannelId, API_Key):
    ChannelId = ChannelId or None
    API_Key = API_Key or None


    API_URL = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={}&maxResults=1&order=date&type=video&key={}".format(ChannelId, API_Key)


    def get_video():
        request = json.loads(requests.get(API_URL).text)
        videoId = request["items"][0]["id"]["videoId"]
        

        video_url = "https://youtube.com/watch/" + videoId
        return video_url
    

    try:
        return get_video()
    
    except Exception as e:
        print("Error has occurred in YouTube.py/v3GetVideo(), could not complete response.")
        print("Exception:")
        print(e)
        return False