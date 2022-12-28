from secretConfig import username, password


def ao3Login():
    loginUrl = 'https://archiveofourown.org/users/login'
    page = session.get(loginUrl)
    pagelines = page.text.split("\n")
    for index, line in enumerate(pagelines):
        if '<meta name="csrf-param" content="authenticity_token"/>' in line:
            token = find_between(pagelines[index + 1], 'content="', '"/>')
            print('Found AO3 login token', token)

    login_data = {'user[login]': username, 'user[password]': password,
                  'user[remember_me]': 1, 'authenticity_token': token}
    page = session.post(loginUrl, login_data)
    if '<div class="flash notice">Successfully logged in.</div>' in page.text:
        loggedIn = True
    if loggedIn:
        print('Logged into AO3 successfully.')
        print('Starting discord bot...')
        # startDiscordBot()
        parseStory()
    else:
        print('ERROR logging into AO3')

# ao3Login()
