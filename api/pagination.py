import graphene
from graphene import relay
from graphql_relay.connection.arrayconnection import (
    get_offset_with_default,
    offset_to_cursor,
)


def limitskip(count, **kwargs):
    """
    Return limit/offest values for mongo cursor.

    Args:
        first (int): limit of documents in the query
        last (int): limit of documents in the query from the end of the collection
        after (str): skip of ducuments in the query, expects base64 string
        before (str): skip of documents in the query from the end, expects base64 string
    """
    limit = count
    skip = get_offset_with_default(kwargs.get("after"))

    if before := kwargs.get("before"):
        limit = get_offset_with_default(before) - 1

    if first := kwargs.get("first"):
        limit = min(first, limit)
    elif last := kwargs.get("last"):
        skip = max(limit - last, skip)

    return limit, skip


class MotorConnectionField(relay.ConnectionField):
    """Mongo Motor relay ConnectionField implementation."""

    @classmethod
    async def resolve_connection(cls, connection_type, args, resolved):
        """
        Resolve connection object with pagination.

        Args:
            connection_type: relay connection type
            args (dict): query arguments
            resolved (tuple): pair of mongo motor collection cursor and count values

        Returns:
            relay.Connection: connection_type with query limited by limit and offset
        """
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
