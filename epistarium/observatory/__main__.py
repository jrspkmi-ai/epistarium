"""Launch the local live observatory without requiring an AI host."""
import argparse
from pathlib import Path
from .server import serve

def main(argv=None):
    parser=argparse.ArgumentParser(prog='epistarium observatory',description='Local research monitoring with approval gates')
    parser.add_argument('--root',default=str(Path.home()/'.epistarium-observatory'),help='Private local directory for run state and artifacts')
    parser.add_argument('--port',type=int,default=4782)
    parser.add_argument('--open',action='store_true',help='Open the browser when the server starts')
    parser.add_argument('--no-browser',action='store_true',help='Do not open a browser')
    parser.add_argument('--idea',help='Start a real Jorhas run with this topic')
    parser.add_argument('--mode',choices=('pathfind','full'),default='pathfind')
    parser.add_argument('--fixture',help='User-approved local synthetic JSON fixture for Path Finding')
    parser.add_argument('--config',help='User-approved JSON config for the actual Python workflow')
    parser.add_argument('--online',action='store_true',help='Requires browser approval before external requests')
    parser.add_argument('--lang',choices=('en','id'),default='en')
    parser.add_argument('--as-of',help='YYYY-MM-DD for reproducibility')
    args=parser.parse_args(argv)
    if not 1024<=args.port<=65535:parser.error('Port must be in 1024..65535')
    if args.fixture and not args.idea:parser.error('--fixture requires --idea')
    if args.mode=='full' and args.fixture:parser.error('Path Finding fixture is not a Full Research input')
    initial=None
    if args.idea:
        import json
        try:
            conf=json.loads(Path(args.config).read_text('utf-8')) if args.config else None
        except (OSError,ValueError) as exc:parser.error('Config unavailable or invalid: '+type(exc).__name__)
        initial={'idea':args.idea,'mode':args.mode,'fixture':args.fixture,'config':conf,
                 'online':args.online,'language':args.lang,'as_of':args.as_of}
    return serve(args.root,args.port,open_browser=args.open and not args.no_browser,initial_run=initial)
if __name__=='__main__':raise SystemExit(main())
