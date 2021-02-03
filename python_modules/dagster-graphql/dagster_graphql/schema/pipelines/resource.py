import graphene
from dagster import check
from dagster.core.snap import ConfigSchemaSnapshot, ResourceDefSnap

from ..config_types import GrapheneConfigTypeField


class GrapheneResource(graphene.ObjectType):
    name = graphene.NonNull(graphene.String)
    description = graphene.String()
    configField = graphene.Field(GrapheneConfigTypeField)

    class Meta:
        name = "Resource"

    def __init__(self, config_schema_snapshot, resource_def_snap):
        super().__init__()
        self._config_schema_snapshot = check.inst_param(
            config_schema_snapshot, "config_schema_snapshot", ConfigSchemaSnapshot
        )
        self._resource_dep_snap = check.inst_param(
            resource_def_snap, "resource_def_snap", ResourceDefSnap
        )
        self.name = resource_def_snap.name
        self.description = resource_def_snap.description

    def resolve_configField(self, _graphene_info):
        return (
            GrapheneConfigTypeField(
                config_schema_snapshot=self._config_schema_snapshot,
                field_snap=self._resource_dep_snap.config_field_snap,
            )
            if self._resource_dep_snap.config_field_snap
            else None
        )