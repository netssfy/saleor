from graphene import ObjectType, String, Schema, List
from ..core.fields import BaseField
from .types import BulkOrderCampaign
from ..core.doc_category import DOC_CATEGORY_BULK_ORDER
from ...bulk_order import models

class BulkOrderQueries(ObjectType):
    bulk_order_campaign = BaseField(
        BulkOrderCampaign,
        description="look up bulk order campaign",
        doc_category=DOC_CATEGORY_BULK_ORDER
    )
    all_campaign = List(BulkOrderCampaign)

    @staticmethod
    def resolve_bulk_order_campaign(_root, info):
        return BulkOrderCampaign(name="foobar")

    @staticmethod
    def resolve_all_campaign(_root, info):
        return models.BulkOrderCampaign.objects.all()
