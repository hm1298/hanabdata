"""Script to update user information"""

from tools.update import update_user

if __name__ == '__main__':
    username = input('enter username to update: ')
    update_user(username)
