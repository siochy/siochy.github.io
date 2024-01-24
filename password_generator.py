# generating safe password with 8-16 symbols
# including capital and lower letters, digits, other symbols
# and not giving same password as before

import random
import time


def generic_password(size):
    # take size of list, generate symbols for every index
    # and return list of random symbols that allowed in typical passwords
    # in utf-8 from 33 to 126
    # then turn list into string

    list_of_syms = list()
    for i in range(size):
        rnd_sym = chr(random.randint(33, 126))
        list_of_syms.append(rnd_sym)
    password_string = ''
    return password_string.join(list_of_syms)


def check_conditions(generated_password):
    # take generated password and check for conditions
    # capital letters, lower letters, digits, other symbols

    if not generated_password.isalnum() \
            and not generated_password.islower() \
            and not generated_password.isupper() \
            and generated_password.lower().islower():
        return True


def check_previous(generated_password):
    # check existing file with previous passwords
    # if it doesn't then create and write new password
    # if it does then check if new password is created in past

    try:
        with open('passwords', 'r') as file:
            prev_pass = list()
            for line in file:
                prev_pass.append(line.rstrip('\n'))
    except FileNotFoundError:
        with open('passwords', 'w') as file:
            file.write(f'{generated_password}\n')
        return True
    else:
        if generated_password not in prev_pass:
            with open('passwords', 'a') as file:
                file.write(f'{generated_password}\n')
                return True


def mixer():
    # mix generated passwords and rewrite to file

    prev_pass_list = list()
    with open('passwords', 'r') as file:
        for line in file:
            prev_pass_list.append(line)
    random.shuffle(prev_pass_list)
    with open('passwords', 'w') as file:
        for password in prev_pass_list:
            file.write(password)


def create_password():
    # create safe password size 8-16 and check if it's created in past

    while True:
        len_of_pass = random.randint(8, 16)
        password = generic_password(len_of_pass)
        checker_cond = check_conditions(password)
        if checker_cond:
            checker_prev = check_previous(password)
            if checker_prev:
                print(password)
                mixer()
                another_pass = input('Another one?\ny/n\n')
                if another_pass.lower() != 'y':
                    break


if __name__ == '__main__':
    create_password()
