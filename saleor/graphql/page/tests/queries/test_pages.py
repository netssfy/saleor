import graphene
import pytest
from django.utils import timezone
from freezegun import freeze_time

from .....page.models import Page
from .....tests.utils import dummy_editorjs
from ....tests.utils import get_graphql_content

QUERY_PAGES_WITH_FILTER = """
    query ($filter: PageFilterInput) {
        pages(first: 5, filter:$filter) {
            totalCount
            edges {
                node {
                    id
                }
            }
        }
    }
"""


@pytest.mark.parametrize(
    "page_filter, count",
    [
        ({"search": "Page1"}, 2),
        ({"search": "about"}, 1),
        ({"search": "test"}, 1),
        ({"search": "slug"}, 3),
        ({"search": "Page"}, 2),
    ],
)
def test_pages_query_with_filter(
    page_filter, count, staff_api_client, permission_manage_pages, page_type
):
    query = QUERY_PAGES_WITH_FILTER
    Page.objects.create(
        title="Page1",
        slug="slug_page_1",
        content=dummy_editorjs("Content for page 1"),
        page_type=page_type,
    )
    Page.objects.create(
        title="Page2",
        slug="slug_page_2",
        content=dummy_editorjs("Content for page 2"),
        page_type=page_type,
    )
    Page.objects.create(
        title="About",
        slug="slug_about",
        content=dummy_editorjs("About test content"),
        page_type=page_type,
    )
    variables = {"filter": page_filter}
    staff_api_client.user.user_permissions.add(permission_manage_pages)
    response = staff_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    assert content["data"]["pages"]["totalCount"] == count


def test_pages_query_with_filter_by_page_type(
    staff_api_client, permission_manage_pages, page_type_list
):
    query = QUERY_PAGES_WITH_FILTER
    page_type_ids = [
        graphene.Node.to_global_id("PageType", page_type.id)
        for page_type in page_type_list
    ][:2]

    variables = {"filter": {"pageTypes": page_type_ids}}
    staff_api_client.user.user_permissions.add(permission_manage_pages)
    response = staff_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    assert content["data"]["pages"]["totalCount"] == 2


def test_pages_query_with_filter_by_ids(
    staff_api_client, permission_manage_pages, page_list, page_list_unpublished
):
    query = QUERY_PAGES_WITH_FILTER

    page_ids = [
        graphene.Node.to_global_id("Page", page.pk)
        for page in [page_list[0], page_list_unpublished[-1]]
    ]
    variables = {"filter": {"ids": page_ids}}
    staff_api_client.user.user_permissions.add(permission_manage_pages)
    response = staff_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    assert content["data"]["pages"]["totalCount"] == len(page_ids)


QUERY_PAGE_WITH_SORT = """
    query ($sort_by: PageSortingInput!) {
        pages(first:5, sortBy: $sort_by) {
            edges{
                node{
                    title
                }
            }
        }
    }
"""


@pytest.mark.parametrize(
    "page_sort, result_order",
    [
        ({"field": "TITLE", "direction": "ASC"}, ["About", "Page1", "Page2"]),
        ({"field": "TITLE", "direction": "DESC"}, ["Page2", "Page1", "About"]),
        ({"field": "SLUG", "direction": "ASC"}, ["About", "Page2", "Page1"]),
        ({"field": "SLUG", "direction": "DESC"}, ["Page1", "Page2", "About"]),
        ({"field": "VISIBILITY", "direction": "ASC"}, ["Page2", "About", "Page1"]),
        ({"field": "VISIBILITY", "direction": "DESC"}, ["Page1", "About", "Page2"]),
        ({"field": "CREATION_DATE", "direction": "ASC"}, ["Page1", "About", "Page2"]),
        ({"field": "CREATION_DATE", "direction": "DESC"}, ["Page2", "About", "Page1"]),
        (
            {"field": "PUBLICATION_DATE", "direction": "ASC"},
            ["Page1", "Page2", "About"],
        ),
        (
            {"field": "PUBLICATION_DATE", "direction": "DESC"},
            ["About", "Page2", "Page1"],
        ),
    ],
)
def test_query_pages_with_sort(
    page_sort, result_order, staff_api_client, permission_manage_pages, page_type
):
    with freeze_time("2017-05-31 12:00:01"):
        Page.objects.create(
            title="Page1",
            slug="slug_page_1",
            content=dummy_editorjs("p1."),
            is_published=True,
            publication_date=timezone.now().replace(year=2018, month=12, day=5),
            page_type=page_type,
        )
    with freeze_time("2019-05-31 12:00:01"):
        Page.objects.create(
            title="Page2",
            slug="page_2",
            content=dummy_editorjs("p2."),
            is_published=False,
            publication_date=timezone.now().replace(year=2019, month=12, day=5),
            page_type=page_type,
        )
    with freeze_time("2018-05-31 12:00:01"):
        Page.objects.create(
            title="About",
            slug="about",
            content=dummy_editorjs("Ab."),
            is_published=True,
            page_type=page_type,
        )
    variables = {"sort_by": page_sort}
    staff_api_client.user.user_permissions.add(permission_manage_pages)
    response = staff_api_client.post_graphql(QUERY_PAGE_WITH_SORT, variables)
    content = get_graphql_content(response)
    pages = content["data"]["pages"]["edges"]

    for order, page_name in enumerate(result_order):
        assert pages[order]["node"]["title"] == page_name