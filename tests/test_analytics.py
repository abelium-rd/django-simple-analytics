import pytest

from simple_analytics import middleware
from simple_analytics.models import VisitPerPage


@pytest.mark.parametrize(
    "test_path",
    [
        "/some-path",
        "/some-path/",
    ],
)
def test_normalize_request_path(test_path):
    assert not middleware.normalize_request_path(test_path).endswith("/")


def test_normalize_request_path_allows_root():
    assert middleware.normalize_request_path("/") == "/"


@pytest.mark.django_db
def test_process_analytics_no_existing_analytics_for_page(run_analytics, analytics_count):
    assert analytics_count() == 1


@pytest.mark.django_db
def test_process_analytics_existing_analytics_for_page(
    page_analytics, run_analytics, first_row_analytics
):
    assert first_row_analytics().view_count == 2


@pytest.mark.django_db
def test_process_analytics_keeps_found_and_not_found_visits_to_one_page_apart(test_request):
    middleware.process_analytics(test_request, exists=False)
    middleware.process_analytics(test_request, exists=True)
    middleware.process_analytics(test_request, exists=True)

    visits = sorted(VisitPerPage.objects.values_list("exists", "view_count"))
    assert visits == [(False, 1), (True, 2)]
