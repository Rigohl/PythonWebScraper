import pytest
from src.intelligence.rule_engine import Rule, RuleCondition, RuleAction, RuleEngine

# Fixtures for sample data
@pytest.fixture
def sample_domain_data_high_error():
    return {
        'domain': 'example.com',
        'error_rate': 0.6,
        'response_time': 1.2,
        'structure_drift_score': 0.1,
        'healing_ratio': 0.05,
        'hour_success_gain': 0.1,
        'best_hour': 10
    }

@pytest.fixture
def sample_domain_data_slow():
    return {
        'domain': 'slowsite.com',
        'error_rate': 0.1,
        'response_time': 3.5,
        'response_time_ratio': 2.0, # response_time / global_avg
        'global_avg': 1.75
    }

@pytest.fixture
def sample_domain_data_drift():
    return {
        'domain': 'drifty.com',
        'error_rate': 0.2,
        'response_time': 1.0,
        'structure_drift_score': 0.55
    }

# Tests for RuleCondition
class TestRuleCondition:
    def test_evaluate_gte_true(self, sample_domain_data_high_error):
        condition = RuleCondition(metric='error_rate', operator='gte', value=0.5)
        assert condition.evaluate(sample_domain_data_high_error) is True

    def test_evaluate_gte_false(self, sample_domain_data_high_error):
        condition = RuleCondition(metric='error_rate', operator='gte', value=0.7)
        assert condition.evaluate(sample_domain_data_high_error) is False

    def test_evaluate_lt_true(self, sample_domain_data_slow):
        condition = RuleCondition(metric='error_rate', operator='lt', value=0.2)
        assert condition.evaluate(sample_domain_data_slow) is True

    def test_evaluate_eq_true(self):
        condition = RuleCondition(metric='domain', operator='eq', value='example.com')
        assert condition.evaluate({'domain': 'example.com'}) is True

    def test_evaluate_contains_true(self):
        condition = RuleCondition(metric='domain', operator='contains', value='example')
        assert condition.evaluate({'domain': 'example.com'}) is True

    def test_evaluate_pattern_true(self):
        condition = RuleCondition(metric='domain', operator='pattern', value=r'example\\.com')
        assert condition.evaluate({'domain': 'example.com'}) is True

    def test_evaluate_invalid_metric(self, sample_domain_data_high_error):
        condition = RuleCondition(metric='non_existent_metric', operator='gte', value=0.5)
        assert condition.evaluate(sample_domain_data_high_error) is False

# Tests for RuleAction
class TestRuleAction:
    def test_execute(self):
        action = RuleAction(
            type='suggest',
            category='stability',
            severity='high',
            template='High error rate on {domain}: {error_rate}'
        )
        data = {'domain': 'test.com', 'error_rate': 0.8}
        result = action.execute(data)
        assert result['type'] == 'suggest'
        assert result['category'] == 'stability'
        assert result['message'] == 'High error rate on test.com: 0.8'

# Tests for Rule
class TestRule:
    def test_evaluate_true(self, sample_domain_data_high_error):
        rule = Rule.from_dict({
            'id': 'test_rule',
            'condition': {'metric': 'error_rate', 'operator': 'gte', 'value': 0.5},
            'action': {'type': 'suggest', 'category': 'stability', 'template': 'Error rate is high'}
        })
        result = rule.evaluate(sample_domain_data_high_error)
        assert result is not None
        assert result['rule_id'] == 'test_rule'
        assert result['message'] == 'Error rate is high'

    def test_evaluate_false(self, sample_domain_data_high_error):
        rule = Rule.from_dict({
            'id': 'test_rule',
            'condition': {'metric': 'error_rate', 'operator': 'lt', 'value': 0.5},
            'action': {'type': 'suggest', 'category': 'stability', 'template': 'Error rate is low'}
        })
        result = rule.evaluate(sample_domain_data_high_error)
        assert result is None

    def test_evaluate_disabled(self, sample_domain_data_high_error):
        rule = Rule.from_dict({
            'id': 'test_rule',
            'condition': {'metric': 'error_rate', 'operator': 'gte', 'value': 0.5},
            'action': {'type': 'suggest', 'category': 'stability', 'template': 'Error rate is high'},
            'metadata': {'enabled': False}
        })
        result = rule.evaluate(sample_domain_data_high_error)
        assert result is None

# Tests for RuleEngine
class TestRuleEngine:
    def test_initialization(self):
        engine = RuleEngine()
        assert len(engine.rules) > 0
        assert 'high_error_rate_backoff' in engine.rules

    def test_evaluate_all_triggers_rule(self, sample_domain_data_high_error):
        engine = RuleEngine()
        results = engine.evaluate_all(sample_domain_data_high_error)
        assert len(results) > 0
        assert results[0]['rule_id'] == 'high_error_rate_backoff'

    def test_evaluate_all_triggers_multiple_rules(self, sample_domain_data_drift):
        # This data should trigger the drift rule
        engine = RuleEngine()
        results = engine.evaluate_all(sample_domain_data_drift)
        assert len(results) > 0
        assert 'structural_drift_high' in [r['rule_id'] for r in results]

    def test_evaluate_all_no_trigger(self):
        engine = RuleEngine()
        data = {'error_rate': 0.1, 'structure_drift_score': 0.1}
        results = engine.evaluate_all(data)
        assert len(results) == 0

    def test_add_and_remove_rule(self):
        engine = RuleEngine()
        initial_count = len(engine.rules)
        new_rule = Rule.from_dict({
            'id': 'custom_rule',
            'condition': {'metric': 'custom_metric', 'operator': 'eq', 'value': 'test'},
            'action': {'type': 'alert', 'category': 'custom', 'template': 'Custom rule triggered'}
        })
        engine.add_rule(new_rule)
        assert len(engine.rules) == initial_count + 1
        assert 'custom_rule' in engine.rules

        results = engine.evaluate_all({'custom_metric': 'test'})
        assert len(results) == 1
        assert results[0]['rule_id'] == 'custom_rule'

        engine.remove_rule('custom_rule')
        assert len(engine.rules) == initial_count
        assert 'custom_rule' not in engine.rules