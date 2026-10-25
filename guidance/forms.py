from typing import Any

from django import forms

from guidance.engine.channels import PREFERENCES
from guidance.engine.model import Answer, QuestionDef, Unknown

UNKNOWN_VALUE = "__unknown__"


class AnswerForm(forms.Form):
    def __init__(
        self,
        question: QuestionDef,
        data: Any = None,
        initial_answer: Answer | None = None,
    ) -> None:
        super().__init__(data)
        self.question = question
        choices = [(option.slug, option.label) for option in question.options]
        selected: list[str] = []
        unknown = initial_answer is Unknown.UNKNOWN
        if isinstance(initial_answer, frozenset):
            selected = sorted(initial_answer)
        if question.kind == "SINGLE":
            if question.allows_unknown:
                choices.append((UNKNOWN_VALUE, "Não sei"))
            self.fields["answer"] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                initial=UNKNOWN_VALUE if unknown else (selected[0] if selected else None),
            )
        else:
            self.fields["answer"] = forms.MultipleChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                required=False,  # vazio = "nenhuma destas"
                initial=selected,
            )
            if question.allows_unknown:
                self.fields["unknown"] = forms.BooleanField(
                    label="Não sei", required=False, initial=unknown
                )

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean() or {}
        if cleaned.get("unknown") and cleaned.get("answer"):
            raise forms.ValidationError('Marque "Não sei" ou escolha opções, não os dois.')
        return cleaned

    def cleaned_answer(self) -> Answer:
        value = self.cleaned_data["answer"]
        if value == UNKNOWN_VALUE or self.cleaned_data.get("unknown"):
            return Unknown.UNKNOWN
        return frozenset([value] if isinstance(value, str) else value)


class SearchForm(forms.Form):
    q = forms.CharField(label="Qual serviço você procura?", min_length=2, max_length=100)


class ChannelPreferenceForm(forms.Form):
    preference = forms.ChoiceField(
        label="Como você prefere ser atendido?",
        choices=[(p.slug, p.label) for p in PREFERENCES.values()],
        widget=forms.RadioSelect,
    )
