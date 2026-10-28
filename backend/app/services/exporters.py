def stamp(seconds,vtt=False):
 ms=max(0,round(seconds*1000)); h,rem=divmod(ms,3600000); m,rem=divmod(rem,60000); s,ms=divmod(rem,1000); return f'{h:02}:{m:02}:{s:02}{"." if vtt else ","}{ms:03}'
def export_srt(lines): return '\n\n'.join(f'{i}\n{stamp(x["start"])} --> {stamp(x["end"])}\n{x["text"]}' for i,x in enumerate(lines,1))+'\n'
def export_vtt(lines): return 'WEBVTT\n\n'+'\n\n'.join(f'{stamp(x["start"],True)} --> {stamp(x["end"],True)}\n{x["text"]}' for x in lines)+'\n'
def export_txt(lines): return '\n'.join(x['text'] for x in lines)+'\n'
def ass_time(t):
 cs=max(0,round(t*100)); h,rem=divmod(cs,360000); m,rem=divmod(rem,6000); s,cs=divmod(rem,100); return f'{h}:{m:02}:{s:02}.{cs:02}'
def export_ass(lines):
 head='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Noto Sans,58,&H00FFFFFF,&H0000D7FF,&H00000000,&H80000000,1,0,1,3,1,2,80,80,70,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
 rows=[]
 for x in lines:
  text=x['text'].replace('{',r'\{').replace('}',r'\}').replace('\n',r'\N'); rows.append(f'Dialogue: 0,{ass_time(x["start"])},{ass_time(x["end"])},Default,,0,0,0,,{text}')
 return head+'\n'.join(rows)+'\n'
