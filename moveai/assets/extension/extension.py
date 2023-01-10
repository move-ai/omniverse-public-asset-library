from ctypes import alignment
import omni.ext
from .window import MoveaiAssetsMarketlaceWindow


class MoveaiAssetsMarketlace(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[moveai.assets] Move.ai Public Asset Library startup")
        self._window = MoveaiAssetsMarketlaceWindow(ext_id)

    def on_shutdown(self):
        if self._window is not None:
            self._window.destroy()
            self._window = None
            print("[moveai.assets] Move.ai Public Asset Library shutdown")
