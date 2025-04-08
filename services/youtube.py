import requests


class YouTubeService:
    def __init__(self, api_key):

        self.api_key = api_key
        self.base_url = 'https://www.googleapis.com/youtube/v3'

    def get_video_title(self, video_id):

        url = f"{self.base_url}/videos"
        params = {
            'part': 'snippet',
            'id': video_id,
            'key': self.api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            items = data.get('items', [])
            if not items:
                return f"No video found for ID: {video_id}"

            title = items[0]['snippet']['title']
            return title

        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"
