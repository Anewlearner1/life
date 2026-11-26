"""Synthesize a 32 s instrumental score at 90 BPM (12 bars of 4/4) for 《終點線》.
Bars 1-6 verse (sparse piano + soft pad), 7-10 chorus (strings, low hits, piano octaves),
bar 10 downbeat (24.0 s) = finish-tape hit, bars 11-12 resolve to C and ring out."""
import numpy as np, wave, sys, os
SR=48000; BPM=90; BEAT=60/BPM; BAR=4*BEAT; DUR=32.0
N=int(SR*(DUR+0.0)); L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
def hz(n): return 440*2**((n-69)/12)
NOTE={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def m(s):  # 'A3' -> midi
    return 12*(int(s[-1])+1)+NOTE[s[0]]+(1 if '#' in s else 0)
def add(sig,t,pan=0.0,gain=1.0):
    i=int(t*SR); j=min(N,i+len(sig)); sig=sig[:j-i]*gain
    L[i:j]+=sig*np.sqrt((1-pan)/2); R[i:j]+=sig*np.sqrt((1+pan)/2)
def piano(n,dur=2.5,vel=0.5):
    t=np.arange(int(SR*dur))/SR; f=hz(n); s=np.zeros_like(t)
    for k,a in enumerate([1,.5,.28,.15,.08,.05],1):
        s+=a*np.sin(2*np.pi*f*k*t*(1+0.0004*k*k))*np.exp(-t*(1.2+0.9*k))
    att=np.minimum(1,t/0.004); return vel*s*att
def pad(notes,dur,vel=0.12,att=1.2):
    t=np.arange(int(SR*dur))/SR; s=np.zeros_like(t)
    for n in notes:
        for d in (-0.08,0,0.08):
            ph=2*np.pi*hz(n)*2**(d/12)*t
            s+=np.sin(ph)+0.3*np.sin(2*ph)+0.12*np.sin(3*ph)
    env=np.minimum(1,t/att)*np.minimum(1,(dur-t)/0.8)
    return vel*s*env/len(notes)
def boom(vel=0.9,dur=1.6):
    t=np.arange(int(SR*dur))/SR
    f=45+70*np.exp(-t*18); s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3.2)
    nz=rng.standard_normal(len(t))*np.exp(-t*40)*0.15
    return vel*(s+nz)
def swell(dur,vel=0.25):
    t=np.arange(int(SR*dur))/SR; nz=rng.standard_normal(len(t))
    nz=np.convolve(nz,np.ones(40)/40,'same'); return vel*nz*(t/dur)**2
CH={'Am':['A2','C4','E4','A4'],'F':['F2','A3','C4','F4'],'C':['C3','E4','G4','C5'],'G':['G2','B3','D4','G4'],
    'Em':['E2','B3','E4','G4'],'Dm':['D3','A3','D4','F4']}
prog=['Am','F','C','G','Am','F','F','G','Am','C','F','C']   # one chord per bar
for b,c in enumerate(prog):
    t0=b*BAR; notes=[m(x) for x in CH[c]]
    chorus=6<=b<=9; outro=b>=10
    # bass note
    add(piano(notes[0],3.5,0.35 if not chorus else 0.5),t0,-0.2)
    # piano arpeggio (8ths in verse, quarters doubled in chorus)
    arp=[notes[1],notes[2],notes[3],notes[2]]*2
    for i,n in enumerate(arp):
        if b<2 and i%2: continue                       # very sparse at start
        add(piano(n+(12 if chorus and i%2==0 else 0),2.0,0.22 if not chorus else 0.28),t0+i*BEAT/2,0.25 if i%2 else -0.1)
    # pad from bar 3, strings-like in chorus
    if b>=2: add(pad(notes[1:]+([notes[1]+12] if chorus else []),BAR+0.6,0.10 if b<6 else 0.2,1.0 if b<6 else 0.3),t0,0)
    # low hits
    if chorus or b==5: add(boom(0.55 if b==5 else 0.8),t0,0)
    if chorus: add(boom(0.35),t0+2*BEAT,0)
# accents
add(boom(0.5,1.2),0.9,0)                 # S1 fall (~0.9 s into film)
add(swell(BAR,0.18),5*BAR,0.0)           # riser into chorus at 16 s
add(swell(BEAT*2,0.2),24.0-2*BEAT,0.0)   # riser into tape break
add(boom(1.0,2.2),24.0,0)                # finish tape hit (bar 10 downbeat)
add(pad([m('C4'),m('E4'),m('G4'),m('C5')],2*BAR,0.18,0.5),10*BAR,0)  # outro bed
# simple reverb
ir_t=np.arange(int(SR*1.8))/SR; ir=rng.standard_normal(len(ir_t))*np.exp(-ir_t*3.0)*0.02
def rev(x): 
    from numpy.fft import rfft,irfft; n=len(x)+len(ir); n2=1<<(n-1).bit_length()
    return irfft(rfft(x,n2)*rfft(ir,n2),n2)[:len(x)]
L=L+rev(L)*0.6; R=R+rev(R[::-1])[::-1]*0+rev(R)*0.6
# fade in 0.05 s, fade out last 2.5 s
env=np.ones(N); fi=int(0.05*SR); env[:fi]=np.linspace(0,1,fi)
fo=int(2.5*SR); env[-fo:]=np.linspace(1,0,fo)**1.5
L*=env; R*=env
peak=max(abs(L).max(),abs(R).max()); L=L/peak*0.89; R=R/peak*0.89
out=sys.argv[1]
os.makedirs(os.path.dirname(out),exist_ok=True)
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([L,R],1)*32767).astype('<i2').tobytes())
print('wrote',out,N/SR,'s')
