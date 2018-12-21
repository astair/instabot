import os
import sys
import time
import yaml
import random
import logging
import argparse
from datetime import datetime
from InstagramAPI import InstagramAPI

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Hi, I'm a little Instabot!")

    parser.add_argument("COMMAND",
                        type=str,
                        choices=["like", "like_back", "comment", "comment_back", "follow"],
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
    with open(args.CONFIG, "r") as stream:
        try:
            config = yaml.load(stream)
        except yaml.YAMLError as err:
            print(err)

    logging.info("Logging into Instagram.")
    username = config["account"]["username"]
    API = InstagramAPI(username, config["account"]["password"])
    API.login()

    # Some common parameters
    n_pics =  config["settings"]["n_pics"]
    n_user = config["settings"]["n_user"]
    hashtag = config["settings"]["hashtag"]
    user = config["settings"]["user"]
    location = config["settings"]["location"]
    wait = config["settings"]["wait"]
    comment = config["settings"]["comment"]

    comments = open(config["comments"], "rt").readlines()
    comments = [c.strip() for c in comments]

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
                for pic in pics:
                    media_id = pic["pk"]
                    API.like(media_id)
                    if comment:
                        comment = random.sample(comments, 1)[0]
                        logging.info(f"Commenting '{comment}'")
                        API.comment(media_id, comment)
                    time.sleep(wait)

        if hashtag:
            if hashtag.startswith("#"):
                hashtag = hashtag[1:]

            logging.info(f"Searching for hashtag {hashtag}")
            response = API.getHashtagFeed(hashtag)

            pics = API.LastJson["ranked_items"][:n_pics]

            logging.info(f"Liking first {n_pics} posts")
            pics = API.LastJson["items"][:n_pics]
            for pic in pics:
                media_id = pic["pk"]
                API.like(media_id)
                if comment:
                    comment = random.sample(comments, 1)[0]
                    logging.info(f"Commenting '{comment}'")
                    API.comment(media_id, comment)
                time.sleep(wait)

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
            for pic in pics:
                media_id = pic["pk"]
                API.like(media_id)
                if comment:
                    comment = random.sample(comments, 1)[0]
                    logging.info(f"Commenting '{comment}'")
                    API.comment(media_id, comment)
                time.sleep(wait)

    if args.COMMAND == "like_back":
        if not user:
            user = username

        response = API.searchUsername(user)
        user_id = API.LastJson["user"]["pk"]

        logging.info("Listing followers")
        API.getUserFollowings(user_id)
        my_followers = [user["pk"] for user in API.LastJson["users"]]

        API.searchUsername(user)
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
                for pic in pics:
                    media_id = pic["pk"]
                    API.like(media_id)
                    if comment:
                        comment = random.sample(comments, 1)[0]
                        logging.info(f"Commenting '{comment}'")
                        API.comment(media_id, comment)
                    time.sleep(wait)
