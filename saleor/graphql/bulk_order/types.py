from graphene import ObjectType, String, Schema
from ...bulk_order import models
from ..core.types.model import ModelObjectType

class BulkOrderCampaign(ModelObjectType[models.BulkOrderCampaign]):
    name = String(description="name of campaign")

    class Meta:
        model = models.BulkOrderCampaign
