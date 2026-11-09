#!/usr/bin/env python3
# 備份回復專員 dashboard v1.4 (usage + backup log + restore log); own code, no third-party content.
# Data:    usage_dash.py --lang zh|en [--input report.txt] [--failing "a,b"]
# Log:     usage_dash.py --log backup|restore --data '{json}'
# Check:   usage_dash.py --check 1 [--remind-days N]
# Prune:   usage_dash.py --prune "path1|path2"
import argparse,datetime,glob,json,os,re,shutil
try:
    from zoneinfo import ZoneInfo;TZ=ZoneInfo('Europe/London')
except Exception: TZ=None
p=argparse.ArgumentParser()
for k,d in [('--lang','zh'),('--input',''),('--dir','/workspace/Bot 備份/用量'),('--logs','/workspace/Bot 備份/紀錄'),('--out',''),
            ('--view',''),('--failing',''),('--log',''),('--data',''),('--root','/workspace/Bot 備份'),('--remind-days','7'),
            ('--cleanup-gb','1'),('--cleanup-max','10'),('--check',''),('--prune','')]: p.add_argument(k,default=d)
a=p.parse_args();Z=a.lang!='en';T=lambda zh,en:zh if Z else en
NOW=datetime.datetime.now(TZ)
# ---------- 紀錄（只存允許的欄位，絕不存密碼、金鑰或登入資料） ----------
BAD=re.compile(r'password|passwd|token|secret|api[_-]?key|cookie|bearer|密碼|金鑰|登入',re.I)
def clean(o):
    if isinstance(o,dict): return {k:clean(v) for k,v in o.items() if not BAD.search(str(k))}
    if isinstance(o,list): return [clean(x) for x in o]
    if isinstance(o,str) and (re.search(r'(password|passwd|secret|api[_-]?key|token|bearer|密碼|金鑰)\s*[:=：]',o,re.I) or re.search(r'[A-Za-z0-9_\-]{32,}',o)): return '[已略去]'
    return o
def rows(n):
    f=os.path.join(a.logs,n+'.jsonl');o=[]
    if os.path.exists(f):
        for ln in open(f,encoding='utf-8'):
            try: o.append(json.loads(ln))
            except Exception: pass
    o=sorted(o,key=lambda r:r.get('time') or r.get('date') or '',reverse=True)
    if n!='backups': return o
    m={}  # 同一 time 的雲端／桌面副本紀錄合併為一次備份
    for r in o:
        k=r.get('time','')
        if k in m:
            for l in r.get('locations',[]):
                if l not in m[k].setdefault('locations',[]): m[k]['locations'].append(l)
        else: m[k]=dict(r)
    return list(m.values())
def mb(r):
    if isinstance(r.get('size_bytes'),(int,float)): return r['size_bytes']/1e6
    x=re.match(r'([\d.]+)\s*(KB|MB|GB|TB)',str(r.get('size','')),re.I)
    return float(x.group(1))*{'KB':1e-3,'MB':1,'GB':1e3,'TB':1e6}[x.group(2).upper()] if x else None
def fmt_mb(v): return f'{v/1000:.1f} GB' if abs(v)>=1000 else f'{v:.0f} MB'
def diff(cur,prev):
    if not cur or not prev: return None
    c,q=cur.get('counts',{}),prev.get('counts',{});o={'counts':{}}
    for k in ('memories','routines','skills','settings'):
        if isinstance(c.get(k),int) and isinstance(q.get(k),int): o['counts'][k]=c[k]-q[k]
    a1,a0=set(cur.get('role_names') or []),set(prev.get('role_names') or [])
    o['roles_added'],o['roles_removed']=(sorted(a1-a0),sorted(a0-a1)) if a1 and a0 else ([],[])
    if isinstance(cur.get('roles'),int) and isinstance(prev.get('roles'),int): o['roles_delta']=cur['roles']-prev['roles']
    m1,m0=mb(cur),mb(prev);o['size_mb']=None if m1 is None or m0 is None else m1-m0
    return o
CNAME={'memories':('記憶','memories'),'routines':('定時任務','routines'),'skills':('技能','skills'),'settings':('設定','settings')}
def sg(v): return f'+{v}' if v>0 else ('−'+str(-v) if v<0 else '±0')
def diff_line(d):
    if not d: return T('首次備份紀錄，下次開始比較。','First logged backup; comparison starts next time.')
    parts=[f'{T(CNAME[k][0],CNAME[k][1])} {sg(v)}' for k,v in d['counts'].items()]
    if d['roles_added']: parts.append(T('新增角色 ','roles added: ')+'、'.join(d['roles_added']))
    if d['roles_removed']: parts.append(T('少了角色 ','roles removed: ')+'、'.join(d['roles_removed']))
    if d['size_mb'] is not None: parts.append(T('大小 ','size ')+('+' if d['size_mb']>=0 else '−')+fmt_mb(abs(d['size_mb'])))
    return T('與上次比較：','Since last backup: ')+('，' if Z else ', ').join(parts)+('。' if Z else '.')
if a.log:
    assert a.log in ('backup','restore');r=clean(json.loads(a.data))
    r.setdefault('time' if a.log=='backup' else 'date',NOW.strftime('%Y-%m-%d %H:%M'));r.setdefault('tz','Europe/London')
    prev=rows('backups') if a.log=='backup' else []
    os.makedirs(a.logs,exist_ok=True);open(os.path.join(a.logs,a.log+'s.jsonl'),'a',encoding='utf-8').write(json.dumps(r,ensure_ascii=False)+'\n')
    if a.log=='backup':
        pv=next((x for x in prev if x.get('time')!=r['time']),None)
        print(json.dumps({'ok':True,'diff_line':'' if any(x.get('time')==r['time'] for x in prev) else diff_line(diff(r,pv))},ensure_ascii=False))
    else: print('ok')
    raise SystemExit
# ---------- 主選單檢查（只讀本機檔案） ----------
BKDIR=re.compile(r'\d{4}-\d\d-\d\d.*')
def dsize(p):
    t=0
    for dp,_,fs in os.walk(p):
        for f in fs:
            try: t+=os.lstat(os.path.join(dp,f)).st_size
            except OSError: pass
    return t
def folders():
    return sorted([os.path.join(a.root,d) for d in os.listdir(a.root) if BKDIR.fullmatch(d) and os.path.isdir(os.path.join(a.root,d))]) if os.path.isdir(a.root) else []
if a.check:
    bk=rows('backups');days=None;line=''
    if bk:
        try: days=(NOW.date()-datetime.date.fromisoformat(bk[0]['time'][:10])).days
        except Exception: days=None
    if days is None and not bk: line=T('尚未有備份紀錄','No backup has been logged yet')
    elif days is not None and days>int(a.remind_days): line=T(f'上次備份已是 {days} 日前',f'Last backup was {days} days ago')
    fs=[(f,dsize(f)) for f in folders()];tot=sum(z for _,z in fs);lim=float(a.cleanup_gb)*1e9;mx=int(a.cleanup_max);pick=[]
    if tot>lim or len(fs)>mx:
        cand=fs[:-3] if len(fs)>3 else [];t=tot;n=len(fs)
        for f,z in cand:
            if t<=lim and n<=mx: break
            pick.append({'path':f,'size':fmt_mb(z/1e6)});t-=z;n-=1
    print(json.dumps({'days_since_backup':days,'reminder':line,'total':fmt_mb(tot/1e6),'backups':len(fs),
        'cleanup':{'folders':pick,'keep':[os.path.basename(f) for f,_ in fs[-3:]]} if pick else None},ensure_ascii=False,indent=1))
    raise SystemExit
if a.prune:  # 只在用戶於確認卡按「刪除這些」後使用；只限 bot 電腦，不碰雲端
    fs=folders();keep=set(fs[-3:]);done=[]
    for f in [x.strip() for x in a.prune.split('|') if x.strip()]:
        f=os.path.abspath(f)
        if os.path.dirname(f)==os.path.abspath(a.root) and f in fs and f not in keep:
            shutil.rmtree(f);done.append(os.path.basename(f))
    print(json.dumps({'deleted':done},ensure_ascii=False));raise SystemExit
BK,RS=rows('backups'),rows('restores')
# ---------- 用量 ----------
os.makedirs(a.dir,exist_ok=True)
snaps=sorted(f for f in glob.glob(os.path.join(a.dir,'*.json')) if re.fullmatch(r'\d{4}-\d\d-\d\d-\d{4}\.json',os.path.basename(f)))
def load(f):
    try: return json.load(open(f,encoding='utf-8'))
    except Exception: return None
snap=old=None;stamp=NOW.strftime('%Y-%m-%d-%H%M')
if a.input:
    txt=open(a.input,encoding='utf-8').read()
    g=lambda r:(re.search(r,txt).group(1).strip() if re.search(r,txt) else '')
    snap={'time':NOW.strftime('%Y-%m-%d %H:%M'),'plan':g(r'Plan:\s*(.+)'),'used':g(r'usage limit:\s*([\d.]+%)'),
     'reset':g(r'resets\s+(.+?)\s+their local time'),'left':g(r'\(in ([^)]+)\)'),'period':g(r'usage (?:this week|in the last [^(]*)\s*\(([^)]+)\)'),'bots':{}}
    cur=None
    for ln in txt.splitlines():
        m=re.match(r'^(\s*)- (.+?): (<)?(\d+(?:\.\d+)?)%(?:, (.*))?$',ln)
        if not m: continue
        sh=0.5 if m.group(3) else float(m.group(4));name=m.group(2).strip();note=m.group(5) or ''
        if not m.group(1): cur=name;snap['bots'][name]={'share':sh,'routines':{}}
        elif cur:
            if name.lower().startswith('not from a routine'): snap['bots'][cur]['chat']=sh;continue
            r=re.search(r'about (\d+) runs? a week',note)
            snap['bots'][cur]['routines'][name]={'share':sh,'runs':int(r.group(1)) if r else None,'trigger':'watches' in note}
    old=load(snaps[-1]) if snaps else None
    json.dump(snap,open(os.path.join(a.dir,stamp+'.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
elif snaps:
    snap=load(snaps[-1]);old=load(snaps[-2]) if len(snaps)>1 else None;stamp=os.path.basename(snaps[-1])[:-5]
snap=snap or {'time':'','plan':'','used':'','reset':'','left':'','period':'','bots':{}}
def zhreset(x):
    m=re.match(r'(\w+), (\w+) (\d+) at (\d+:\d+)',x or '');W=dict(Monday='一',Tuesday='二',Wednesday='三',Thursday='四',Friday='五',Saturday='六',Sunday='日')
    M='Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
    return f"{M.index(m.group(2)[:3])+1}月{m.group(3)}日（{W.get(m.group(1),'')}）{m.group(4)}" if Z and m and m.group(2)[:3] in M else (x or '')
RESET=zhreset(snap['reset']);LEFT=(snap['left'].replace('d ','日 ').replace('d','日').replace('h','小時') if Z else snap['left'])
SPECIAL=('deleted','other people','group chat')
DN=lambda b:(T('已刪除的 bot、群組對話及他人的 bot','Deleted bots, group chats & others') if b.lower().startswith('deleted bots') else b)
def flat(s):
    o={}
    for b,v in (s or {}).get('bots',{}).items():
        o[b]=v['share']
        for r,rv in v['routines'].items(): o[b+' › '+r]=rv['share']
    return o
new,up=[],[]
if old:
    fo,fn=flat(old),flat(snap)
    for k,v in fn.items():
        if k not in fo and not any(x in k.lower() for x in SPECIAL): new.append((k,v))
        elif k in fo and v-fo[k]>=2: up.append((k,fo[k],v))
# 建議：只列受影響佔比 ≥5%，最多 2 條，每條一句
KW=[('新聞|動向|摘要|news|digest|trend',T('新聞','news')),('同步|sync|運動|health|workout',T('運動同步','workout sync')),
    ('郵件|電郵|mail|inbox',T('郵件','mail')),('備份|backup',T('備份','backup')),('研究|research',T('研究','research'))]
SN=lambda b:re.split(r'\s*[・·．]\s*',b)[0].strip() or b
P=lambda x:int(x+0.5);NUM=dict(zip(range(2,10),'兩三四五六七八九'))
PCT=lambda x:T(f'（佔約 {P(x)}%）',f' (about {P(x)}% of usage)')
R=[(b,r,v) for b,bv in snap['bots'].items() for r,v in bv['routines'].items() if not any(x in r.lower() for x in SPECIAL)]
sug=[];fail=[x.strip() for x in a.failing.split(',') if x.strip()]
for pat,lab in KW:
    grp=[(b,r,v) for b,r,v in R if re.search(pat,r,re.I)]
    if len(grp)<2: continue
    tot=sum(v['share'] for _,_,v in grp);bs=list(dict.fromkeys(SN(b) for b,_,_ in grp));n=len(grp)
    t=(T(f'合併{bs[0]}{NUM.get(n,n)}個{lab}任務',f"Merge {bs[0]}'s {n} {lab} routines") if len(bs)==1 else T(f'合併{"、".join(bs)}的{lab}任務',f"Merge the {lab} routines of {', '.join(bs)}"))+PCT(tot)
    sug.append((tot,'merge',t,[r for _,r,_ in grp]))
merged={t for x in sug for t in x[3]}
for b,r,v in R:
    if r in merged and r not in fail: continue
    if r in fail: sug.append((v['share'],'pause',T(f'暫停{SN(b)}的「{r}」',f'Pause {SN(b)}\'s "{r}"')+PCT(v['share']),[r]))
    elif v['trigger']: sug.append((v['share'],'batch',T(f'把「{r}」改為每日處理一次',f'Batch "{r}" into one daily run')+PCT(v['share']),[r]))
    elif (v['runs'] or 0)>=7: sug.append((v['share'],'freq',T(f'把「{r}」改為只在工作日執行',f'Run "{r}" on weekdays only')+PCT(v['share']),[r]))
sug=sorted([x for x in sug if x[0]>=5],key=lambda x:-x[0])[:2]
NONE=T('暫無值得調整的項目','Nothing worth changing right now')
# ---------- 文字（後備）及結構化資料（供 Grok Page） ----------
LOC={'bot':T('bot 電腦','Bot computer'),'drive':'Google Drive','notion':'Notion','desktop':T('桌面副本','Desktop copy'),'download':T('下載 .zip','.zip download')}
CN=[('memories',T('記憶','Memories')),('routines',T('定時任務','Routines')),('skills',T('技能','Skills')),('settings',T('設定','Settings'))]
ST=lambda s:T('完整','Complete') if s=='complete' else T('部分完成','Partial')
def ago(t):
    try:
        d=(NOW.date()-datetime.date.fromisoformat(t[:10])).days;return T('今日','today') if d==0 else T(f'{d} 日前',f'{d} days ago')
    except Exception: return ''
def locs(r): return T('、',', ').join(LOC.get(l.get('type'),l.get('type','')) for l in r.get('locations',[]))
TX={'usage':'\n'.join([T('用量','Usage')+f" {snap['time']}",T('已用','Used')+f": {snap['used'] or '—'}  "+T('重設','Resets')+f": {RESET} ({LEFT})"]
     +[f"- {DN(b)}: {v['share']:g}%" for b,v in sorted(snap['bots'].items(),key=lambda x:-x[1]['share'])]+[T('建議','Suggestions')+':']+([f'  {i+1}. {s[2]}' for i,s in enumerate(sug)] or ['  '+NONE])),
    'backups':'\n'.join([T('備份紀錄','Backup log')]+[f"- {r.get('time')} · {locs(r)} · {ST(r.get('status'))}" for r in BK[:6]] or [T('未有備份紀錄','No backups yet')]),
    'restores':'\n'.join([T('回復紀錄','Restore log')]+[f"- {r.get('date')} · {T('來源','from')} {r.get('source')} · "+', '.join(x.get('name','') for x in r.get('roles',[])) for r in RS[:6]] or [T('未有回復紀錄','No restores yet')])}
bots_out=[{'name':DN(b),'share':v['share'],
    'routines':[{'name':rn,'share':rv['share'],'runs':rv.get('runs'),'trigger':bool(rv.get('trigger'))} for rn,rv in v.get('routines',{}).items()],
    'chat':v.get('chat')} for b,v in sorted(snap['bots'].items(),key=lambda x:-x[1]['share'])]
bk_out=[]
for i,r in enumerate(BK[:12]):
    item={'time':r.get('time'),'ago':ago(r.get('time','')),'locations':[{'type':l.get('type'),'label':LOC.get(l.get('type'),l.get('type','')),'path':l.get('path','')} for l in r.get('locations',[])],
          'roles':r.get('roles'),'counts':r.get('counts') or {},'size':r.get('size',''),'status':r.get('status'),'status_label':ST(r.get('status')),'notes':r.get('notes') or ''}
    if i==0:
        d=diff(r,BK[1] if len(BK)>1 else None)
        item['diff_line']=diff_line(d);item['diff']=d
    bk_out.append(item)
rs_out=[{'date':r.get('date'),'ago':ago(r.get('date','')),'source':r.get('source',''),
         'roles':[{'name':x.get('name',''),'mode':x.get('mode','')} for x in r.get('roles',[])],
         'added':r.get('added') or {},'skipped':r.get('skipped') or [],'status':r.get('status')} for r in RS[:12]]
menu=[T('更新','Refresh')]+[T('照做：','Do it: ')+s[2] for s in sug]+[T('返回主選單','Back to main menu')]
out={
 'lang':'zh' if Z else 'en',
 'updated':NOW.strftime('%Y-%m-%d %H:%M'),
 'usage':{'time':snap.get('time',''),'plan':snap.get('plan',''),'used':snap.get('used',''),'reset':RESET,'left':LEFT,
          'period':snap.get('period',''),'bots':bots_out,
          'compare':{'new':len(new),'up':len(up),'first':not bool(old)},
          'suggestions_none':NONE},
 'backups':bk_out,
 'restores':rs_out,
 'text':TX,
 'suggestions':[{'kind':s[1],'text':s[2],'targets':s[3]} for s in sug],
 'menu':menu,
 'footer':{'mark':'m','label':'minny.app','href':'https://minny.app'},
 'tabs':[{'id':'usage','label':T('用量','Usage')},{'id':'backups','label':T('備份紀錄','Backups')},{'id':'restores','label':T('回復紀錄','Restores')}],
 'title':T('備份回復專員','Backup & Restore Officer'),
 'summary':T(f"每週用量上限已用 {snap.get('used') or '—'}，重設：{RESET or '—'}（{LEFT or '—'}）",
             f"Weekly usage limit {snap.get('used') or '—'} used; resets {RESET or '—'} ({LEFT or '—'})")
}
print(json.dumps(out,ensure_ascii=False,indent=1))
