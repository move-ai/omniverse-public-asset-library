from functools import partial
import omni.ui as ui
import omni.kit
from urllib import request
from pathlib import Path
from .utils import get_data, get_random_frame, get_img_size, download_motion
import webbrowser

IMG_SIZE_DEVISOR = 2


class MoveaiAssetsMarketlaceWindow(ui.Window):
    data = get_data("https://molibapi.move.ai/motions")

    def __init__(self, ext_id):
        super().__init__("Move.ai Public Asset Library", width=500, height=600, visible=True)

        self.frame.set_build_fn(self._build_ui)
        self.deferred_dock_in("Content", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)
        self.asset_path_default: str = (
            omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id) + "/data"
        )

        self.asset_path_current: str = None

    def _set_path_current(self, path: str):
        self.asset_path_current = path

    def _build_ui(self):
        self.image_preview_width: int = None
        self.image_preview_height: int = None

        with self.frame:
            # Assets path and get previews button
            with ui.VStack():
                with ui.CollapsableFrame("Settings", height=0):
                    with ui.VStack():
                        with ui.HStack(height=20):
                            ui.Spacer(width=3)
                            ui.Label("Assets Path", width=70, height=0)
                            self.asset_field = ui.StringField(name="asset_path")

                            if not self.asset_path_current:
                                self.asset_field.model.set_value(self.asset_path_default)
                            else:
                                self.asset_field.model.set_value(self.asset_path_current)

                            self.asset_field.model.add_value_changed_fn(
                                lambda m: self._set_path_current(m.get_value_as_string())
                            )

                        ui.Button("Update Preview", width=0, height=0, clicked_fn=lambda: self._build_ui())

                # Grid with previews and import buttons
                with ui.CollapsableFrame("Preview"):
                    self.get_preview()

                with ui.HStack(height=20, style={"Button":{"background_color": "0xFFFF7E09"}}):
                    ui.Button("Join iPhone beta", width=0, height=0, clicked_fn=partial(
                                        webbrowser.open,
                                        "https://www.move.ai/mobile-device"
                                    ))

    def get_preview(self):
        self.asset_path = Path(self.asset_field.model.get_value_as_string())
        previews_path = self.asset_path / "previews"
        previews_path.mkdir(parents=True, exist_ok=True)

        with ui.HStack():
            with ui.ScrollingFrame(
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            ):

                self.asset_grid = ui.VGrid(style={"margin": 3})
                with self.asset_grid:
                    for motion in self.data["motions"]:
                        preview_path = previews_path / f"{motion['title']}.mp4"

                        preview = request.urlretrieve(motion["files"]["preview_url"], preview_path)

                        img_preview = get_random_frame(str(preview_path))

                        if not self.image_preview_width:
                            self.image_preview_width, self.image_preview_height = get_img_size(img_preview)
                            self.asset_grid.column_width = self.image_preview_width / IMG_SIZE_DEVISOR

                        with ui.VStack():
                            image = ui.Image(
                                img_preview,
                                fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                                alignment=ui.Alignment.CENTER,
                                height=self.image_preview_height / IMG_SIZE_DEVISOR,
                            )

                            with ui.HStack():
                                ui.Label(motion["title"], alignment=ui.Alignment.LEFT)

                                button = ui.Button(
                                    text="Import motion",
                                    name=motion["title"],
                                    alignment=ui.Alignment.RIGHT,
                                    width=0,
                                    height=0,
                                    asset_path=self.asset_path,
                                    clicked_fn=partial(
                                        download_motion,
                                        Path(self.asset_field.model.get_value_as_string()),
                                        motion["title"],
                                    ),
                                )

