# Social Media API 

The API allows users to create profiles, follow other users, 
create and retrieve posts, manage likes and comments, 
and perform basic social media actions

### Installing / Getting started:

Python 3 must be installed

```shell
git clone https://github.com/arsenmakovei/social-media-api.git
cd restaurant_kitchen_service
python3 -m venv venv
source venv/bin/activate (on macOS)
venv\Scripts\activate (on Windows)
pip install -r requirements.txt 
python manage.py migrate
python manage.py runserver # Starts Django Server
```

### Features:

* JWT authenticated
* Admin panel /admin/
* Documentation is located at api/doc/swagger/
* User profile creation and updating with profile picture, bio, and other details
* User profile retrieval and searching for users by username or other criteria
* Follow/unfollow functionality with the ability to view lists of followed and following users
* Post creation with text content and optional media attachment
* Users сan like/unlike posts, view the list of posts they have liked
* Users can add comments to posts and view comments on posts.