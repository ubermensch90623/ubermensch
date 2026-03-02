"""Mailbox 유닛 테스트."""

import asyncio

import pytest

from ubermensch.core.mailbox import BROADCAST, Mailbox


@pytest.fixture
def mailbox():
    mb = Mailbox()
    mb.register("alice")
    mb.register("bob")
    mb.register("charlie")
    return mb


class TestRegistration:
    def test_register(self, mailbox: Mailbox):
        assert set(mailbox.registered_agents) == {"alice", "bob", "charlie"}

    def test_register_duplicate_is_safe(self, mailbox: Mailbox):
        mailbox.register("alice")
        assert mailbox.registered_agents.count("alice") == 1

    def test_unregister(self, mailbox: Mailbox):
        mailbox.unregister("charlie")
        assert "charlie" not in mailbox.registered_agents

    def test_unregister_nonexistent_is_safe(self, mailbox: Mailbox):
        mailbox.unregister("nobody")  # no error


class TestSend:
    async def test_send_message(self, mailbox: Mailbox):
        msg = await mailbox.send("alice", "bob", "hello", body="hi there")
        assert msg.sender == "alice"
        assert msg.recipient == "bob"
        assert msg.subject == "hello"
        assert msg.body == "hi there"
        assert msg.id  # non-empty
        assert msg.timestamp > 0

    async def test_send_arrives_at_recipient(self, mailbox: Mailbox):
        await mailbox.send("alice", "bob", "test")
        assert mailbox.has_mail("bob")
        assert not mailbox.has_mail("alice")
        assert not mailbox.has_mail("charlie")

    async def test_send_to_unregistered(self, mailbox: Mailbox):
        msg = await mailbox.send("alice", "nobody", "test")
        assert msg.recipient == "nobody"  # 메시지 객체는 반환되지만 전달은 안 됨

    async def test_multiple_messages_fifo(self, mailbox: Mailbox):
        await mailbox.send("alice", "bob", "first")
        await mailbox.send("charlie", "bob", "second")
        await mailbox.send("alice", "bob", "third")

        msg1 = await mailbox.receive("bob", timeout=0.1)
        msg2 = await mailbox.receive("bob", timeout=0.1)
        msg3 = await mailbox.receive("bob", timeout=0.1)

        assert msg1.subject == "first"
        assert msg2.subject == "second"
        assert msg3.subject == "third"


class TestBroadcast:
    async def test_broadcast_reaches_all_except_sender(self, mailbox: Mailbox):
        await mailbox.broadcast("alice", "announcement", body="important")
        assert mailbox.has_mail("bob")
        assert mailbox.has_mail("charlie")
        assert not mailbox.has_mail("alice")

    async def test_broadcast_message_content(self, mailbox: Mailbox):
        msg = await mailbox.broadcast("alice", "news")
        assert msg.sender == "alice"
        assert msg.recipient == BROADCAST
        assert msg.subject == "news"


class TestReceive:
    async def test_receive_with_timeout(self, mailbox: Mailbox):
        msg = await mailbox.receive("alice", timeout=0.05)
        assert msg is None

    async def test_receive_unregistered(self, mailbox: Mailbox):
        msg = await mailbox.receive("nobody", timeout=0.05)
        assert msg is None

    async def test_receive_nowait_empty(self, mailbox: Mailbox):
        msg = mailbox.receive_nowait("alice")
        assert msg is None

    async def test_receive_nowait_with_message(self, mailbox: Mailbox):
        await mailbox.send("bob", "alice", "ping")
        msg = mailbox.receive_nowait("alice")
        assert msg is not None
        assert msg.subject == "ping"

    async def test_receive_nowait_unregistered(self, mailbox: Mailbox):
        msg = mailbox.receive_nowait("nobody")
        assert msg is None

    async def test_receive_blocks_until_message(self, mailbox: Mailbox):
        async def send_later():
            await asyncio.sleep(0.05)
            await mailbox.send("bob", "alice", "delayed")

        _task = asyncio.create_task(send_later())
        msg = await mailbox.receive("alice", timeout=2.0)
        assert msg is not None
        assert msg.subject == "delayed"


class TestUtilities:
    async def test_has_mail(self, mailbox: Mailbox):
        assert not mailbox.has_mail("alice")
        await mailbox.send("bob", "alice", "test")
        assert mailbox.has_mail("alice")

    async def test_has_mail_unregistered(self, mailbox: Mailbox):
        assert not mailbox.has_mail("nobody")

    async def test_pending_count(self, mailbox: Mailbox):
        assert mailbox.pending_count("alice") == 0
        await mailbox.send("bob", "alice", "1")
        await mailbox.send("charlie", "alice", "2")
        assert mailbox.pending_count("alice") == 2

    async def test_pending_count_unregistered(self, mailbox: Mailbox):
        assert mailbox.pending_count("nobody") == 0

    async def test_drain(self, mailbox: Mailbox):
        await mailbox.send("bob", "alice", "m1")
        await mailbox.send("charlie", "alice", "m2")
        await mailbox.send("bob", "alice", "m3")

        messages = mailbox.drain("alice")
        assert len(messages) == 3
        assert [m.subject for m in messages] == ["m1", "m2", "m3"]
        assert not mailbox.has_mail("alice")

    async def test_drain_empty(self, mailbox: Mailbox):
        messages = mailbox.drain("alice")
        assert messages == []

    async def test_drain_unregistered(self, mailbox: Mailbox):
        messages = mailbox.drain("nobody")
        assert messages == []
