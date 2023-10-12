from LoginSecurity import LoginSecurity, clear

def main():
    login_security = LoginSecurity()

    while True:
        clear()
        print('Choose any of the following options: ')

        if not login_security.is_logged_in():
            print('1. Register\n2. Login\n3. Exit\n')
            choice = input('>> ')

            match(choice):
                case '1':
                    login_security.register()

                case '2':
                    login_security.login()

                case '3':
                    break

                case _:
                    pass

        else:
            print('1. Change username\n2. Change password\n3. Logout\n4. Delete Account\n5. Exit\n')
            choice = input('>> ')

            match(choice):
                case '1':
                    login_security.change_username()

                case '2':
                    login_security.change_password()

                case '3':
                    login_security.logout()

                case '4':
                    login_security.delete_account()

                case '5':
                    break

                case _:
                    pass

if __name__ == '__main__':
    main()