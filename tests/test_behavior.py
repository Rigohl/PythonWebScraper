# tests/test_behavior.py
import os
import tempfile
import shutil
import pytest

# --- Test for self-improvement simulation output ---

def test_simulation_improvement_output():
    """Test that when simulation mode is enabled, a diff file is produced in the specified output directory."""
    try:
        from self_improvement import simulate_improvements
    except ImportError:
        pytest.skip('simulate_improvements not implemented')

    temp_dir = tempfile.mkdtemp()
    try:
        # Call the simulate_improvements function with simulation_output_dir set to temp_dir
        improvement_file = simulate_improvements(simulation_output_dir=temp_dir)
        # Check that the file was created
        assert improvement_file is not None, "No improvement file path returned"
        assert os.path.exists(improvement_file), "Improvement file was not created"
    finally:
        shutil.rmtree(temp_dir)


# --- Test for ThoughtManager behavior ---

def test_thought_manager():
    """Test that the ThoughtManager can score and select a thought."""
    try:
        from src.thought_engine import ThoughtManager
    except ImportError:
        pytest.skip('ThoughtManager not implemented')

    tm = ThoughtManager()
    tm.add_thought('Test thought', score=10)
    selected = tm.select_best_thought()
    assert selected is not None, "No thought selected"
    assert 'Test thought' in selected, "Selected thought does not match the input thought"


if __name__ == '__main__':
    # If run directly, execute the tests
    import sys
    sys.exit(pytest.main([__file__]))
