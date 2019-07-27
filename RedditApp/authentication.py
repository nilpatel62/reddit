from imgurpython import ImgurClient

client_id = '95eb3736be8e9a5'
client_secret = '3d46054a66c1f606c8fb1b8f9eeb52630807b2bc'

client = ImgurClient(client_id, client_secret)
credentials = client.authorize('66d99a11af', 'pin')
print(credentials['access_token'])
print(credentials['refresh_token'])
client.set_user_auth(credentials['access_token'], credentials['refresh_token'])

