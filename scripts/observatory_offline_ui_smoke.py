"""Headless Chromium UI test without network, using an actual synthetic Jorhas run.

This tests visual layout and controls, NOT a live browser/server connection.
"""
from pathlib import Path
from threading import Thread
from tempfile import TemporaryDirectory
import json
import re
import time
import argparse
from epistarium.observatory.store import ObservatoryStore
from epistarium.observatory.runner import ObservatoryRunner

ROOT=Path(__file__).resolve().parents[1]

def run(out,chromium='/usr/bin/chromium'):
    from playwright.sync_api import sync_playwright
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    with TemporaryDirectory(prefix='epi-offline-ui-') as directory:
        store=ObservatoryStore(directory)
        r=store.create('SYNTHETIC: Digital crisis communication research',fixture=str(ROOT/'examples/f4_synthetic/pathfinder_cases.json'))
        runner=ObservatoryRunner(store);runner.launch(r['id'])
        for i in range(300):
            if store.get(r['id'])['status']=='AWAITING_APPROVAL':break
            time.sleep(.02)
        state=store.get(r['id'])
        assert state['status']=='AWAITING_APPROVAL',state['status']
        safe={k:v for k,v in state.items() if k not in ('config','fixture')}
        bundled={'run':safe,'evidence':store.evidence_summary(r['id']),
                 'artifacts':store.artifacts(r['id']),
                 'recent_events':store.events(r['id'])[-30:]}
        page_js=(ROOT/'epistarium/observatory/static/app.js').read_text(encoding='utf-8')
        css=(ROOT/'epistarium/observatory/static/style.css').read_text(encoding='utf-8')
        html=(ROOT/'epistarium/observatory/static/index.html').read_text(encoding='utf-8')
        html=re.sub(r'<link rel="stylesheet" href="/style.css">','',html)
        html=re.sub(r'<script src="/app.js" defer></script>','',html)
        bootstrap=f'''(()=>{{
          const kv=new Map();Object.defineProperty(window,'localStorage',{{configurable:true,value:{{
            getItem:(k)=>kv.get(k)||null,setItem:(k,v)=>kv.set(k,String(v)),removeItem:(k)=>kv.delete(k)
          }}}});
          const full={json.dumps(bundled,ensure_ascii=False)};
          window.fetch=async(url,init)=>{{
            const p=String(url);
            let data={{}};
            if(p==='/api/boot')data={{token:'offline-mock-token',default_language:'en',default_theme:'dark'}};
            else if(p==='/api/runs')data={{runs:[{{id:full.run.id,idea:full.run.idea,mode:full.run.mode,status:full.run.status}}]}};
            else if(p.startsWith('/api/runs/'))data=full;
            return {{ok:true,json:async()=>data}};
          }};
          window.EventSource=class{{constructor(){{}}addEventListener(){{}}close(){{}}}};
        }})();'''
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
            page=browser.new_page(viewport={'width':1680,'height':1000},device_scale_factor=1)
            errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
            page.set_content(html,wait_until='load')
            page.add_style_tag(content=css)
            page.evaluate(bootstrap)
            page.add_script_tag(content=page_js)
            page.locator('#count-review').filter(has_text='1').wait_for(timeout=9000)
            assert page.locator('#count-queued').inner_text()=='9'
            assert page.locator('#run-status').inner_text()=='AWAITING_APPROVAL'
            assert page.locator('#persona-board .persona-card').count()==10
            assert 'SYNTHETIC' in page.locator('#constraint-text').inner_text()
            dark=output/'observatory_dark_en_synthetic.png';page.screenshot(path=str(dark),full_page=True)
            page.locator('#lang-id').click()
            assert page.locator('#lang-id').get_attribute('aria-pressed')=='true'
            assert page.get_by_text('Peringatan dan batasan').count()==1
            page.locator('#theme-toggle').click()
            assert page.evaluate('document.documentElement.dataset.theme')=='light'
            light=output/'observatory_light_id_synthetic.png';page.screenshot(path=str(light),full_page=True)
            page.get_by_role('button',name='Setujui',exact=True).click()
            assert page.locator('#approval-dialog').is_visible()
            page.locator('#approval-dialog button[value="cancel"]').click()
            assert not page.locator('#approval-dialog').is_visible()
            assert not errors,errors
            browser.close()
        return {'status':'PASS','screenshots':[str(dark),str(light)],'test_mode':'OFFLINE_UI_WITH_REAL_SYNTHETIC_JORHAS_OUTPUT',
                'browser':'Chromium headless','language_switch':'PASS','theme_switch':'PASS',
                'persona_cards':10,'approval_dialog':'PASS','page_errors':errors,
                'local_server_browser_connectivity':'NOT_RUN_OR_BLOCKED_IN_THIS_ENVIRONMENT'}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',required=True);a.add_argument('--chromium',default='/usr/bin/chromium')
    args=a.parse_args();report=run(args.out,args.chromium)
    Path(args.out,'OFFLINE_UI_REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
