from pymongo import MongoClient

WTF_CSRF_ENABLED = True
SECRET_KEY = 'Put your secret key here'
DB_NAME = 'bookshelf'

DATABASE = MongoClient('localhost',27017)[DB_NAME]
BOOKIMPORT_COLLECTION = DATABASE.bookimports
LIBRARY_COLLECTION = DATABASE.books
POSTS_COLLECTION = DATABASE.posts
USERS_COLLECTION = DATABASE.users
SETTINGS_COLLECTION = DATABASE.settings

DEBUG = True