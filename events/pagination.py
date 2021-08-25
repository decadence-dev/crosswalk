import graphene
from graphene import relay
from graphql_relay.connection.arrayconnection import (
    get_offset_with_default,
    offset_to_cursor,
)


def limitskip(count, **kwargs):
    limit = count
    skip = get_offset_with_default(kwargs.get("after"))

    if before := kwargs.get("before"):
        limit = get_offset_with_default(before) - 1

    if first := kwargs.get("first"):
        limit = min(skip + first, limit)
    elif last := kwargs.get("last"):
        skip = max(limit - last, skip)

    return limit, skip


def gen_slice_pipeline(field, *fields, **kwargs):
    skip = get_offset_with_default(kwargs.get("after"))
    fields_project = {fld: 1 for fld in fields}
    if after := kwargs.get("after"):
        after_value = get_offset_with_default(after)
        yield {
            "$project": {
                field: {
                    "$slice": [f"${field}", {"$subtract": [after_value, "$count"]}]
                },
                **fields_project,
            }
        }

    if before := kwargs.get("before"):
        before_value = get_offset_with_default(before)
        yield {
            "$project": {
                field: {"$slice": [f"${field}", before_value - skip - 1]},
                **fields_project,
            }
        }

    if first := kwargs.get("first"):
        yield {"$project": {field: {"$slice": [f"${field}", first]}, **fields_project}}
    elif last := kwargs.get("last"):
        yield {"$project": {field: {"$slice": [f"${field}", -last]}, **fields_project}}


class SlicelessConnectionField(relay.ConnectionField):
    @classmethod
    async def resolve_connection(cls, connection_type, args, resolved):
        resolved = resolved or {}
        data = resolved.get("docs", [])
        count = resolved.get("count", 0)
        limit, skip = limitskip(count, **args)

        edges = [
            connection_type.Edge(node=doc, cursor=offset_to_cursor(skip + idx))
            for idx, doc in enumerate(data, 1)
        ]

        first_edge_cursor = edges[0].cursor if edges else None
        first_edge_index = get_offset_with_default(first_edge_cursor)

        last_edge_cursor = edges[-1].cursor if edges else None
        last_edge_index = get_offset_with_default(last_edge_cursor)

        return connection_type(
            edges=edges,
            page_info=graphene.PageInfo(
                start_cursor=first_edge_cursor,
                end_cursor=last_edge_cursor,
                has_previous_page=first_edge_index > 1,
                has_next_page=last_edge_index < count,
            ),
        )
