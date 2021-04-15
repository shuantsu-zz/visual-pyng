import time, os, json

from envelopes import Envelope

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

#====================================================

config = json.loads(open('config.json', 'r', encoding='utf8').read())

FREQUENCY_MINUTES = config['frequencyMinutes'] # Time, in minutes, that take to rerun the job
PAUSE_SECONDS = config['pauseSeconds'] # Time, in seconds that takes to wait for the page to load
PASSWORD = config['password'] # Your gmail app password
EMAIL_FROM = config['emailFrom'] # "From" e-mail address
EMAIL_TO = config['emailTo'] # "To" e-mail adress
SCREEN_HEIGHT = config['screenHeight'] # Screenshot height
SCREEN_WIDTH = config['screenWidth']  # Screenshot width
SITES = config['sites'] # Format: [url, description]

#====================================================

def send_mail(filename, complete_filename, message):
    
    envelope = Envelope(
        from_addr=(EMAIL_FROM, EMAIL_FROM),
        to_addr=(EMAIL_TO, EMAIL_TO),
        subject=filename,
        text_body=message
    )
    envelope.add_attachment(complete_filename)

    envelope.send('smtp.googlemail.com', login=EMAIL_TO,
                  password=PASSWORD, tls=True)

#====================================================

def main(url, filename):

    options = Options()
    options.headless = True
    
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'    
    options.add_argument('user-agent={0}'.format(user_agent))

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

    print(f'Accessing: {url} ({filename})')

    driver.get(url)
    
    driver.set_window_size(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    time.sleep(PAUSE_SECONDS)
    
    complete_filename = filename + '.png'
    
    content = ''
    
    if os.path.isfile(complete_filename):
        content = open(complete_filename, 'rb').read()
    
    driver.save_screenshot(complete_filename)
    
    if content != open(complete_filename, 'rb').read():
        if content == '':
            message = 'First access to (%s) ... stay tuned for updates ;-)' % url
        else:
            message = '%s - %s - UPDATED!' % (url, filename)
        print(message)
        print('SENDING EMAIL...')
        send_mail(filename, complete_filename, message)
        print('EMAIL SENT!')
    else:
        print('No changes :(')

    driver.close()

#====================================================

while 1:
    try:
        for url, filename in SITES:
            main(url, filename)
        print('trying again in:', FREQUENCY_MINUTES, 'minutes. Now: %s' % time.strftime('%c'))
        time.sleep(FREQUENCY_MINUTES * 60)
    except Exception as e:
        print(e)
        print('An error occurred... trying again in 30 seconds')
        time.sleep(30)