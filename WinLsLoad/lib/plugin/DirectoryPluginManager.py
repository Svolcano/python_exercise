import logging
import os
import sys

from imp import find_module,load_module,acquire_lock,release_lock

from PluginManager import PluginManager

logger = logging.getLogger(__name__)

class DirectoryPluginManager(PluginManager):
    """
    Plugin manager that loads plugins from plugin directories.
    """
    name = "directory"

    def __init__(self, plugin_dir, plugins=()):
        config = {}
        default_directory = plugin_dir
        self.directories = config.get("directories", (default_directory,))
        logger.info("========DirectoryPlugManager========%s", plugins)
        PluginManager.__init__(self, plugins)

    def loadPlugins(self):
        """
        Load plugins by iterating files in plugin directories.
        """
        plugins = []
        logger.info("********Directory directories:%s", self.directories)
        for dir in self.directories:
            try:
                for f in os.listdir(dir):
                    if f.endswith(".py") and f != "__init__.py" and f != "Plugin.py":
                        plugins.append((f[:-3], dir))
            except OSError, e:
                logger.info(e)
                continue

        fh  = None
        mod = None
        logger.info("********Directory all plugins:%s", plugins)
        for (name, dir) in plugins:
            try:
                acquire_lock()
                fh, filename, desc = find_module(name, [dir])
                logger.info("********Directory fh:%s,filename:%s,desc:%s:,name:%s", fh, filename, desc, name)
                old = sys.modules.get(name)
                if old is not None:
                    # make sure we get a fresh copy of anything we are trying
                    # to load from a new path
                    del sys.modules[name]
                mod = load_module(name, fh, filename, desc)
            finally:
                if fh:
                    fh.close()
                release_lock()
            if hasattr(mod, "__all__"):
                logger.info("********Directory mod  __all__:%s", mod.__all__)
                attrs = [getattr(mod, x) for x in mod.__all__]
                logger.info("********Directory attrs:%s", attrs)
                for plug in attrs:
                    try:
                        if True == plug.is_servlet :
                            pass
                    except:
                        continue
                    self._loadPlugin(plug())


