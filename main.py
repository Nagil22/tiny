import os,json,urllib.request,time
E=os.environ.get("MAKEFUN_ENV_URL","http://store:8080")
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':20000}
PST=[0,0,0,0,0,0,0,0,5,10,10,-20,-20,10,10,5,5,-5,-10,0,0,-10,-5,5,0,0,0,20,20,0,0,0,5,5,5,10,10,5,5,5,10,10,10,20,20,10,10,10,20,20,20,30,30,20,20,20,0,0,0,0,0,0,0,0]
N=[-33,-31,-18,-14,14,18,31,33];K=[-33,-32,-31,-30,-18,-17,-16,-15,-14,-1,1,14,15,16,17,18,30,31,32,33]
D={'p':[0],'n':N,'b':[-17,-15,15,17],'r':[-16,-1,1,16],'q':[-17,-16,-15,-1,1,15,16,17],'k':K}
def post(p,d):
    r=urllib.request.Request(E+p,json.dumps(d).encode(),{'Content-Type':'application/json'})
    return json.loads(urllib.request.urlopen(r).read())
def parse(f):
    b=[None]*128;i=0
    for c in f.split()[0]:
        if c=='/':i+=8
        elif c.isdigit():i+=int(c)
        else:b[i]=c;i+=1
    return b
def gen(b,t):
    m=[]
    for i in range(128):
        if i&0x88:continue
        p=b[i]
        if not p or p.isupper()!=t:continue
        l=p.lower()
        if l=='p':
            f=i-16 if t else i+16
            if not b[f] and not f&0x88:m.append((i,f))
            for o in (-15,-17):
                j=i+o
                if not j&0x88 and b[j] and b[j].isupper()!=t:m.append((i,j))
        else:
            for o in D[l]:
                j=i+o
                while not j&0x88:
                    q=b[j]
                    if q and q.isupper()==t:break
                    m.append((i,j))
                    if q or l in 'nk':break
                    j+=o
    return m
def att(b,s,t):
    for i in range(128):
        if i&0x88:continue
        p=b[i]
        if not p or p.isupper()!=t:continue
        l=p.lower()
        if l=='p':
            if i+(16 if t else -16)+(-1 if s%16>i%16 else 1)==s:return 1
        elif l=='k':
            if abs(s-i)in(1,15,16,17):return 1
        else:
            for o in D[l]:
                j=i+o
                while not j&0x88:
                    if j==s:return 1
                    if b[j]:break
                    j+=o
    return 0
def legal(b,t):
    r=[]
    for f,to in gen(b,t):
        c=b[to];b[to]=b[f];b[f]=None
        k=next((i for i in range(128) if not i&0x88 and b[i]==('K' if t else 'k')),None)
        if k is None or not att(b,k,not t):r.append((f,to))
        b[f]=b[to];b[to]=c
    return r
def ev(b):
    s=0
    for i in range(128):
        if i&0x88:continue
        p=b[i]
        if p:
            v=V[p.lower()]+PST[(i>>4)*8+(i&7) if p.isupper() else 63-((i>>4)*8+(i&7))]
            s+=v if p.isupper() else -v
    return s
def sr(b,t,d,a,be):
    if d==0:return ev(b)
    ms=legal(b,t)
    if not ms:return -9999 if t else 9999
    ms.sort(key=lambda m:V.get((b[m[1]] or ' ').lower(),0)-V.get(b[m[0]].lower(),0),reverse=True)
    for f,to in ms:
        c=b[to];b[to]=b[f];b[f]=None
        s=-sr(b,not t,d-1,-be,-a)
        b[f]=b[to];b[to]=c
        if s>=be:return be
        if s>a:a=s
    return a
def main():
    g=post("/game",{})
    while g.get("status")=="your_move":
        b=parse(g["fen"]);t=g["fen"].split()[1]=='w'
        best=None;bs=-99999
        for m in g["legal_moves"]:
            f=(8-int(m[1]))*16+(ord(m[0])-97)
            to=(8-int(m[3]))*16+(ord(m[2])-97)
            c=b[to];b[to]=b[f];b[f]=None
            s=-sr(b,not t,3,-99999,99999)
            b[f]=b[to];b[to]=c
            if s>bs:bs=s;best=m
        g=post("/move",{"game":g["game"],"move":best})
if __name__=="__main__":main()
