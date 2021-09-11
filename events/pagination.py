import graphene
from graphene import relay
from graphql_relay.connection.arrayconnection import (
    get_offset_with_default,
    offset_to_cursor,
)


def limitskip(count, **kwargs):
    # TODO fix limit/offset calculation logic
    #  Currently it acts wrong.
    limit = count
    skip = get_offset_with_default(kwargs.get("after"))

    if before := kwargs.get("before"):
        limit = get_offset_with_default(before) - 1

    if first := kwargs.get("first"):
        limit = min(skip + first, limit)
    elif last := kwargs.get("last"):
        skip = max(limit - last, skip)

    return limit, skip


class MotorConnectionField(relay.ConnectionField):
    @classmethod
    async def resolve_connection(cls, connection_type, args, resolved):
        cursor, count = resolved
        limit, skip = limitskip(count, **args)

        if limit:
            cursor.limit(limit)

        if skip:
            cursor.skip(skip)

        edges = [
            connection_type.Edge(node=doc, cursor=offset_to_cursor(skip + idx))
            for idx, doc in enumerate([_ async for _ in cursor], 1)
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
