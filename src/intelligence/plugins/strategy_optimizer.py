from ..plugin_manager import BrainPlugin
import time

class StrategyOptimizerPlugin(BrainPlugin):
    name = "strategy_optimizer"
    version = "0.1"
    capabilities = ["strategy_tuning"]

    def on_load(self, brain_ref):
        self.brain = brain_ref
        self.last_eval = 0

    def periodic_tick(self):
        if time.time() - self.last_eval < 600:
            return None
        self.last_eval = time.time()
        if not hasattr(self.brain, 'strategy_history') or not self.brain.strategy_history:
            return None
        # Simple heuristic: promote goals with higher confidence
        avg_conf = sum(s['confidence'] for s in self.brain.strategy_history) / len(self.brain.strategy_history)
        high = [s for s in self.brain.strategy_history if s['confidence'] >= avg_conf]
        suggestion = None
        if high:
            suggestion = {
                'promote_goal': high[-1]['goal'],
                'avg_conf': avg_conf,
                'candidate_conf': high[-1]['confidence']
            }
        return suggestion
