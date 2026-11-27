"""FINAL B2 (S1 window 1.47; micro-fades; 1 s end fade). Rough cut: six 5.333 s windows (one per shot, bars at 90 BPM), BT.601->BT.709, lanczos 720p->1080p, light unsharp.
Variants: music only / music + low-level original clip ambience."""
import subprocess, sys, os
D=5.333333
SH=[('01',1.47),('02',1.00),('03',2.30),('04',0.00),('05',0.93),('06',2.20)]
clips='06_clips'; music='07_output/music/score_v1.wav'
vf="scale=1920:1080:flags=lanczos:in_color_matrix=bt601:out_color_matrix=bt709,unsharp=5:5:0.6:5:5:0.0,format=yuv420p"
def build(out,ambience):
    cmd=['ffmpeg','-y','-v','error']
    for n,_ in SH: cmd+=['-i',f'{clips}/shot_{n}_v1.mp4']
    cmd+=['-i',music]
    fc=[]
    for i,(n,s) in enumerate(SH):
        fc.append(f'[{i}:v]trim=start={s}:end={s+D},setpts=PTS-STARTPTS,fps=24,{vf}[v{i}]')
    fc.append(''.join(f'[v{i}]' for i in range(len(SH)))+f'concat=n={len(SH)}:v=1:a=0[vout]')
    mi=len(SH)
    if ambience:
        for i,(n,s) in enumerate(SH):
            fc.append(f'[{i}:a]atrim=start={s}:end={s+D},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={D-0.02}:d=0.02[a{i}]')
        fc.append(''.join(f'[a{i}]' for i in range(len(SH)))+f'concat=n={len(SH)}:v=0:a=1,volume=0.35[amb]')
        fc.append(f'[{mi}:a]atrim=0:32,asetpts=PTS-STARTPTS,aresample=48000[mus]')
        fc.append('[mus][amb]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95,afade=t=out:st=31.0:d=1.0[aout]')
    else:
        fc.append(f'[{mi}:a]atrim=0:32,asetpts=PTS-STARTPTS,aresample=48000,alimiter=limit=0.95[aout]')
    cmd+=['-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]',
          '-c:v','libx264','-crf','16','-preset','slow','-pix_fmt','yuv420p',
          '-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv',
          '-c:a','aac','-b:a','256k','-movflags','+faststart','-t','32',out]
    subprocess.run(cmd,check=True)
os.makedirs('07_output',exist_ok=True)
which=sys.argv[1] if len(sys.argv)>1 else 'both'
if which in('music','both'): pass
if which in('ambience','both'): build('07_output/final_finish_line_B2.mp4',True)
