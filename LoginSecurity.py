from getpass import getpass
import json
import os
from platform import system as syst
from sys import stderr, stdout
from time import sleep
from random import randint
from datetime import datetime
from termcolor import colored, cprint

#! Python 3.10 and later supported ONLY

"""
    TODOS:

1. Email-Based Registration (includes OTP)
2. "Forgot Password" system (includes OTP)
3. Improve Logging System
4. Password Strength Checker
"""

# function to reduce syntax in the actual class
def sleeping_print(text: str, file = stdout, duration: int = 2):
    print(text, file=file)
    sleep(duration)

# function to clear the terminal
def clear():
    # if the os is Windows
    if syst() == 'Windows':
        os.system('cls')
    
    else:
        os.system('clear')

# class for secure account system
class LoginSecurity:
    # constructor
    def __init__(
            self, *, 
            file_folder='login_files', 
            file_name='accounts.json', 
            logs_file='logs.txt',
            clear_terminal=True
        ):
        # stores whether the user is currently logged in or not
        self.__logged_in = False

        # stores the username of the currently logged used
        self.__current_user = ''

        # stores all user accounts
        # key -> string (username), value -> string (password)
        self.__accounts = {}

        # amount of seconds of timeout if the user gets
        # the password wrong in timeout_tries amount
        self.timeout_duration = 30
        self.timeout_tries = 3

        # configures whether the terminal will be cleared beforehand or not
        self.clear_terminal = clear_terminal

        # the key which is required for encryption and decryption of passwords

        # this specific range of keys is selected because it facilitates the encryption
        # as it allows only 4-digit numbers to generate when used in encryption

        # random value used to facilitate file-to-file encryption, i.e. each file has its own key
        self.__key = randint(32, 79)

        # storing the file folder and the file name where the accounts will be saved
        self.file_folder = file_folder
        self.file_name = file_name
        self.file_loc = os.path.join(file_folder, file_name)
        self.logs = os.path.join(file_folder, logs_file) # logs file

        # colored messages to be printed in the console
        self.error = colored('ERROR:  ', 'red')
        self.heading_color = 'green'
        self.program = colored('PROGRAM:  ', 'blue')

        # if the file folder is not created, create one
        if not os.path.exists(self.file_folder):
            os.mkdir(self.file_folder)

        # if the file itself is not created, create one
        if not os.path.exists(self.file_loc):
            with open(self.file_loc, 'w') as file: 
                # stores the encryption key which is generated for this file
                json.dump({"key": chr(self.__key)}, file)

        # if the logs files does not exists
        if not os.path.exists(self.logs):
            with open(self.logs, 'w') as file:
                print(f'[{datetime.now()}]\nCreated Log File.\n', file=file)

        # loading the file into the accounts dict
        self.__load_file()

        # retrieving the key from the file
        self.__key = ord(self.__accounts['key'])

    # private function to update the logs
    def __save_logs(self, message):
        # opening the logs file in append mode
        with open(self.logs, 'a') as file:
            print(f'[{datetime.now()}]\n{message}\n', file=file)
    
    # priavte function to load the file into the accounts dict
    def __load_file(self):
        # opening the file and updating the accounts dict
        with open(self.file_loc, 'r') as file:
            self.__accounts = json.load(file)

    # priavte function to update the file from the accounts dict
    def __save_file(self):
        # opening the file, clearing the entire file and dumping the dict into the file
        with open(self.file_loc, 'w') as file:
            file.truncate()
            json.dump(self.__accounts, file)
        
    # private function which returns the password of a given user
    def __get_password(self, name: str):
        return self.__accounts[name]
    
    # function which returns the currently logged user
    def get_current_user(self):
        return self.__current_user
    
    # function which returns whether the user is logged in
    def is_logged_in(self):
        return self.__logged_in
    
    # private function which encrypts the given password
    def __encrypt_password(self, password: str):
        encrypted = ''

        # iterating through the password
        for ch in password:
            # for each character, it is first converted to its ascii value, then
            # the ascii value is multiplied with the key and the result is added to the string
            # this is how this simple encryption works
            encrypted += str(ord(ch) * self.__key)

        return encrypted

    # private function which decrypts the encrypted password
    def __decrypt_password(self, password: str):
        # dividing the string into four-digit substrings in a list
        listed_text = [password[i : i + 4] for i in range(0, len(password), 4)]

        # every value in the list is divided by the key to obtain the original ascii values
        listed_text = [int(int(i) / self.__key) for i in listed_text]

        # each value is converted to its character form
        listed_text = [chr(i) for i in listed_text]

        # concatenating all of the values, resulting in the decypher
        return ''.join(listed_text)

    # private function to verify that if a user-entered password is appropriate or not
    def __verified_password(self, password):
        # if password is shorter than six characters
        if len(password) < 6:
            print(f'{self.error}Password cannot be lesser than 6 characters.', file=stderr)
            return False
        
        # if the password contains whitespaces
        if ' ' in password:
            print(f'{self.error}Detected whitespaces in password.', file=stderr)
            return False
        
        # iterating through the password
        for ch in password:
            # ascii value of the character
            ascii_value = ord(ch)

            # if the ascii value is not applicable to be a good password
            if ascii_value < 33 or ascii_value > 126:
                print(f'{self.error}{ch} is an invalid character.', file=stderr)
                return False
            
        # returns True if all the conditions are met
        return True

    # function to register accounts
    def register(self):
        # if the terminal is allows to clean
        if self.clear_terminal: clear()

        cprint('REGISTRATION PAGE\n', self.heading_color)
        name = password = ''

        # loop running until user provides valid response
        while True:
            # username input
            name = input('Enter your username: ')

            # if there is already an account with the given username or name is empty
            if name in self.__accounts or name == '':
                print(f'{self.error}This account already exists.', file=stderr)
                continue

            break
        
        # loop running until user provides valid response
        while True:
            # getting the password
            password = getpass('Enter your password: ')

            # if the password is not verified
            if not self.__verified_password(password):
                continue
            
            break

        # creating new account, logging in the user and updating the current user
        self.__accounts[name] = self.__encrypt_password(password)
        self.__current_user = name
        self.__logged_in = True

        # updating the file
        self.__save_file()

        # updating logs
        self.__save_logs(f'Account registered: {name}')

        sleeping_print(f'{self.program}Successfully registered your account.')

    # function to login to an existing account
    def login(self):
        # if the terminal is allows to clean
        if self.clear_terminal: clear()

        cprint('LOGIN PAGE\n', self.heading_color)

        name = password = ''

        # loop running until user provides valid response
        while True:
            # username input
            name = input('Enter your username: ')

            # if the name is empty or the name is the encryption key or the name is not logged in already
            if not name in self.__accounts or name == '' or name == 'key':
                print(f'{self.error}Account with specified name doesnot exist.', file=stderr)
                continue
            
            break

        # stores the account password
        acc_password = self.__get_password(name)

        # number of tries until user is timed out
        tries = self.timeout_tries

        # loop running until user provides valid response
        while True:
            # if the user runs out of tries
            if tries == 0:
                sleeping_print(
                    f'{self.program}You have been timed out for {self.timeout_duration} seconds.',
                    duration=self.timeout_duration
                )
                tries = self.timeout_tries
            
            # password input
            password = getpass('Enter your password: ')

            # if the input password is equal to the original account password
            if password == self.__decrypt_password(acc_password):
                self.__logged_in = True
                self.__current_user = name
                sleeping_print(f'{self.program}Successfully logged in.')

                # updating logs
                self.__save_logs(f'Account logged in: {name}')
                break

            # if wrong password is given
            print(f'{self.error}Incorrect Password.', file=stderr)
            tries -= 1

    # function to change the username of the currently logged user
    def change_username(self):
        # if the terminal is allows to clean
        if self.clear_terminal: clear()
        
        cprint('CHANGE USERNAME PAGE\n', self.heading_color)

        # if the user is not logged in
        if not self.is_logged_in():
            sleeping_print(f'{self.error}User is not logged in.', file=stderr)
            return
        
        old_password = new_username = ''

        # stores the account password
        acc_password = self.__get_password(self.__current_user)

        # number of tries until user is timed out
        tries = self.timeout_tries

        # loop running until user provides valid response
        while True:
            # if the user runs out of tries
            if tries == 0:
                sleeping_print(
                    f'{self.program}You have been timed out for {self.timeout_duration} seconds.',
                    duration=self.timeout_duration
                )
                tries = self.timeout_tries
            
            # old password as user input
            old_password = getpass('Enter your old password: ')

            # if the old password is given wrong
            if old_password != self.__decrypt_password(acc_password):
                print(f'{self.error}Wrong password entered.', file=stderr)
                tries -= 1
                continue

            break

        # loop running until user provides valid response
        while True:
            # new username input
            new_username = input('Enter your new username: ')

            # if no username is provided
            if new_username == '':
                print(f'{self.error}Invalid username provided.', file=stderr)
                continue

            # if the new username is already defined
            if new_username in self.__accounts.keys():
                print(f'{self.error}This username already exists.', file=stderr)
                continue
            
            break
        
        # updating logs
        self.__save_logs(f'Account changed name: {self.__current_user} ---> {new_username}')

        # setting the password for the new user, deleting the old user and changing the current user
        self.__accounts[new_username] = self.__get_password(self.__current_user)
        self.__accounts.pop(self.__current_user)
        self.__current_user = new_username

        # updating the file
        self.__save_file()

        sleeping_print(f'{self.program}Successfully changed your username.')

    # function to change password of the user's account
    def change_password(self):
        # if the terminal is allows to clean
        if self.clear_terminal: clear()
        
        cprint('CHANGE PASSWORD PAGE\n', self.heading_color)

        # if the user is not logged in
        if not self.is_logged_in():
            sleeping_print(f'{self.error}User is not logged in.', file=stderr)
            return

        old_password = new_password = ''

        # stores the account password
        acc_password = self.__get_password(self.__current_user)

        # number of tries until user is timed out
        tries = self.timeout_tries

        # loop running until user provides valid response
        while True:
            # if the user runs out of tries
            if tries == 0:
                sleeping_print(
                    f'{self.program}You have been timed out for {self.timeout_duration} seconds.',
                    duration=self.timeout_duration
                )
                tries = self.timeout_tries
            
            # old password as user input
            old_password = getpass('Enter your old password: ')

            # if the old password is given wrong
            if old_password != self.__decrypt_password(acc_password):
                print(f'{self.error}Wrong password entered.', file=stderr)
                tries -= 1
                continue
            
            break

        # loop running until user provides valid response
        while True:
            # getting the new password for the user
            new_password = getpass('Enter your new password: ')

            # if the new password is not verified
            if not self.__verified_password(new_password):
                continue

            break

        # storing the new password
        self.__accounts[self.__current_user] = self.__encrypt_password(new_password)

        # updating the file
        self.__save_file()

        # updating logs
        self.__save_logs(f'Account changed password: {self.__current_user}')

        sleeping_print(f'{self.program}Successfully changed your password.')

    # logging out of existing account
    def logout(self):
        # if the terminal is allows to clean
        if self.clear_terminal: clear()
        
        cprint('LOGOUT PAGE\n', self.heading_color)

        # if the user is not logged in
        if not self.is_logged_in():
            sleeping_print(f'{self.error}User is not logged in.', file=stderr)
            return

        # verifying if the user is sure about their decision
        surity = input('Are you sure you want to log out? (y/n): ') == 'y'

        # if the user is unsure
        if not surity:
            sleeping_print(f'{self.program}Aborting your choice.')
            return
        
        # updating logs
        self.__save_logs(f'Account logged out: {self.__current_user}')

        # logging out and changing the current_user to empty
        self.__logged_in = False
        self.__current_user = ''

        sleeping_print(f'{self.program}Successfully logged out of your account.')

    # function to delete user accounts
    def delete_account(self):
        # if the terminal is allows to clean
        if self.clear_terminal: clear()
        
        cprint('ACCOUNT DELETION PAGE\n', self.heading_color)

        # if the user is not logged in
        if not self.is_logged_in():
            sleeping_print(f'{self.error}User is not logged in.', file=stderr)
            return

        # retrieving the actual password of the user
        acc_password = self.__get_password(self.__current_user)

        # number of tries until user is timed out
        tries = self.timeout_tries

        # loop running until user provides valid response
        while True:
            # if the user runs out of choice
            if tries == 0:
                sleeping_print(
                    f'{self.program}You have been timed out for {self.timeout_duration} seconds.',
                    duration=self.timeout_duration
                )
                tries = self.timeout_tries

            # accepting user password
            password = getpass('Enter your password to verify your choice: ')

            # if input password is not the same as account password
            if not password == self.__decrypt_password(acc_password):
                print(f'{self.error}Wrong password enterted.', file=stderr)
                tries -= 1
                continue

            break
        
        # updating logs
        self.__save_logs(f'Account deleted: {self.__current_user}')

        # removing the account from the 'accounts' dict, and logging out the user
        self.__accounts.pop(self.__current_user)
        self.__logged_in = False
        self.__current_user = ''

        # updating the file
        self.__save_file()

        sleeping_print(f'{self.program}Successfully deleted your account.')
    

# this portion is only present for debugging
if __name__ == '__main__':
    log = LoginSecurity()
    log.register()
    log.login()
    log.change_username()
    log.change_password()
    log.logout()
    log.login()
    log.delete_account()
    log.login()