# coding:utf-8
from models import *
import logging
LOG = logging.getLogger("CENI")


def get_island_ovss(island):
    """获取island所有交换机
    """
    LOG.debug('island_get_ovs')
