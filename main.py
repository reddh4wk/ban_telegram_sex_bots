#+++++++==-------------------:--------------:-::::-----::---=--=+====*+============-=+=-==-
#========-----------------------------------:--:--+***++==-----=+====*=============-===-==:
#====---------------------------::::::------:--=*%%%##%%%%*=---=+====*=============-===-==:
#=====---------------------------:------------#%%%%%%#%%%%%%+--=+--==+=============-===-==:
#====---------------------------------------=#@%%##*=+*#%%%%%===+---=+===--========-===-==:
#=--------------------------------------:----%%==--==+**#@@@%%*=+---=+===--========-===-==:
#=========-----------------------------------*#*******#**#%%%%***----+===--========-===-==:
#+++++++++==----------------===============--==++=**++***###%@%#+----+===--========-===-==:
#=========------------------------------------**+*##****#%%#%%%*+=---+===--========-===-==:
#++++++++++++=--=:----::======================**+##***##%%%%#%##****+++==--========-===-==-
#====----------=+*+=-+**-----------------=**#+%%##*###%@@%%%#%########**+==========-===-=+=
#==-------------==-=-===--------------=*###%%*=%#####%%@@@%#%%%%##%#####**=========-===-===
#--------------=========----::::::::=*#%%%#*++-=%@@@%%%%%%%%%%%#%%%%%######*==-====-===-===
#--------------==========----:::::-*%%%%%#**+==--+*%**#%@@%##%%%%%%%%%######*=--===-==+====
#=========-----==-=======--------+#%%%%%%%*+=====--+#%%%%%#%%%%%%%%%%%%%%%###+---=====+====
#=========---------==-----------*%%%%%%%%%%###***======++*####%%@%%%%%%####%%*----=========
#===---------------==----------*%%%%%%@%%%%%%%%%##*+=======-==++****##%%%%%%%*----=========
#=-----------------==---------*%%%%%@@%%%%%%%%%%%%%%#*=================+*%%%@#----=+===+==-
#------------------=---------*%%%%@@@@%%%%%%%%%%%%%@@%%#*+====++++++++++*#@@@%+---=+===+==-
#---------------------------#%%%%%@@@@%%%%%%%%%%@@@@@@@@@@#*+++++++*****#%%@@%*---=+=======
#==========----------------++==+%@@@@@%%%%%%%@@%%%%%%%@@@@@@@%##******##%%@@@@%=--=+======-
#========----------------=*++=++*%@@@@@%%%%%%%%%%%%%%%%%@@@@@@@@@@%%%%%@@@@@@@@%--=+======-
#=============----------+++=++++*##@#%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@@@@@@@@@#-=+==--==-
#=====-----------------+++++**##*+*=*%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@@@%%%#++==--==-
#------------:--------+++++**#*=::::#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@@@%%%*=--===-
#--------------------++==+*#*=:::::=%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@@@@@@@@@%%%%%+------
#::::::::::---------=====**=::::::-%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@%%%@@@@@@@*------
#=======-------==-----=+=-:::-----%%%%%%%%%%%@%%%%%%%%@@@@%@@%%%%%%%@@@@@@%%%%@@@@@@#------
#==--------==++*=====+*****#*#**#####*#%%%#%##%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@@@@@@@@%---::-
#++++++++++++++*+++=+++++++++++**#########****###%%%%@@@%%%%%%%%%%%%%%%%%%%@@@@@@@@@#-:-::-
#====-==----::-=:====++*++++======****##***##############***************#####****#%%*---:::
#::.:..:.---::::::::::..:::::::--:-===++*#%%%%%####################*****++*+==*#*-+#*====--

# THIS SCRIPT WORKS AT LEAST WITH PYTHON 3.7.0 and 3.9.2. (I tried both, 09 November 2023)
#
# Please install pip on your system. Use your package maanger if you're using Linux or this if you're using Windows:
# curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
# python get-pip.py
#
# Then use pip to install these packages:
#
# pip install dataset telepot nudenet
#
# Just be sure to install python and the needed dependecies and launch the file by giving the path to your python bin, e.g:
#
# python ./main.py (assuming you are positioned in the same folder of the .py file)
#
# Oh, also remember to get a telegram bot TOKEN from the botfather bot and replace the MAIN_TOKEN variable value with it.
# Also make sure your bot is in your public group with admin priviledges and disable the privacy setting of your bot from botfather chat using /setprivacy command or whatever it is.
# I think this should be it...

# BOT's TOLERANCE. A LOWER TOLERANCE WILL BRING HARDER JUDJMENTS
bot_tolerance=120

########################################
### IMPORT NECESSARY LIBRARIES
########################################

# TO EVAL STRING MORE SECURELY THAN JUST eval()
from ast import literal_eval
# TO MESS WITH DATES
from datetime import datetime
from datetime import timedelta
# TO BE BFF WITH OS
import os
# TO GET KINKY WITH DATABASES
import dataset
# TO DETECT NUDITY
from nudenet import NudeDetector
# TO DOWNLOAD PROFILE PICTURES
import urllib
import requests 

########################################
### TOOLS
########################################

# GET THIS FILE NAME
THIS_FILENAME_EXT=os.path.basename(__file__)
THIS_FILENAME=os.path.splitext(THIS_FILENAME_EXT)[0]
THIS_FOLDER=os.path.abspath(os.path.dirname(__file__))

# TO USE SAME DATE FORMAT EVERYWHERE (UNIX TIMESTAMPS)
def get_time():
    now = datetime.now()
    return int(now.timestamp())

# TO CONVERT TIMESTAMPS TO A HUMAN-FRIENDLY FORMAT
def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp)

def len2_and_positive_int(command):
    try:
        command = command.split()
        if len(command) == 1:
            return None
        elif len(command) == 2:
            parameter = int(command[1])
            if isinstance(parameter, int):
                if int(command[1]) > 0:
                    return parameter
                else:
                    return False
        else:
            return False
    except ValueError:
        return False  

########################################
### DATABASE
########################################

# SET UP/CONNECT TO THE DB TABLES
db = dataset.connect('sqlite:///'+os.path.join(THIS_FOLDER, THIS_FILENAME+'.sqlite'))
chat_db = db['chat']
scanned_db = db['scanned']
member_db = db['member']

# REGISTER A NEW CHAT (chat_db)
def db_update_group_ref(chat_id, chat_title, status=0, tolerance=bot_tolerance):
    now = get_time()
    history=[(1,now)]
    chat_db.upsert(dict(chat_id=chat_id, chat_title=chat_title, added_on=get_time(), status=status, tolerance=tolerance, uptime=0, history=str(history)), ['chat_id'])
    return True

# GET STATUS ON A CHAT (chat_db)
def db_get_status_on_chat(chat_id, chat_title):
    for each in chat_db:
        if chat_id == each['chat_id']:
            return each['status']
    db_update_group_ref(chat_id, chat_title)
    return False

# UPDATE STATUS (THEREFORE HISTORY AND UPTIME TOO) ON A CHAT (chat_db)
def db_update_status_on_chat(chat_id, chat_title):
    for each in chat_db:
        if chat_id == each['chat_id']:
            new_status = int(not each['status'])
            chat_history = literal_eval(each['history'])
            current_time = get_time()
            new_history = chat_history
            new_history.append((new_status, current_time))
            chat_db.update(dict(chat_id=chat_id, status=new_status, history=str(new_history)), ['chat_id'])
            db_update_uptime_in_chat(chat_id, chat_history, each['uptime'], new_status)
            return new_status   
    db_update_group_ref(chat_id, chat_title, 1)
    return True

# GET HOW LONG BOT HAS BEEN RUNNING IN ONE (OR ALL) GROUPS (chat_db)
def db_get_uptime_on_chat(chat_id=False):
    if chat_id is False:
        total = 0
        for each in chat_db:
            total += each['uptime']
            status = each['status']
            if status:
                history=literal_eval(each['history'])
                last_time_from_history=history[len(history)-1][1]
                delta = int(get_time()) - last_time_from_history
                total += delta
        return total
    else:
        for each in chat_db:
            if chat_id == each['chat_id']:
                uptime = each['uptime']
                status = each['status']
                if status:
                    history=literal_eval(each['history'])
                    last_time_from_history=history[len(history)-1][1]
                    delta = int(get_time()) - last_time_from_history
                    return uptime+delta
                else:
                    return uptime

# UPDATE UPTIME ON A CHAT (chat_db)
def db_update_uptime_in_chat(chat_id, chat_history, uptime, status):
    if not status:
        new_uptime = uptime + chat_history[len(chat_history)-1][1] - chat_history[len(chat_history)-2][1]
        chat_db.update(dict(chat_id=chat_id, uptime=new_uptime), ['chat_id'])
        return True
    return False

# GET TOLERANCE ON A CHAT (chat_db)
def db_get_tolerance_on_chat(chat_id, chat_title):
    for each in chat_db:
        if chat_id == each['chat_id']:
            return each['tolerance']
    db_update_group_ref(chat_id, chat_title)
    return bot_tolerance

# REGISTER A NEW MEMBER (member_db)
def db_add_new_member_ref(message_id, chat_id, chat_title, user_id, user_first_name, user_last_name, username, time):
    member_db.upsert(dict(message_id=message_id, chat_id=chat_id, chat_title=chat_title, user_id=user_id, user_first_name=user_first_name, user_last_name=user_last_name, username=username, date=time), ['user_id'])
    return True

# DELETE A MEMBER FROM DB (member_db)
def db_delete_member_ref(chat_id, user_id):
    member_db.delete(chat_id=chat_id, user_id=user_id)
    return True

# UPDATE MEMBERS (member_db)
def db_update_members(chat_id):
    for each in db_get_chat_members(chat_id):
        if not user_is_member(chat_id, each['user_id']):
            db_delete_member_ref(chat_id, each['user_id'])
    return True

# GET_CHAT_MEMBERS (member_db)
def db_get_chat_members(chat_id):
    return member_db.find(chat_id=chat_id)

# GET_HIGHEST_SCORES (scanned_db)
def db_get_highest_scores(chat_id, limit, banned=1):
    if chat_id is False:
        return scanned_db.find(banned=banned, order_by=['-score','username'], _limit=limit)
    else:
        return scanned_db.find(banned=banned, chat_id=chat_id, order_by=['-score','username'], _limit=limit)

# GET_LAST_SCORES (scanned_db)
def db_get_last_scores(chat_id, limit):
    lasts = []
    for each in scanned_db.find(chat_id=chat_id, order_by=['date'], _limit=limit):
        user_id_folder = os.path.join(THIS_FOLDER, str(each['user_id']))
        filename = os.path.join(user_id_folder, 'results.txt')
        with open(filename, "r") as f:
            file_contents = f.read()
        each['results'] = file_contents
        lasts.append(each)
    return lasts

# REGISTER A NEW SCAN (scanned_db)
def db_update_scan_ref(result):
    scanned_db.upsert(dict(chat_id=result['chat_id'], chat_title=result['chat_title'], user_id=result['user_id'], user_first_name=result['user_first_name'], username=result['username'], date=result['date'], score=result['score'], banned=result['banned']), ['chat_id','user_id'])
    return True

# TO COUNT BANS IN ONE (OR ALL) GROUPS (scanned_db)
def db_get_total_bans(chat_id=False):
    if not chat_id:
        return scanned_db.count(banned='1')
    else:
        return scanned_db.count(banned='1', chat_id=chat_id)

########################################
### GET AND SCAN WITH NUDENET
########################################

# CHECK IF LAST AND FIRST NAME ARE THE SAME. VERY UNUSUAL FOR A HUMAN, UNLIKE THESE BOTS I'M FACING NOWADAYS.
def same_names(user_id):
    member=member_db.find_one(user_id=user_id)
    if member['user_first_name'] == member['user_last_name']:
        return True
    else:
        return False

priority_1 = ["FEMALE_GENITALIA_EXPOSED","ANUS_EXPOSED","MALE_GENITALIA_EXPOSED"]
priority_2 = ["BUTTOCKS_EXPOSED","FEMALE_BREAST_EXPOSED","ANUS_COVERED"]
priority_3 = ["BUTTOCKS_COVERED","FEMALE_BREAST_COVERED","FEMALE_GENITALIA_COVERED","FEMALE_GENITALIA_COVERED"]
priority_4 = ["FEET_EXPOSED","BELLY_EXPOSED","ARMPITS_EXPOSED"]
forbidden = priority_1 + priority_2 + priority_3 + priority_4

# TO GET THE PROFILE PICTURES OF A USER
def get_profile_pictures(user_id):
    profile_picture = bot.get_user_profile_photos(user_id)
    user_id_folder = os.path.join(THIS_FOLDER, str(user_id))
    if not os.path.exists(user_id_folder):
        os.makedirs(user_id_folder)
    file_paths = []
    photo_number = 0
    for photo in profile_picture.photos:
        file_path = os.path.join(user_id_folder, str(user_id) + '_' + str(photo_number) + '_' + str(photo[0].file_unique_id) + '.jpg')
        urllib.request.urlretrieve(bot.get_file_url(photo[0].file_id), file_path)
        photo_number += 1
    return True

# TO PARSE THE PICTURES OF THE SELECTED USER_ID
def scan_pictures(user_id):
    user_id_folder = os.path.join(THIS_FOLDER, str(user_id))
    jpg_paths = []
    virdict_content = []
    score = 0
    total_score = 0
    for filename in os.listdir(user_id_folder):
        if filename.endswith('.jpg'):
            jpg_paths.append(os.path.join(user_id_folder, filename))
    for each in jpg_paths:
        result = check_nudity(each)
        if len(result) > 0:
            img_class = result[0]['class']
            if img_class in forbidden:
                if img_class in priority_1:
                    score=int(round(result[0]['score']*200))
                if img_class in priority_2:
                    score=int(round(result[0]['score']*150))
                if img_class in priority_3:
                    score=int(round(result[0]['score']*50))
                if img_class in priority_4:
                    score=int(round(result[0]['score']*20))
                img_number = str(os.path.basename(each).split("_")[1])
                img_IA_score = str(round(result[0]['score']*100, 2))
                img_MY_score = str(score)
                log_result = img_class+" detected at "+img_IA_score+"% in image #"+img_number+". Score: "+img_MY_score
                virdict_content.append(log_result)
                total_score+=score
    #Often these bots have the same first and last names...
    if same_names(user_id):
        virdict_content.append("First name and last name are the same. Score: 100")
        total_score+=120
    if len(jpg_paths) > 0:
        virdict_content.append("TOTAL SCORE: "+str(total_score))
        relative_score=int(round(total_score/len(jpg_paths)))
        virdict_content.append("RELATIVE SCORE: "+str(relative_score))
    else:
        relative_score=0
    if len(virdict_content) > 0:
        with open(os.path.join(user_id_folder,"results.txt"), "w") as f:
            for row in virdict_content:
                f.write(row + "\n")
        f.close()
    return total_score

# TO DETERMINE IF THE SOURCE IMAGE PRESENTS NUDITY
def check_nudity(image):
    detector = NudeDetector()
    result = detector.detect(image)
    return result

########################################
### CLEAN-UP MEMBERSHIP & CHAT
########################################

# TRIAL PROCESS
def start_trial(chat_id, user_id):
    member=member_db.find_one(chat_id=chat_id, user_id=user_id)
    member['date']=get_time()
    get_profile_pictures(member['user_id'])
    score = scan_pictures(member['user_id'])
    member['score']=score
    if score > bot_tolerance:
        ban_sentence=True
    else:
        ban_sentence=False
    if ban_sentence:
        delete_message_from_chat(member['chat_id'], member['message_id'], member['chat_title'], member['user_first_name'])
        ban_user_from_chat(member['chat_id'], member['user_id'], member['chat_title'], member['user_first_name'])
        member["banned"]=1
    else:
        member["banned"]=0
    db_update_scan_ref(member)
    return member["banned"]

# PURGE COMMAND
def demand_purge_on_chat(chat_id):
    counter=0
    db_update_members(chat_id)
    for each in db_get_chat_members(chat_id):
        counter += start_trial(each['chat_id'], each['user_id'])
    db_update_members(chat_id)
    return counter
        
# BANS A USER FROM A GROUP
def ban_user_from_chat(chat_id, user_id, chat_title, user_first_name):
    try:
        bot.kick_chat_member(chat_id, user_id)
        print("User {} ({}) banned from group {} ({})".format(user_first_name, user_id, chat_title, chat_id))
        return True
    except telebot.apihelper.ApiException as e:
        print("Error banning user {} ({}) from group {} ({}): {}".format(user_first_name, user_id, chat_title, chat_id, e))

# DELETES A MESSAGE IN CHAT
def delete_message_from_chat(chat_id, message_id, chat_title, user_first_name):
    try:
        bot.delete_message(chat_id, message_id)
        print("Deleted message {} sent by {} from chat {}".format(message_id, user_first_name, chat_id))
        return True
    except telebot.apihelper.ApiException as e:
        print("Error deleting message {} sent by {} from group {}: {}".format(message_id, user_first_name, chat_id, e))

########################################
### TELEBOT - INITIALIZATION
########################################

# THE API TELEGRAM TOKEN GENERATED BY BOTFATHER BOT
TEST_TOKEN = 'Here you could paste another token for a bot you may want to use for test purposes in parallel.'
MAIN_TOKEN = 'PASTE_HERE_THE_BOT_TOKEN'

# TO SET UP THE MAIN BOT
import telebot
if THIS_FILENAME == "test_bot_name":
    bot = telebot.TeleBot(TEST_TOKEN)
else:
    bot = telebot.TeleBot(MAIN_TOKEN)

########################################
### TELEBOT - TOOLS
########################################

bot_name = bot.get_me().first_name

def member_is_admin(message):
    member = bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status in ['creator','administrator']:
        return True
    else:
        bot.reply_to(message, "This command requires administrator-level or superior priviledges.")
        return False

def user_is_member(chat_id, user_id):
    member = bot.get_chat_member(chat_id, user_id)
    if member.status in ['creator','administrator','member','restricted']:
        return True
    else:
        return False

########################################
### TELEBOT - HANDLERS
########################################

msg_positive_integer = "This command only takes one additional optional argument, a positive integer."

# START
@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, """\
Hi, I am """+bot_name+"""! I can automatically ban users that join groups I am a member of if they presents explicit sexual contents.
""")

# HELP
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, """
List of the commands:
/help: Display this message.
/status: Display the current status [on/off] of the bot in this chat.
/listen: Toggle the current setting for the bot activity in this chat.
/purge: Initiate a trial process for all known users in this chat.
/tolerance: Modify the tolerance parameter of the bot.
/stats: Display statistics of the activity of the bot.
/top: Shows the accounts banned for the highest amount of sins.
/last: Shows last scan results in detail.
""")

# LISTEN
@bot.message_handler(commands=['purge'])
def send_help(message):
    if member_is_admin(message):
        banned = demand_purge_on_chat(message.chat.id)
        if banned:
            if banned > 1:
                bot.reply_to(message, str(banned)+" sinners were banned during the purge.")
            else:
                bot.reply_to(message, str(banned)+" sinners was banned during the purge.")
        else:
            bot.reply_to(message, "This chat is not sinful enough for my tolerance maybe?")

# LISTEN
@bot.message_handler(commands=['listen'])
def send_help(message):
    if member_is_admin(message):
        status = db_update_status_on_chat(message.chat.id, message.chat.title)
        if status == True:
            bot.reply_to(message, "Activity has been enabled!")
        elif status == False:
            bot.reply_to(message, "Activity has been disabled!")
        else:
            bot.reply_to(message, "There was an error while retrieving the current status. If you can, contact the Administrator. If not, I'm sorry.")

# GET THE CURRENT STATUS
@bot.message_handler(commands=['status'])
def send_help(message):
        status = db_get_status_on_chat(message.chat.id, message.chat.title)
        if status == True:
            bot.reply_to(message, bot_name+" is active on this chat. Use /listen to toggle activity.")
        elif status == False:
            bot.reply_to(message, bot_name+" is not active on this chat. Use /listen to toggle activity.")
        else:
            bot.reply_to(message, "There was an error while retrieving the current status. If you can, contact the Administrator. If not, I'm sorry.")

# ADJUST TOLERANCE
@bot.message_handler(commands=['tolerance'])
def modify_tolerance(message):
    if member_is_admin(message):
        new_tolerance = len2_and_positive_int(message.text)
        if new_tolerance == None:
            current_tolerance = db_get_tolerance_on_chat(message.chat.id, message.chat.title)
            if current_tolerance == None:
                bot.reply_to(message, "Current tolerance: "+str(bot_tolerance))
            else:
                bot.reply_to(message, "Current tolerance: "+str(chat_db.find_one(chat_id=message.chat.id)['tolerance']))
        elif new_tolerance:
            db_update_group_ref(message.chat.id, message.chat.title, tolerance=new_tolerance)
            bot.reply_to(message, "Tolerance updated.")
        else:
            bot.reply_to(message, msg_positive_integer)

# DISPLAY STATISTICS
@bot.message_handler(commands=['stats'])
def stats(message):
    chat_uptime = db_get_uptime_on_chat(message.chat.id)
    ban_in_this_chat = db_get_total_bans(message.chat.id)
    if chat_uptime or ban_in_this_chat:
        total_bans = db_get_total_bans()
        if chat_uptime < 86400:
            daily_ratio = ban_in_this_chat
        else:
            daily_ratio = int(ban_in_this_chat/(chat_uptime/(60*60*24)))
        reply = bot_name+" banned "+str(ban_in_this_chat)+" sinners in this chat (and "+str(total_bans)+f" in total).\n"+bot_name+" listened for "+str(timedelta(seconds=chat_uptime))+", roughly "+str(daily_ratio)+" ban/day so far."
        bot.reply_to(message, reply)
    else:
        bot.reply_to(message, "The bot hasn't been active yet so far in this chat. Activate it with /listen command to eventually see some stats.")

# DISPLAY TOP PLAYERS
@bot.message_handler(commands=['top'])
def top(message):
    def reply(message, highest_scores):
        result=""
        counter = 1
        for each in highest_scores:
            result+=(str(counter)+f". @{each['username']}, score: {each['score']}\n")
            counter+=1
        if counter == 1:
            bot.reply_to(message, "No statistics are available yet.")
        else:
            bot.reply_to(message, result)
    limit = len2_and_positive_int(message.text)
    if limit == None:
        reply(message, db_get_highest_scores(message.chat.id, 3))
    elif limit:
        reply(message, db_get_highest_scores(message.chat.id, limit))
    else:
        bot.reply_to(message, msg_positive_integer)

# DISPLAY LAST SCAN
@bot.message_handler(commands=['last'])
def top(message):
    def reply(message, last_scores):
        result=""
        counter = 1
        for each in last_scores:
            result+=(str(counter)+f". @{each['username']}\n{each['results']}\n")
            counter+=1
        if counter == 1:
            bot.reply_to(message, "No statistics are available yet.")
        else:
            bot.reply_to(message, result)
    limit = len2_and_positive_int(message.text)
    if limit == None:
        reply(message, db_get_last_scores(message.chat.id, 1))
    elif limit:
        reply(message, db_get_last_scores(message.chat.id, limit))
    else:
        bot.reply_to(message, msg_positive_integer)

# GET INFO ABOUT NEW MEMBERS
@bot.message_handler(content_types=["new_chat_members"])
def get_info_about_new_members(message):
    if 'last_name' in message.json['new_chat_member']:
        last_name = message.json['new_chat_member']['last_name']
    else:
        last_name = None
    if 'username' in message.json['new_chat_member']:
        username = message.json['new_chat_member']['username']
    else:
        username = None
    db_add_new_member_ref(message.id, message.chat.id, message.chat.title, message.json['new_chat_member']['id'], message.json['new_chat_member']['first_name'], last_name, username, get_time())
    is_active = db_get_status_on_chat(message.chat.id, message.chat.title)
    if is_active:
        start_trial(message.chat.id, message.json['new_chat_member']['id'])
    return True

# LOOK FOR BAN MESSAGES AND DELETES HIS OWN
#@bot.message_handler(action=["ban", "kick_chat_member", "left_chat_member", "new_])
#def on_ban(event):
#    print("test")
#    message = event.message
#    if message.from_user.id == bot.id:
#        delete_message_from_chat(message.chat.id, message.id, message.chat.title, message.json['new_chat_member']['first_name'])

########################################
### TELEBOT - START
########################################

# Start the polling
try:
    bot.infinity_polling()
except KeyboardInterrupt:
    bot.stop_polling()
