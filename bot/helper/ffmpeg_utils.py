import asyncio
import os
import sys
import json
import time


import ffmpeg
from subprocess import call, check_output
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

def get_codec(filepath, channel='v:0'):
    output = check_output(['ffprobe', '-v', 'error', '-select_streams', channel,
                            '-show_entries', 'stream=codec_name,codec_tag_string', '-of', 
                            'default=nokey=1:noprint_wrappers=1', filepath])
    return output.decode('utf-8').split()

async def encode(filepath,chatid):
    enpa="encode\\"+str(chatid)
    os.makedirs(enpa,exist_ok=True)
    basefilepath, extension = os.path.splitext(filepath)
    print("basefilepath : "+basefilepath+" | extension : "+extension)
    output_filepath =  basefilepath + '.HEVC' + '.mp4'
    output_filepath=str(output_filepath).replace("downloads",enpa)
    assert(output_filepath != filepath)
    if os.path.isfile(output_filepath):
        print('Skipping "{}": file already exists'.format(output_filepath))
        return output_filepath
    print(filepath)
    # Get the video channel codec
    video_codec = get_codec(filepath, channel='v:0')
    if video_codec == []:
        print('Skipping: no video codec reported')
        return None
    # Video transcode options
   # if video_codec[0] == 'hevc':
    #    if video_codec[1] == 'hvc1':
     #       print('Skipping: already h265 / hvc1')
      #      return None
       # else:
            # Copy stream to hvc1
        #    video_opts = '-c:v copy -tag:v hvc1'
    #else:
        # Transcode to h265 / hvc1
    video_opts =  '-preset ultrafast -c:v libx265 -crf 27 -map 0:v'

    # Get the audio channel codec
    audio_codec = get_codec(filepath, channel='a:0')
    if audio_codec == []:
        audio_opts = ''
    elif audio_codec[0] == 'aac':
        audio_opts = '-c:a copy -map 0:a'
    else:
        audio_opts = '-c:a aac -map 0:a'

    subtitle_opts=" -c:s copy -map 0:s? "
    print((['ffmpeg', '-i', filepath] + video_opts.split() + audio_opts.split() +subtitle_opts.split()+ [output_filepath,'-y']))
    call(['ffmpeg', '-i', filepath] + video_opts.split() + audio_opts.split() +subtitle_opts.split()+ [output_filepath,'-y'])
    #call(['ffmpeg', '-i', filepath] + video_opts.split() + audio_opts.split() + [output_filepath])

    #os.remove(filepath)
    return output_filepath






def get_thumbnail(in_filename, path, ttl):
    out_filename = os.path.join(path, in_filename + ".jpg")
    os.makedirs(path,exist_ok=True)
    open(out_filename, 'a').close()
    try:
        (
            ffmpeg
            .input(in_filename,ss=ttl)
            .output(out_filename, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return out_filename
    except ffmpeg.Error as e:
      return None

def get_duration(filepath):
    metadata = extractMetadata(createParser(filepath))
    if metadata.has("duration"):
      return metadata.get('duration').seconds
    else:
      return 0

def get_width_height(filepath):
    metadata = extractMetadata(createParser(filepath))
    if metadata.has("width") and metadata.has("height"):
      return metadata.get("width"), metadata.get("height")
    else:
      return 1280, 720
