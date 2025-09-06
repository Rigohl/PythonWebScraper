import pytest

from src.tui.app import ToastContainer, ToastNotification


@pytest.mark.asyncio
async def test_toast_lifecycle():
    """Tests that toasts can be shown and removed."""

    # Test notification logic without mounting
    container = ToastContainer()
    initial_count = len(container.notifications)

    toast = ToastNotification("Test message", "success", 0.1)
    container.notifications.append(toast)
    assert toast.message == "Test message"
    assert len(container.notifications) == initial_count + 1

    # Simulate removal after duration
    container.notifications.remove(toast)
    assert len(container.notifications) == initial_count


def test_toast_simple_lifecycle():
    """Test toast creation, showing, and removal."""
    from src.tui.app import ToastContainer

    container = ToastContainer()

    # Create a toast
    toast = ToastNotification("Test message", "info", 1.0)

    # Add to container (logic only)
    container.notifications.append(toast)
    assert toast in container.notifications
    assert len(container.notifications) == 1

    # Remove toast manually
    container.notifications.remove(toast)
    assert toast not in container.notifications
    assert len(container.notifications) == 0
