"""Preferência de atendimento (RN14): só reordena canais, nunca os esconde."""

from collections.abc import Sequence
from dataclasses import dataclass

from guidance.engine.model import ChannelDef


@dataclass(frozen=True, slots=True)
class ChannelPreference:
    slug: str
    label: str
    kinds: frozenset[str]  # vazio = sem preferência
    missing_notice: str  # RN11: "não informado", nunca "não existe"


# Slugs em português, como os demais valores de URL e sessão (`recomecar`, `respostas`).
# EMAIL não pertence a nenhum grupo: nunca é priorizado.
PREFERENCES: dict[str, ChannelPreference] = {
    p.slug: p
    for p in (
        ChannelPreference(
            "internet",
            "Pela internet ou aplicativo",
            frozenset({"ONLINE", "APP"}),
            "Atendimento pela internet ou aplicativo não informado na fonte para esta etapa.",
        ),
        ChannelPreference(
            "telefone",
            "Por telefone",
            frozenset({"PHONE"}),
            "Atendimento por telefone não informado na fonte para esta etapa.",
        ),
        ChannelPreference(
            "presencial",
            "Pessoalmente",
            frozenset({"IN_PERSON"}),
            "Atendimento presencial não informado na fonte para esta etapa.",
        ),
        ChannelPreference("tanto-faz", "Tanto faz", frozenset(), ""),
    )
}


def order_channels(
    channels: Sequence[ChannelDef], preference: ChannelPreference | None
) -> tuple[ChannelDef, ...]:
    """Canais preferidos primeiro; a ordem original é mantida dentro de cada grupo."""
    if preference is None:
        return tuple(channels)
    return tuple(sorted(channels, key=lambda c: c.kind not in preference.kinds))  # sort é estável


def lacks_preferred(channels: Sequence[ChannelDef], preference: ChannelPreference | None) -> bool:
    """True quando há preferência real e a etapa tem canais, mas nenhum a atende.

    Sem nenhum canal a página já mostra "Não informado"; o aviso seria redundante.
    """
    return (
        preference is not None
        and bool(preference.kinds)
        and bool(channels)
        and not any(c.kind in preference.kinds for c in channels)
    )
