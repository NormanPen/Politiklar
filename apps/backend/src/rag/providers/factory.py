"""Factory and registry for modular AI providers."""

from collections.abc import Callable

from core.settings import Settings
from .base import AIProvider
from .gemini import GeminiProvider

_PROVIDER_REGISTRY: dict[str, type[AIProvider] | Callable[[Settings], AIProvider]] = {
    "gemini": GeminiProvider,
}


def register_ai_provider(
    name: str,
    provider_cls_or_factory: type[AIProvider] | Callable[[Settings], AIProvider],
) -> None:
    """Registers an AI provider class or factory by name."""
    _PROVIDER_REGISTRY[name.lower().strip()] = provider_cls_or_factory


def get_ai_provider(settings: Settings, provider_name: str | None = None) -> AIProvider:
    """Instantiates and returns the requested AI provider."""
    selected_name = (provider_name or getattr(settings, "ai_provider", "gemini")).lower().strip()
    provider_cls = _PROVIDER_REGISTRY.get(selected_name)
    if provider_cls is None:
        supported = ", ".join(sorted(_PROVIDER_REGISTRY.keys()))
        raise ValueError(
            f"Unknown AI provider '{selected_name}'. Supported providers: {supported}"
        )
    return provider_cls(settings)
