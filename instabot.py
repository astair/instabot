import os
import sys
import time
import yaml
import random
import logging
import argparse
from datetime import datetime
from instabot.api.InstagramAPI import InstagramAPI

# CONST
HERE = os.path.abspath(os.path.dirname(sys.argv[0]))
os.chdir(HERE)

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Hi, I'm Hugo These little Instabot!")

    parser.add_argument("COMMAND",
                        type=str,
                        choices=["like", "like_back", "follow", "unfollow"],
                        metavar="<COMMAND>",
                        help="A command for the Instabot.")

    parser.add_argument("--config", "-c",
                        dest="CONFIG",
                        type=str,
                        metavar="<CONFIG>",
                        default="config.yaml",
                        help="A config file with the search/comment options.")

    args = parser.parse_args()
    return args

def load_liked_pics(logging, likes_log_file="logs/likes.log"):
    try:
        with open(likes_log_file, "rt", encoding="utf8") as f:
            likes_log = f.readlines()
        likes_log = set([int(c.strip()) for c in likes_log])
    except FileNotFoundError as err:
        logging.info(f"No '{likes_log_file}' found, making a new one")
        likes_log = set()
    return likes_log

def read_follow_log(logging, follow_log_file="logs/follow.log"):
    try:
        with open(follow_log_file, "rt", encoding="utf8") as f:
            follow_log = f.readlines()
        for i in range(len(follow_log)):
            follow_log[i] = follow_log[i].strip().split("\t")
            follow_log[i][0] = int(follow_log[i][0])
    except FileNotFoundError as err:
        logging.info(f"No '{likes_log_file}' found, making a new one")
        follow_log = list()
    return follow_log

# MAIN
if __name__ == "__main__":
    args = interface()

    # Set up logging
    logging.basicConfig(
        level = logging.INFO,
        format = "[%(levelname)s]  %(message)s",
        handlers = [
            logging.StreamHandler()
    ])
    # Really don't need to hear about dropped connections
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARNING)

    # Load config
    with open(args.CONFIG, "r", encoding="utf8") as f:
        try:
            config = yaml.load(f)
        except yaml.YAMLError as err:
            print(err)

    # Load comments
    comment = config["settings"]["comment"]
    comments_file = config["comments"]
    try:
        with open(comments_file, "rt", encoding="utf8") as f:
            comments = f.readlines()
        comments = [c.strip() for c in comments]
    except FileNotFoundError:
        logging.warning(f"{comments_file} was not found. Continuing without comments.")
        comments = None
        comment = False

    # Some common parameters
    n_pics =  config["settings"]["n_pics"]
    n_user = config["settings"]["n_user"]
    hashtag = config["settings"]["hashtag"]
    user = config["settings"]["user"]
    location = config["settings"]["location"]
    min_wait = config["settings"]["min_wait"]
    max_wait = config["settings"]["max_wait"]
    follow_days = config["settings"]["follow_days"]
    follow_by = config["settings"]["follow_by"]

    # Set log files
    try:
        follow_log_file = config["follow_log"]
        if not os.path.isfile(follow_log_file):
            logging.warning(f"No '{follow_log_file}' found, using logs/follow.log")
            follow_log_file = "logs/follow.log"
    except KeyError:
        follow_log_file = "logs/follow.log"
    try:
        likes_log_file = config["likes_log"]
        if not os.path.isfile(likes_log_file):
            logging.warning(f"No '{likes_log_file}' found, using logs/likes.log")
            likes_log_file = "logs/likes.log"
    except KeyError:
        likes_log_file = "logs/likes.log"

    # The actual BOT
    logging.info("Logging into Instagram")
    acc_username = config["account"]["username"]
    password = config["account"]["password"]
    API = InstagramAPI(acc_username, password)
    # Set device
    device = config["account"]["device"]
    API.setDevice(device)
    # Set proxy
    try:
        ip = config["proxy"]["ip"]
        port = config["proxy"]["port"]
        proxy = f"{acc_username}:{password}@{ip}:{port}"
        API.setProxy(proxy)
    except:
        logging.warning("Proxy was not set, continuing without")
    API.login()

    if args.COMMAND == "like":
        likes_log = load_liked_pics(logging, likes_log_file)

        if user:
            logging.info(f"Searching for user {user}")
            response = API.searchUsername(user)
            user_id = API.LastJson["user"]["pk"]

            logging.info(f"Getting first {n_user} followers")
            response = API.getUserFollowers(user_id)
            followers = API.LastJson["users"][:n_user]

            for fer in followers:
                username = fer["username"]
                user_id = fer["pk"]

                logging.info(f"Getting user feed of {username}")
                try:
                    response = API.getUserFeed(user_id)
                except:
                    logging.info(f"{username} does not want us to see their profile")
                    continue
                if not response:
                    continue

                pics = API.LastJson["items"][:n_pics]
                likes_log = API.likePics(pics, logging, do_comment=comment,
                    comments=comments, wait=[min_wait, max_wait],
                    likes_log=likes_log)

        if hashtag:
            if hashtag.startswith("#"):
                hashtag = hashtag[1:]

            logging.info(f"Searching for hashtag {hashtag}")
            response = API.getHashtagFeed(hashtag)

            pics = API.LastJson["items"][:n_pics]
            likes_log = API.likePics(pics, logging, do_comment=comment, comments=comments,
                wait=[min_wait, max_wait], likes_log=likes_log)

        if location:

            logging.info(f"Searching for location {location}")
            response = API.searchLocation(location)

            loc = API.LastJson["items"][0]["location"]
            loc_name = loc["name"]
            loc_id = loc["pk"]
            logging.info(f"{loc_name} found as first result")
            logging.info(f"Getting feed of {loc_name}")
            response = API.getLocationFeed(loc_id)

            pics = API.LastJson["items"][:n_pics]
            likes_log = API.likePics(pics, logging, do_comment=comment, comments=comments,
                wait=[min_wait, max_wait], likes_log=likes_log)

    if args.COMMAND == "like_back":
        likes_log = load_liked_pics(logging, likes_log_file)

        logging.info(f"Listing followers of {acc_username}")
        my_followers = API.getAllFollowerIDs(acc_username)

        logging.info(f"Getting first {n_pics} posts")
        pic_ids = API.getAllPictureIDs(acc_username)[:n_pics]

        for media_id in pic_ids:
            API.getMediaLikers(media_id)
            likers = [user for user in API.LastJson["users"]
                if user["pk"] not in my_followers]

            for liker in likers:
                username = liker["username"]
                user_id = liker["pk"]

                logging.info(f"Getting user feed of {username}")
                try:
                    response = API.getUserFeed(user_id)
                except:
                    logging.info(f"{username} does not want us to see their profile")
                    continue
                if not response:
                    logging.info(f"{username} does not want us to see their profile")
                    continue

                logging.info(f"Liking first {n_pics} posts")
                pics = API.LastJson["items"][:n_pics]
                likes_log = API.likePics(pics, logging, do_comment=comment,
                    comments=comments, wait=[min_wait, max_wait],
                    likes_log=likes_log)

    if args.COMMAND == "follow":
        follow_log = read_follow_log(logging, follow_log_file)
        logged_ids = set([f[0] for f in follow_log])
        follower_ids = set(API.getAllFollowerIDs(acc_username))
        follower_ids |= logged_ids

        if user:
            logging.info(f"Searching for user {user}")
            response = API.searchUsername(user)
            user_id = API.LastJson["user"]["pk"]

            if follow_by == "liker":
                logging.info(f"Getting first {n_user} likers of first picture.")
                pic_id = API.getAllPictureIDs(user)[0]["pk"]
                pic_likers = API.getMediaLikers(pic_id)
                followers = API.LastJson["users"]

            if follow_by == "follower":
                logging.info(f"Getting first {n_user} followers")
                response = API.getUserFollowers(user_id)
                followers = API.LastJson["users"]

            for fer in followers[:n_user]:
                username = fer["username"]
                user_id = fer["pk"]
                if user_id in follower_ids:
                    continue

                logging.info(f"Following {username}")
                response = API.follow(user_id)

                with open(follow_log_file, "at", encoding="utf8") as fout:
                    now = datetime.now().strftime("%Y-%m-%d_%H:%M")
                    fout.write("\t".join((str(user_id), username, now)) + "\n")

                follow_log = read_follow_log(logging, follow_log_file)
                logged_ids = set([f[0] for f in follow_log])
                follower_ids |= logged_ids
                time.sleep(random.randint(min_wait, max_wait))

    if args.COMMAND == "unfollow":
        follow_log = read_follow_log(logging, follow_log_file)

        for f in follow_log:
            now = datetime.now()
            delta = now - datetime.strptime(f[2], "%Y-%m-%d_%H:%M")
            if delta.total_seconds() / (24 * 60 * 60) > follow_days:
                logging.info(f"Unfollowing {f[1]}")
                API.unfollow(f[0])
                flog = read_follow_log(logging, follow_log_file)
                for fl in flog:
                    if f[0] == fl[0]:
                        flog.remove(fl)
                with open(follow_log_file, "wt", encoding="utf8") as fout:
                    for fl in flog:
                        fout.write("\t".join(map(str, fl)) + "\n")
                time.sleep(random.randint(min_wait, max_wait))
