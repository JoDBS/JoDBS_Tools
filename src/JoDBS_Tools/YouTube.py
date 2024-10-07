import requests

class YouTube:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://www.googleapis.com/youtube/v3'

    def get_latest_video(self, channel_id):
        url = f'{self.base_url}/search'
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'maxResults': 1,
            'order': 'date',
            'type': 'video',
            'key': self.api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            video = data['items'][0]
            video_id = video['id']['videoId']
            title = video['snippet']['title']
            description = video['snippet']['description']
            thumbnails = video['snippet']['thumbnails']
            return {
                'video_id': video_id,
                'title': title,
                'description': description
            }
        else:
            return None