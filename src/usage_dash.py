#!/usr/bin/env python3
# 備份回復專員 dashboard v1.4 (usage + backup log + restore log); own code, no third-party content.
# Render:  usage_dash.py --lang zh|en [--input report.txt] [--view 1180x820] [--failing "a,b"]
# Log:     usage_dash.py --log backup|restore --data '{json}'
import argparse,datetime,glob,html,json,os,re,shutil,subprocess
try:
    from zoneinfo import ZoneInfo;TZ=ZoneInfo('Europe/London')
except Exception: TZ=None
p=argparse.ArgumentParser()
for k,d in [('--lang','zh'),('--input',''),('--dir','Bot 備份/用量'),('--logs','Bot 備份/紀錄'),('--out',''),
            ('--view','1180x820'),('--failing',''),('--log',''),('--data',''),('--root','Bot 備份'),('--remind-days','7'),
            ('--cleanup-gb','1'),('--cleanup-max','10'),('--check',''),('--prune','')]: p.add_argument(k,default=d)
a=p.parse_args();Z=a.lang!='en';T=lambda zh,en:zh if Z else en
NOW=datetime.datetime.now(TZ);e=html.escape
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
    c,q=cur.get('counts',{}),prev.get('counts',{});o={'counts':{},'sample':bool(cur.get('sample') or prev.get('sample'))}
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
# ---------- 文字（後備） ----------
LOC={'bot':T('bot 電腦','Bot computer'),'drive':'Google Drive','notion':'Notion','desktop':T('桌面副本','Desktop copy'),'download':T('下載 .zip','.zip download')}
ICON={'bot':'▣','drive':'△','notion':'N','desktop':'⌂','download':'↓'}
CN=[('memories',T('記憶','Memories')),('routines',T('定時任務','Routines')),('skills',T('技能','Skills')),('settings',T('設定','Settings'))]
ST=lambda s:T('完整','Complete') if s=='complete' else T('部分完成','Partial')
def ago(t):
    try:
        d=(NOW.date()-datetime.date.fromisoformat(t[:10])).days;return T('今日','today') if d==0 else T(f'{d} 日前',f'{d} days ago')
    except Exception: return ''
def locs(r): return T('、',', ').join(LOC.get(l.get('type'),l.get('type','')) for l in r.get('locations',[]))
TX={'usage':'\n'.join([T('用量','Usage')+f" {snap['time']}",T('已用','Used')+f": {snap['used'] or '—'}  "+T('重設','Resets')+f": {RESET} ({LEFT})"]
     +[f"- {DN(b)}: {v['share']:g}%" for b,v in sorted(snap['bots'].items(),key=lambda x:-x[1]['share'])]+[T('建議','Suggestions')+':']+([f'  {i+1}. {s[2]}' for i,s in enumerate(sug)] or ['  '+NONE])),
    'backups':'\n'.join([T('備份紀錄','Backup log')]+[f"- {r.get('time')} · {locs(r)} · {ST(r.get('status'))}"+(' ['+T('示例','sample')+']' if r.get('sample') else '') for r in BK[:6]] or [T('未有備份紀錄','No backups yet')]),
    'restores':'\n'.join([T('回復紀錄','Restore log')]+[f"- {r.get('date')} · {T('來源','from')} {r.get('source')} · "+', '.join(x.get('name','') for x in r.get('roles',[]))+(' ['+T('示例','sample')+']' if r.get('sample') else '') for r in RS[:6]] or [T('未有回復紀錄','No restores yet')])}
# ---------- HTML ----------
CSS='''*{box-sizing:border-box}html,body{margin:0;height:100%;overflow:hidden}
body{font-family:"Inter","Noto Sans CJK TC","Noto Sans CJK HK",system-ui,sans-serif;background:#eef1f6;color:#151a26;-webkit-font-smoothing:antialiased}
.app{height:100vh;display:flex;flex-direction:column;gap:14px;padding:22px 34px 10px}
.top{display:flex;align-items:center;gap:14px}.logo{width:42px;height:42px;border-radius:12px;background:linear-gradient(140deg,#4f7cff,#7a5cff);display:grid;place-items:center;color:#fff;font-size:21px;box-shadow:0 6px 16px #4f7cff40}
.brand b{display:block;font-size:19px;letter-spacing:.2px}.brand small{color:#7a8396;font-size:13px}
.tabs{margin-left:auto;display:flex;background:#e2e6ee;border-radius:12px;padding:4px;gap:2px}.tabs span{padding:8px 18px;border-radius:9px;font-size:15px;color:#596275;font-weight:500;white-space:nowrap}
.tabs .on{background:#fff;color:#151a26;font-weight:650;box-shadow:0 1px 3px #0002}
.main{flex:1;min-height:0;display:grid;gap:16px}
.card{background:#fff;border-radius:18px;padding:20px 22px;box-shadow:0 1px 2px #0000000d,0 8px 24px #1b2a4a0d;min-height:0;overflow:hidden;display:flex;flex-direction:column}
h3{margin:0 0 14px;font-size:14px;color:#7a8396;font-weight:600;letter-spacing:.3px;text-transform:uppercase}
.u{grid-template-columns:330px 1fr;grid-template-rows:1fr auto}
.ring{width:190px;height:190px;border-radius:50%;margin:6px auto 16px;background:conic-gradient(#4f7cff calc(var(--p)*1%),#e8ecf3 0);display:grid;place-items:center}
.ring div{width:150px;height:150px;border-radius:50%;background:#fff;display:grid;place-items:center;text-align:center}.ring b{font-size:38px;letter-spacing:-1px}.ring small{display:block;color:#7a8396;font-size:13px}
.kv{display:flex;justify-content:space-between;padding:9px 0;border-top:1px solid #eef0f4;font-size:15px}.kv span{color:#7a8396}
.bar{display:grid;grid-template-columns:1fr auto;align-items:center;gap:4px 12px;margin:0 0 13px}.bar span{font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.bar b{font-size:15px;font-variant-numeric:tabular-nums}
.bar i{grid-column:1/3;height:8px;border-radius:4px;background:#eef1f6;overflow:hidden}.bar i::after{content:"";display:block;height:100%;width:calc(var(--w)*1%);background:linear-gradient(90deg,#4f7cff,#7a5cff);border-radius:4px}
.bar.x i::after{background:#c3c9d6}.bars{flex:1;display:flex;flex-direction:column;justify-content:space-around}.bars .bar{margin:0}
.det{margin-top:auto;border-top:1px solid #eef0f4;padding-top:12px}.det div{display:grid;grid-template-columns:110px 1fr;gap:10px;padding:5px 0;font-size:14px}.det span{color:#7a8396}.det code{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:13px;color:#3a4256;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.empty{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px}.empty::before{content:"";width:56px;height:56px;border-radius:16px;background:#f1f4fa url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%239aa2b2' stroke-width='1.8'%3E%3Ccircle cx='12' cy='12' r='9'/%3E%3Cpath d='M12 7v5l3 2'/%3E%3C/svg%3E") center/26px no-repeat}
.sg{grid-column:1/3;display:flex;flex-direction:row;gap:14px;align-items:center;padding:16px 22px}.sg .t{font-size:14px;color:#7a8396;font-weight:600;white-space:nowrap}
.pill{display:inline-flex;align-items:center;gap:8px;background:#f2f5ff;color:#2d4fd6;border:1px solid #dfe6ff;border-radius:999px;padding:8px 14px;font-size:15px;font-weight:550}
.pill.m{background:#f4f5f8;color:#7a8396;border-color:#e6e8ee;font-weight:500}.chg{margin-left:auto;font-size:14px;color:#7a8396;white-space:nowrap}
.b{grid-template-columns:1.25fr 1fr}
.hero .when{font-size:34px;font-weight:700;letter-spacing:-.5px;margin:2px 0 4px}.sub{color:#7a8396;font-size:14px}
.st{display:inline-block;font-size:13px;font-weight:650;padding:4px 10px;border-radius:999px;margin-left:8px;vertical-align:middle}.ok{background:#e3f7ec;color:#14804a}.pa{background:#fff3df;color:#a35c00}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 16px}.chip{display:inline-flex;align-items:center;gap:7px;border:1px solid #e3e7ef;border-radius:10px;padding:6px 11px;font-size:14px;background:#fafbfd}
.chip i{font-style:normal;width:20px;height:20px;border-radius:6px;background:#eef2ff;color:#4f7cff;display:grid;place-items:center;font-size:12px;font-weight:700}
.chip.new i{background:#e3f7ec;color:#14804a}.chip.mg i{background:#fff3df;color:#a35c00}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;flex:1;max-height:150px}.tile{display:flex;flex-direction:column;justify-content:center;padding:14px 18px}.tile{background:#f6f8fb;border-radius:12px;padding:12px 14px}.tile b{display:block;font-size:40px;letter-spacing:-.5px}.tile span{font-size:13px;color:#7a8396}
.note{margin-top:14px;font-size:14px;color:#a35c00;background:#fff8ec;border-radius:10px;padding:10px 12px;line-height:1.45}
.row{display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center;padding:12px 0;border-top:1px solid #eef0f4}.row:first-of-type{border-top:0}
.row .d{width:10px;height:10px;border-radius:50%;background:#22a565}.row .d.pa{background:#f0a020}.row b{font-size:15px}.row small{display:block;color:#7a8396;font-size:13px;margin-top:2px}
.row .r{font-size:13px;color:#7a8396;text-align:right}.empty{color:#9aa2b2;font-size:15px;padding:24px 0;text-align:center}
.tag{font-size:11px;font-weight:700;color:#8a5cf6;background:#f1ebff;border-radius:6px;padding:2px 6px;margin-left:6px;vertical-align:middle}
.cmp{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:14px}.ct{font-size:13px;color:#7a8396;font-weight:600;margin-right:4px}
.dl{display:inline-flex;align-items:baseline;gap:6px;border-radius:9px;padding:6px 10px;font-size:15px;font-weight:650;font-variant-numeric:tabular-nums}.dl small{font-size:12px;font-weight:500;opacity:.8}
.dl.up{background:#e3f7ec;color:#14804a}.dl.dn{background:#fde8e8;color:#b42318}.dl.eq{background:#f1f3f7;color:#596275}
.banner{background:#f1ebff;color:#5b3ab8;border-radius:12px;padding:9px 14px;font-size:14px}
@media (max-width:900px){.u,.b{grid-template-columns:1fr;grid-template-rows:none}.sg{grid-column:auto}}
@media (max-width:900px) and (min-width:601px){.app{padding:30px}.u .card:first-child{display:grid;grid-template-columns:200px 1fr;gap:0 24px;align-items:center}.u .card:first-child h3{grid-column:1/3}.ring{margin:0;grid-row:2/5}.kv{grid-column:2}.u{grid-template-rows:auto 1fr auto}.b{grid-template-rows:auto 1fr}}
@media (max-width:600px){.app{padding:14px 14px 6px;gap:10px}.brand small{display:none}.top{flex-wrap:wrap}.tabs{margin:0;width:100%}.tabs span{flex:1;text-align:center;padding:8px 4px;font-size:14px}
.main{gap:10px}.card{padding:14px 16px;border-radius:16px}h3{margin-bottom:10px}
.u .card:first-child{display:grid;grid-template-columns:118px 1fr;gap:0 16px;align-items:center}.u .card:first-child h3{grid-column:1/3}
.ring{width:112px;height:112px;margin:0;grid-row:2/5}.kv{grid-column:2}.u{grid-template-rows:auto 1fr auto}.ring div{width:88px;height:88px}.ring b{font-size:24px}.ring small{font-size:11px}.kv{font-size:14px;padding:6px 0}
.bar{margin-bottom:9px}.bar:nth-of-type(n+6){display:none}.sg{flex-wrap:wrap;gap:8px;padding:12px 16px}.pill{font-size:14px;white-space:normal}.chg{margin:0}
.hero .when{font-size:26px}.tiles{grid-template-columns:repeat(2,1fr);gap:8px}.tile{padding:9px 12px}.tile b{font-size:22px}.tiles{flex:none}.chips{margin:10px 0}
.row{padding:9px 0}.det{display:none}.empty{padding:12px 0}.bars{justify-content:flex-start;gap:9px}.row:nth-of-type(n+4){display:none}.note{font-size:13px}}
.foot{display:flex;justify-content:center;align-items:center;flex-shrink:0;padding:2px 0 0}
.foot a{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 18px;text-decoration:none;color:#7a8396;line-height:1}
.foot img{width:18px;height:auto;display:block;pointer-events:none;flex-shrink:0}
.foot span{font-size:13px;font-weight:500;letter-spacing:.2px;color:#7a8396}
'''
TABS=[('usage',T('用量','Usage')),('backups',T('備份紀錄','Backups')),('restores',T('回復紀錄','Restores'))]
def chips(ls): return ''.join(f'<span class=chip><i>{ICON.get(l.get("type"),"•")}</i>{e(LOC.get(l.get("type"),l.get("type","")))}</span>' for l in ls)
def tag(r): return f'<span class=tag>{T("示例","SAMPLE")}</span>' if r.get('sample') else ''
def usage():
    try: pc=float(snap['used'].rstrip('%'))
    except Exception: pc=0
    bots=sorted(snap['bots'].items(),key=lambda x:-x[1]['share']);mx=max([v['share'] for _,v in bots]+[1])
    bars=''.join(f'<div class="bar{" x" if any(s in b.lower() for s in SPECIAL) else ""}"><span>{e(DN(b))}</span><b>{v["share"]:g}%</b><i style="--w:{v["share"]/mx*100:.0f}"></i></div>' for b,v in bots[:7]) or f'<div class=empty>{T("未有用量資料","No usage data yet")}</div>'
    sp=''.join(f'<span class=pill>{e(s[2])}</span>' for s in sug) or f'<span class="pill m">{NONE}</span>'
    ch=(T(f'新增 {len(new)} 項・增加 {len(up)} 項',f'{len(new)} new · {len(up)} up') if old else T('首次記錄，下次開始比較','First snapshot'))
    return f'''<div class="main u"><div class=card><h3>{T("本週用量","This week")}</h3><div class=ring style="--p:{pc}"><div><span><b>{e(snap['used'] or '—')}</b><small>{T("已用","used")}</small></span></div></div>
<div class=kv><span>{T("重設","Resets")}</span><b>{e(RESET or '—')}</b></div><div class=kv><span>{T("尚餘時間","Time left")}</span><b>{e(LEFT or '—')}</b></div><div class=kv><span>{T("方案","Plan")}</span><b>{e(snap['plan'] or '—')}</b></div></div>
<div class=card><h3>{T("各 bot 佔比","Share by bot")}</h3><div class=bars>{bars}</div></div><div class="card sg"><span class=t>💡 {T("建議","Suggestions")}</span>{sp}<span class=chg>{ch}</span></div></div>'''
def backups():
    if not BK: return f'<div class="main"><div class=card><div class=empty>{T("未有備份紀錄。按主選單「即時備份」開始。","No backups yet.")}</div></div></div>'
    r=BK[0];c=r.get('counts',{});pa=r.get('status')!='complete'
    tiles=''.join(f'<div class=tile><b>{c.get(k,"—")}</b><span>{lab}</span></div>' for k,lab in CN)
    note=f'<div class=note>{e(r.get("notes",""))}</div>' if r.get('notes') else ''
    d=diff(r,BK[1] if len(BK)>1 else None)
    if d:
        it=[(T(CNAME[k][0],CNAME[k][1]),sg(v),v) for k,v in d['counts'].items()]+[(T('角色','Role'),'+'+x,1) for x in d['roles_added']]+[(T('角色','Role'),'−'+x,-1) for x in d['roles_removed']]
        if d['size_mb'] is not None: it.append((T('大小','Size'),('+' if d['size_mb']>=0 else '−')+fmt_mb(abs(d['size_mb'])),d['size_mb']))
        stag=('<span class=tag>'+T('示例','SAMPLE')+'</span>') if d['sample'] else ''
        cmp=f'<div class=cmp><span class=ct>{T("與上次比較","vs previous")}{stag}</span>'+''.join(f'<span class="dl {"up" if v>0 else "dn" if v<0 else "eq"}"><small>{e(l)}</small>{e(t)}</span>' for l,t,v in it)+'</div>'
    else: cmp=f'<div class=cmp><span class=ct>{diff_line(None)}</span></div>'
    det=''.join(f'<div><span>{e(LOC.get(l.get("type"),l.get("type","")))}</span><code>{e(l.get("path",""))}</code></div>' for l in r.get('locations',[]))
    lst=''.join(f'<div class=row><span class="d{" pa" if x.get("status")!="complete" else ""}"></span><div><b>{e(x.get("time",""))}</b>{tag(x)}<small>{e(locs(x))}</small></div><span class=r>{e(x.get("size",""))}<br>{ST(x.get("status"))}</span></div>' for x in BK[1:7]) or f'<div class=empty>{T("只有一次備份紀錄","Only one backup so far")}</div>'
    return f'''<div class="main b"><div class="card hero"><h3>{T("最新備份","Latest backup")}</h3><div class=when>{e(r.get("time",""))}<span class="st {"pa" if pa else "ok"}">{ST(r.get("status"))}</span>{tag(r)}</div>
<div class=sub>{ago(r.get("time",""))} · {r.get("roles","—")} {T("個角色","roles")} · {e(r.get("size",""))}</div><div class=chips>{chips(r.get("locations",[]))}</div><div class=tiles>{tiles}</div>{cmp}{note}<div class=det>{det}</div></div>
<div class=card><h3>{T("較早的備份","Earlier backups")}</h3>{lst}</div></div>'''
def restores():
    if not RS: return f'<div class="main"><div class=card><div class=empty>{T("未有回復紀錄","No restores yet")}</div></div></div>'
    r=RS[0];ad=r.get('added',{});sm=any(x.get('sample') for x in RS)
    rl=''.join(f'<span class="chip {"new" if x.get("mode")=="new" else "mg"}"><i>{"+" if x.get("mode")=="new" else "⇄"}</i>{e(x.get("name",""))}</span>' for x in r.get('roles',[]))
    tiles=''.join(f'<div class=tile><b>{ad.get(k,0)}</b><span>{T("新增","Added")} {lab}</span></div>' for k,lab in CN[:3])+f'<div class=tile><b>{len(r.get("skipped",[]))}</b><span>{T("已略過","Skipped")}</span></div>'
    det=''.join(f'<div><span>{e(x.get("name",""))}</span><code>{T("新建角色","New role") if x.get("mode")=="new" else T("合併到現有角色","Merged into existing")}</code></div>' for x in r.get('roles',[]))
    sk=f'<div class=note>{T("略過","Skipped")}：{e("、".join(r.get("skipped",[])))}</div>' if r.get('skipped') else ''
    lst=''.join(f'<div class=row><span class="d{" pa" if x.get("status")=="partial" else ""}"></span><div><b>{e(x.get("date",""))}</b>{tag(x)}<small>{T("來源","From")} {e(x.get("source",""))} · {e("、".join(y.get("name","") for y in x.get("roles",[])))}</small></div><span class=r>{len(x.get("roles",[]))} {T("個角色","roles")}</span></div>' for x in RS[1:7]) or f'<div class=empty>{T("只有一次回復紀錄","Only one restore so far")}</div>'
    bn=f'<div class=banner>{T("示例資料：未有真實回復紀錄，只供測試顯示。","Sample data: no real restores yet; shown for testing only.")}</div>' if sm else ''
    return f'''{bn}<div class="main b"><div class="card hero"><h3>{T("最新回復","Latest restore")}</h3><div class=when>{e(r.get("date",""))}{tag(r)}</div>
<div class=sub>{T("來源備份","Source backup")} {e(r.get("source",""))} · {ago(r.get("date",""))}</div><div class=chips>{rl}</div><div class=tiles>{tiles}</div>{sk}<div class=det>{det}</div></div>
<div class=card><h3>{T("較早的回復","Earlier restores")}</h3>{lst}</div></div>'''
BODY={'usage':usage,'backups':backups,'restores':restores}
MINNY_M='data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20380%20258%22%20role%3D%22img%22%20aria-label%3D%22m%22%3E%3Cpath%20fill%3D%22%239acba4%22%20fill-rule%3D%22evenodd%22%20d%3D%22M347.69%2C29.00%20C341.57%2C19.22%20336.28%2C14.14%20328.00%2C9.31%20C319.72%2C4.49%20305.50%2C1.23%20298.00%2C0.06%20C290.50%2C-1.10%20289.17%2C0.27%20283.00%2C2.31%20C276.83%2C4.35%20271.33%2C4.54%20261.00%2C12.31%20C250.67%2C20.08%20229.17%2C42.22%20221.00%2C48.94%20C212.83%2C55.66%20214.83%2C52.33%20212.00%2C52.62%20C209.17%2C52.92%20208.67%2C53.91%20204.00%2C50.69%20C199.33%2C47.47%20189.83%2C37.08%20184.00%2C33.31%20C178.17%2C29.54%20175.00%2C28.77%20169.00%2C28.06%20C163.00%2C27.35%20155.17%2C27.12%20148.00%2C29.06%20C140.83%2C31.00%20131.67%2C37.70%20126.00%2C39.69%20C120.33%2C41.68%20119.33%2C43.56%20114.00%2C41.00%20C108.67%2C38.44%20100.83%2C28.76%2094.00%2C24.31%20C87.17%2C19.86%2078.67%2C16.19%2073.00%2C14.31%20C67.33%2C12.44%2065.50%2C11.90%2060.00%2C13.06%20C54.50%2C14.23%2047.45%2C15.32%2040.00%2C21.31%20C32.55%2C27.30%2021.14%2C38.89%2015.31%2C49.00%20C9.49%2C59.11%207.60%2C59.50%205.06%2C82.00%20C2.52%2C104.50%200.02%2C162.67%200.06%2C184.00%20C0.10%2C205.33%202.60%2C201.83%205.31%2C210.00%20C8.02%2C218.17%2010.86%2C226.29%2016.31%2C233.00%20C21.76%2C239.71%2031.05%2C246.43%2038.00%2C250.25%20C44.95%2C254.07%2050.33%2C254.82%2058.00%2C255.94%20C65.67%2C257.05%2075.67%2C258.44%2084.00%2C256.94%20C92.33%2C255.44%20102.29%2C250.59%20108.00%2C246.94%20C113.71%2C243.28%20115.59%2C239.82%20118.25%2C235.00%20C120.91%2C230.18%20123.75%2C230.33%20123.94%2C218.00%20C124.12%2C205.67%20119.65%2C173.67%20119.38%2C161.00%20C119.10%2C148.33%20120.53%2C147.45%20122.31%2C142.00%20C124.09%2C136.55%20126.45%2C131.80%20130.06%2C128.31%20C133.68%2C124.82%20139.51%2C121.73%20144.00%2C121.06%20C148.49%2C120.40%20152.79%2C121.16%20157.00%2C124.31%20C161.21%2C127.47%20166.43%2C134.39%20169.25%2C140.00%20C172.07%2C145.61%20172.97%2C149.33%20173.94%2C158.00%20C174.91%2C166.67%20173.54%2C184.00%20175.06%2C192.00%20C176.58%2C200.00%20179.24%2C202.34%20183.06%2C206.00%20C186.89%2C209.66%20192.18%2C212.90%20198.00%2C213.94%20C203.82%2C214.98%20212.68%2C214.07%20218.00%2C212.25%20C223.32%2C210.43%20226.32%2C207.38%20229.94%2C203.00%20C233.55%2C198.62%20235.39%2C199.17%20239.69%2C186.00%20C243.99%2C172.83%20250.36%2C136.67%20255.75%2C124.00%20C261.14%2C111.33%20267.30%2C111.33%20272.00%2C110.00%20C276.70%2C108.67%20280.78%2C112.50%20283.94%2C116.00%20C287.09%2C119.50%20289.43%2C124.00%20290.94%2C131.00%20C292.45%2C138.00%20293.49%2C145.33%20293.00%2C158.00%20C292.51%2C170.67%20287.45%2C195.00%20288.00%2C207.00%20C288.55%2C219.00%20292.81%2C224.89%20296.31%2C230.00%20C299.81%2C235.11%20304.05%2C236.12%20309.00%2C237.69%20C313.95%2C239.25%20317.67%2C240.38%20326.00%2C239.38%20C334.33%2C238.38%20350.72%2C235.92%20359.00%2C231.69%20C367.28%2C227.46%20372.35%2C223.11%20375.69%2C214.00%20C379.02%2C204.89%20379.46%2C195.17%20379.00%2C177.00%20C378.54%2C158.83%20375.32%2C123.17%20372.94%2C105.00%20C370.55%2C86.83%20368.90%2C80.67%20364.69%2C68.00%20C360.48%2C55.33%20353.80%2C38.78%20347.69%2C29.00%20Z%22%2F%3E%3Cg%20id%3D%22eyes%22%3E%3Cellipse%20cx%3D%22110.64%22%20cy%3D%2297.70%22%20rx%3D%2216.79%22%20ry%3D%2219.08%22%20fill%3D%22%2338312d%22%2F%3E%3Cellipse%20cx%3D%22106.22%22%20cy%3D%2291.44%22%20rx%3D%223.05%22%20ry%3D%223.05%22%20fill%3D%22%23ffffff%22%2F%3E%3Cellipse%20cx%3D%22225.10%22%20cy%3D%2292.36%22%20rx%3D%2216.02%22%20ry%3D%2219.08%22%20fill%3D%22%2338312d%22%2F%3E%3Cellipse%20cx%3D%22220.37%22%20cy%3D%2285.64%22%20rx%3D%223.05%22%20ry%3D%223.05%22%20fill%3D%22%23ffffff%22%2F%3E%3C%2Fg%3E%3C%2Fsvg%3E%0A'
FOOT=f'<div class=foot><a href="https://minny.app" target="_blank" rel="noopener noreferrer" aria-label="minny.app"><img src="{MINNY_M}" alt="" width="18"><span>minny.app</span></a></div>'
out=os.path.abspath(a.out or a.dir);os.makedirs(out,exist_ok=True)
w,h=(int(x) for x in a.view.lower().split('x'));br=next((x for x in ('chromium','chromium-browser','google-chrome','google-chrome-stable') if shutil.which(x)),None)
res={}
for k,lab in TABS:
    tabs=''.join(f'<span class="{"on" if kk==k else ""}">{ll}</span>' for kk,ll in TABS)
    page=f'<!doctype html><html lang={"zh-Hant" if Z else "en"}><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><style>{CSS}</style></head><body><div class=app><div class=top><div class=logo>⛨</div><div class=brand><b>{T("備份回復專員","Backup & Restore Officer")}</b><small>{T("更新於","Updated")} {NOW.strftime("%Y-%m-%d %H:%M")}</small></div><div class=tabs>{tabs}</div></div>{BODY[k]()}{FOOT}</div></body></html>'
    hp=os.path.join(out,f'dash-{k}-{w}x{h}.html');pp=hp[:-5]+'.png';open(hp,'w',encoding='utf-8').write(page);ok=False
    if br:
        try:
            subprocess.run([br,'--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars',f'--window-size={w},{h}','--force-device-scale-factor=2',f'--screenshot={pp}','file://'+hp],capture_output=True,timeout=60);ok=os.path.exists(pp)
        except Exception: ok=False
    res[k]=pp if ok else None
menu=[T('用量','Usage'),T('備份紀錄','Backups'),T('回復紀錄','Restores'),T('更新','Refresh')]+[T('照做：','Do it: ')+s[2] for s in sug]+[T('返回主選單','Back to main menu')]
print(json.dumps({'png':res,'text':TX,'suggestions':[{'kind':s[1],'text':s[2],'targets':s[3]} for s in sug],'menu':menu},ensure_ascii=False,indent=1))
