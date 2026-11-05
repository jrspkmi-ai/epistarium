"""Optional interactive UI smoke test. Requires Playwright and Chromium, not runtime dependencies."""
from pathlib import Path
from threading import Thread
from time import sleep
from tempfile import TemporaryDirectory
import argparse
import json
from epistarium.observatory.server import ObservatoryServer
from epistarium.observatory.runner import ObservatoryRunner


def run(out_dir, chromium='/usr/bin/chromium'):
    from playwright.sync_api import sync_playwright
    out=Path(out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    root=out/'private-workspace'
    server=ObservatoryServer(root,0)
    server_thread=Thread(target=server.serve_forever,daemon=True)
    server_thread.start()
    fixture=Path(__file__).resolve().parents[1]/'examples/f4_synthetic/pathfinder_cases.json'
    state=server.store.create('SYNTHETIC: Digital crisis communication',fixture=str(fixture),language='en')
    server.runner.launch(state['id'])
    for attempt in range(200):
        if server.store.get(state['id'])['status']=='AWAITING_APPROVAL':break
        sleep(.05)
    else:raise AssertionError('Synthetic run did not arrive at approval gate')
    url=f'http://127.0.0.1:{server.server_port}/?run={state["id"]}'
    evidence={}
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=chromium,args=['--no-sandbox','--disable-dev-shm-usage'])
            page=browser.new_page(viewport={'width':1660,'height':1000},device_scale_factor=1)
            errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
            page.goto(url,wait_until='networkidle')
            page.get_by_text('Research Observatory').first.wait_for()
            page.locator('#run-status').wait_for()
            assert page.locator('#run-status').inner_text()=='AWAITING_APPROVAL'
            assert page.locator('#count-queued').inner_text()=='9'
            assert page.locator('#count-review').inner_text()=='1'
            assert 'SYNTHETIC' in page.locator('#constraint-text').inner_text()
            dark=out/'observatory_dark_en_synthetic.png'
            page.screenshot(path=str(dark),full_page=True)
            page.locator('#lang-id').click()
            assert page.locator('#persona-board').count()==1
            assert page.get_by_text('Peringatan dan batasan').count()==1
            page.locator('#theme-toggle').click()
            assert page.evaluate('document.documentElement.dataset.theme')=='light'
            light=out/'observatory_light_id_synthetic.png'
            page.screenshot(path=str(light),full_page=True)
            page.get_by_role('button',name='Setujui',exact=True).click()
            page.locator('#approval-dialog').wait_for(state='visible')
            page.locator('#decision-reason').fill('Reviewed as synthetic fixture, not verified evidence.')
            page.locator('#confirm-decision').click()
            page.locator('#approval-dialog').wait_for(state='hidden')
            page.wait_for_function("document.querySelector('#run-status').textContent.trim() === 'RELEASE_AUTHORIZED'",timeout=15000)
            assert page.locator('#approvals-count').inner_text()=='0'
            assert not errors, errors
            evidence={'status':'PASS','screenshots':[str(dark),str(light)],'run_status':server.store.get(state['id'])['status'],
                      'language':page.evaluate('document.documentElement.lang'),'theme':page.evaluate('document.documentElement.dataset.theme'),
                      'browser':'Chromium headless','page_errors':errors,'test_data':'SYNTHETIC, NOT EMPIRICAL'}
            browser.close()
    finally:
        server.shutdown();server.server_close();server_thread.join(timeout=3)
    return evidence

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--chromium',default='/usr/bin/chromium')
    args=p.parse_args()
    result=run(args.out,args.chromium)
    Path(args.out,'browser_smoke.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
