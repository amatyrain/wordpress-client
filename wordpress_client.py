import base64
import requests


class WordPressClient:
    def __init__(self, base_url, username, app_password):
        self.base_url = f'{base_url}/?rest_route='
        # self.base_url = f'{base_url}/wp-json'

        credentials = username + ':' + app_password
        token = base64.b64encode(credentials.encode())
        self.headers = {
            'Authorization': 'Basic ' + token.decode('utf-8')
        }

        self.image_save_path = "/tmp/image.jpeg"
        self.per_page_limit = 100

    def _request(self, method, endpoint, data=None, params=None, files=None):
        url = f'{self.base_url}/{endpoint}'
        print(f'url: {url}')
        print(f'method: {method}')
        print(f'data: {data}')

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                files=files,
            )
        except Exception as e:
            raise Exception(e)

        if response.status_code >= 400:
            print(response.status_code)
            print(response.text)
            raise Exception(response.json())

        return response

    def get_posts(self):
        url = f"{self.base_url}/wp/v2/posts"
        response = requests.get(url)
        return response.json()

    def get_post(self, post_id):
        url = f"{self.base_url}/wp/v2/posts/{post_id}"
        response = requests.get(url)
        return response.json()

    def create_post(
        self,
        title,
        content,
        categories: list[str] | None = [],
        tags: list[str] | None = [],
        featured_media: int | None = None,
        status="publish"
    ) -> str:
        endpoint = "wp/v2/posts"
        method = 'POST'
        data = {
            "title": title,
            "content": content,
            "status": status,
        }

        if len(categories) > 0:
            data['categories'] = categories
        if len(tags) > 0:
            data['tags'] = tags
        if featured_media is not None:
            data['featured_media'] = featured_media

        response = self._request(method, endpoint, data=data)

        return response.json()['id']

    def update_post(self, post_id, data):
        endpoint = f"wp/v2/posts/{post_id}"
        method = 'DELETE'
        response = self._request(method, endpoint, data=data)
        return response.json()

    def delete_post(self, post_id):
        endpoint = f"wp/v2/posts/{post_id}"
        method = 'DELETE'

        response = self._request(method, endpoint)
        return response.json()

    def create_media(self, image_url: str) -> int:
        """_summary_

        Args:
            image_url: 画像URL

        Returns:
            int: メディアID
        """
        response = requests.get(image_url)
        with open(self.image_save_path, 'wb') as f:
            f.write(response.content)

        endpoint = "wp/v2/media"
        files = {'file': open(self.image_save_path, 'rb')}
        method = 'POST'
        response = self._request(method, endpoint, files=files)

        print(response.json())

        return response.json()['id']

    def delete_media(self, media_id):
        endpoint = f"wp/v2/media/{media_id}"
        method = 'DELETE'
        data = {
            "force": True
        }

        response = self._request(method, endpoint, data=data)
        return response.json()

    def get_categories(self):
        endpoint = "wp/v2/categories"
        method = 'GET'
        page = 1
        categories = []

        is_end = False
        while not is_end:
            data = {
                'page': page,
                'per_page': self.per_page_limit,
            }
            response = self._request(method, endpoint, data=data)
            response_json = response.json()

            if len(response_json) == 0:
                is_end = True
                break

            for category in response.json():
                categories.append(category)

            page += 1

        return categories

    def create_category(self, name):
        endpoint = "wp/v2/categories"
        method = 'POST'
        data = {
            "name": name,
        }

        response = self._request(method, endpoint, data=data)
        return response.json()

    def get_tags(self) -> list:
        endpoint = "wp/v2/tags"
        method = 'GET'
        page = 1
        tags = []

        is_end = False
        while not is_end:
            data = {
                'page': page,
                'per_page': self.per_page_limit,
            }
            response = self._request(method, endpoint, data=data)
            response_json = response.json()
            # print(response_json)

            if len(response_json) == 0:
                is_end = True
                break

            for tag in response.json():
                tags.append(tag)

            page += 1

        return tags

    def create_tag(self, name):
        endpoint = "wp/v2/tags"
        method = 'POST'
        data = {
            "name": name,
        }

        response = self._request(method, endpoint, data=data)
        return response.json()
