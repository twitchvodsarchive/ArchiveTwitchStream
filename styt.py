import os
import logging
import time
import config

this_key = config.rtmp_key
exe_ff = config.ffmpeg_exe

def this():
  t = time.localtime()
  current_time = time.strftime("%H:%M:%S", t)
  command = 'streamlink --twitch-low-latency twitch.tv/' + config.username + ' best -o - | ' + exe_ff + ' -re -i pipe:0 -c:v copy -c:a aac -ar 44100 -ab 128k -ac 2 -strict -2 -flags +global_header -bsf:a aac_adtstoasc -b:v 6300k -preset fast -f flv rtmp://a.rtmp.youtube.com/live2/' + this_key
  os.system(command)
  logging.info('stream has finish no loop it')

if __name__ == "__main__":
   logging.basicConfig(filename="styt.log", level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
   logging.getLogger().addHandler(logging.StreamHandler())
   logging.info('script is started now')
   this()
   exit()
