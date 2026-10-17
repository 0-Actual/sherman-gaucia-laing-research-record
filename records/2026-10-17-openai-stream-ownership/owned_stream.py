"""Explicit ownership of an Agents SDK stream through public cancellation APIs.

Original project addition. See LICENSE-SCOPE.md and the repository LICENSE.
This module has no OpenAI import and copies no SDK implementation.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Protocol, TypeVar


Event = TypeVar("Event", covariant=True)


class StreamResult(Protocol[Event]):
    is_complete: bool

    def stream_events(self) -> AsyncIterator[Event]: ...

    def cancel(self) -> None: ...


async def _settle(task: asyncio.Task[None]) -> tuple[BaseException | None, BaseException | None]:
    """Retain cleanup ownership even when its waiting caller is cancelled again."""
    interruption: BaseException | None = None
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError as error:
            if task.cancelled():
                break
            interruption = error
        except BaseException:
            break
    try:
        task.result()
    except BaseException as error:
        return error, interruption
    return None, interruption


@asynccontextmanager
async def owned_stream(result: StreamResult[Event]) -> AsyncIterator[AsyncIterator[Event]]:
    """Own one stream, cancel on early exit, and await its cleanup boundary.

    Use exactly one consumer inside this context. Normal exhaustion does not
    request cancellation. A break, body failure, or caller cancellation does.
    Tools and providers must cooperate with cancellation; this is not a sandbox,
    a timeout, or a rollback mechanism for effects that have already happened.
    """
    source = result.stream_events()
    exhausted = False
    source_failed = False
    primary_error: BaseException | None = None

    async def events() -> AsyncIterator[Event]:
        nonlocal exhausted, source_failed
        while True:
            try:
                event = await anext(source)
            except StopAsyncIteration:
                exhausted = True
                return
            except BaseException:
                source_failed = True
                raise
            yield event

    iterator = events()
    try:
        yield iterator
    except BaseException as error:
        primary_error = error
        raise
    finally:
        async def cleanup() -> None:
            if not exhausted and not result.is_complete:
                result.cancel()
            await iterator.aclose()
            if not exhausted:
                # A cancelled source iterator can already be closed before its
                # background producer settles. Re-enter the public drain path.
                remaining = result.stream_events() if source_failed else source
                async for _ in remaining:
                    pass

        cleanup_task = asyncio.create_task(cleanup())
        cleanup_error, interruption = await _settle(cleanup_task)
        outcome_error = primary_error if primary_error is not None else interruption
        if outcome_error is None:
            outcome_error = cleanup_error
        if outcome_error is not None:
            for secondary in (cleanup_error, interruption):
                if secondary is not None and secondary is not outcome_error:
                    outcome_error.add_note(
                        "Stream cleanup also encountered " + type(secondary).__name__
                        + "; exception text is omitted to avoid copying payload data."
                    )
            if primary_error is None:
                raise outcome_error
