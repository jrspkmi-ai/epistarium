"""Execute actual Jorhas Python functions with observable checkpoints."""
from threading import Thread
from .events import observe_steps
from .store import ObservatoryStore
from ..i18n import language_context

PERSONA_STEPS = {
    'liora':'Liora','agresa':'Agresa','retho':'Retho','domares':'Domares',
    'synthia':'Synthia','vanlan':'Vanlan','ideon':'Ideon','ideon origo':'Ideon',
    'quilo':'Quilo','huxley':'Huxley',
}


class ObservatoryRunner:
    def __init__(self,store:ObservatoryStore):
        self.store=store
        self.threads={}

    def launch(self,run_id):
        with self.store.lock:
            state=self.store.get(run_id)
            if state['status']!='QUEUED':raise ValueError('Run is not queued')
            if run_id in self.threads and self.threads[run_id].is_alive():raise ValueError('Run already active')
            self.store.update(run_id,status='RUNNING')
            thread=Thread(target=self._worker,args=(run_id,),daemon=True,name='epistarium-'+run_id[:8])
            self.threads[run_id]=thread
            thread.start()

    def decide(self,run_id,decision,reason=''):
        response=self.store.record_decision(run_id,decision,reason)
        if decision=='approve' and response['record']['gate']=='ONLINE_ACCESS':
            self.launch(run_id)
        return response['state']

    def _worker(self,run_id):
        from .. import jorhas
        state=self.store.get(run_id)
        self.store.persona(run_id,'Jorhas','RUNNING',detail='Jorhas started the actual Python workflow.')
        self.store.append(run_id,'execution_started',mode=state['mode'],synthetic=state['synthetic'],
                          message='Python workflow started. No semantic verification implied.')

        def on_step(step):
            status=step.get('status','NOT_RUN')
            name=str(step.get('step',''))
            persona=PERSONA_STEPS.get(name.lower())
            if persona:
                self.store.persona(run_id,persona,status if status in ('SUCCESS','PARTIAL','BLOCKED','FAILED') else 'NOT_RUN',
                                   detail=f'{persona}: recorded {status}')
            self.store.append(run_id,'python_step',step=name[:90],status=status,
                              message=f'Python step {name[:80]} recorded {status}.',
                              input_count=len(step.get('inputs') or []),output_count=len(step.get('outputs') or []))
        try:
            with language_context(state['language']),observe_steps(on_step):
                target=self.store.outputs/run_id
                if state['mode']=='pathfind':
                    result=jorhas.pathfind(state['idea'],target,fixture=state['fixture'],
                           config=state['config'],allow_live=state['online_requested'],
                           as_of=state['as_of'],timezone=state['timezone'])
                    execution=result['manifest']['status']
                    deliverable='PARTIAL'
                else:
                    result=jorhas.full_research(state['idea'],target,config=state['config'],
                           as_of=state['as_of'],timezone=state['timezone'],allow_live=state['online_requested'])
                    execution=result['execution_status']
                    deliverable=result['deliverable_status']
            self.store.persona(run_id,'Jorhas',execution if execution in ('SUCCESS','PARTIAL','BLOCKED','FAILED') else 'PARTIAL',
                               detail=f'Jorhas completed orchestration; execution status {execution}.')
            self.store.update(run_id,status='AWAITING_APPROVAL',execution_status=execution,
                              deliverable_status=deliverable,pending_gate='FINAL_ARTIFACT')
            self.store.append(run_id,'approval_requested',gate='FINAL_ARTIFACT',
                              message='Researcher review is required before authorizing the run package; no claim is automatically verified.')
        except Exception as exc:
            # Only show exception type in the UI; full source paths or private
            # input content never appear in the public browser event feed.
            self.store.persona(run_id,'Jorhas','FAILED',detail='Execution failed; inspect local logs.')
            self.store.update(run_id,status='FAILED',execution_status='FAILED',deliverable_status='INCOMPLETE')
            self.store.append(run_id,'execution_failed',error_type=type(exc).__name__,
                              message='The Python workflow failed; run stopped without approval.')
