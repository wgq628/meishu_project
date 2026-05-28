#!/usr/bin/env python3
"""
maintain_counters.py - 昆仑系统引用计数器维护工具

功能：
1. add-aliases — 为 memory-index.md 的所有条目生成规范引用别名字段
2. count — 从最新分析报告的洞察卡表格读取引用，更新 memory-index.md 的引用次数
3. init — 初始化所有条目的"近30天活跃"字段（系统诞生后前30天统一设为基线值）

使用方式：
  python3 memory/maintain_counters.py add-aliases   # 批量添加别名字段
  python3 memory/maintain_counters.py count          # 统计最新报告的引用
  python3 memory/maintain_counters.py init           # 初始化活跃基线

注意：本工具修改 memory-index.md 文件。建议先备份。
"""

import os
import re
import sys
from datetime import date, datetime

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_INDEX = os.path.join(WORKSPACE, "memory-index.md")
ANALYSIS_DIR = os.path.join(WORKSPACE, "memory", "analysis")

TODAY = date.today()
TODAY_STR = TODAY.isoformat()

# ============================================================
# 别名映射表（手工维护，覆盖自动生成的别名）
# ============================================================
ALIAS_OVERRIDES = {
    "认知-技术错配（Cognition-Technology Mismatch, CTM）": "CTM法则, 认知-技术错配法则, CTM",
    "S-I-D复合链条": "S-I-D链条, SID链条, SID复合链条",
    "S-I-D链条·合规成本传导变体": "SID合规传导, S-I-D合规变体",
    "防御均衡法则": "防御均衡",
    "支付行业的基础设施化——涌现判定": "支付基础设施化",
    "支付入口的隐形化——涌现判定（第二层）": "支付入口隐形化",
    "加速版增长的极限——基模": "加速增长极限",
    "BCS三阶战略（根据地-现金流-制高点）": "BCS三阶战略, BCS, BCS法则, BCS战略",
    "五类根因分析法（A-E）": "五类根因, A-E根因分析",
    "存量锁定下的马太效应（模式①修正版）": "存量锁定马太效应, 模式①修正版",
    "目标置换（模式④）": "目标置换, 模式④",
    "结构性剪刀差（抽象模式）": "结构性剪刀差",
    "问题变异律（核心-边缘模式）": "问题变异律",
    "三层解耦分析框架（跨系统/跨标准场景）": "三层解耦, 层解耦",
    "认证锁替代技术锁": "认证锁, 认证替代技术",
    "政府主权级认证锁（认证锁子分类）": "政府主权级认证锁, 主权级认证锁",
    "低端颠覆的生态限定条件（Christensen修正）": "Christensen修正, Christensen生态限定",
    "三路径并行资源分配法则(80/15/5)": "80/15/5法则, 三路径并行, 80/15/5",
    "议程设置权（权力维⑤）": "议程设置权, 权力维⑤",
    "传播学三框架（信息扩散/议程设置/框架理论）": "传播学三框架",
    "伦理学三框架（后果论/义务论/正义论）": "伦理学三框架",
    "法学框架①：权利义务分析": "法学①, 权利义务分析",
    "法学框架②：归责机制": "法学②, 归责机制",
    "法学框架③：程序正义 vs 实质正义": "法学③, 程序正义实质正义",
    "法律人格错位": "法律人格",
    "公平性审查三步法（伦理学·十六字诀·工序②）": "公平性审查, 公平性三步法",
    "照护赤字剪刀差": "照护剪刀差",
    "照护剪刀差城乡变异律": "剪刀差城乡变异, 城乡变异律",
    "伴随式意图捕获机制": "意图捕获",
    "监管时滞法则": "监管时滞",
    "溯源三原则": "溯源原则",
    "反身性思考": "反身性",
    "五维压力测试框架": "五维测试, 压力测试",
    "不对称性拷问": "不对称拷问",
    "三刀判别法": "三刀法",
    "临界值校准法": "临界值校准",
    "替换测试": "替换测试法",
    "痛点归因测试": "痛点归因",
    "生存优先于发展": "生存优先",
    "失效原点定位法": "失效原点",
    "认知演化日志范式": "认知日志, 演化日志",
    "联结桥库": "联结桥, bridges.md",
    "反脆弱池": "反脆弱, anti-fragility",
    "结构化命题记录体系": "结构化命题, MEMORY.md格式",
}


def auto_alias(name):
    """从条目名自动生成规范引用别名"""
    # 检查是否有手工覆盖
    if name in ALIAS_OVERRIDES:
        return ALIAS_OVERRIDES[name]
    
    # 如果名称中有括号，括号前为主名
    parts = name.split('（', 1)
    if len(parts) > 1:
        main = parts[0].strip()
        
        # 检查括号内是否有英文缩写
        inner = parts[1].rstrip('）')
        en_abbr = re.findall(r'[A-Z]{2,}', inner)
        if en_abbr:
            return f"{main}, {', '.join(en_abbr)}"
        
        return main
    
    # 去掉方括号
    name_clean = name.replace('[', '').replace(']', '').strip()
    return name_clean


# ============================================================
# 子命令实现
# ============================================================

def cmd_add_aliases():
    """为所有条目添加规范引用别名字段"""
    with open(MEMORY_INDEX, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按条目分割（以 "### " 开头的行为新条目，排除分类标题 "### ———"）
    lines = content.split('\n')
    result = []
    i = 0
    
    added_count = 0
    skipped_count = 0
    already_has_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 检测条目开头：以 "### " 开头且不是分类标题（不含 ———）
        # 也支持方括号格式 "### [name]"
        is_entry = False
        entry_name = None
        
        m1 = re.match(r'^### (.+?)$', line)
        if m1:
            name = m1.group(1).strip()
            if '———' not in name and '记忆索引' not in name[:6] and '模板' not in name[:4]:
                is_entry = True
                entry_name = name
                if entry_name.startswith('[') and entry_name.endswith(']'):
                    entry_name = entry_name[1:-1].strip()
        
        if is_entry:
            result.append(line)
            i += 1
            
            # 检查接下来几行是否已有别名或规范引用别名
            already_has_alias = False
            look_ahead = 0
            while i + look_ahead < len(lines) and look_ahead < 5:
                next_line = lines[i + look_ahead]
                if next_line.strip().startswith('- **') and ('规范引用别名' in next_line or '引用别名' in next_line):
                    already_has_alias = True
                    already_has_count += 1
                    break
                if next_line.strip() == '' or not next_line.startswith('- **'):
                    break
                look_ahead += 1
            
            if already_has_alias:
                # 已有别名字段，保留原样
                while i < len(lines) and (lines[i].startswith('- **') or lines[i].strip() == ''):
                    result.append(lines[i])
                    i += 1
            else:
                # 需要添加别名字段
                alias = auto_alias(entry_name)
                result.append(f'- **规范引用别名**：{alias}')
                added_count += 1
        else:
            result.append(line)
            i += 1
    
    # 写回文件
    with open(MEMORY_INDEX, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))
    
    print(f"✅ 别名处理完毕")
    print(f"   新增：{added_count} 条")
    print(f"   已存在：{already_has_count} 条")
    print(f"   跳过（非条目行）：{skipped_count} 条")


def cmd_count():
    """从最新分析报告统计引用"""
    # 找最新的分析报告
    report_files = []
    for f in os.listdir(ANALYSIS_DIR):
        if f.endswith('.md') and f != 'index.md' and f != 'TEMPLATE.md':
            full = os.path.join(ANALYSIS_DIR, f)
            report_files.append((os.path.getmtime(full), full))
    
    if not report_files:
        print("❌ 未找到分析报告")
        return
    
    # 按修改时间排序，取最新的
    report_files.sort(reverse=True)
    latest_path = report_files[0][1]
    print(f"📄 扫描报告：{os.path.basename(latest_path)}")
    
    with open(latest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找洞察卡表格
    # 格式：| 编号 | 标题 | 摘要 | 置信度 | 对应memory-index条目 |
    # 需要找到表格体（行以 | 开头，包含数字编号）
    in_table = False
    references = []
    
    for line in content.split('\n'):
        # 检测表格分隔行
        if '|' in line and all(p.strip() in ('', '-', '---', '----', '-----') for p in line.split('|')[1:-1]):
            in_table = True
            continue
        
        if in_table and line.startswith('| '):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            # 检查是否是洞察卡行（有编号且至少5列）
            if len(parts) >= 5 and (parts[0].isdigit() or parts[0].startswith('R-')):
                ref_text = parts[4]  # 对应memory-index条目列
                if ref_text and ref_text != '-':
                    references.append(ref_text)
        
        # 检测到下一个一级/二级标题时退出表格
        if in_table and line.startswith('## '):
            in_table = False
    
    if not references:
        print("⚠️  未在报告中找到洞察卡引用")
        return
    
    print(f"🔗 发现 {len(references)} 条引用：{references}")
    
    # 读取 memory-index.md
    with open(MEMORY_INDEX, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析所有条目，构建别名→条目偏移的映射
    lines = content.split('\n')
    entries = []  # (start_line, name, aliases)
    
    i = 0
    while i < len(lines):
        m = re.match(r'^### (.+?)$', lines[i])
        if m and '———' not in m.group(1) and '记忆索引' not in m.group(1)[:6] and '模板' not in m.group(1)[:4]:
            name_full = m.group(1).strip()
            name = name_full.replace('[', '').replace(']', '').strip()
            aliases = [name]
            
            # 检查后续行获取别名
            j = i + 1
            while j < len(lines) and j < i + 8:
                am = re.search(r'\*\*规范引用别名\*\*：(.+)', lines[j])
                if am:
                    alias_text = am.group(1).strip()
                    aliases = [a.strip() for a in alias_text.split(',')]
                    break
                j += 1
            
            entries.append((i, name, aliases))
        i += 1
    
    print(f"📚 memory-index.md 共 {len(entries)} 个条目")
    
    # 对每条引用做匹配
    matched = 0
    unmatched = []
    
    for ref_text in references:
        ref_clean = ref_text.strip()
        found = False
        
        for start_line, entry_name, aliases in entries:
            # 精确匹配别名
            if any(ref_clean == alias for alias in aliases):
                found = True
                _update_entry_count(lines, start_line, entry_name)
                matched += 1
                break
            
            # 包含匹配（别名包含引用文本 或 引用文本包含别名）
            if any(ref_clean in alias or alias in ref_clean for alias in aliases):
                found = True
                _update_entry_count(lines, start_line, entry_name)
                matched += 1
                break
        
        if not found:
            unmatched.append(ref_text)
    
    # 写回文件
    with open(MEMORY_INDEX, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ 引用更新完成")
    print(f"   匹配成功：{matched} 条")
    if unmatched:
        print(f"   ⚠️ 未匹配：{unmatched}")
    
    return matched, unmatched


def _update_entry_count(lines, start_line, entry_name):
    """更新单个条目的引用计数和活跃日期"""
    # 在 entry_name 下查找引用次数、最后活跃、近30天活跃字段
    for offset in range(1, 10):
        idx = start_line + offset
        if idx >= len(lines):
            break
        line = lines[idx]
        
        # 更新引用次数
        rm = re.match(r'(-\s+\*\*引用次数\*\*：)(\d+)', line)
        if rm:
            new_count = int(rm.group(2)) + 1
            lines[idx] = f"{rm.group(1)}{new_count}"
            continue
        
        # 更新最后活跃
        lm = re.match(r'(-\s+\*\*最后活跃\*\*：)([\d-]+)', line)
        if lm:
            lines[idx] = f"{lm.group(1)}{TODAY_STR}"
            continue
        
        # 更新近30天活跃（重新计算）
        am = re.match(r'(-\s+\*\*近30天活跃\*\*：)(\d+)(.*)', line)
        if am:
            # 重新计算近30天活跃：检查当前日期与最后活跃之差
            last_active = None
            for j in range(1, 10):
                check_idx = start_line + j
                if check_idx >= len(lines):
                    break
                la_m = re.search(r'\*\*最后活跃\*\*：([\d-]+)', lines[check_idx])
                if la_m:
                    try:
                        last_active = datetime.strptime(la_m.group(1), '%Y-%m-%d').date()
                    except ValueError:
                        pass
                    break
            
            suffix = am.group(2) if len(am.groups()) > 2 else am.group(3) if len(am.groups()) > 2 else ''
            
            if last_active and (TODAY - last_active).days <= 30:
                # 更新近30天活跃计数
                new_act = int(am.group(2)) + 1
                lines[idx] = f"{am.group(1)}{new_act}{am.group(3) if len(am.groups()) > 2 else ''}"
            else:
                # 最后活跃>30天，或无法确定，置为1
                lines[idx] = f"{am.group(1)}1{am.group(3) if len(am.groups()) > 2 else ''}"
            
            break

    print(f"   📈 {entry_name} → 引用+1")


def cmd_init():
    """初始化所有条目的活跃基线"""
    with open(MEMORY_INDEX, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    updated_count = 0
    
    for i, line in enumerate(lines):
        # 更新最后活跃——如果为空或未知，设为今天
        lm = re.match(r'(-\s+\*\*最后活跃\*\*：)(\s*)$', line)
        if lm:
            lines[i] = f"{lm.group(1)}{TODAY_STR}"
            updated_count += 1
            continue
        
        # 检查"近30天活跃：0" → 判断是否在最近30天诞生的，是则设为基线
        am = re.match(r'(-\s+\*\*近30天活跃\*\*：)(0)\s*$', line)
        if am:
            # 找这条目对应的最后活跃日期
            last_active = None
            for j in range(max(0, i-15), i):
                la_m = re.search(r'\*\*最后活跃\*\*：([\d-]+)', lines[j])
                if la_m:
                    try:
                        la_date = datetime.strptime(la_m.group(1), '%Y-%m-%d').date()
                        if (TODAY - la_date).days <= 30:
                            last_active = la_date
                    except ValueError:
                        pass
            
            if last_active:
                # 诞生在30天内 → 设置基线活跃
                lines[i] = f"{am.group(1)}1"
                updated_count += 1
    
    with open(MEMORY_INDEX, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ 活跃基线初始化完成")
    print(f"   更新：{updated_count} 条")
    return updated_count


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 memory/maintain_counters.py <子命令>")
        print("  子命令: add-aliases   — 批量添加规范引用别名字段")
        print("  子命令: count          — 从最新报告统计引用")
        print("  子命令: init           — 初始化活跃基线")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "add-aliases":
        cmd_add_aliases()
    elif cmd == "count":
        cmd_count()
    elif cmd == "init":
        cmd_init()
    else:
        print(f"❌ 未知子命令: {cmd}")
        sys.exit(1)
