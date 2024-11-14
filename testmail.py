# NEED APPROVAL FROM ADMIN
from O365 import Account
from O365.utils import FileSystemTokenBackend
from config2 import CONFIG

# Set up token backend for persistent authentication
token_backend = FileSystemTokenBackend(token_path='.')

# Configure credentials
credentials = (CONFIG['CLIENT_ID'], CONFIG['CLIENT_SECRET'])

# Initialize account with token backend
account = Account(credentials, token_backend=token_backend)

# Authenticate with required scopes
if not account.is_authenticated:
    account.authenticate(scopes=['basic', 'message_all'])

# Create and send message
m = account.new_message()
m.to.add('mukesh@adarone.com')
m.subject = 'Testing!'
m.body = "George Best quote: I've stopped drinking, but only while I'm asleep."
m.send()