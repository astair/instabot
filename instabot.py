import os
import sys
import time
import yaml
import random
import logging
import argparse
from datetime import datetime
from instabot.api.InstagramAPI import InstagramAPI

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Hi, I'm a little Instabot!")

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

    def load_liked_pics():
        try:
            with open("logs/likes.log", "r") as f:
                follow_log = yaml.load(f)
        except FileNotFoundError as err:
            follow_log = []
        

if __name__ == "__main__":
    args = interface()

    # Set up logging
    logging.basicConfig(
        level = logging.INFO,
        format = "[%(levelname)s]  %(message)s",
        handlers = [
            logging.StreamHandler()
    ])

    # Load config
    with open(args.CONFIG, "r", encoding="utf8") as f:
        try:
            config = yaml.load(f)
        except yaml.YAMLError as err:
            print(err)

    # Load comments
    comment = config["settings"]["comment"]
    try:
        with open(config["comments"], "rt", encoding="utf8") as f:
            comments = f.readlines()
        comments = [c.strip() for c in comments]
    except FileNotFoundError:
        logging.warning(f"{config["comments"]} was not found. Continuing        without comments.")
        comment = False

    logging.info("Logging into Instagram.")
    acc_username = config["account"]["username"]
    device = config["account"]["device"]
    API = InstagramAPI(acc_username, config["account"]["password"])
    API.setDevice(device)
    API.login()

    # Some common parameters
    n_pics =  config["settings"]["n_pics"]
    n_user = config["settings"]["n_user"]
    hashtag = config["settings"]["hashtag"]
    user = config["settings"]["user"]
    location = config["settings"]["location"]
    min_wait = config["settings"]["min_wait"]
    max_wait = config["settings"]["max_wait"]
    follow_days = config["settings"]["follow_days"]

    if args.COMMAND == "like":
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

                logging.info(f"Liking first {n_pics} posts")
                pics = API.LastJson["items"][:n_pics]
                API.likePics(pics, logging, do_comment=comment,
                    comments=comments, wait=[min_wait, max_wait])

        if hashtag:
            if hashtag.startswith("#"):
                hashtag = hashtag[1:]

            logging.info(f"Searching for hashtag {hashtag}")
            response = API.getHashtagFeed(hashtag)

            pics = API.LastJson["ranked_items"][:n_pics]

            logging.info(f"Liking first {n_pics} posts")
            pics = API.LastJson["items"][:n_pics]
            API.likePics(pics, logging, do_comment=comment, comments=comments,
                wait=[min_wait, max_wait])

        if location:

            logging.info(f"Searching for location {location}")
            response = API.searchLocation(location)

            loc = API.LastJson["items"][0]["location"]
            loc_name = loc["name"]
            loc_id = loc["pk"]
            logging.info(f"{loc_name} found as first result")
            logging.info(f"Getting feed of {loc_name}")

            response = API.getLocationFeed(loc_id)

            logging.info(f"Liking first {n_pics} posts")
            pics = API.LastJson["items"][:n_pics]
            API.likePics(pics, logging, do_comment=comment, comments=comments,
                wait=[min_wait, max_wait])

    if args.COMMAND == "like_back":
        if not user:
            user = acc_username

        response = API.searchUsername(user)
        user_id = API.LastJson["user"]["pk"]

        logging.info("Listing followers")
        API.getUserFollowings(user_id)
        my_followers = [user["pk"] for user in API.LastJson["users"]]

        API.searchUsername(username)
        user_id = API.LastJson["user"]["pk"]

        logging.info(f"Getting first {n_pics} posts")
        API.getUserFeed(user_id)
        pics = API.LastJson["items"][:n_pics]

        for pic in pics:
            media_id = pic["pk"]
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
                API.likePics(pics, logging, do_comment=comment,
                    comments=comments, wait=[min_wait, max_wait])

    if args.COMMAND == "follow":

        try:
            with open("logs/follow.log", "r") as f:
                follow_log = yaml.load(f)
        except FileNotFoundError as err:
            print(err)
            follow_log = []
        except yaml.YAMLError as err:
            print(err)
            follow_log = []
        if not follow_log:
            follow_log = []

        now = datetime.now().strftime("%Y-%m-%d_%H:%M")

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

                logging.info(f"Following {username}")
                response = API.follow(user_id)
                if response:
                    follow_log.append((user_id, username, now))
                time.sleep(random.randint(min_wait, max_wait))

            with open("logs/follow.log", "w") as fout:
                yaml.dump(follow_log, fout)

    if args.COMMAND == "unfollow":

        with open("logs/follow.log", "r") as f:
            follow_log = yaml.load(f)

        now = datetime.now()

        new_follow_log = []
        for f in follow_log:
            delta = now - datetime.strptime(f[2], "%Y-%m-%d_%H:%M")
            if delta.days > follow_days:
                logging.info(f"Unfollowing {f[1]}")
                API.unfollow(f[0])
                time.sleep(random.randint(min_wait, max_wait))
            else:
                new_follow_log.append(f)

        with open("logs/follow.log", "w") as fout:
            yaml.dump(new_follow_log, fout)
