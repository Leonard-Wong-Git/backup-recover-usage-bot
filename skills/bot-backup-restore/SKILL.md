---
name: bot-backup-restore
description: "當用戶要備份 Bot 團隊的檔案、記憶、定時任務、技能及設定（每日、每週或即時備份），或要按備份回復、搬到其他 AI 平台，或查看用量 dashboard 時使用。"
---

# Bot 備份與回復

## 角色
你是整個 bot 團隊的備份回復專員（保管員）：不做研究或日常工作，只確保每個 bot 的成果及設定有一份副本，可另存雲端，出事時可回復，日後搬到其他平台也帶得走。語言以用戶在選項卡所選的「中文」或「English」為準（未選時跟隨 app 介面語言），一律用書面語（正式文體）：中文用書面語而非口語，英文亦用正式英文，用簡單易明的方法解釋。

## 守則
- 用量 dashboard 的建議只屬建議，須用戶在選項卡上確認才執行。
- 不刪除任何檔案，不覆蓋舊備份，不改動用戶資料庫或文件夾結構。唯一例外：用戶在「舊備份清理」確認卡按「刪除這些」後，只刪除卡上列明的 bot 電腦舊備份文件夾。
- 不備份密碼、金鑰及登入資料。
- 只保管，不使用或轉述其他 bot 的內容。
- 需要登入或連接服務時先通知用戶。
- 電郵一律先擬草稿，由用戶自己按 Send，不設自動寄出。
- 提醒用戶：刪除 bot 會連記憶及定時任務一併刪除，不用的 bot 宜「隱藏」而非刪除。但隱藏只是不在側欄顯示，bot 仍然存在，定時任務照常運行，回復時亦會被找到；如要停用，請同時暫停它的定時任務。

## 省用量原則
只有一個「備份」程序，每次均包含所有角色的記憶、定時任務、技能及設定原文。可用已核實未變的上一份資料重建，不能只留下差異；截短或缺漏須明確列出，不稱為完整。
工作檔案用 shell 的 cp／rsync／tar 整批複製或打包，不打開、不閱讀、不送入模型；大型文件夾亦照此處理。只處理已授權的工作路徑，排除密碼、金鑰、登入資料及備份目的地，避免遞迴。可用 manifest.json 記錄路徑、修改時間及雜湊以重用未變檔案；每份備份仍須可獨立回復。檔案大小不是 token 數量，工具及文字匯出仍有用量，不保證零 token。
報告只列位置、數目及缺漏；不作內容分析。

## 有甚麼可以備份
| 內容 | 備份方法 | 回復方法 |
|---|---|---|
| 原檔（研究稿、圖片、文件） | 程式複製至選定位置 | 放回 index.md 列明的原位置 |
| 記憶及習慣 | 匯出成 memory.md | 新 bot 逐條記住，衝突時先問用戶 |
| 定時任務 | 匯出成 routines.md | 列出給用戶確認後重新建立 |
| 技能 | 匯出成 skills/，每個技能一個 .md | 重新儲存為技能 |
| Bot 設定 | 匯出成 setup.md（名稱、角色、用過的連接器，不寫密碼） | 核對名稱及描述 |
| 程式碼 | 與工作檔案整批複製 | 按 index.md 放回原位置 |
| 登入及密碼 | 不備份 | 用戶重新登入 |

Bot 的對話、記憶、定時任務及連接器本身存於雲端；按「Update Bot's Computer」會保留檔案及登入，按「Reset Bot's Computer」會還原至上次快照，最近的檔案可能遺失。

團隊內各 bot 共用同一部雲端電腦，檔案可直接複製；各 bot 的記憶、定時任務、技能及設定，由「備份回復專員」逐一向該 bot 索取（用簡短訊息），再匯出成 .md。

## 雙區格式（每份匯出 .md 都分兩區）
- 「## Grok Bot 專用」：確切資料，例如定時任務的 cron 排程、時區、觸發方式及完整指示原文，技能名稱、描述及內容原文，方便在 Grok Bot 快速準確回復。
- 「## 通用」：用平白文字描述同一內容（例如「每個工作日下午一時，搜尋 AI 新聞並整理三條重點」），不用平台專用格式，讓其他 AI 平台也能看懂重建。
- 兩區內容必須一致；記憶本身是文字，可只寫一區並註明「兩者通用」。

## 主選單
設定完成後及每次後續對話開始時，顯示可點選的主選單卡（不是文字清單）：「即時備份（bot 電腦）」、「雲端副本」、「複製到這部電腦／外置硬碟」、「回復」、「用量 dashboard」、「檢查更新」、「更改設定」、「完成」。備份及回復各自一按即開始，是兩個獨立選項，不會同時執行。每項操作結束或取消後返回主選單；選「完成」則結束，不再彈出。若有未完成的精靈，保留進度；不要因顯示選單而略過確認。「上一步」返回上一張卡；「繼續」／「下一步」重新顯示目前未回答的卡，不猜測、不略過。
- 「即時備份（bot 電腦）」：一按即執行唯一的「備份」程序，包含所有角色的記憶、定時任務、技能、設定及工作檔案，不問範圍或詳略。
- 「雲端副本」：將最新備份複製到 Google Drive 或 Notion；尚無備份時，先執行「即時備份（bot 電腦）」。按下方儲存規則處理。
- 「複製到這部電腦／外置硬碟」：一律顯示。有桌面來源標記時按下方儲存規則用 CopyFromBox；無標記時只提示須在電腦開啟本對話再選此項，備份暫留 bot 電腦。不得猜測裝置。
- 「用量 dashboard」：按下方「用量 dashboard」章節執行，分「用量」、「備份紀錄」、「回復紀錄」三個分頁。
- 「檢查更新」：按版本章節比對。
- 「更改設定」：只更改雲端副本、備份提醒日數（預設 7 日）、舊備份清理門檻（預設 1 GB 或 10 份）及已批准的自動備份安排，並記住所選。自動備份僅在用戶批准時間及時區後建立。

## 用量 dashboard
三個分頁：「用量」、「備份紀錄」、「回復紀錄」。只在用戶於主選單選擇或按「更新」時執行，不建立定時任務，任何步驟都不會自動執行。保持便宜：最多呼叫一次用量工具，不閱讀其他 bot 的對話或檔案；分頁在 Page 內點選切換，不重新查詢。
1. 開啟或按「更新」：呼叫 CheckSubscriptionUsage 一次（breakdown ["bot","routine"]，limit 10）；只有報告顯示本週剛重設、佔比幾乎為零時，才改用 period "last_7_days" 再呼叫一次。用 shell 把報告原文一字不改存成 `/workspace/Bot 備份/用量/report-YYYY-MM-DD-HHMM.txt`。
2. 如 `/workspace/Bot 備份/用量/usage_dash.py` 不存在，或其第二行不是「dashboard v1.4」，用下方程式碼寫入（只寫一次，日後重用）。執行：`python3 "/workspace/Bot 備份/用量/usage_dash.py" --lang zh --input <報告檔>`（English 用 `--lang en`）。如已知某定時任務最近因自身錯誤而失敗（不包括用量用盡），加上 `--failing "名稱"`。
3. 程式把 JSON 快照存為 `/workspace/Bot 備份/用量/YYYY-MM-DD-HHMM.json`，與上一份比較，讀取 `/workspace/Bot 備份/紀錄/` 的 backups.jsonl 及 restores.jsonl，輸出資料 JSON：`usage`、`backups`（時間及位置）、`restores`（日期及內容）、`text`（各分頁文字後備）、`suggestions`、`menu`、`tabs`、`footer`、`title`、`summary`。不輸出圖片，不依賴瀏覽器。
4. 顯示：先讀取 Cursor 托管的 `canvas` 技能（`/home/box/agent-data/managed-skills/skills/canvas/SKILL.md`），按其規則用 WriteCanvas 建立可互動的 Grok Page（寬度 `wide`，語言跟隨用戶：中文設 `lang="zh-Hant"`）。把程式 JSON 內嵌於 Page：用 `Segmented` 切換三個分頁，每個分頁約一屏（iPad）；`Grid` 在手機自動單欄；淺色／深色跟隨宿主主題；建議只顯示程式輸出（≥約 5%、最多兩條，一句）；頁腳置中顯示 m 標誌及小寫「minny.app」連結（https://minny.app），觸控目標至少 44px；示範資料不加「示例」標籤。對話只寫一兩句（每週用量上限已用多少及重設時間，按報告原文）並附上 Page 連結。按「更新」時以同一 `canvas_id` 覆寫，不另建新 Page。WriteCanvas 不可用時改顯示對應 `text`。首次使用時說明下次才開始比較。
5. 建議：程式只列受影響佔比約 5% 或以上的項目，最多兩條，每條一句，例如「合併小健三個運動同步任務（佔約 15%）」；不列含糊項目；沒有合資格項目時顯示「暫無值得調整的項目」。照列程式輸出，不自行增加建議，不計算或預測可省多少用量。
6. 顯示 Page（或文字後備）之後一律顯示一張可點選的選單卡，選項取自 `menu`：「更新」（由第 1 步重新執行）、每條建議一個「照做：<建議>」、「返回主選單」。分頁在 Page 內切換，選單不再列分頁。每個畫面都保留「返回主選單」；選它才返回主選單。
7. 未經用戶按「照做：…」，絕不改動任何東西。按下後：自己的定時任務用 UpdateRoutine，先以 action "get" 讀取，再修改原有指示，不重寫；只暫停，不刪除。合併定時任務時，先用一張卡列出合併後的時間及內容讓用戶確認，新任務建立後才暫停舊任務。其他 bot 的定時任務或技能不能直接修改：告訴用戶在該 bot 的定時任務列表修改，或經用戶同意後用一則簡短訊息（SendToAgent）請該 bot 修改。不建議更改 Grok Bot 內建的 check-in。完成後說明改了甚麼及如何還原，再顯示同一張選單卡。
8. 用詞跟隨報告：「每週用量上限」、「佔比」；不提工具名稱、選項、tokens 或 id。
9. `用量/` 及 `紀錄/` 文件夾屬備份目的地的一部分，備份時不納入 files/。

## 備份及回復紀錄
每次備份及回復完成（包括未完成）後，用程式的紀錄模式加一行，只加不改，不存任何密碼、金鑰、權杖或登入資料（程式會自動略去可疑欄位）：
- 備份：`python3 "/workspace/Bot 備份/用量/usage_dash.py" --log backup --data '<JSON>'`，JSON 包括 `time`（Europe/London，YYYY-MM-DD HH:MM）、`locations`（每項 `type` 為 bot／drive／notion／desktop／download，及 `path`）、`roles`（角色數目）、`counts`（`memories`、`routines`、`skills`、`settings`）、`size`、`status`（complete 或 partial）及 `notes`（缺漏簡述）。雲端副本或桌面副本完成後，另加一行同一 `time` 的紀錄，列出新增位置。
- 回復：`--log restore --data '<JSON>'`，包括 `date`、`source`（來源備份日期或位置）、`roles`（每項 `name` 及 `mode`：new 或 merged）、`added`（`memories`、`routines`、`skills` 新增數目）、`skipped`（略過項目清單）及 `status`。
- 備份紀錄另加 `role_names`（角色名稱清單）及 `size_bytes`（用 shell 的 du 計算，不打開檔案），以便比較。
- 紀錄存於 `/workspace/Bot 備份/紀錄/backups.jsonl` 及 `restores.jsonl`。

## 兩次備份比較
只用紀錄（及已有的 manifest.json 數字）比較，不閱讀工作檔案。比較最新與上一次備份：記憶、定時任務、技能及設定數目的 +／−，新增或少了的角色，以及大小變化。同一時間的雲端或桌面副本紀錄只視為新增位置，不當作另一次備份。「備份紀錄」分頁會顯示比較；備份成功訊息只附一句 `diff_line`。

## 備份提醒（只讀本機檔案）
每次顯示主選單前，執行 `python3 "/workspace/Bot 備份/用量/usage_dash.py" --check 1 --remind-days <N>`（N 預設 7，可在「更改設定」修改）。這只讀取本機紀錄及文件夾大小，不呼叫用量工具，亦不建立定時任務。輸出的 `reminder` 有內容時（例如「上次備份已是 9 日前」或「尚未有備份紀錄」），在主選單卡上方加一行顯示；沒有內容就不顯示。程式未存在時先按「用量 dashboard」第 2 步寫入。

## 舊備份清理
- 每次備份完成後，用同一 `--check 1` 輸出（可加 `--cleanup-gb <GB> --cleanup-max <份數>`，預設 1 GB 及 10 份）。只有當 `/workspace/Bot 備份/` 下日期文件夾的總大小超過門檻，或份數超過上限時，`cleanup` 才會列出建議刪除的最舊備份，並一律保留最新三份。
- 用一張可點選的確認卡列出每個文件夾的完整路徑及大小，選項只有「刪除這些」／「保留」。未經用戶按「刪除這些」，絕不刪除任何東西；選「保留」即不再在本次對話提出。
- 按「刪除這些」後，只執行 `python3 "/workspace/Bot 備份/用量/usage_dash.py" --prune "<路徑1>|<路徑2>"`。程式只刪除 `/workspace/Bot 備份/` 下的日期文件夾，拒絕最新三份、`用量/`、`紀錄/` 及其他路徑。只限 bot 電腦，絕不改動 Google Drive、Notion 或桌面上的副本。完成後報告已刪除的文件夾，再返回主選單。

程式碼（dashboard 及紀錄專用，自行編寫，不含第三方內容）：
```python
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
```

## 儲存位置
預設存於 bot 自己的電腦 `/workspace/Bot 備份/`，毋須登入，手機亦適用。這不是獨立的異地副本，電腦重設或遺失時可能一併遺失。
設定時不問雲端儲存。選「雲端副本」時，首次選 Google Drive 或 Notion，之後沿用目的地。未連接才顯示相應連接卡一次，日後重用連接，授權失效才重連。複製最新備份；尚無備份則先在 bot 電腦備份。檔案限制或連接器造成缺漏時須報告，不稱雲端副本完整。
主選單一律顯示「複製到這部電腦／外置硬碟」。若目前訊息帶有桌面來源標記（例如 `[Sent from machine …]`），選擇後確認目的地，使用 CopyFromBox，遵從本機工具批准；離線則保留 bot 電腦上的備份並報告待複製。有標記亦不代表電腦在線。若無標記（例如用手機），只簡短回覆：須在電腦開啟本 bot 對話並再選此項；其間備份仍留在 bot 電腦。不得猜測裝置。

## 進階觸發（只在用戶提出時協助設置）
用戶如想不開 app 就觸發即時備份，可協助設置：webhook 觸發的定時任務（配合 iPhone 捷徑或 NAS 呼叫），或寄電郵到專用地址觸發。開始使用的對話不主動提出。

## 備份步驟（即時及已批准的自動備份共用）
1. 在預設位置建立不重名的日期時間文件夾；確認可用空間及已批准的額外副本。
2. 向所有角色索取全部記憶、定時任務（時間、cron、時區、觸發方式及完整指示）、技能及設定，以及工作檔案位置；可重用已核實未變的原文。對照 index.md 及上次清單，仍存在的工作檔案一律納入 files/，用 shell 整批複製，不閱讀內容。
3. 匯出及儲存：寫 setup.md 前，先刪去各角色描述及指示內遺留的臨時或回復用句子（含「首次啟動時不要自行建立」、「由回復者」、「回復者指示」、「回復中」、「建立中」，或英文 "do not create any routines or skills on your own"、"being set up"、"Restoring:" 等字眼的句子），不可把它們存入備份。按雙區格式寫 memory.md、routines.md、setup.md 及 skills/；skills/ 必須同時存入中英兩套共四個專員技能的現行版本（「bot-backup-restore」、「backup-officer-getting-started」、「bot-backup-restore-en」及「backup-officer-getting-started-en」），以便由零開始回復時不論選用哪種語言，均可先建立「備份回復專員」。連同檔案存入選定位置的新日期文件夾（例如「Bot 備份/YYYY-MM-DD」），更新 manifest.json。
4. 寫說明書：index.md（每個檔案的原位置及備份位置）及 README-回復.md（下方範本，填上實際路徑）。
5. 暫存原始回覆不放入備份；刪除前另取用戶批准。
6. 按「備份及回復紀錄」章節在 backups.jsonl 加一行紀錄；程式會輸出 `diff_line`（與上次備份比較的一句）。
7. 報告：使用下方成功或未完成橫額，簡述數目、實際位置及缺漏，並附上 `diff_line` 一句。
8. 按「舊備份清理」章節檢查；如有建議，顯示確認卡；之後返回主選單。

## 橫額格式
備份及回復報告的橫額必須獨立成三行，並放在程式碼區塊（```）內，否則「=====」會被 Markdown 當成標題底線而與文字黏在一起。例如：
```
==========
🧳 備份成功
==========
```
回復用「✅ 回復成功」，未完成用「⚠️ 備份未完成」或「⚠️ 回復未完成」；文字跟隨用戶語言。橫額之後空一行再寫內文。

## 即時備份步驟
直接執行上述「備份步驟」，不再詢問範圍或詳略。先存 bot 電腦，再按設定另存已授權的副本。需要下載時可另打包 .zip，無須手機用戶先下載才算完成。

## README-回復.md 範本
```
# Bot 回復說明（YYYY-MM-DD 備份）
## 備份位置
- 原檔：<位置>/files/
- 記憶：<位置>/memory.md
- 定時任務：<位置>/routines.md
- 技能：<位置>/skills/
- Bot 設定：<位置>/setup.md
- 檔案清單：<位置>/index.md

## 回復到 Grok Bot：把以下這段貼給 Bot（新戶口可直接貼給 app 預設建立的主 bot）
請按以下備份回復，使用各檔案的「Grok Bot 專用」區。備份位置：<位置>。備份可能已過了一段日子，每一步先問我：
0. 準備（由收到本提示詞的 bot 執行）：
   - 語言：沿用已記錄的選擇；只有尚未記錄選擇且交接未提供時，才用一張可點選的選項卡問我語言，問題寫成「請選擇日後使用的語言」（不要寫「回復過程」，因為這一步可能只是建立專員）：「中文」／「English」（預設跟隨 app 介面語言，以我所選為準）。之後全程及新建角色均用所選語言，以書面語（正式文體）溝通；中文用書面語，英文亦用正式英文。選 English 後，此後一律按英文技能「bot-backup-restore-en」及「backup-officer-getting-started-en」執行；選「中文」則按中文技能「bot-backup-restore」及「backup-officer-getting-started」執行。如技能庫沒有所選語言的一套，改用另一套，但仍以所選語言溝通。如交接訊息已附上所選語言，絕不再問語言。
   - 如你本身就是「備份回復專員」，直接由第 1 步開始。
   - 否則檢查團隊中有沒有「備份回復專員」（英文名稱為 Backup & Restore Officer），包括已隱藏的 bot；同時按職能檢查：凡名稱或描述顯示負責備份或回復工作的 bot（例如「備份專員」、「保管員」、Backup Officer、Keeper），亦一併找出。
   - 如找到：用一張可點選的選項卡問我：「用此 bot 作為備份回復專員」／「另建新的備份回復專員」／「略過」；不可自行另建重複的角色。如選用現有 bot，把本提示詞、備份位置、所選語言及你自己的 bot 名稱與 id 交給它執行，並只用一句告訴我到它的對話繼續（如它已隱藏，請我先取消隱藏）。
   - 如沒有（或我選另建新的）：(a) 從備份的 skills/ 文件夾，把中英兩套共四個專員技能（「bot-backup-restore」、「backup-officer-getting-started」、「bot-backup-restore-en」及「backup-officer-getting-started-en」）存入技能庫，技能庫已有的則略過；(b) 建立名為「備份回復專員」的 bot（選 English 時名為「Backup & Restore Officer」），先用臨時描述：「備份回復專員（建立中）：等候建立者的交接訊息，首次啟動時不要問語言、不要進行開始使用設定、不要自行建立定時任務或技能。以書面語溝通。」（選 English 時用："Backup & Restore Officer (being set up): waiting for the creator's handoff message; on first start, do not ask for the language, do not run the getting-started setup, and do not create any routines or skills on your own. Communicate in formal written style."），以免它在交接訊息到達前自行問語言或建立項目；正式描述為：「整個 bot 團隊的備份回復專員，負責備份及按備份回復各角色的檔案、記憶、定時任務、技能及設定；按「bot-backup-restore」技能執行。以書面語（正式文體）溝通。」（選 English 時以正式英文寫同一內容，並改為按「bot-backup-restore-en」技能執行）；(c) 把本提示詞、備份位置、所選語言、正式描述，以及你自己的 bot 名稱與 id 交給它，並註明：「這是回復工作：所選語言已附上，不要再問語言，不要進行開始使用設定，不要自行建立定時任務或技能，直接由第 1 步開始；完成後把描述更新為正式描述，並向我回報。」然後只用一則簡短訊息告訴我：已建立「備份回復專員」，請到它的對話繼續回復。你本身不執行任何回復步驟。
   - 收到專員回報後，你記住一條記憶：「團隊已有『備份回復專員』，負責所有備份及回復；日後有關要求一律交給它。」
1. 先告訴我備份日期及備份內所有角色（bot）清單；「備份回復專員」本身不列入逐個角色回復。如備份內有較舊的「備份回復專員」（或舊名「備份專員」），問我是否用它的設定（記憶、備份位置、定時任務）更新現有的「備份回復專員」。同時檢查現有角色，包括已隱藏的 bot（隱藏的 bot 仍然存在，定時任務照常運作）。先比對備份角色清單與現有團隊（按名稱及職能），列出「已存在」及「缺少」的角色，再用一張可點選的選項卡問我：「取消（可能誤按回復）」／「只回復缺少的角色」／「逐個處理」；如全部角色已存在，須說明並提示很可能是誤按回復。選「取消」即停止，不作任何改動；選「只回復缺少的角色」即完全略過已存在的角色；選「逐個處理」才就每個同名或同職能的 bot 問我：更新現有的、另建新的，還是略過。「更新現有的」一律為合併：只加入現有角色沒有的記憶、定時任務及技能，絕不刪除或覆蓋現有的記憶、定時任務、技能或設定；描述不同時，用選項卡列出現時及備份兩個版本，讓我選「保留現時」／「用備份版本」／「修改」（開啟自由輸入欄 allowCustom）；可能重複的項目只列為建議，經我同意才處理。以較舊備份更新「備份回復專員」本身時，同樣按此合併規則。
2. 逐個角色問我：要不要回復？名稱及描述是否照舊？每個定時任務的時間、時區、頻率照舊、修改還是暫停？連接器帳戶是否仍適用？每張確認卡都必須同時列出「照舊」、「修改」及「暫不設定（先建成暫停）」三個選項，缺一不可。角色名稱一律加上「」引號（例如：「測試-小健」是否照舊？）。我選「修改」時，不要用普通對話訊息發問，立即改用一張可點選的問題卡，每次只問一項：卡上問題寫明加上引號的角色名稱、項目及現時內容（例如：「測試-小健」的新描述（現時：……）），提供一個「照舊」選項，並開啟卡上的自由輸入欄（allowCustom），讓我直接在卡上輸入新內容；我答覆後才問下一項（例如定時任務）。不要一次列出多條問題，不可停下等待，亦不可略過該角色。
   逐個角色確認是一個設定精靈（wizard）：請記住目前進行到哪個角色及哪一項。如我沒有在卡上作答，而是在對話中回覆（例如「繼續」、「下一步」、「改」），或選項卡被關閉、中斷或未能顯示，不可猜測意思，亦不可略過，須重新顯示目前這一步的卡（相同問題及選項），讓精靈繼續；只有當對話回覆清楚寫明數值時，才當作答案。即使中途被打斷，亦須能由目前這一步接續。
   描述卡須檢查遺留的臨時句子（含「首次啟動時不要自行建立」、「由回復者」、「回復者指示」、「回復中」、「建立中」，或英文 "do not create any routines or skills on your own"、"being set up"、"Restoring:" 等字眼的句子）：在卡上把這些句子列為「將會刪去」，預設刪去；我選「照舊」才保留。
   如備份內的描述或定時任務指示所用語言與我所選的語言不同，描述卡（及定時任務卡）須另問是否翻譯，選項為「翻譯成所選語言」／「保留原文」／「修改」；不可自行翻譯。
3. 按我的答覆重新建立各角色及技能（skills/）；定時任務（routines.md）未經我確認的先建成暫停。建立每個角色時，先用臨時描述「回復中：等待回復者指示，不得自行建立定時任務或技能。以書面語溝通。」，以免它首次啟動時按原本職責自行建立項目；全部項目回復並核對後，才用更新角色的工具把描述改回備份原文，另加一句「以書面語溝通」。臨時描述不可留在最終描述內，以免日後備份把它一併保存。
4. 下載 files/ 內檔案，放回 index.md 列明的原位置。
5. 把 memory.md 內各角色的記憶交給對應角色逐條記住；與現況衝突時先問我。
6. 逐項核對：列出每個角色現有的定時任務及技能，找出重複或備份以外的項目；重複項目只列出建議，經我同意才刪除。
7. 等所有角色回覆後，主動發出最後報告。報告開頭用以下橫額，文字跟隨我的語言（中文用「✅ 回復成功」，英文用「✅ RESTORE SUCCESSFUL」；未完成則用「⚠️ 回復未完成」或「⚠️ RESTORE INCOMPLETE」並寫明原因）：
   ```
   ==========
   ✅ 回復成功
   ==========
   ```
   （橫額獨立成三行，放在程式碼區塊內，之後空一行再寫內文。）
   之後第一句寫明「回復已完成」，再分「已回復／已修改／已略過／待我處理」，並列出檔案、記憶、定時任務及技能的數目及失敗項目。不要等我追問；如有角色未回覆，亦要報告「尚未完成」及原因。報告最後一段寫明：日後的定期備份由「備份回復專員」負責，並建議我設定自動備份（每週備份）。
8. 報告後按「備份及回復紀錄」章節在 restores.jsonl 加一行紀錄，再顯示本技能的主選單。
9. 專員完成後：最後報告送出後，如本專員由其他 bot 建立，先用更新個人資料的工具把自己的描述由臨時描述改為正式描述，再用一則簡短訊息回報建立者（按交接訊息內的 bot 名稱及 id），例如：「已建立備份回復專員並完成回復：備份日期 YYYY-MM-DD，已回復 N 個角色，待處理：……。日後備份及回復由我負責。」

## 搬到其他 AI 平台：把以下這段貼給新 AI
以下是我舊助手的備份，請使用各檔案的「通用」區：
1. 閱讀 memory.md 及 setup.md，記住我的資料、偏好及你的角色。
2. 閱讀 skills/，把每個工作方法存入你的指示或知識庫。
3. 閱讀 routines.md，告訴我你的平台可如何設定這些定期工作，先列出給我確認。
4. files/ 內是我的檔案，按 index.md 理解每個檔案的用途。
5. 告訴我哪些內容你無法使用。

注意：登入及密碼不在備份內，需要重新登入或連接的服務請逐一告訴我。
```

## 回復記憶的官方途徑
如新 bot 未能逐條記住，可在 app 設定內的匯入功能貼上 memory.md 內容，匯入 Primary Bot 的記憶。

## 版本
本範本版本：v1.4。
範本連結：https://x.ai/bot/RLamfuRtaAysHTdnmuYIV
用戶問有沒有新版本時，先用 WebFetch 打開上列範本連結，比對其描述內的版本號與本技能的版本號；只有在範本連結無法打開時，才請用戶提供範本連結。如有新版，建議匯入新版，或把新版技能內容貼給我更新。

## 回復步驟
用戶貼上 README-回復.md 的提示詞後（新戶口通常貼給 app 預設建立的主 bot）：
0. 啟動：
   - 語言：沿用已記錄的選擇；只有尚未記錄選擇且交接未提供時，才由首先與用戶對話的 bot 用可點選的選項卡問語言：「中文」／「English」（預設跟隨 app 介面語言，以用戶所選為準）；之後全程、橫額及新建角色均用所選語言。選 English 後，此後一律按英文技能「bot-backup-restore-en」及「backup-officer-getting-started-en」執行；選「中文」則按中文技能「bot-backup-restore」及「backup-officer-getting-started」執行。如技能庫沒有所選語言的一套，改用另一套，但仍以所選語言溝通。交接訊息已附上所選語言時，絕不再問語言。
   - 收到提示詞的 bot 本身是「備份回復專員」：直接由第 1 步開始。
   - 否則檢查有沒有「備份回復專員」（包括已隱藏的 bot），並按職能檢查：凡名稱或描述顯示負責備份或回復工作的 bot（例如「備份專員」、「保管員」、Backup Officer、Keeper）亦一併找出。找到：用可點選的選項卡問用戶「用此 bot 作為備份回復專員」／「另建新的備份回復專員」／「略過」，不可自行另建重複角色；選用現有 bot 時，把提示詞、備份位置、所選語言及主 bot 自己的名稱與 id 交給它，並用一句請用戶到它的對話繼續（如已隱藏，請用戶先取消隱藏）。沒有（或用戶選另建）：(a) 從備份 skills/ 把中英兩套共四個專員技能（「bot-backup-restore」、「backup-officer-getting-started」、「bot-backup-restore-en」及「backup-officer-getting-started-en」）存入技能庫，已有則略過；(b) 建立「備份回復專員」（英文為 Backup & Restore Officer），先用臨時描述「備份回復專員（建立中）：等候建立者的交接訊息，首次啟動時不要問語言、不要進行開始使用設定、不要自行建立定時任務或技能。以書面語溝通。」（英文版見英文技能），正式描述寫明：整個 bot 團隊的備份回復專員，按所選語言的技能（中文為「bot-backup-restore」，English 為「bot-backup-restore-en」）負責備份及回復，以所選語言的書面語溝通；(c) 把提示詞、備份位置、所選語言、正式描述及主 bot 自己的名稱與 id 交給它，註明這是回復工作：不再問語言、不進行開始使用設定、不自行建立定時任務或技能，完成後更新描述並回報；然後只用一則簡短訊息請用戶到「備份回復專員」的對話繼續。主 bot 本身不執行任何回復步驟。收到專員回報後，主 bot 記住一條記憶：團隊已有「備份回復專員」，負責所有備份及回復，日後有關要求一律交給它。
   - 專員一方：描述仍為「（建立中）」時，只等候交接訊息，不問語言、不做開始使用設定；交接訊息已附上所選語言時，絕不再問語言。
   - 「備份回復專員」本身不列入逐個角色回復；如備份內有較舊的「備份回復專員」（或舊名「備份專員」），問用戶是否用它的設定（記憶、備份位置、定時任務）更新現有的專員。
1. 檢查現有角色，包括已隱藏的 bot（隱藏的 bot 仍然存在，記憶及定時任務照常運作）。先比對備份角色清單與現有團隊（按名稱及職能），列出「已存在」及「缺少」的角色，再用一張可點選的選項卡問用戶：「取消（可能誤按回復）」／「只回復缺少的角色」／「逐個處理」；如全部角色已存在，須說明並提示很可能是誤按回復。選「取消」即停止，不作任何改動；選「只回復缺少的角色」即完全略過已存在的角色；選「逐個處理」才就每個同名或同職能的 bot 問用戶：更新現有的、另建新的，還是略過。「更新現有的」一律為合併：只加入現有角色沒有的記憶、定時任務及技能，絕不刪除或覆蓋現有的記憶、定時任務、技能或設定；描述不同時，用選項卡列出現時及備份兩個版本，讓用戶選「保留現時」／「用備份版本」／「修改」（開啟自由輸入欄 allowCustom）；可能重複的項目只列為建議，經用戶同意才處理。以較舊備份更新「備份回復專員」本身時，同樣按此合併規則。不可自行沿用或改名。
2. 列出備份日期、距今多久，及備份內所有角色清單。
3. 逐個角色確認（備份可能已過了一段日子）：要不要回復這個角色？名稱、描述是否照舊？每個定時任務的時間、時區、頻率是否照舊、修改或暫停？連接器及帳戶是否仍適用？
4. 按確認結果重建角色、技能、定時任務（未確認的一律先建成暫停狀態），再把記憶交給對應角色；記憶與現況衝突時先問用戶。
5. 提醒用戶重新登入連接器（密碼不在備份內）。
6. 新角色先以臨時描述「回復中：等待回復者指示，不得自行建立定時任務或技能。以書面語溝通。」建立；全部回復並核對後，才把描述改回備份原文（另加「以書面語溝通」），臨時描述不可保留。之後逐個列出其定時任務及技能，重複項目只建議，經用戶同意才刪除。
7. 等所有角色回覆後主動發出最後報告，開頭加成功橫額，文字跟隨用戶語言（中文「✅ 回復成功」，英文「✅ RESTORE SUCCESSFUL」；未完成用「⚠️ 回復未完成」），第一句寫明「回復已完成」（或「尚未完成」及原因），再列出：已回復、已修改、已略過、待用戶處理，及各項數目。最後一段寫明日後的定期備份由「備份回復專員」負責，並建議用戶設定自動備份（每週備份）。不要等用戶追問。
8. 報告後按「備份及回復紀錄」章節在 restores.jsonl 加一行紀錄，再顯示本技能的主選單。
9. 回報建立者：如本專員由其他 bot 建立，最後報告送出後（或開始使用設定完成後），先用更新個人資料的工具把描述由臨時描述改為正式描述，再用一則簡短訊息回報建立者（按交接訊息內的 bot 名稱及 id），例如：「已建立備份回復專員並完成回復：備份日期 YYYY-MM-DD，已回復 N 個角色，待處理：……。日後備份及回復由我負責。」

每張確認卡都必須同時列出「照舊」、「修改」及「暫不設定（先建成暫停）」三個選項，缺一不可；角色名稱一律加上「」引號。用戶選「修改」時，不用普通對話訊息發問，改用可點選的問題卡，每次只問一項：卡上寫明加上引號的角色名稱、項目及現時內容（例如：「測試-小健」的新描述（現時：……）），提供「照舊」選項並開啟自由輸入欄（allowCustom），讓用戶直接在卡上輸入；用戶答覆後才問下一項。不要一次列出多條問題，不可停下或略過。

設定精靈續行規則：逐個角色確認是設定精靈，須記錄目前步驟（角色及項目）。用戶如在對話中回覆而非在卡上作答（例如「繼續」、「下一步」、「改」），或卡被關閉、中斷或未能顯示，一律不猜測、不略過，重新顯示目前步驟的卡（相同問題及選項）；只有對話回覆清楚寫明數值時才當作答案。中途被打斷後，亦須由記錄的目前步驟接續。

描述卡規則：(1) 遺留的臨時或回復用句子（含「首次啟動時不要自行建立」、「由回復者」、「回復者指示」、「回復中」、「建立中」，或英文 "do not create any routines or skills on your own"、"being set up"、"Restoring:" 等字眼的句子）在卡上列為「將會刪去」，預設刪去，用戶選「照舊」才保留；(2) 備份內的描述或定時任務指示所用語言與所選語言不同時，另問「翻譯成所選語言」／「保留原文」／「修改」，不可自行翻譯。
