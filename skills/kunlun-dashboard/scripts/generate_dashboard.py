#!/usr/bin/env python3
"""generate_dashboard.py — 昆仑·全视 仪表盘生成器 v3.0
7 Tab: 🏠总览|🖥️环境|🤖Agent|⏰定时任务|🛠技能|🔗流水线|💰Token|🐒昆仑
"""
import os, re, json, subprocess, sys, platform
from datetime import datetime, date, timezone, timedelta
from collections import Counter, defaultdict
from pathlib import Path

def _find_root():
    cur = Path(os.path.dirname(os.path.abspath(__file__)))
    for _ in range(10):
        if (cur / 'MEMORY.md').is_file(): return cur
        cur = cur.parent
    return Path.cwd()

ROOT = _find_root()
OPENCLAW_AGENTS_DIR = Path.home() / '.openclaw' / 'agents'
OPENCLAW_SESSIONS_DIR = OPENCLAW_AGENTS_DIR / 'main' / 'sessions'
CODEX_SESSIONS_DIR = Path.home() / '.codex' / 'sessions'
NOW = datetime.now(timezone.utc)
TODAY = date.today().isoformat()

_SESSION_FILES_CACHE = None

def _run(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except: return ""

def _setup_stdout():
    # Avoid Windows GBK console failures when printing emoji/CJK logs.
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except:
        pass

def _glob_with_mtime(base: Path, pattern: str):
    if not base.is_dir():
        return []
    fs = []
    try:
        for p in base.glob(pattern):
            if p.is_file():
                try:
                    fs.append((p, p.stat().st_mtime))
                except:
                    continue
    except:
        return []
    return fs

def _discover_session_files():
    global _SESSION_FILES_CACHE
    if _SESSION_FILES_CACHE is not None:
        return _SESSION_FILES_CACHE
    fs = []
    fs.extend(_glob_with_mtime(OPENCLAW_SESSIONS_DIR, '*.trajectory.jsonl'))
    fs.extend(_glob_with_mtime(CODEX_SESSIONS_DIR, '**/rollout-*.jsonl'))
    fs.sort(key=lambda x: x[1], reverse=True)
    _SESSION_FILES_CACHE = [f for f, _ in fs]
    return _SESSION_FILES_CACHE

def _iter_jsonl(path: Path):
    try:
        for line in path.read_text('utf-8', errors='ignore').split('\n'):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except:
                continue
    except:
        return

def _extract_prompt_event(d):
    t = d.get('type')
    if t == 'prompt.submitted':
        p = (d.get('data', {}) or {}).get('prompt', '')
        return p if isinstance(p, str) else ''
    if t == 'event_msg' and (d.get('payload', {}) or {}).get('type') == 'user_message':
        p = (d.get('payload', {}) or {}).get('message', '')
        return p if isinstance(p, str) else ''
    return ''

def _extract_usage_event(d):
    t = d.get('type')
    if t == 'model.completed':
        data = d.get('data', {}) or {}
        u = data.get('usage') or {}
        return {
            'in': int(u.get('input', 0) or 0),
            'out': int(u.get('output', 0) or 0),
            'model': (data.get('model') or 'openclaw').strip()[:30] or 'openclaw',
        }
    if t == 'event_msg' and (d.get('payload', {}) or {}).get('type') == 'token_count':
        info = (d.get('payload', {}) or {}).get('info') or {}
        u = info.get('last_token_usage') or {}
        return {
            'in': int(u.get('input_tokens', 0) or 0),
            'out': int(u.get('output_tokens', 0) or 0),
            'model': 'codex',
        }
    return None

def _extract_event_date(d):
    ts = d.get('timestamp') or d.get('ts') or ''
    if not isinstance(ts, str) or len(ts) < 10:
        return ''
    # Codex rollout timestamps are UTC. Convert to local day to keep daily stats accurate.
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.astimezone().date().isoformat()
    except:
        pass
    maybe_date = ts[:10]
    try:
        date.fromisoformat(maybe_date)
        return maybe_date
    except:
        return ''

def _extract_session_label(path: Path):
    name = path.name
    if name.endswith('.trajectory.jsonl'):
        return name[:24]
    if name.startswith('rollout-'):
        return name[8:27]
    return name[:24]

def _pick_primary_file(paths):
    existing = [p for p in paths if p.is_file()]
    if not existing:
        return None
    try:
        return max(existing, key=lambda p: p.stat().st_size)
    except:
        return existing[0]

# ═══ 采集层 ═══

def collect_environment():
    env = {}
    is_windows = os.name == 'nt'
    env.update(
        os=platform.platform() or 'N/A',
        kernel=platform.version() or 'N/A',
        arch=platform.machine() or 'N/A',
        hostname=platform.node() or 'N/A',
        uptime=_run("uptime -p") or (_run("uptime")[:50] if not is_windows else 'N/A'),
        container=os.path.isfile('/.dockerenv') or os.path.isfile('/run/.containerenv')
    )
    pkg = Path.home()/'openclaw/node_modules/openclaw/package.json'
    if pkg.is_file():
        try:
            env['openclaw_version'] = json.loads(pkg.read_text()).get('version','?')
        except:
            env['openclaw_version'] = '?'
    else:
        env['openclaw_version'] = '?'
    codex_v = _run("codex --version")
    env['codex_version'] = codex_v.splitlines()[0].strip() if codex_v else '?'
    env.update(node_version=_run("node --version"), python_version=(sys.version.split()[0] if sys.version else '?'))

    # Gateway process info (best-effort; platform-specific)
    env.update(gw_pid='N/A', gw_cpu_pct='?', gw_mem_pct='?', gw_uptime='?', gw_mem_kb=0)
    if not is_windows:
        gw = _run("ps aux|grep -E 'openclaw.*gateway'|grep -v grep|head -1").split()
        if len(gw) >= 11:
            pid = gw[1]
            env.update(gw_pid=pid, gw_cpu_pct=gw[2], gw_mem_pct=gw[3])
            et = _run(f"ps -p {pid} -o etimes=")
            try:
                s = int(et)
                env['gw_uptime'] = f"{s//3600}h {(s%3600)//60}m"
            except:
                env['gw_uptime'] = '?'
            rss = _run(f"ps -p {pid} -o rss=")
            try:
                env['gw_mem_kb'] = int(rss)
            except:
                env['gw_mem_kb'] = 0

    # CPU/load
    try:
        load = os.getloadavg()
        load_1m, load_5m, load_15m = f"{load[0]:.2f}", f"{load[1]:.2f}", f"{load[2]:.2f}"
    except:
        load_1m = load_5m = load_15m = '?'
    env.update(
        load_1m=load_1m,
        load_5m=load_5m,
        load_15m=load_15m,
        cpu_cores=str(os.cpu_count() or '?'),
        cpu_model=(platform.processor() or '?')[:60]
    )

    # Memory (prefer psutil if present, fallback to shell parsing)
    mem = {}
    try:
        import psutil  # type: ignore
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
        mem = dict(
            total_gb=round(vm.total/1073741824,1),
            used_gb=round(vm.used/1073741824,1),
            avail_gb=round(vm.available/1073741824,1),
            used_pct=round(float(vm.percent),1),
            swap_total_gb=round(sm.total/1073741824,1),
            swap_used_gb=round(sm.used/1073741824,1),
            swap_used_pct=round(float(sm.percent),1),
        )
    except:
        if not is_windows:
            for line in _run("free -b|tail -n+2").split('\n'):
                parts = line.split()
                if not parts:
                    continue
                if parts[0].startswith('Mem:') and len(parts) >= 7:
                    t=int(parts[1]);u=int(parts[2]);a=int(parts[6])
                    mem.update(total_gb=round(t/1073741824,1),used_gb=round(u/1073741824,1),
                               avail_gb=round(a/1073741824,1),used_pct=round(u/t*100,1) if t else 0)
                elif parts[0].startswith('Swap:') and len(parts) >= 3:
                    st=int(parts[1]);su=int(parts[2])
                    mem['swap_total_gb']=round(st/1073741824,1);mem['swap_used_gb']=round(su/1073741824,1)
                    mem['swap_used_pct']=round(su/st*100,1) if st else 0
    env['memory'] = mem

    # Disk usage
    disks = []
    if is_windows:
        out = _run("wmic logicaldisk where drivetype=3 get DeviceID,FreeSpace,Size /format:csv")
        for line in out.splitlines():
            line = line.strip()
            if not line or line.startswith("Node,") or ',' not in line:
                continue
            parts = line.split(',')
            if len(parts) < 4:
                continue
            dev, free_s, size_s = parts[1], parts[2], parts[3]
            try:
                total = int(size_s); free = int(free_s); used = max(total - free, 0)
                use_pct = int(round((used / total) * 100)) if total else 0
                disks.append(dict(
                    mount=dev,
                    type=dev,
                    total=f"{round(total/1073741824,1)}G",
                    used=f"{round(used/1073741824,1)}G",
                    avail=f"{round(free/1073741824,1)}G",
                    use_pct=str(use_pct),
                ))
            except:
                continue
    else:
        for line in _run("df -h|tail -n+2").split('\n'):
            parts = line.split()
            if len(parts) >= 6 and parts[0].startswith('/'):
                disks.append(dict(mount=parts[5],type=parts[0],total=parts[1],
                                  used=parts[2],avail=parts[3],use_pct=parts[4].replace('%','')))
    env['disks'] = disks[:8]

    # Listening ports
    ports = []
    if is_windows:
        for line in _run("netstat -ano").splitlines():
            s = line.strip()
            if not s.startswith("TCP"):
                continue
            cols = s.split()
            if len(cols) < 5 or cols[3] != "LISTENING":
                continue
            local = cols[1]
            pid = cols[4]
            port = local.rsplit(':', 1)[-1] if ':' in local else local
            ports.append(dict(port=port, pid=pid, program='unknown'))
    else:
        for line in _run("ss -tlnp").strip().split('\n'):
            parts = line.split()
            if len(parts) >= 5 and parts[0].startswith('LISTEN'):
                addr = parts[3]
                port = addr.rsplit(':',1)[-1] if ':' in addr else addr
                prog = parts[-1] if len(parts) > 5 else ''
                pid = ''
                pm = re.search(r'pid=(\d+)',prog)
                if pm:
                    pid = pm.group(1)
                ports.append(dict(port=port,pid=pid,program=prog.split(',')[0][:30] if prog else 'unknown'))
    env['ports'] = ports

    if is_windows:
        env['security'] = dict(root_ssh=False, readonly_fs=not os.access(str(ROOT), os.W_OK))
    else:
        rl = _run("grep 'PermitRootLogin yes' /etc/ssh/sshd_config 2>/dev/null|grep -v '^#'")
        env['security'] = dict(root_ssh=bool(rl), readonly_fs=not os.access('/tmp', os.W_OK))
    return env

def collect_agents():
    def looks_like_agent_dir(p: Path) -> bool:
        return any((p / fn).is_file() for fn in ('SOUL.md', 'IDENTITY.md', 'MEMORY.md'))

    def build_agent_row(entry: Path, name: str):
        a = dict(name=name, soul='❌', identity='❌', memory='❌', memory_dir='❌', status='🔴', last_active='')
        sf = entry/'SOUL.md'
        if sf.is_file():
            a['soul'] = '✅' if sf.stat().st_size > 50 else '⚠️'
        if (entry/'IDENTITY.md').is_file():
            a['identity'] = '✅'
        mf = entry/'MEMORY.md'
        if mf.is_file():
            a['memory'] = '✅' if mf.stat().st_size > 200 else '⚠️'
        else:
            # Kunlun workspace flavor: no MEMORY.md but has memory tree + core index files.
            kunlun_memory_signals = [
                (entry / 'memory').is_dir(),
                (entry / 'memory-index.md').is_file(),
                (entry / 'resonance-net.md').is_file(),
                (entry / 'anti-fragility-pool.md').is_file(),
            ]
            if sum(1 for x in kunlun_memory_signals if x) >= 2:
                a['memory'] = '✅'
        md = entry/'memory'
        if md.is_dir():
            fs = list(md.rglob('*.md'))
            a['memory_dir'] = f'{len(fs)}条' if fs else '🟡 空'
        elif (entry / 'memory-index.md').is_file():
            a['memory_dir'] = '索引模式'
        recent = 0
        try:
            for f in entry.rglob('*'):
                if f.is_file():
                    recent = max(recent, f.stat().st_mtime)
        except:
            pass
        if recent:
            a['last_active'] = datetime.fromtimestamp(recent).strftime('%m-%d %H:%M')
        signals = [a['soul'] == '✅', a['identity'] == '✅', a['memory'] in ('✅', '⚠️')]
        score = sum(1 for x in signals if x)
        a['status'] = '🟢' if score >= 2 else '🟡' if score == 1 else '🔴'
        return a

    agents = []
    seen = set()

    # Current workspace can itself be a valid agent-like root in Kunlun setups.
    if looks_like_agent_dir(ROOT):
        agents.append(build_agent_row(ROOT, f'{ROOT.name} (workspace)'))
        seen.add(str(ROOT.resolve()))

    # By default only show current workspace to avoid confusing duplicate rows.
    # Set KUNLUN_DASHBOARD_INCLUDE_OPENCLAW=1 to also include ~/.openclaw/workspace.
    if os.environ.get('KUNLUN_DASHBOARD_INCLUDE_OPENCLAW', '').strip() == '1':
        openclaw_workspace = Path.home() / '.openclaw' / 'workspace'
        if openclaw_workspace.is_dir() and looks_like_agent_dir(openclaw_workspace):
            rp = str(openclaw_workspace.resolve())
            if rp not in seen:
                agents.append(build_agent_row(openclaw_workspace, 'openclaw-workspace'))
                seen.add(rp)

    agents_root = OPENCLAW_AGENTS_DIR/'main'
    if agents_root.is_dir():
        for entry in sorted(agents_root.iterdir()):
            if not entry.is_dir() or entry.name.startswith('.'):
                continue
            # Skip runtime/session folders and only accept real agent payloads.
            if entry.name.lower() in ('sessions', 'logs', 'tmp', 'cache'):
                continue
            if not looks_like_agent_dir(entry):
                continue
            rp = str(entry.resolve())
            if rp in seen:
                continue
            agents.append(build_agent_row(entry, entry.name))
            seen.add(rp)
    return agents

def collect_cron():
    jobs=[]
    try:
        r=subprocess.run(['openclaw','cron','list','--json'],capture_output=True,text=True,timeout=8)
    except:
        r = None
    if r is not None:
        try:
            for j in json.loads(r.stdout).get('jobs',[]):
                s=j.get('state',{});lm=s.get('lastRunAtMs');nm=s.get('nextRunAtMs')
                st=s.get('lastRunStatus','never')
                jobs.append(dict(name=j.get('name',''),schedule=j.get('schedule',{}).get('expr',''),
                                last_status='✅' if st=='ok' else '❌' if st=='error' else '⚪',
                                last_time=datetime.fromtimestamp(lm/1000).strftime('%m-%d %H:%M') if lm else '',
                                next_time=datetime.fromtimestamp(nm/1000).strftime('%m-%d %H:%M') if nm else '',
                                delivery=j.get('delivery',{}).get('mode','none')))
        except:
            pass
    if jobs:
        return jobs

    auto_root = Path.home() / '.codex' / 'automations'
    if not auto_root.is_dir():
        return jobs
    try:
        import tomllib  # py3.11+
        for tf in sorted(auto_root.glob('*/automation.toml')):
            try:
                data = tomllib.loads(tf.read_text('utf-8', errors='ignore'))
            except:
                continue
            kind = (data.get('kind') or '').strip()
            if kind not in ('cron', 'heartbeat'):
                continue
            jobs.append(dict(
                name=(data.get('name') or tf.parent.name)[:60],
                schedule=(data.get('rrule') or data.get('schedule') or '')[:80],
                last_status='⚪',
                last_time='',
                next_time='',
                delivery=f'codex:{kind}',
            ))
    except:
        pass
    return jobs

def collect_skills():
    dirs={'workspace/skills':ROOT/'skills','core_skills':Path.home()/'core_skills',
          'kunlun-dist':ROOT/'kunlun-dist','plugin-skills':Path.home()/'.openclaw'/'plugin-skills',
          'codex-skills':Path.home()/'.codex'/'skills'}
    all_sk=[]
    for label,d in dirs.items():
        if not d.is_dir(): continue
        for sub in sorted(d.iterdir()):
            if not sub.is_dir() or sub.name.startswith('.'): continue
            sk=dict(name=sub.name,category=label,version='',status='🟢',desc='')
            sm=sub/'SKILL.md'
            if sm.is_file():
                try:
                    t=sm.read_text('utf-8',errors='ignore')
                    vm=re.search(r'^version:\s*([\d.]+)',t,re.MULTILINE)
                    if vm: sk['version']=vm.group(1)
                    # 从description提取前80字符（避免可变长后行断言导致异常）
                    dm=re.search(r'^description:\s*\|\s*\n((?:[ \t]+.*\n?)*)',t,re.MULTILINE)
                    if dm:
                        desc_lines=[ln.strip() for ln in dm.group(1).splitlines() if ln.strip()]
                        if desc_lines:
                            sk['desc']=' '.join(desc_lines)[:80]
                    dm2=re.search(r'^description:\s*(.+)',t,re.MULTILINE)
                    if not sk['desc'] and dm2: sk['desc']=dm2.group(1).strip()[:80]
                except: sk['status']='🔴'
            else: sk['status']='🟡'
            all_sk.append(sk)
    return all_sk

PHASE_DEFS=[
    (1,'复杂度判定',['复杂度判定','三问门控','行为信号检测']),
    (1,'复杂度感知器',['复杂度','深度','depth_index']),
    (2,'多框架并行器',['多框架','并行框架','交叉验证']),
    (3,'学科响应网络',['学科响应','自激活','特征匹配','匹配度']),
    (4,'十六字诀螺旋',['十六字诀','螺旋','去粗取精','去伪存真']),
    (5,'OCGS Core',['OCGS','系统边界','回路','基模','消费接口']),
    (6,'域适应三棱镜',['三棱镜','域适应','维度自适应','E/S/P']),
    (7,'免疫系统',['免疫系统','证伪','反例','条件依赖']),
    (8,'多尺度时间',['多尺度','时间分析','持久战','三阶段','防御','相持','反攻']),
    (9,'抽象蒸馏塔',['抽象','蒸馏','L1','L2','L3','L4']),
    (10,'认知知识图',['知识图','三视图','推理','分析','摘要']),
    (11,'横向贯穿',['能量管理','动态回溯','跨分析继承']),
]

def collect_pipeline_and_phases():
    phase_data={}
    ad=ROOT/'memory'/'analysis'
    if ad.is_dir():
        for f in sorted(ad.glob('*.md')):
            if f.name in ('TEMPLATE.md','index.md'): continue
            try: text=f.read_text('utf-8',errors='ignore')
            except: continue
            tm=re.search(r'^# (.+)',text,re.MULTILINE)
            title=tm.group(1)[:50] if tm else f.name
            phases=[dict(num=pn,name=pn2,done=any(kw in text for kw in kws)) for pn,pn2,kws in PHASE_DEFS]
            phase_data[f.name]=dict(title=title,phases=phases,total=sum(1 for p in phases if p['done']))
    tasks=[]
    for f in _discover_session_files()[:5]:
        prompts=[];model='';ui=0;uo=0;all_prompts=[];first_prompt=''
        for d in _iter_jsonl(f):
            p = _extract_prompt_event(d)
            if isinstance(p, str) and p.strip():
                p = p.strip()
                prompts.append(p[:80])
                all_prompts.append(p[:120])
                if not first_prompt:
                    first_prompt = p[:120]
            u = _extract_usage_event(d)
            if u:
                ui += u['in']
                uo += u['out']
                if u['model']:
                    model = u['model'][:30]
        if prompts:
            tasks.append(dict(summary=prompts[-1][:80],first_prompt=first_prompt[:120],
                             all_prompts=all_prompts,model=model or 'codex',
                             usage_in=ui,usage_out=uo,usage_total=ui+uo,
                             sessions=len(prompts),file=_extract_session_label(f)))
    return tasks, phase_data

def collect_token():
    ti=0;to=0;mu=defaultdict(lambda:dict(in_=0,out_=0))
    for f in _discover_session_files()[:10]:
        for d in _iter_jsonl(f):
            u = _extract_usage_event(d)
            if not u:
                continue
            inp = u['in']; out = u['out']; mdl = u['model'] or 'unknown'
            ti += inp
            to += out
            mu[mdl]['in_'] += inp
            mu[mdl]['out_'] += out
    cost=ti*2e-6+to*8e-6
    return dict(total_in=ti,total_out=to,total=ti+to,cost=round(cost,4),model_usage=dict(mu))

def collect_token_daily():
    dates=defaultdict(lambda:{'in':0,'out':0,'count':0})
    for f in _discover_session_files()[:100]:
        seen=set()
        for d in _iter_jsonl(f):
            u = _extract_usage_event(d)
            if not u:
                continue
            ts = _extract_event_date(d)
            if ts:
                if ts not in seen:
                    dates[ts]['count'] += 1
                    seen.add(ts)
                dates[ts]['in'] += u['in']
                dates[ts]['out'] += u['out']
    trend=[]
    for d in sorted(dates):
        s=dates[d]
        trend.append({'date':d,'in':s['in'],'out':s['out'],'total':s['in']+s['out'],'sessions':s['count']})
    wd = date.today()
    today_total=sum(t['total'] for t in trend if t['date']==TODAY)
    week_total=sum(t['total'] for t in trend if t['date'] and wd-timedelta(days=7)<=date.fromisoformat(t['date'])<=wd)
    month_total=sum(t['total'] for t in trend if t['date'][:7]==TODAY[:7])
    return trend[-14:], today_total, week_total, month_total

# ═══ 昆仑数据 ═══

def parse_version():
    try:
        t=(ROOT/'VERSION.md').read_text('utf-8')
        m=re.search(r'^##\s*(v[\d.]+)',t,re.MULTILINE)
        if not m:
            m=re.search(r'kunlun-system:\s*v?([\d.]+)',t,re.IGNORECASE)
        ver=(m.group(1).lstrip('v') if m else '未知')
        hist=[];it=False
        for line in t.split('\n'):
            if '|' in line and all(p.strip() in ('','-','---') for p in line.split('|')[1:-1]): it=True; continue
            if it and line.startswith('| '):
                parts=[p.strip() for p in line.split('|')[1:-1]]
                if len(parts)>=3 and parts[0].replace('**','').strip().startswith('v'):
                    hist.append(dict(version=parts[0].replace('**',''),date=parts[1],summary=parts[2]))
        return ver,hist
    except: return '未知',[]

def parse_harmonics():
    hs=[]
    src = _pick_primary_file([ROOT/'resonance-net.md', ROOT/'memory'/'resonance-net.md'])
    if not src:
        return hs
    try:
        t=src.read_text('utf-8', errors='ignore')
        for b in re.split(r'(?=^### 谐波 #)',t,flags=re.MULTILINE):
            m=re.search(r'### 谐波 #(\d+)：(.+)',b)
            if not m: continue
            h=dict(id=int(m.group(1)),name=m.group(2).strip(),intensity=0,
                   status='🟡 候选' if '候选' in b else '🟢 正式')
            im=re.search(r'\*\*强度\*\*：(\d+)',b)
            if im: h['intensity']=int(im.group(1))
            hs.append(h)
    except:
        pass
    return hs

def parse_memory_index():
    entries=[]
    sk_entries=[]  # 学科桥条目
    tool_entries=[]  # 工具/法则
    src = _pick_primary_file([ROOT/'memory-index.md', ROOT/'memory'/'memory-index.md'])
    if not src:
        return entries, sk_entries, tool_entries
    try:
        t=src.read_text('utf-8', errors='ignore')
        cp=[(m.start(),m.end(),m.group(1).strip()) for m in re.finditer(r'^### ———(.+)———',t,re.MULTILINE)]
        for ib in re.split(r'(?=^### (?![———\[]))',t,flags=re.MULTILINE):
            ib=ib.strip()
            if not ib.startswith('### '): continue
            first=ib.split('\n')[0].strip()
            if '———' in first or '模板' in first or '记忆索引' in first or '工具/法则名称' in first: continue
            if first.startswith('### ['): continue
            m=re.search(r'### (.+)',first)
            if not m: continue
            name=m.group(1).strip()
            if name.startswith('[') and name.endswith(']'): name=name[1:-1].strip()
            pos=t.find(name)
            cat='未分类'
            if pos>=0:
                for cs,ce,cn in cp:
                    if pos>ce: cat=cn
            e=dict(name=name,category=cat,status='🟡',trust_level='',discipline='')
            tm=re.search(r'\*\*信度等级\*\*：([Tt][1-4])',ib)
            if tm: e['trust_level']=tm.group(1).upper()
            sm=re.search(r'\*\*验证状态\*\*：([\U0001f7e2\U0001f7e1\U0001f534])',ib)
            if sm: e['status']=sm.group(1)
            dm=re.search(r'\*\*所属学科\*\*：(.+)',ib)
            if dm: e['discipline']=dm.group(1).strip()
            entries.append(e)
            if '学科' in cat: sk_entries.append(e)
            if '工具' in cat or '法则' in cat: tool_entries.append(e)
    except:
        pass
    return entries, sk_entries, tool_entries

def parse_reports():
    rs=[]
    try:
        t=(ROOT/'memory/analysis/index.md').read_text('utf-8'); it=False
        for line in t.split('\n'):
            if '|' in line and all(p.strip() in ('','-','---') for p in line.split('|')[1:-1]): it=True; continue
            if it and line.startswith('| '):
                parts=[p.strip() for p in line.split('|')[1:-1]]
                if len(parts)>=4 and parts[0].isdigit():
                    rs.append(dict(id=parts[0],date=parts[1],title=parts[2],output=parts[3]))
    except: pass
    return rs

def parse_antifragility():
    cs=[]
    src = _pick_primary_file([ROOT/'anti-fragility-pool.md', ROOT/'memory'/'anti-fragility-pool.md'])
    if not src:
        return cs
    try:
        t=src.read_text('utf-8', errors='ignore')
        for b in re.split(r'(?=#### 挑战 #)',t):
            m=re.search(r'#### 挑战 #(\d+)',b)
            if not m: continue
            c=dict(id=int(m.group(1)),status='🟡',sharpness='')
            sm=re.search(r'\*\*状态\*\*：([\U0001f7e2\U0001f7e1\U0001f534])',b)
            if sm: c['status']=sm.group(1)
            sm2=re.search(r'\*\*尖锐度\*\*：([⭐]+)',b)
            if sm2: c['sharpness']=sm2.group(1)
            cs.append(c)
        for b in re.split(r'(?=### 议题 #)',t):
            m=re.search(r'### 议题 #(\d+)',b)
            if m:
                c=dict(id=100+int(m.group(1)),status='🟡',sharpness='⭐⭐⭐',is_open_issue=True)
                sm=re.search(r'\*\*状态\*\*：([\U0001f7e2\U0001f7e1\U0001f534])',b)
                if sm: c['status']=sm.group(1)
                cs.append(c)
    except:
        pass
    return cs

def parse_bridge_registry_stats():
    reg = ROOT / 'knowledge-tree' / 'registry.md'
    if not reg.is_file():
        return None
    try:
        t = reg.read_text('utf-8', errors='ignore')
    except:
        return None
    # Bridge sections are §2~§12, each includes (Qxx)
    bridge_sections = re.findall(r'^# §\d+ .*\(Q\d{2}\)', t, flags=re.MULTILINE)
    if not bridge_sections:
        return None
    # Count active and gap status rows from each bridge archive table.
    active = len(re.findall(r'状态\s*\|\s*🟢\s*活跃', t))
    gap = len(re.findall(r'状态\s*\|\s*⚪\s*缺口', t))
    total = len(bridge_sections)
    return {
        'total': total,
        'active': active,
        'gap': gap,
    }

def parse_bridge_registry_entries():
    reg = ROOT / 'knowledge-tree' / 'registry.md'
    if not reg.is_file():
        return []
    try:
        t = reg.read_text('utf-8', errors='ignore')
    except:
        return []
    entries = []
    blocks = re.split(r'(?=^# §\d+ .*?\(Q\d{2}\))', t, flags=re.MULTILINE)
    for b in blocks:
        hm = re.search(r'^# §\d+ .*?\(Q\d{2}\)', b, flags=re.MULTILINE)
        if not hm:
            continue
        bridge_name = hm.group(0).strip()
        for raw in b.splitlines():
            line = raw.strip()
            if not line.startswith('|'):
                continue
            parts = [p.strip() for p in line.split('|')[1:-1]]
            # Discipline rows are expected as:
            # 学科 | 信度 | 主/辅 | 状态 | 核心工具 | 归桥日期
            if len(parts) < 5:
                continue
            if parts[0] in ('学科', '字段') or parts[0].startswith('---'):
                continue
            trust_m = re.search(r'(T[1-4])', parts[1], flags=re.IGNORECASE)
            if not trust_m:
                continue
            status_cell = parts[3] if len(parts) >= 4 else ''
            status_m = re.search(r'([🟢🟡🔴⚪])', status_cell)
            st = status_m.group(1) if status_m else '🟡'
            disc = parts[0]
            entries.append({
                'name': disc,
                'category': '学科桥（registry）',
                'status': st,
                'trust_level': trust_m.group(1).upper(),
                'discipline': disc,
                'bridge': bridge_name,
            })
    return entries

def collect_kunlun_stats(entries, harmonics):
    views={'axioms':0,'studies':0,'cases':0}
    vd=ROOT/'memory/views'
    if (vd/'axiom-cards-index.md').is_file():
        t=(vd/'axiom-cards-index.md').read_text('utf-8',errors='ignore')
        views['axioms']=len([l for l in t.split('\n') if l.strip().startswith('### AC-') and 'TEMPLATE' not in l])
    if (vd/'study-cards-index.md').is_file():
        t=(vd/'study-cards-index.md').read_text('utf-8',errors='ignore')
        views['studies']=len([l for l in t.split('\n') if l.strip().startswith('### SC-') and 'TEMPLATE' not in l])
    if (vd/'case-library-index.md').is_file():
        t=(vd/'case-library-index.md').read_text('utf-8',errors='ignore')
        views['cases']=len([l for l in t.split('\n') if l.strip().startswith('### CL-') and 'TEMPLATE' not in l])
    bridge_count=len([h for h in harmonics if '正式' in h['status']])
    bridge_candidate=len([h for h in harmonics if '候选' in h['status']])
    # Fallback to Q-Bridge registry when resonance-net is still a placeholder.
    if bridge_count == 0 and bridge_candidate == 0:
        br = parse_bridge_registry_stats()
        if br:
            bridge_count = br.get('active', 0)
            bridge_candidate = br.get('gap', 0)
    disciplines=Counter(e.get('discipline','') for e in entries if e.get('discipline'))
    tools=sum(1 for e in entries if '工具' in e.get('category','') or '法则' in e.get('category',''))
    trust=Counter(e.get('trust_level','') for e in entries if e.get('trust_level'))
    return views, bridge_count, bridge_candidate, disciplines, tools, trust

# ═══ CSS ═══

CSS="""
:root{--bg:#0f1923;--card:#1a2a3a;--card-hover:#1e3044;--border:#2a3f52;--text:#e0e8f0;--muted:#7a8a9a;--accent:#f59e0b;--green:#22c55e;--yellow:#eab308;--red:#ef4444;--blue:#3b82f6;--purple:#a855f7;--cyan:#06b6d4}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
.container{max-width:1400px;margin:0 auto;padding:20px}
.header{display:flex;justify-content:space-between;align-items:center;padding:16px 0;border-bottom:1px solid var(--border);margin-bottom:24px}
.header h1{font-size:24px;font-weight:700;color:var(--accent)}
.header h1 small{font-size:13px;color:var(--muted);font-weight:400;margin-left:10px}
.header .meta{font-size:12px;color:var(--muted);margin-top:4px}
.tab-bar{display:flex;gap:4px;margin-bottom:20px;overflow-x:auto;padding-bottom:4px;border-bottom:2px solid var(--border)}
.tab-btn{padding:8px 18px;border:1px solid var(--border);border-radius:8px 8px 0 0;background:var(--card);color:var(--muted);cursor:pointer;font-size:13px;font-weight:500;white-space:nowrap;transition:all .15s}
.tab-btn:hover{background:var(--card-hover);color:var(--text)}
.tab-btn.active{background:var(--accent);color:#000;border-color:var(--accent);font-weight:600}
.tab-pane{display:none}
.tab-pane.active{display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:24px}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:24px}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px;transition:transform .15s}
.card:hover{transform:translateY(-1px);border-color:var(--accent)}
.card .lbl{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.card .val{font-size:28px;font-weight:700}
.card .sub{font-size:12px;color:var(--muted);margin-top:4px}
.green{color:var(--green)}.yellow{color:var(--yellow)}.red{color:var(--red)}.blue{color:var(--blue)}
.tbl-wrap{background:var(--card);border:1px solid var(--border);border-radius:10px;overflow-x:auto;margin-bottom:16px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;padding:10px 14px;background:rgba(255,255,255,.04);color:var(--muted);font-weight:600;border-bottom:1px solid var(--border)}
td{padding:8px 14px;border-bottom:1px solid rgba(255,255,255,.04)}
tr:hover td{background:rgba(255,255,255,.02)}
.tag{display:inline-block;padding:2px 7px;border-radius:4px;font-size:11px;font-weight:600}
.tag-green{background:rgba(34,197,94,.15);color:var(--green)}
.tag-yellow{background:rgba(234,179,8,.15);color:var(--yellow)}
.tag-red{background:rgba(239,68,68,.15);color:var(--red)}
.tag-blue{background:rgba(59,130,246,.15);color:var(--blue)}
.tag-cyan{background:rgba(6,182,212,.15);color:var(--cyan)}
.badge{display:inline-flex;align-items:center;gap:3px;padding:2px 7px;border-radius:99px;font-size:11px}
.badge-green{background:rgba(34,197,94,.15);color:var(--green)}
.badge-yellow{background:rgba(234,179,8,.15);color:var(--yellow)}
.badge-gray{background:rgba(136,153,170,.15);color:var(--muted)}
.phase-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(125px,1fr));gap:6px;margin-top:8px}
.phase-item{padding:5px 8px;border-radius:5px;font-size:11px;font-weight:500;text-align:center}
.phase-done{background:rgba(34,197,94,.12);color:var(--green);border:1px solid rgba(34,197,94,.25)}
.phase-miss{background:rgba(239,68,68,.12);color:var(--red);border:1px solid rgba(239,68,68,.25)}
.chart-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:24px}
.chart-card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px}
.chart-card h3{font-size:13px;color:var(--muted);margin-bottom:10px}
section{margin-bottom:24px}
section h2{font-size:18px;font-weight:600;margin-bottom:12px;color:var(--accent);display:flex;align-items:center;gap:8px}
.footer{text-align:center;padding:20px 0;color:var(--muted);font-size:12px;border-top:1px solid var(--border);margin-top:20px}
.env-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px;margin-bottom:12px}
.env-item{padding:6px 10px;background:rgba(255,255,255,.03);border-radius:6px;font-size:12px;display:flex;align-items:center}
.env-item .ek{color:var(--muted);flex-shrink:0;min-width:80px}
.env-item .ev{font-weight:500;margin-left:4px}
.progress-bar{height:6px;background:var(--border);border-radius:3px;overflow:hidden;margin:4px 0}
.progress-fill{height:100%;border-radius:3px}
.filter-bar{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.filter-btn{padding:4px 12px;border:1px solid var(--border);border-radius:20px;background:var(--card);color:var(--muted);cursor:pointer;font-size:12px;transition:all .15s}
.filter-btn:hover{background:var(--card-hover);color:var(--text)}
.filter-btn.active{background:var(--accent);color:#000;border-color:var(--accent)}
.collapse-toggle{cursor:pointer;user-select:none}
.collapse-toggle:hover{color:var(--accent)}
.collapse-toggle.active{color:var(--accent)}
.collapse-body{display:none;padding:12px 0 0 0;border-top:1px solid var(--border);margin-top:8px}
.collapse-body.open{display:block}
.date-range{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap}
.date-btn{padding:4px 12px;border:1px solid var(--border);border-radius:6px;background:var(--card);color:var(--muted);cursor:pointer;font-size:12px;transition:all .15s}
.date-btn:hover{background:var(--card-hover);color:var(--text)}
.date-btn.active{background:var(--blue);color:#000;border-color:var(--blue)}
.sec-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:12px}
.kunlun-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;margin-bottom:16px}
@media(max-width:768px){.chart-row,.grid-2{grid-template-columns:1fr}.tab-btn{padding:6px 12px;font-size:12px}}
"""

# ═══ 渲染 ═══

def render_env(env):
    mem=env.get('memory',{});disks=env.get('disks',[]);ports=env.get('ports',[]);sec=env.get('security',{})
    cstr='✅ 是' if env.get('container') else '否'
    dr=''.join(f'<tr><td>{d["mount"]}</td><td style=font-size:11px;color:var(--muted)>{d["type"]}</td><td>{d["total"]}</td><td>{d["used"]}</td><td>{d["avail"]}</td><td><span class="tag {"tag-green" if int(d["use_pct"])<60 else "tag-yellow" if int(d["use_pct"])<80 else "tag-red"}">{d["use_pct"]}%</span></td></tr>' for d in disks)
    pr=''.join(f'<tr><td>{p["port"]}</td><td>{p["program"][:25]}</td><td>{p["pid"]}</td><td><span class="tag tag-green">🟢 运行</span></td></tr>' for p in ports)
    return f'''
<section><h2>📋 系统概览</h2></section>
<div class="env-grid">
  <div class="env-item"><span class="ek">操作系统</span><span class="ev">{env.get("os","N/A")[:45]}</span></div>
  <div class="env-item"><span class="ek">内核</span><span class="ev">{env.get("kernel","?")}</span></div>
  <div class="env-item"><span class="ek">架构</span><span class="ev">{env.get("arch","?")}</span></div>
  <div class="env-item"><span class="ek">主机名</span><span class="ev">{env.get("hostname","?")}</span></div>
  <div class="env-item"><span class="ek">运行时长</span><span class="ev">{env.get("uptime","?")}</span></div>
  <div class="env-item"><span class="ek">容器环境</span><span class="ev">{cstr}</span></div>
  <div class="env-item"><span class="ek">Codex CLI</span><span class="ev">{env.get("codex_version","?")}</span></div>
  <div class="env-item"><span class="ek">OpenClaw</span><span class="ev">{env.get("openclaw_version","?")}</span></div>
  <div class="env-item"><span class="ek">Node</span><span class="ev">{env.get("node_version","?")}</span></div>
  <div class="env-item"><span class="ek">Python</span><span class="ev">{env.get("python_version","?")}</span></div>
</div>
<section><h2>⚡ Gateway 进程</h2></section>
<div class="env-grid">
  <div class="env-item"><span class="ek">PID</span><span class="ev">{env.get("gw_pid","N/A")}</span></div>
  <div class="env-item"><span class="ek">运行时长</span><span class="ev">{env.get("gw_uptime","?")}</span></div>
  <div class="env-item"><span class="ek">CPU %</span><span class="ev">{env.get("gw_cpu_pct","?")}%</span></div>
  <div class="env-item"><span class="ek">内存 %</span><span class="ev">{env.get("gw_mem_pct","?")}%</span></div>
  <div class="env-item"><span class="ek">RSS</span><span class="ev">{env.get("gw_mem_kb",0)//1024} MB</span></div>
</div>
<section><h2>💾 资源使用</h2></section>
<div class="env-grid">
  <div class="env-item"><span class="ek">CPU</span><span class="ev">{env.get("cpu_model","?")} ({env.get("cpu_cores","?")}核)</span></div>
  <div class="env-item"><span class="ek">负载 1/5/15m</span><span class="ev">{env.get("load_1m","?")} / {env.get("load_5m","?")} / {env.get("load_15m","?")}</span></div>
</div>
<div class="grid-2">
  <div class="card"><div class="lbl">内存</div>
    <div style=font-size:13px;margin:4px 0;>{mem.get("used_gb","?")}GB / {mem.get("total_gb","?")}GB</div>
    <div class="progress-bar"><div class="progress-fill" style="width:{mem.get("used_pct",0)}%;background:var(--{"green" if mem.get("used_pct",0)<60 else "yellow" if mem.get("used_pct",0)<80 else "red"})"></div></div>
    <div class="sub">{mem.get("used_pct",0)}% 已用 · 可用 {mem.get("avail_gb",0)}GB</div>
  </div>
  <div class="card"><div class="lbl">Swap</div>
    <div style=font-size:13px;margin:4px 0;>{mem.get("swap_used_gb","?")}GB / {mem.get("swap_total_gb","?")}GB</div>
    <div class="progress-bar"><div class="progress-fill" style="width:{mem.get("swap_used_pct",0)}%;background:var(--{"green" if mem.get("swap_used_pct",0)<30 else "yellow" if mem.get("swap_used_pct",0)<60 else "red"})"></div></div>
    <div class="sub">{mem.get("swap_used_pct",0)}% 已用</div>
  </div>
</div>
<section><h2>💿 磁盘</h2></section>
<div class="tbl-wrap"><table><thead><tr><th>挂载点</th><th>类型</th><th>总容量</th><th>已用</th><th>可用</th><th>使用率</th></tr></thead><tbody>{dr or '<tr><td colspan=6 style=text-align:center;color:var(--muted)>无磁盘数据</td></tr>'}</tbody></table></div>
<section><h2>🔌 端口列表</h2></section>
<div class="tbl-wrap"><table><thead><tr><th>端口</th><th>程序</th><th>PID</th><th>状态</th></tr></thead><tbody>{pr or '<tr><td colspan=4 style=text-align:center;color:var(--muted)>⚠️ 容器环境无ss权限</td></tr>'}</tbody></table></div>
<p style=font-size:12px;color:var(--muted);>最后扫描: {datetime.now().strftime("%H:%M:%S")}</p>
<section><h2>🔒 安全</h2></section>
<div class="env-grid">
  <div class="env-item"><span class="ek">Root SSH</span><span class="ev">{"🔴 允许" if sec.get("root_ssh") else "✅ 禁止"}</span></div>
  <div class="env-item"><span class="ek">文件系统</span><span class="ev">{"🔴 只读" if sec.get("readonly_fs") else "✅ 可写"}</span></div>
</div>'''

def render_skills(skills):
    cats=Counter(s['category'] for s in skills)
    cat_keys=list(cats.keys())
    btns='<button class="filter-btn active" onclick="filterSkills(\'all\')">全部({})</button>'.format(len(skills))
    for ck in cat_keys:
        cnt=sum(1 for s in skills if s['category']==ck)
        lab=ck.split('/')[-1]
        btns+=f'<button class="filter-btn" onclick="filterSkills(\'{ck}\')">{lab}({cnt})</button>'
    rows=''.join(f'''<tr class="skill-row" data-cat="{s["category"]}">
  <td>{s["name"][:40]}</td>
  <td><span class="badge badge-green">{s["category"].split("/")[-1]}</span></td>
  <td>{s["version"] or "-"}</td>
  <td><span class="tag {"tag-green" if s["status"]=="🟢" else "tag-yellow"}">{s["status"]}</span></td>
  <td style=font-size:11px;color:var(--muted);max-width:200px;overflow:hidden;text-overflow:ellipsis;>{s.get("desc","")[:50]}</td>
</tr>''' for s in skills)
    return f'''
<p style=font-size:12px;color:var(--muted);margin-bottom:12px;>{" · ".join(f"{k}:{v}" for k,v in cats.most_common())} | 共{len(skills)}个</p>
<div class="filter-bar" id=skillFilters>{btns}</div>
<div class="tbl-wrap"><table><thead><tr><th>名称</th><th>类别</th><th>版本</th><th>状态</th><th>简介</th></tr></thead><tbody>{rows}</tbody></table></div>
<script>
function filterSkills(cat) {{
  document.querySelectorAll('#skillFilters .filter-btn').forEach(b=>b.classList.toggle('active',b.textContent.includes(cat)||(cat==='all'&&b.textContent.includes('全部'))));
  document.querySelectorAll('.skill-row').forEach(r=>r.style.display=(cat==='all'||r.dataset.cat===cat)?'':'none');
}}
</script>'''

def render_pipeline(tasks, phase_data):
    th=''.join(f'''<div class="card" style=margin-bottom:12px;>
  <div class="collapse-toggle" onclick="this.nextElementSibling.classList.toggle('open');this.classList.toggle('active')">
    <div class="flex" style=margin-bottom:6px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;>
      <span class="tag tag-cyan" style=font-size:11px;>{t.get("sessions",1)}轮</span>
      <span style=font-size:12px;color:var(--muted);>模型:{t.get("model","?")[:20]}</span>
      <span style=font-size:12px;color:var(--muted);>Token:{f"{t['usage_total']:,}" if t["usage_total"] else "-"}</span>
      <span style=font-size:12px;color:var(--muted);margin-left:auto;>▶ 展开</span></div>
    <div style=font-size:13px;>📝 {t["summary"]}</div>
  </div>
  <div class=collapse-body>
    <div class=env-grid style=margin-top:8px;>
      <div class=env-item><span class=ek>轨迹文件</span><span class=ev>{t["file"]}</span></div>
      <div class=env-item><span class=ek>会话轮次</span><span class=ev>{t.get("sessions",1)}轮</span></div>
      <div class=env-item><span class=ek>输入Token</span><span class=ev>{t["usage_in"]:,}</span></div>
      <div class=env-item><span class=ek>输出Token</span><span class=ev>{t["usage_out"]:,}</span></div>
      <div class=env-item><span class=ek>模型</span><span class=ev>{t.get("model","?")[:30]}</span></div>
    </div>
    <section><h2 style=font-size:14px;>📋 对话轨迹</h2></section>
    <div style=font-size:11px;color:var(--muted);max-height:200px;overflow-y:auto;padding:6px;background:rgba(0,0,0,.15);border-radius:6px;>
      <div style=margin-bottom:6px;font-weight:500;color:var(--text);>📌 起始: {t.get("first_prompt","")}</div>
      {"".join(f'<div style=padding:3px 0;>{"▸ " if i%2==0 else "◂ "}{p[:60]}</div>' for i,p in enumerate(t.get("all_prompts",[])))}
    </div>
  </div></div>''' for t in tasks)
    ph=''.join(f'''<div class="card" style=margin-bottom:12px;>
  <div class="collapse-toggle" onclick="this.nextElementSibling.classList.toggle('open');this.classList.toggle('active')">
    <div class="flex" style=margin-bottom:8px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;>
      <span class="tag tag-cyan" style=font-size:11px;>{pd["total"]}/11 工序</span>
      <span style=font-size:13px;>📄 {pd["title"][:50]}</span>
      <span style=font-size:12px;color:var(--muted);margin-left:auto;>▶ 展开</span></div>
  </div>
  <div class=collapse-body>
    <div class=phase-grid>{"".join(f'<div class="phase-item {"phase-done" if p["done"] else "phase-miss"}">#{p["num"]} {p["name"]}</div>' for p in pd["phases"])}</div>
  </div></div>''' for fname,pd in sorted(phase_data.items()))
    total_phases=sum(pd['total'] for pd in phase_data.values())
    max_phases=len(phase_data)*11 if phase_data else 1
    pct=round(total_phases/max_phases*100) if max_phases else 0
    return f'''
<section><h2>📗 最近会话 <span style=font-size:12px;color:var(--muted);font-weight:400>点击展开详情</span></h2></section>
{th or '<div class="card" style=text-align:center;color:var(--muted);padding:20px;>⚠️ 无会话轨迹数据</div>'}
<section><h2>⚙️ 十一阶工序覆盖</h2></section>
<div class=grid style=grid-template-columns:repeat(auto-fit,minmax(120px,1fr));margin-bottom:12px;>
  <div class=card><div class=lbl>总工序覆盖率</div><div class=\"val green\">{pct}%</div><div class=sub>{total_phases}/{max_phases}</div></div>
  <div class=card><div class=lbl>分析报告数</div><div class=val>{len(phase_data)}</div><div class=sub>memory/analysis/</div></div>
</div>
<section><h2>⚙️ 十一阶工序详情</h2></section>
{ph or '<div class="card" style=text-align:center;color:var(--muted);padding:20px;>暂无分析报告工序数据</div>'}'''

def render_token(token, token_daily, today_total, week_total, month_total):
    trend, td, wd, md = token_daily, today_total, week_total, month_total
    tk_total = f"{token['total']:,}" if token['total'] else "0"
    tk_pct = round(td/(token['total'] or 1)*100) if td else 0
    # 每日趋势数据
    date_labels=json.dumps([t['date'][5:] for t in trend])
    in_data=json.dumps([round(t['in']/1000,1) for t in trend])
    out_data=json.dumps([round(t['out']/1000,1) for t in trend])
    return f'''
<div class="date-range">
  <button class="date-btn active" data-range=all onclick="switchTokenRange('all')">全部({tk_total})</button>
  <button class="date-btn" data-range=today onclick="switchTokenRange('today')">今日({td:,})</button>
  <button class="date-btn" data-range=week onclick="switchTokenRange('week')">本周({wd:,})</button>
  <button class="date-btn" data-range=month onclick="switchTokenRange('month')">本月({month_total:,})</button>
</div>
<div class="grid" style=grid-template-columns:repeat(4,1fr);>
  <div class="card" id=tokenTotal><div class=lbl>总消耗</div><div class="val green">{token["total"]:,}</div><div class=sub>Input+Output</div></div>
  <div class="card" id=tokenIn><div class=lbl>Input</div><div class=val>{token["total_in"]:,}</div><div class=sub>{token["total_in"]/(token["total"] or 1)*100:.0f}%</div></div>
  <div class="card" id=tokenOut><div class=lbl>Output</div><div class=val>{token["total_out"]:,}</div><div class=sub>{token["total_out"]/(token["total"] or 1)*100:.0f}%</div></div>
  <div class="card" id=tokenCost><div class=lbl>估算费用</div><div class="val yellow">${token["cost"]:.4f}</div><div class=sub>近10个会话日志</div></div>
</div>
{('''
<div class="chart-card" style=margin-bottom:16px;>
  <h3>📈 每日Token趋势</h3>
  <canvas id=tokenChart style=max-height:250px;></canvas>
</div>''') if trend else ''}
<script>
var tokenTrendData = {{labels:{date_labels},in:{in_data},out:{out_data},total:{json.dumps([round(t['total']/1000,1) for t in trend])}}};
function switchTokenRange(mode) {{
  document.querySelectorAll('.date-btn').forEach(b=>b.classList.toggle('active',b.dataset.range===mode));
  if(mode==='all'){{document.getElementById('tokenTotal').querySelector('.val').textContent='{token["total"]:,}';return;}}
  var key = mode==='today' ? 'td' : mode==='week' ? 'wd' : 'md';
}}
</script>
<div class="tbl-wrap"><table><thead><tr><th>模型</th><th>Input</th><th>Output</th><th>总计</th></tr></thead><tbody>{''.join(f'<tr><td>{mdl}</td><td>{u["in_"]:,}</td><td>{u["out_"]:,}</td><td>{u["in_"]+u["out_"]:,}</td></tr>' for mdl,u in sorted(token.get('model_usage',{}).items(),key=lambda x:-(x[1]['in_']+x[1]['out_']))[:10]) or '<tr><td colspan=4 style=text-align:center;color:var(--muted)>暂无usage数据</td></tr>'}</tbody></table></div>'''

def render_kunlun(env, agents, cron, skills, pipe_tasks, pipe_phases, token, token_daily, today_total, week_total, month_total,
                  entries, sk_entries, tool_entries, harmonics, reports, challenges, version, hist,
                  views, bridge_count, bridge_candidate, disciplines, tools, trust):
    trust_c=Counter(e.get('trust_level','') for e in entries if e.get('trust_level'))
    cats=defaultdict(list)
    for e in entries: cats[e['category']].append(e)
    ccr=''.join(f'<tr><td>{cat}</td><td>{len(items)}</td><td><span class="tag tag-green">{sum(1 for i in items if i["status"]=="🟢")}</span></td><td><span class="tag tag-yellow">{sum(1 for i in items if i["status"]!="🟢")}</span></td></tr>' for cat,items in sorted(cats.items(),key=lambda x:-len(x[1])))
    hr=''.join(f'<tr><td>#{h["id"]}</td><td>{h["name"]}</td><td><strong>{h["intensity"]}</strong></td><td><span class="tag {"tag-green" if "正式" in h["status"] else "tag-yellow"}">{h["status"]}</span></td></tr>' for h in sorted(harmonics,key=lambda x:-x['intensity']))
    rr=''.join(f'<tr><td>{r["id"]}</td><td>{r["date"]}</td><td>{r["title"]}</td><td style=max-width:200px;color:var(--muted);>{r["output"][:30]}</td></tr>' for r in reports)
    chr_=''.join(f'<tr><td>{"议题" if c.get("is_open_issue") else "挑战"}#{c["id"]-100 if c.get("is_open_issue") else c["id"]}</td><td>{c["sharpness"]}</td><td><span class="tag {"tag-green" if c["status"]=="🟢" else "tag-yellow"}">{c["status"]}</span></td></tr>' for c in challenges[:10])
    # 学科分布
    disc_rows=''.join(f'<tr><td>{d}</td><td>{c}</td></tr>' for d,c in disciplines.most_common(10))
    return f'''
<div class=kunlun-grid>
  <div class=card><div class=lbl>知识条目</div><div class="val green">{len(entries)}</div><div class=sub>🟢{sum(1 for e in entries if e["status"]=="🟢")}·🟡{sum(1 for e in entries if e["status"]!="🟢")}</div></div>
  <div class=card><div class=lbl>学科桥</div><div class=val>{bridge_count}</div><div class=sub>候选{bridge_candidate}</div></div>
  <div class=card><div class=lbl>学科分类</div><div class=val>{len(disciplines)}</div><div class=sub>不同学科</div></div>
  <div class=card><div class=lbl>工具/法则</div><div class=val>{tools}</div><div class=sub>可用</div></div>
  <div class=card><div class=lbl>公理卡</div><div class=val>{views['axioms']}</div><div class=sub>T1 核心信仰</div></div>
  <div class=card><div class=lbl>学习卡</div><div class=val>{views['studies']}</div><div class=sub>T3 学习中</div></div>
  <div class=card><div class=lbl>案例库</div><div class=val>{views['cases']}</div><div class=sub>T4 档案</div></div>
  <div class=card><div class=lbl>版本</div><div class=val style=font-size:18px;>v{version}</div><div class=sub>{TODAY}</div></div>
  <div class=card><div class=lbl>信度等级</div><div class=val style=font-size:14px;>T1×{trust_c.get("T1",0)} T2×{trust_c.get("T2",0)}</div><div class=sub>T3×{trust_c.get("T3",0)} T4×{trust_c.get("T4",0)}</div></div>
  <div class=card><div class=lbl>分析报告</div><div class=val>{len(reports)}</div><div class=sub>完整存档</div></div>
  <div class=card><div class=lbl>反脆弱池</div><div class=val>{len(challenges)}</div><div class=sub>挑战+议题</div></div>
</div>
<div class="grid-2"><div><section><h2>📚 知识分类</h2></section><div class="tbl-wrap"><table><thead><tr><th>分类</th><th>总数</th><th>🟢</th><th>🟡</th></tr></thead><tbody>{ccr}</tbody></table></div></div>
<div><section><h2>🛡️ 反脆弱池</h2></section><div class="tbl-wrap"><table><thead><tr><th>条目</th><th>尖锐度</th><th>状态</th></tr></thead><tbody>{chr_ or "<tr><td colspan=3 style=text-align:center;color:var(--muted)>暂无</td></tr>"}</tbody></table></div></div></div>
<section><h2>🔗 谐波全表</h2></section><div class="tbl-wrap"><table><thead><tr><th>#</th><th>名称</th><th>强度</th><th>状态</th></tr></thead><tbody>{hr or "<tr><td colspan=4 style=text-align:center;color:var(--muted)>暂无</td></tr>"}</tbody></table></div>
<div class="grid-2" style=margin-top:16px;><div><section><h2>📖 学科分布（前10）</h2></section><div class="tbl-wrap"><table><thead><tr><th>学科</th><th>条目数</th></tr></thead><tbody>{disc_rows or '<tr><td colspan=2 style=text-align:center;color:var(--muted)>暂无</td></tr>'}</tbody></table></div></div>
<div><section><h2>📄 分析报告</h2></section><div class="tbl-wrap"><table><thead><tr><th>#</th><th>日期</th><th>标题</th><th>产出</th></tr></thead><tbody>{rr or "<tr><td colspan=4 style=text-align:center;color:var(--muted)>暂无</td></tr>"}</tbody></table></div></div></div>'''

def main():
    _setup_stdout()
    print("🐒 昆仑·全视 仪表盘生成器 v3.0\n")
    print("📥 采集昆仑认知数据...")
    version,hist=parse_version()
    harmonics=parse_harmonics()
    entries,sk_entries,tool_entries=parse_memory_index()
    if not entries:
        bridge_entries = parse_bridge_registry_entries()
        if bridge_entries:
            entries = bridge_entries
            sk_entries = bridge_entries
    reports=parse_reports()
    challenges=parse_antifragility()
    views, bridge_count, bridge_candidate, disciplines, tools, trust = collect_kunlun_stats(entries, harmonics)
    print(f"  版本:{version}  谐波:{len(harmonics)}条  条目:{len(entries)}条  报告:{len(reports)}份  挑战:{len(challenges)}个")
    print(f"  学科桥:{bridge_count} 学科:{len(disciplines)} 工具:{tools} 公理卡:{views['axioms']} 学习卡:{views['studies']} 案例:{views['cases']}")
    print("📥 采集系统运行时数据...")
    env=collect_environment()
    agents=collect_agents()
    cron=collect_cron()
    skills=collect_skills()
    pipe_tasks,pipe_phases=collect_pipeline_and_phases()
    token=collect_token()
    token_daily, today_total, week_total, month_total = collect_token_daily()
    print(f"  环境: {env.get('os','')[:20]} | CPU:{env.get('cpu_cores','?')}核({env.get('load_1m','?')}) | Mem:{env.get('memory',{}).get('used_pct','?')}% | 端口:{len(env.get('ports',[]))}个 | GW:{env.get('gw_uptime','?')}")
    print(f"  Agent:{len(agents)}个 | Cron:{len(cron)}个 | 技能:{len(skills)}个 | Token:{token['total']:,} | 工序报告:{len(pipe_phases)}份 | 日Token:{today_total:,}")
    print("\n🎨 渲染 HTML...")
    a_ok=sum(1 for a in agents if a['status']=='🟢')
    c_ok=sum(1 for c in cron if c['last_status']=='✅')
    tk=f"{(token['total']/1000):.0f}K" if token['total'] else '—'
    tot_ph=sum(pd['total'] for pd in pipe_phases.values())
    max_ph=len(pipe_phases)*11 or 1
    pct=round(tot_ph/max_ph*100)
    # 总览卡: 新增关键指标
    ov=f'''<div class="grid">
  <div class="card"><div class=lbl>🖥️ 系统健康</div><div style=padding:2px 0;><div style=display:flex;justify-content:space-between;font-size:11px;><span>CPU负载</span><span>{env.get("load_1m","?")}</span></div><div style=display:flex;justify-content:space-between;font-size:11px;><span>内存</span><span>{env.get("memory",{}).get("used_pct","?")}%</span></div><div style=display:flex;justify-content:space-between;font-size:11px;><span>Gateway</span><span>{env.get("gw_uptime","?")}</span></div></div><div class=sub>{env.get("os","N/A")[:30]}</div></div>
  <div class="card"><div class=lbl>🔌 端口</div><div class=val>{len(env.get("ports",[]))}</div><div class=sub>系统监听</div></div>
  <div class="card"><div class=lbl>🤖 Agent</div><div class=val>{a_ok}<span style=font-size:16px;color:var(--muted)>/{len(agents)}</span></div><div class=sub>SOUL完整:{a_ok}/{len(agents)}</div></div>
  <div class="card"><div class=lbl>⏰ 定时任务</div><div class=val>{c_ok}<span style=font-size:16px;color:var(--muted)>/{len(cron)}</span></div><div class=sub>近期正常:{c_ok}/{len(cron)}</div></div>
  <div class="card"><div class=lbl>🛠 技能</div><div class=val>{len(skills)}</div><div class=sub>多目录·{len([s for s in skills if s['status']=='🟢'])}正常</div></div>
  <div class="card"><div class=lbl>💰 Token</div><div class="val green">{tk}</div><div class=sub>今日{round(today_total/1000,1)}K · ${token["cost"]:.4f}</div></div>
  <div class="card"><div class=lbl>📊 昆仑知识</div><div class=val>{len(entries)}</div><div class=sub>知识·{bridge_count}桥·{tools}工具</div></div>
  <div class="card"><div class=lbl>🔗 工序覆盖率</div><div class="val green">{pct}%</div><div class=sub>{tot_ph}/{max_ph} · {len(pipe_phases)}报告</div></div>
  <div class="card"><div class=lbl>📚 学习生态</div><div class=val>{views['axioms']}公理+{views['studies']}学习+{views['cases']}案例</div><div class=sub>{len(harmonics)}谐波 · {len(disciplines)}学科</div></div>
</div>'''
    ar=''.join(f'<tr><td>{a["name"]}</td><td><span class="tag {"tag-green" if a["status"]=="🟢" else "tag-yellow"}">{a["status"]}</span></td><td>{a["soul"]}</td><td>{a["identity"]}</td><td>{a["memory"]}</td><td>{a["memory_dir"]}</td><td>{a["last_active"] or "-"}</td></tr>' for a in agents)
    agt_tab=f'<div class="tbl-wrap"><table><thead><tr><th>名称</th><th>状态</th><th>SOUL</th><th>身份</th><th>MEMORY</th><th>记忆目录</th><th>最后活跃</th></tr></thead><tbody>{ar or "<tr><td colspan=7 style=text-align:center;color:var(--muted)>无Agent</td></tr>"}</tbody></table></div>'
    cr=''.join(f'<tr><td>{c["name"][:40]}</td><td style=font-family:monospace;font-size:12px>{c["schedule"]}</td><td>{c["last_status"]}</td><td>{c["last_time"] or "-"}</td><td>{c["next_time"] or "-"}</td><td><span class="badge {"badge-green" if c["delivery"]!="none" else "badge-gray"}">{c["delivery"]}</span></td></tr>' for c in cron)
    cron_tab=f'<div class="tbl-wrap"><table><thead><tr><th>名称</th><th>调度</th><th>最近状态</th><th>上次运行</th><th>下次运行</th><th>投递</th></tr></thead><tbody>{cr or "<tr><td colspan=6 style=text-align:center;color:var(--muted)>无定时任务</td></tr>"}</tbody></table></div>'
    html=f'''<!DOCTYPE html>
<html lang=zh-CN>
<head><meta charset=UTF-8><meta content="width=device-width,initial-scale=1" name=viewport>
<title>昆仑·全视 仪表盘</title>
<script src=https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js></script>
<style>{CSS}</style></head>
<body><div class=container>
<div class=header><div><h1>🐒 昆仑·全视 <small>v{version}</small></h1><div class=meta>🔄 {TODAY} {datetime.now().strftime("%H:%M")} · 昆仑认知+系统运行时</div></div><div><span class="badge badge-green">● 运行中</span></div></div>
<div class=tab-bar>
  <button class="tab-btn active" onclick="showTab(0)">🏠 总览</button>
  <button class="tab-btn" onclick="showTab(1)">🖥️ 环境</button>
  <button class="tab-btn" onclick="showTab(2)">🤖 Agent</button>
  <button class="tab-btn" onclick="showTab(3)">⏰ 定时任务</button>
  <button class="tab-btn" onclick="showTab(4)">🛠 技能({len(skills)})</button>
  <button class="tab-btn" onclick="showTab(5)">🔗 流水线</button>
  <button class="tab-btn" onclick="showTab(6)">💰 Token</button>
  <button class="tab-btn" onclick="showTab(7)">🐒 昆仑</button>
</div>
<div id=tab0 class="tab-pane active">{ov}</div>
<div id=tab1 class=tab-pane>{render_env(env)}</div>
<div id=tab2 class=tab-pane>{agt_tab}</div>
<div id=tab3 class=tab-pane>{cron_tab}</div>
<div id=tab4 class=tab-pane>{render_skills(skills)}</div>
<div id=tab5 class=tab-pane>{render_pipeline(pipe_tasks,pipe_phases)}</div>
<div id=tab6 class=tab-pane>{render_token(token,token_daily,today_total,week_total,month_total)}</div>
<div id=tab7 class=tab-pane>{render_kunlun(env,agents,cron,skills,pipe_tasks,pipe_phases,token,token_daily,today_total,week_total,month_total,entries,sk_entries,tool_entries,harmonics,reports,challenges,version,hist,views,bridge_count,bridge_candidate,disciplines,tools,trust)}</div>
<div class=footer>昆仑系统·{TODAY}·仪表盘自动生成</div></div>
<script>
function showTab(n){{document.querySelectorAll('.tab-pane').forEach((e,i)=>e.classList.toggle('active',i===n));document.querySelectorAll('.tab-btn').forEach((e,i)=>e.classList.toggle('active',i===n));}}</script>
<script>
{''}{f'''
var td={json.dumps([{"date":t["date"][5:],"total":round(t["total"]/1000,1)} for t in token_daily])};
new Chart(document.getElementById('tokenChart'),{{type:'bar',data:{{labels:td.map(d=>d.date),datasets:[{{label:'Token(K)',data:td.map(d=>d.total),backgroundColor:'rgba(59,130,246,0.6)',borderColor:'rgba(59,130,246,1)',borderWidth:1,borderRadius:4}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:{{x:{{ticks:{{color:'#8899aa'}}}},y:{{ticks:{{color:'#8899aa'}}}}}}}}}});
''' if token_daily else ''}
</script>
</body></html>'''
    out=ROOT/'dashboard.html'
    out.write_text(html,'utf-8')
    print(f"\n✅ 仪表盘已生成: {out}")
    print(f"   文件大小: {out.stat().st_size:,} 字节")

if __name__=="__main__":
    main()
