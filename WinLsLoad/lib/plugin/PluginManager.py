#coding:utf-8

import logging

logger = logging.getLogger(__name__)

class PluginManager(object):
    """
    Base class for plugin managers. Does not implement loadPlugins, so it
    may only be used with a static list of plugins.
    """
    name = "base"

    def __init__(self, plugins=()):
        self.__plugins = []
        if plugins:
            self.addPlugins(plugins)

    def __iter__(self):
        return iter(self.plugins)

    def addPlugin(self, plug):
        logger.info("PluginManager add plugin:%s", plug)
        self.__plugins.append(plug)

    def addPlugins(self, plugins):
        for plug in plugins:
            self.addPlugin(plug)

    def delPlugin(self, plug):
        if plug in self.__plugins:
            self.__plugins.remove(plug)

    def delPlugins(self, plugins):
        for plug in plugins:
            self.delPlugin(plug)

    def getPlugins(self,name=None):
        plugins = []
        logger.info("self.plugins:%s", self.plugins)
        for plugin in self.__plugins:
            if (name is None or plugin.name == name):
                plugins.append(plugin)
        return plugins

    def getPlugins(self):
        plugins = {}
        logger.info("self.plugins:%s", self.plugins)
        for plugin in self.__plugins:
            plugins[plugin.name] = plugin

        logger.info("plugins:%s", plugins)
        return plugins

    def _loadPlugin(self, plug):       
        loaded = False
        logger.info("******PluginManager  _loadPlugin %s", self.plugins)
        for p in self.plugins:
            if p.name == plug.name:
                loaded = True
                break
        if not loaded:
            self.addPlugin(plug)
            logger.info("%s: loaded plugin %s " % (self.name, plug.name))

    def loadPlugins(self):
        pass

    def _get_plugins(self):
        return self.__plugins

    def _set_plugins(self, plugins):
        self.__plugins = []
        self.addPlugins(plugins)

    plugins = property(_get_plugins, _set_plugins, None,
                       """Access the list of plugins managed by
                       this plugin manager""")
    
    

