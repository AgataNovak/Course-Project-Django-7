from config.settings import CACHE_ENABLED
from sender.models import Receiver, Message, MailDeliver
from django.core.cache import cache


def get_receivers_from_cache():

    if not CACHE_ENABLED:
        return Receiver.objects.all()
    key = "product_list"
    receivers = cache.get(key)
    if receivers is not None:
        return receivers
    receivers = Receiver.objects.all()
    cache.set(key, receivers)
    return receivers


def get_messages_from_cache():

    if not CACHE_ENABLED:
        return Message.objects.all()
    key = "message_list"
    messages = cache.get(key)
    if messages is not None:
        return messages
    messages = Message.objects.all()
    cache.set(key, messages)
    return messages


def get_mailings_from_cache():

    if not CACHE_ENABLED:
        return MailDeliver.objects.all()
    key = "mailing_list"
    mailings = cache.get(key)
    if mailings is not None:
        return mailings
    mailings = MailDeliver.objects.all()
    cache.set(key, mailings)
    return mailings
