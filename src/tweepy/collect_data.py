import tweepy
import pickle
from tweepy import OAuthHandler
from credentials import *
import time

output_path = './data_v2/'

def save_data(filename, data):
    output = open(filename, 'wb')
    pickle.dump(data, output)
    output.close()


auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

data = {}
user_queue = set()
user_queue.add(api.me().id)
node_count = 1
processed_account_count = 0

start = time.time()
protected_accounts = 0
max_node_count = 10000
while True:
    print('Accounts processed: {0}, Queue length: {1}, Protected account count: {2}'.format(processed_account_count,
                                                                                            len(user_queue),
                                                                                            protected_accounts))
    print('Elapsed time: {0}'.format(time.time() - start))
    try:
        user_id = user_queue.pop()
    except KeyError:
        print("Completed.")
        break
    try:
        following = api.friends_ids(user_id)
        followers = api.followers_ids(user_id)
    except tweepy.error.TweepError:
        print('Protected account, skipping.')
        protected_accounts += 1
        continue

    common_users = set(followers) & set(following)
    data[user_id] = common_users
    processed_account_count += 1

    if len(user_queue) + node_count < max_node_count:
        if node_count + len(common_users) > max_node_count:
            for i in range(node_count + len(common_users) - max_node_count):
                common_users.pop()
        user_queue.update(common_users)
        node_count += len(common_users)

    if processed_account_count % 5 == 0:
        save_data('{0}{1}.pkl'.format(output_path, processed_account_count), data)

end = time.time()
save_data('{0}{1}.pkl'.format(output_path, processed_account_count), data)
print('Elapsed time: {0}'.format(end - start))
