from pathlib import Path
p = Path('/workspace/proto-page/index.html')
html = p.read_text(encoding='utf-8')

css = '''
    .dlg-btn {
      position: fixed; top: 14px; left: 14px; z-index: 11;
      appearance: none; border: 1px solid rgba(255,255,255,0.14);
      border-radius: 999px; padding: 8px 12px; font: inherit; font-size: 12px;
      color: #e2e8f0; background: rgba(15,23,42,0.72); backdrop-filter: blur(10px);
      cursor: pointer;
    }
    .dlg-panel {
      position: fixed; top: 52px; left: 14px; z-index: 11;
      width: min(340px, calc(100vw - 28px)); max-height: min(70vh, 520px);
      overflow: auto; padding: 12px; border-radius: 16px;
      background: rgba(15,23,42,0.88); border: 1px solid rgba(255,255,255,0.12);
      backdrop-filter: blur(12px); color: #e2e8f0; display: none;
    }
    .dlg-panel.open { display: block; }
    .dlg-panel h3 {
      margin: 0 0 8px; font-size: 13px; letter-spacing: 0.06em;
      text-transform: uppercase; color: #a5b4fc;
    }
    .dlg-panel .dlg-item {
      width: 100%; text-align: left; appearance: none; border: 0;
      border-radius: 12px; padding: 10px 10px; margin-bottom: 6px;
      background: rgba(255,255,255,0.05); color: #e2e8f0; cursor: pointer;
      font: inherit; font-size: 13px; line-height: 1.35;
    }
    .dlg-panel .dlg-item:hover { background: rgba(167,139,250,0.22); }
    .dlg-panel .dlg-item .say {
      color: #67e8f9; font-weight: 650; display: block; margin-bottom: 2px;
    }
    .dlg-panel .dlg-item .reply {
      color: rgba(226,232,240,0.75); font-size: 12px;
    }
    .dlg-panel .dlg-tip {
      font-size: 11px; color: rgba(226,232,240,0.45); margin-bottom: 8px;
    }
'''
if '.dlg-btn' not in html:
    html = html.replace('    .dock-toggle {', css + '    .dock-toggle {')

markup = '''
  <button type="button" class="dlg-btn" id="dlgListBtn">对话列表</button>
  <div class="dlg-panel" id="dlgPanel" aria-label="Supported dialogs">
    <h3>Supported Dialogs</h3>
    <div class="dlg-tip">Click a line to hear the reply. Say the blue English with the mic.</div>
    <div id="dlgList"></div>
  </div>

'''
if 'id="dlgListBtn"' not in html:
    html = html.replace('<button type="button" class="dock-toggle top" id="togglePicker"', markup + '<button type="button" class="dock-toggle top" id="togglePicker"')

js = r'''
    // Dialog list panel (top-left)
    function renderDialogList() {
      const box = document.getElementById('dlgList');
      if (!box || !DIALOGS || !DIALOGS.dialogs) return;
      box.innerHTML = DIALOGS.dialogs
        .filter((d) => d.id !== 'fallback')
        .map((d) => {
          const say = (d.triggers && d.triggers[0]) ? d.triggers[0] : d.id;
          const more = (d.triggers && d.triggers.length > 1)
            ? ` · also: ${d.triggers.slice(1, 3).join(', ')}`
            : '';
          return `<button type="button" class="dlg-item" data-dlg="${d.id}">
            <span class="say">Say: ${say}${more}</span>
            <span class="reply">Reply: ${d.reply}${d.zh ? '（' + d.zh + '）' : ''}</span>
          </button>`;
        }).join('');
    }

    const dlgListBtn = document.getElementById('dlgListBtn');
    const dlgPanel = document.getElementById('dlgPanel');
    dlgListBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      renderDialogList();
      dlgPanel.classList.toggle('open');
    });
    document.getElementById('dlgList').addEventListener('click', (e) => {
      const btn = e.target.closest('button[data-dlg]');
      if (!btn || !DIALOGS) return;
      const d = DIALOGS.dialogs.find((x) => x.id === btn.dataset.dlg);
      if (d) speakDialog(d);
    });
    document.addEventListener('click', (e) => {
      if (!dlgPanel.classList.contains('open')) return;
      if (e.target.closest('#dlgPanel') || e.target.closest('#dlgListBtn')) return;
      dlgPanel.classList.remove('open');
    });

'''

if 'renderDialogList' not in html:
    # insert after loadDialogs();
    if 'loadDialogs();' not in html:
        raise SystemExit('loadDialogs missing')
    html = html.replace('    loadDialogs();', '    loadDialogs().then(() => renderDialogList());' + '\n' + js, 1)
    # but loadDialogs is async function without return promise properly - it returns promise from async
    # Fix loadDialogs to be awaited - already async so .then works

# Ensure loadDialogs returns properly - it's `async function loadDialogs()` so OK

# Update learn meta voice label if present
html = html.replace('微软神经网络语音 · 非浏览器简易 TTS', '可爱童声音色 AnaNeural · 非浏览器简易 TTS')

p.write_text(html, encoding='utf-8')
print('ui ok', 'dlgListBtn' in html, 'renderDialogList' in html)
