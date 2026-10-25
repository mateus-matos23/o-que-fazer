import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from catalog.models import (
    AnswerOption,
    Dependency,
    Procedure,
    ProcedureDetail,
    Question,
    Rule,
)
from sources.models import Agency, Jurisdiction, Source, SourceSnapshot

pytestmark = pytest.mark.django_db


@pytest.fixture
def agency() -> Agency:
    return Agency.objects.create(
        slug="receita-federal", name="Receita Federal", jurisdiction=Jurisdiction.FEDERAL
    )


@pytest.fixture
def snapshot(agency: Agency) -> SourceSnapshot:
    source = Source.objects.create(
        slug="api-10416",
        agency=agency,
        url="https://servicos.gov.br/api/v1/servicos/10416",
        format=Source.Format.GOVBR_API,
        jurisdiction=Jurisdiction.FEDERAL,
    )
    return SourceSnapshot.objects.create(source=source, content_sha256="a" * 64, raw_text="{}")


def make_procedure(slug: str, agency: Agency, snapshot: SourceSnapshot) -> Procedure:
    return Procedure.objects.create(
        slug=slug,
        title=slug,
        description="d",
        agency=agency,
        jurisdiction=Jurisdiction.FEDERAL,
        snapshot=snapshot,
        excerpt="trecho",
    )


@pytest.fixture
def pair(agency: Agency, snapshot: SourceSnapshot) -> tuple[Procedure, Procedure]:
    return make_procedure("a", agency, snapshot), make_procedure("b", agency, snapshot)


@pytest.fixture
def rule(snapshot: SourceSnapshot) -> Rule:
    return Rule.objects.create(slug="r", explanation="e", snapshot=snapshot, excerpt="trecho")


def make_dependency(
    pair: tuple[Procedure, Procedure],
    snapshot: SourceSnapshot,
    kind: Dependency.Kind,
    rule: Rule | None = None,
) -> Dependency:
    return Dependency.objects.create(
        before=pair[0], after=pair[1], kind=kind, rule=rule, snapshot=snapshot, excerpt="trecho"
    )


def test_conditional_dependency_requires_rule(
    pair: tuple[Procedure, Procedure], snapshot: SourceSnapshot
) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_dependency(pair, snapshot, Dependency.Kind.CONDITIONAL)


def test_non_conditional_dependency_rejects_rule(
    pair: tuple[Procedure, Procedure], snapshot: SourceSnapshot, rule: Rule
) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_dependency(pair, snapshot, Dependency.Kind.MANDATORY, rule)


def test_valid_dependencies_are_accepted(
    pair: tuple[Procedure, Procedure], snapshot: SourceSnapshot, rule: Rule
) -> None:
    make_dependency(pair, snapshot, Dependency.Kind.CONDITIONAL, rule)
    Dependency.objects.all().delete()
    make_dependency(pair, snapshot, Dependency.Kind.MANDATORY)
    assert Dependency.objects.count() == 1


def test_dependency_cannot_point_to_itself(
    pair: tuple[Procedure, Procedure], snapshot: SourceSnapshot
) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        Dependency.objects.create(
            before=pair[0],
            after=pair[0],
            kind=Dependency.Kind.MANDATORY,
            snapshot=snapshot,
            excerpt="trecho",
        )


def test_dependency_pair_is_unique(
    pair: tuple[Procedure, Procedure], snapshot: SourceSnapshot
) -> None:
    make_dependency(pair, snapshot, Dependency.Kind.MANDATORY)
    with pytest.raises(IntegrityError), transaction.atomic():
        make_dependency(pair, snapshot, Dependency.Kind.RECOMMENDED)


def test_option_slug_is_unique_per_question() -> None:
    q1 = Question.objects.create(slug="q1", text="?", kind=Question.Kind.SINGLE)
    q2 = Question.objects.create(slug="q2", text="?", kind=Question.Kind.SINGLE)
    AnswerOption.objects.create(question=q1, slug="sim", label="Sim")
    AnswerOption.objects.create(question=q2, slug="sim", label="Sim")
    with pytest.raises(IntegrityError), transaction.atomic():
        AnswerOption.objects.create(question=q1, slug="sim", label="Sim de novo")


def test_procedure_detail_kind_is_unique_per_procedure(
    pair: tuple[Procedure, Procedure], snapshot: SourceSnapshot
) -> None:
    def detail(procedure: Procedure, kind: ProcedureDetail.Kind) -> ProcedureDetail:
        return ProcedureDetail.objects.create(
            procedure=procedure, kind=kind, text="t", snapshot=snapshot, excerpt="trecho"
        )

    detail(pair[0], ProcedureDetail.Kind.COST)
    detail(pair[0], ProcedureDetail.Kind.DEADLINE)
    detail(pair[1], ProcedureDetail.Kind.COST)
    with pytest.raises(IntegrityError), transaction.atomic():
        detail(pair[0], ProcedureDetail.Kind.COST)


def test_cited_snapshot_cannot_be_deleted(
    pair: tuple[Procedure, Procedure], snapshot: SourceSnapshot
) -> None:
    with pytest.raises(ProtectedError):
        snapshot.delete()
