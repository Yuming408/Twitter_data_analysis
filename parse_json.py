__author__ = 'wanyanxie'

import json
import glob
import collections
import os
import re
import psycopg2
import sys
import shutil

def parse_json_file(input_file,keyword_list):
    filenames = glob.glob(input_file)[1:3]
    for file in filenames:
        parse_json_file_one_block(file, keyword_list)

def parse_json_file_one_block(input, keyword_list):
    tweets = []
    tweet_tag = collections.defaultdict(list)
    node_node = collections.defaultdict(list)

    with open(input) as f:
        for line in f:
           # print line
            tweets.append(json.loads(line))

    print "number of tweets", len(tweets)


    for tweet in tweets:

        update_table(tweet,tweet_tag,node_node,keyword_list)


def update_table(tweet,tweet_tag, node_node, keyword_list):
             created_at = tweet['created_at']
             tweet_id = tweet['id_str']
             tweet_text = tweet['text']
             geo = tweet['geo']
             retweet_count = tweet['retweet_count']
             favorite_count = tweet['favorite_count']
             hashtags = tweet['entities']['hashtags']
             lang = tweet['lang']

             ###### user_based in formation
             user_id = tweet['user']['id_str']
             #user_name = tweet['user']['name']
             location = re.sub(',' , ' ',
                               tweet['user']['location'].encode('utf-8','ignore'))
             #location = re.sub(" +", " ", location).lower()
             #user_description = tweet['user']['description']
            # print location
             followers_count = tweet['user']['followers_count']
             friends_count = tweet['user']['friends_count']
             listed_count = tweet['user']['listed_count']
             favourites_count = tweet['user']['favourites_count']
             statuses_count = tweet['user']['statuses_count']
             user_created_at = tweet['user']['created_at']
             time_zone = tweet['user']['time_zone']
             user_lang = tweet['user']['lang'].encode('utf-8', 'ignore')
             user_mentions = tweet['entities']['user_mentions']


             #profile_background_color = tweet['user']['profile_background_color']
             #profile_text_color = tweet['user']['profile_text_color']
             #profile_use_background_image = tweet['user']['profile_use_background_image']
             #following = tweet['user']['following']
            # print tweet

             try:
                with open('./table/user_base_table', 'a+') as f:
                  #print location.encode('ascii')
                  #print(user_id, str(location),str(user_created_at), str(time_zone), str(user_lang))
                  f.write("%s,%d,%d,%d,%d,%d,%s,%s,%s \n" % \
                          (user_id,
                           #location,
                           followers_count,
                           friends_count,
                           listed_count,
                           favourites_count,
                           statuses_count,
                           user_created_at,
                           time_zone,
                           user_lang))

                with open('./table/tweet_base_table', 'a+') as f:
                     parsed_text = parse_text(tweet_text)
                     f.write("%s,%s,%s,%d,%d,%s,%s,%s \n" % \
                            (tweet_id,
                             user_id,
                             created_at,
                             retweet_count,
                             favorite_count,
                             lang,
                             #tweet_text.replace(',',' ').replace('\n',' ').replace('\t',' ')))
                             parsed_text,
                             get_keyword(parsed_text,keyword_list)))

                with open('./table/tweet_tag_table', 'a+') as f:
                  if tweet['entities'] and len('hashtags')!= 0:
                    for hashtag in hashtags:
                        tweet_tag[user_id].append(hashtag['text'])
                    for key in tweet_tag:
                        for value in tweet_tag.get(key):
                            #print key,value
                            f.write("%s,%s\n" % (key, value))

                with open('./table/edge_table', 'a+') as f:
                  if tweet['entities'] and len(user_mentions)!= 0:
                    for user_id_2 in user_mentions:
                        node_node[user_id].append(user_id_2['id_str'])
                    for key in node_node:
                        for value in node_node.get(key):
                            #print key,value
                            f.write("%s,%s\n" % (key, value))

                  if tweet['in_reply_to_user_id_str']:
                      f.write("%s,%s\n" % (user_id, tweet['in_reply_to_user_id_str']))

                with open('./table/tweet_geo_table', 'a+') as f:
                   if geo and geo['type'] == 'Point':
                      coords = geo['coordinates']
                      f.write("%s, %f,%f\n" % (tweet_id, coords[0], coords[1]))

                # with open('./table/tweet_text_table', 'a+') as f:
                #       text = str(parse_text(tweet_text)).strip()
                #      # print text
                #       f.write("%s,%s\n" % (user_id, text))


             except UnicodeDecodeError, e:
                 # print str(e)
                 pass

             except UnicodeEncodeError, e:
                  #print str(e)
                  pass

def parse_text(text):
    """
    Read an txt file
    Replace numbers, punctuation, tab, carriage return, newline with space
    Normalize w in wordlist to lowercase
    """
    text = text.lower()
    text = re.sub("[^a-z]", " ", text)
    # d = d.replace("\t", " ")
    # d = d.replace("\n", "")
    wordlist = text.split(" ")
    stopWords = ['a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also',
                 'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be',
                 'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'dear',
                 'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for',
                 'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers',
                 'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is',
                 'it', 'its', 'just', 'least', 'let', 'like', 'likely', 'may',
                 'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor',
                 'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our',
                 'own', 'rather', 'said', 'say', 'says', 'she', 'should', 'since',
                 'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then',
                 'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us',
                 've', 'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which',
                 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet',
                 'you', 'your', 'http', 'rt', 'https', 'co']
    wordlist = [w for w in wordlist if (len(w) >= 2 and w not in stopWords)]
    text = ' '.join(wordlist)
    text = re.sub(" +", " ", text)
    return text.strip()


def get_keyword(parsed_text, keyword_list):
    for keyword in keyword_list:
        #print '|'.join(keyword_list).lower()
        regex = re.compile('|'.join(keyword_list).lower())
        #regex = re.compile('^.*hillary.*')
        #print regex
       # pattern = r'^.*(hillary.*)?\b'
       # print re.match(pattern, text).group(0)
        #regex = re.compile(pattern)
        matches = re.search(regex, parsed_text)
        if not matches:
           continue
        else:
           # print matches.group()
            return matches.group().rstrip()




def create_tweet_base_table(cur, filename):
    cur.execute("DROP TABLE IF EXISTS tweet_base_table")
    file = open(filename)
    cur.execute("CREATE TABLE tweet_base_table( "
                   " tweet_id varchar,"
                   " user_id varchar, "
                   " created_time varchar,"
                   " retweet_count integer,"
                   " favorite_count integer, "
                   " lang char(2), "
                   " tweet_text text,"
                   " keyword text "
                   ");")
    cur.copy_from(file, 'tweet_base_table',
                  # columns = ('tweet_id', 'user_id',
                  #           'created_time', 'retweet_count',
                  #           'favorite_count','lang'
                  #               ),
                  sep= ",")



def create_user_base_table(cur, filename):
    cur.execute("DROP TABLE IF EXISTS user_base_table")
    file = open(filename)
    cur.execute("CREATE TABLE user_base_table( "
                   " user_id varchar,"
                   #" location varchar, "
                   " followers_count integer,"
                   " friends_count integer,"
                   " listed_count integer, "
                   " favourites_count integer, "
                   " statuses_count integer, "
                   " user_created_at TIMESTAMP, "
                   " time_zone varchar, "
                   " user_lang varchar"
                   ");")
    cur.copy_from(file, 'user_base_table', sep= ",")



def create_tweet_tag_table(cur, filename):
    cur.execute("DROP TABLE IF EXISTS tweet_tag_table")
    file = open(filename)
    cur.execute("CREATE TABLE tweet_tag_table( "
                   " tweet_id varchar,"
                   " hashtag varchar"
                   ");")
    cur.copy_from(file, 'tweet_tag_table', sep= ",")

def create_edge_table(cur, filename):
    cur.execute("DROP TABLE IF EXISTS edge_table")
    file = open(filename)
    cur.execute("CREATE TABLE edge_table( "
                   " user_id_1 varchar,"
                   " user_id_2 varchar"
                   ");")
    cur.copy_from(file, 'edge_table', sep= ",")

def create_tweet_geo_table(cur, filename):
    cur.execute("DROP TABLE IF EXISTS tweet_geo_table")
    file = open(filename)
    cur.execute("CREATE TABLE tweet_geo_table( "
                   " tweet_id varchar,"
                   " coord1 numeric,"
                   " coord2 numeric"
                   ");")
    cur.copy_from(file, 'tweet_geo_table', sep= ",")


def print_out_table(cur, tablename):
    cur.execute('SELECT * FROM {} limit 20'.format(tablename))
    while(True):
           row = cur.fetchone()
           if row is not None:
               print row
           else:
               break

def copy_to_DB():
    try:
       con = psycopg2.connect(database='tweets')
       cur = con.cursor()
       cur.execute('SELECT version()')
       ver = cur.fetchone()
       print ver


       create_tweet_base_table(cur,
                            './table/tweet_base_table')
       create_user_base_table(cur,
                        './table/user_base_table')
       create_tweet_tag_table(cur,
                        './table/tweet_tag_table')
       create_tweet_geo_table(cur,
                        './table/tweet_geo_table')
       create_edge_table(cur,
                        './table/edge_table')

       print_out_table(cur, 'tweet_base_table')
       print_out_table(cur, 'user_base_table')
       print_out_table(cur, 'tweet_tag_table')
       print_out_table(cur, 'tweet_geo_table')
       print_out_table(cur, 'edge_table')


      # cur_tweet_base.execute('SELECT * FROM tweet_base_table')


    except psycopg2.DatabaseError, e:
           print 'Error %s' % e
           sys.exit(1)

    finally:
      if con:
         con.close()


def read_csv(file):
    data = []
    with open(file) as f:
        for line in f:
            data.append(line.strip('\n').lower())
    return data

def main():
    user_dir = 'table'
    if os.path.exists(user_dir):
       shutil.rmtree(user_dir)
    os.makedirs(user_dir)
    input_file = "./election_data/*.data"
    keyword_list = read_csv('candidates.txt')
    parse_json_file(input_file, keyword_list)
    copy_to_DB()

if __name__ == '__main__':
    main()