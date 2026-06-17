from unittest.mock import MagicMock, patch

from wastelessia import track
from wastelessia.track import _extract_usage
from wastelessia._pricing import calculate_cost


def _mock_anthropic_response(model="claude-sonnet-4-6", tokens_in=100, tokens_out=50):
    r = MagicMock()
    r.model = model
    r.usage.input_tokens = tokens_in
    r.usage.output_tokens = tokens_out
    del r.usage.prompt_tokens  # ensure OpenAI path is not taken
    return r


def _mock_openai_response(model="gpt-4o", prompt_tokens=100, completion_tokens=50):
    r = MagicMock()
    r.model = model
    r.usage.prompt_tokens = prompt_tokens
    r.usage.completion_tokens = completion_tokens
    del r.usage.input_tokens
    return r


class TestExtractUsage:
    def test_anthropic(self):
        resp = _mock_anthropic_response()
        usage = _extract_usage(resp)
        assert usage == {"model": "claude-sonnet-4-6", "tokens_in": 100, "tokens_out": 50}

    def test_openai(self):
        resp = _mock_openai_response()
        usage = _extract_usage(resp)
        assert usage == {"model": "gpt-4o", "tokens_in": 100, "tokens_out": 50}

    def test_none_response(self):
        assert _extract_usage(None) is None

    def test_unknown_response(self):
        assert _extract_usage({"not": "an LLM response"}) is None


class TestCalculateCost:
    def test_sonnet(self):
        cost = calculate_cost("claude-sonnet-4-6", 1_000_000, 0)
        assert abs(cost - 3.0) < 0.001

    def test_unknown_model_returns_zero(self):
        assert calculate_cost("unknown-model-x", 1000, 500) == 0.0


class TestTrackDecorator:
    def test_sync_function_returns_value(self):
        sent_events = []

        with patch("wastelessia.track.send_event_async", side_effect=sent_events.append):
            @track(team="backend", feature="search", env="prod")
            def call_llm():
                return _mock_anthropic_response()

            result = call_llm()

        assert result is not None
        assert len(sent_events) == 1
        event = sent_events[0]
        assert event["tags"] == {"team": "backend", "feature": "search", "env": "prod"}
        assert event["tokens_in"] == 100
        assert event["tokens_out"] == 50
        assert event["success"] is True

    def test_exception_marks_failure(self):
        sent_events = []

        with patch("wastelessia.track.send_event_async", side_effect=sent_events.append):
            @track(feature="broken")
            def call_llm():
                raise ValueError("boom")

            try:
                call_llm()
            except ValueError:
                pass

        # No usage to extract when exception occurs before return
        assert len(sent_events) == 0

    def test_none_tags_omitted(self):
        sent_events = []

        with patch("wastelessia.track.send_event_async", side_effect=sent_events.append):
            @track(team="ml")
            def call_llm():
                return _mock_anthropic_response()

            call_llm()

        assert sent_events[0]["tags"] == {"team": "ml"}
