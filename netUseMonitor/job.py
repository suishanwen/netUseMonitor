import logging
from datetime import datetime, timedelta
from telecom.models import Online

logger = logging.getLogger('django')


def clean():
    now = datetime.now()
    min_ago_15 = now - timedelta(minutes=15)
    Online.objects.filter(update__lt=min_ago_15).delete()
    logger.info("delete inactive")
