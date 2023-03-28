"""Script to update user information"""

from datetime import datetime
from tools.update import update_user

if __name__ == '__main__':
    username = input('enter username to update: ')
    start = datetime.now()
    update_user(username)
    end = datetime.now()
    elapsed = (end - start).total_seconds()
    print(f"To update, it took: {elapsed:.04f} seconds")
