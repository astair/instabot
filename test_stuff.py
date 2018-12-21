from InstagramAPI import InstagramAPI
import time
from datetime import datetime
import argparse

# FUNC
def interface():
    parser = argparse.ArgumentParser(description='Takes the name of a <SEARCH_USER> as an argument and follows the first <n_likers> of the first item in his/her feed.')

    parser.add_argument('USER_NAME',
                        type=str,
                        metavar='<USER_NAME>',
                        help='Your login name.')    

    parser.add_argument('PASSWORD',
                        type=str,
                        metavar='<PASSWORD>',
                        help='Your password.')    

    parser.add_argument('SEARCH_USER',
                        type=str,
                        metavar='<SEARCH_USER>',
                        help='Name of an instagram user.')

    parser.add_argument('-n',
                        dest='n_likers',
                        type=int,
                        default='30',
                        metavar='<n_likers>',
                        help='Number of likers to be followed in each iteration.')

    args = parser.parse_args()
    return args


# MAIN
if __name__ == "__main__":
    args = interface()
    username = args.USER_NAME
    password = args.PASSWORD
    search_user = args.SEARCH_USER
    n_likers = args.n_likers
    count = 0

    # ### EINLOGGEN
    # # Benutzername und Password in Variable speichern
    # username = 'bliblablubb_111'
    # pwd = 'bliblablubb'

    # Beides dem InstagramAPI Objekt übergeben und einloggen 
    API = InstagramAPI(username, password)
    API.login()

    # ### USER SUCHEN
    # # Username in Variable "search_user" speichern 
    # search_user = "magic_fox"

    # Hier suchste den Usernamen und fängst das JSON ab, das 
    # vom Server zurückkommt. Mit 'user' greifste auf die jeweiligen Userdaten 
    # zu. 'pk' bezeichent die User ID (warum auch immer), die dann in der Variable
    # "user_id" gespeichert wird.
    API.searchUsername(search_user)
    user_id = API.LastJson['user']["pk"]


    while True:
        now = datetime.now()
        todays_date = '{0}-{1}'.format(now.month, now.day)

        ### USER FEED FINDEN
        # Mit der "user_id" kannste jetzt den UserFeed suchen, der kommt dann als JSON 
        # Datei in "LastJson" zurück
        API.getUserFeed(user_id)

        # Da sind jetzt alle Infos des Feeds drin.
        # Unter 'items' kommste an die Einträge ran. 
        # Die sind nach Datum geordnet, [0] bezeichnet den neusten Eintrag, [1]
        # den zweitneusten, usw... Python fängt bei 0 an zu zåhlen. Davon speichern 
        # wir dann 'pk', was aus irgendwelchen Gründen der Name der media_id ist.
        media_id = API.LastJson['items'][0]['pk']

        # # Mit der media_id des Eintragen kannste den jetzt zum Beispiel kommentieren
        # text = 'Lit af'
        # API.comment(media_id, text)

        # Oder auf die user zugreifen, die den liken
        API.getMediaLikers(media_id)

        # Davon bekommste dann wieder ein JSON in dem alle Likers drinstehen, und von 
        # denen willste die ID
        likers = API.LastJson['users']
        # Dafür machste ne leere Liste auf:
        id_list = []
        # Und schreibst dann das hier (nennt sich 'for-loop').
        # Im Grunde geht das einfach über alle Menschen (hab ich hier 'guy') genannt
        # und nimmt schmeißt von jedem die ID (wieder 'pk') in die Liste von vorhin
        for guy in likers:
            id_list.append(guy['pk'])

        # Dann kannste noch einen for-loop dran hauen um dann durch die id liste zu 
        # gehen und jedem darin zu folgen. Wenn du hinter id_list '[0:30]' schreibst,
        # dann nimmt er nur die ersten 30. [20:50] würde alle von Position 20 - 50 
        # nehmen, usw...
        for ID in id_list[count:count + n_likers]:
            API.follow(str(ID))
            with open('followed-{0}.txt'.format(todays_date), 'a') as f:
                f.write(str(ID) + '\n')
            # Mit 'unfollow' könnteste denen wieder entfolgen

        count += n_likers
        time.sleep(3600)

    # # So, jetzt wirds advanced:
    # # Jeden dieser Schritte oben kannste wiederum in einen while-loop verpacken:
    # while True:
    #     # Alles was hier drunter steht wird immer wiederholt, bis du das Skript
    #     # abbrichst
    #     print('Waiting...') 
    #     # Und mit time.sleep kannst du das Skript warten lassen.
    #     # Die Zeit wird hier in Sekunden angegeben, müsstest du also umrechnen.
    #     time.sleep(30)


