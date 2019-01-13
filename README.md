# Hi, I'm Samu's little instabot!

## Functions

This instabot understands four commands: like, like_back, follow and unfollow. In a config file (per default `config.yaml`) you can supply a number of options for these commands. Allow me to explain:

### Like

#### Command

```bash
python instabot.py like
```

#### Function

- Get followers of `user`
- Like (and comment if `comment == True`) the first `n_pics` posts of of the first `n_user` followers
- Like (and comment if `comment == True`) the first `n_pics` posts under the hashtag `hashtag`
- Like (and comment if `comment == True`) the first `n_pics` posts at the location `location`
- Between each like, wait between `min_wait` and `max_wait` seconds
- Comments are randomly selected from the file `comments`
- Writes log of all commented pictures in `logs/likes.log` and comments each pic only once


### Like back

#### Command

```bash
python instabot.py like_back
```

#### Function

- Get followers of `username`
- Get users that like the posts of `username`
- Like (and comment if `comment == True`) the first `n_pics` posts of all users that like posts but are not in followers
- Between each like, wait between `min_wait` and `max_wait` seconds
- Comments are randomly selected from the file `comments`
- Writes log of all commented pictures in `logs/likes.log` and comments each pic only once

### Follow

#### Command

```bash
python instabot.py follow
```

#### Function

- Get followers of `user`
- Follow the fist `n_user` followers
- Writes log of all followed users in `logs/follow.log`
- Between each follow, wait between `min_wait` and `max_wait` seconds

### Unfollow

#### Command

```bash
python instabot.py unfollow
```

#### Function

- Reads `logs/follow.log`
- Unfollows all users followed longer than `follow_days` days ago
- Removes all unfollowed users from `logs/follow.log`
- Between each unfollow, wait between `min_wait` and `max_wait` seconds
